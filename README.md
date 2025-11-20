# Multi-AI Chat Platform

A production-ready chat platform that queries multiple AI models (Groq, DeepSeek, OpenAI, Gemini) in parallel, analyzes their responses, and synthesizes a high-quality final answer.

## Features

- **Multi-provider Support**: Simultaneously queries Groq, DeepSeek, OpenAI, and Gemini
- **Real-time Streaming**: Live token streaming from all providers
- **Response Synthesis**: Intelligent aggregation and synthesis of multiple AI responses
- **Chat History**: Persistent chat sessions with message history
- **Quality Rating**: Like/dislike system for final answers
- **Mobile Responsive**: Works on desktop and mobile with dark/light theme

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js (for frontend development)
- API keys for desired AI providers

### Installation

1. **Clone and setup environment:**
```bash
git clone <repository>
cd ai-chat-platform
cp .env.example .env