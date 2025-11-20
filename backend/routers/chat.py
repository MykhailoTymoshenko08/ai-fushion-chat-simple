from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime
import asyncio

from backend.db import get_db
from backend.models import Chat, Message, ProviderResponse
from backend.schemas import (
    ChatCreate, ChatResponse, MessageSend, MessageResponse, 
    ChatHistoryResponse, ProviderResponseSchema
)
from backend.providers.base import ProviderClient
from backend.providers.stubs import StubProvider
from backend.providers.openai import OpenAIProvider
from backend.providers.groq import GroqProvider
from backend.providers.deepseek import DeepSeekProvider
from backend.providers.gemini import GeminiProvider
from backend.aggregator.synth import Synthesizer
from backend.streaming.websocket import websocket_manager

router = APIRouter()

# Initialize providers
providers = {
    "openai": OpenAIProvider(),
    "groq": GroqProvider(), 
    "deepseek": DeepSeekProvider(),
    "gemini": GeminiProvider()
}

# Fallback to stubs if no API keys
active_providers = {}
for name, provider in providers.items():
    if provider.is_configured():
        active_providers[name] = provider
    else:
        active_providers[name] = StubProvider(name)

synthesizer = Synthesizer()

@router.post("/chat/new", response_model=ChatResponse)
async def create_chat(chat_data: ChatCreate, db: AsyncSession = Depends(get_db)):
    chat = Chat(title=chat_data.title)
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return ChatResponse(
        id=chat.id,
        title=chat.title,
        created_at=chat.created_at,
        updated_at=chat.updated_at
    )

@router.post("/chat/send")
async def send_message(
    message_data: MessageSend, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    # Create new chat if no chat_id provided
    if not message_data.chat_id:
        chat = Chat()
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        chat_id = chat.id
    else:
        chat_id = message_data.chat_id
        # Verify chat exists
        result = await db.execute(select(Chat).where(Chat.id == chat_id))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Chat not found")

    # Save user message
    user_message = Message(
        chat_id=chat_id,
        content=message_data.message,
        is_user=True
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)

    # Start background task to process AI responses
    background_tasks.add_task(
        process_ai_responses, 
        chat_id, 
        user_message.id, 
        message_data.message,
        message_data.mode or "aggregate"  # Default to aggregate mode
    )

    return {"chat_id": chat_id, "user_message_id": user_message.id}

async def process_ai_responses(chat_id: str, user_message_id: str, user_message: str, mode: str):
    """Process AI responses based on selected mode"""
    if mode == "single":
        # Use only one provider (default to openai)
        selected_provider = list(active_providers.keys())[0]
        await process_single_provider(chat_id, user_message_id, user_message, selected_provider)
    elif mode == "multiple":
        await process_multiple_providers(chat_id, user_message_id, user_message)
    else:  # aggregate mode
        await process_aggregated_response(chat_id, user_message_id, user_message)

async def process_single_provider(chat_id: str, user_message_id: str, user_message: str, provider_name: str):
    """Process response from a single provider"""
    provider = active_providers.get(provider_name)
    if not provider:
        return

    full_response = ""
    try:
        async for token in provider.generate(user_message):
            await websocket_manager.send_provider_token(chat_id, provider_name, token)
            full_response += token
        
        await websocket_manager.send_provider_token(chat_id, provider_name, "", True)
        
        # Save the response
        async for db in get_db():
            response_message = Message(
                chat_id=chat_id,
                content=full_response,
                is_user=False
            )
            db.add(response_message)
            await db.commit()
            await db.refresh(response_message)

            # Save provider response
            provider_response = ProviderResponse(
                message_id=response_message.id,
                provider=provider_name,
                content=full_response
            )
            db.add(provider_response)
            await db.commit()

    except Exception as e:
        error_msg = f"Error from {provider_name}: {str(e)}"
        await websocket_manager.send_provider_token(chat_id, provider_name, error_msg, True)

async def process_multiple_providers(chat_id: str, user_message_id: str, user_message: str):
    """Process responses from all providers separately"""
    tasks = []
    for provider_name, provider in active_providers.items():
        task = process_single_provider(chat_id, user_message_id, user_message, provider_name)
        tasks.append(task)
    
    await asyncio.gather(*tasks, return_exceptions=True)

async def process_aggregated_response(chat_id: str, user_message_id: str, user_message: str):
    """Process responses from all providers and synthesize them"""
    responses = {}
    tasks = []

    async def collect_provider_response(provider_name: str, provider: ProviderClient):
        full_response = ""
        try:
            async for token in provider.generate(user_message):
                await websocket_manager.send_provider_token(chat_id, provider_name, token)
                full_response += token
            await websocket_manager.send_provider_token(chat_id, provider_name, "", True)
            responses[provider_name] = full_response
        except Exception as e:
            error_msg = f"Error from {provider_name}: {str(e)}"
            await websocket_manager.send_provider_token(chat_id, provider_name, error_msg, True)
            responses[provider_name] = error_msg

    # Start all providers
    for provider_name, provider in active_providers.items():
        task = collect_provider_response(provider_name, provider)
        tasks.append(task)

    # Wait for all providers to complete
    await asyncio.gather(*tasks, return_exceptions=True)

    # Synthesize responses
    synthesized_response = synthesizer.synthesize(responses)
    
    # Stream synthesized response
    for i in range(0, len(synthesized_response), 10):
        token = synthesized_response[i:i+10]
        await websocket_manager.send_synth_token(chat_id, token, False)
        await asyncio.sleep(0.05)  # Simulate streaming
    
    await websocket_manager.send_synth_token(chat_id, "", True)

    # Save synthesized response
    async for db in get_db():
        response_message = Message(
            chat_id=chat_id,
            content=synthesized_response,
            is_user=False
        )
        db.add(response_message)
        await db.commit()
        await db.refresh(response_message)

        # Save all provider responses
        for provider_name, content in responses.items():
            provider_response = ProviderResponse(
                message_id=response_message.id,
                provider=provider_name,
                content=content
            )
            db.add(provider_response)
        await db.commit()

@router.get("/chat/{chat_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(chat_id: str, db: AsyncSession = Depends(get_db)):
    # Get chat
    result = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Get messages
    result = await db.execute(
        select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at)
    )
    messages = result.scalars().all()

    # Get provider responses
    provider_responses = []
    for message in messages:
        if not message.is_user:
            result = await db.execute(
                select(ProviderResponse).where(ProviderResponse.message_id == message.id)
            )
            message_responses = result.scalars().all()
            provider_responses.extend(message_responses)

    return ChatHistoryResponse(
        chat=ChatResponse(
            id=chat.id,
            title=chat.title,
            created_at=chat.created_at,
            updated_at=chat.updated_at
        ),
        messages=[
            MessageResponse(
                id=msg.id,
                chat_id=msg.chat_id,
                content=msg.content,
                is_user=msg.is_user,
                created_at=msg.created_at
            ) for msg in messages
        ],
        provider_responses=[
            ProviderResponseSchema(
                provider=resp.provider,
                content=resp.content,
                response_time=resp.response_time
            ) for resp in provider_responses
        ]
    )