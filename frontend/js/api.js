class ChatAPI {
    constructor() {
        // Use the same origin as the current page
        this.baseURL = window.location.origin;
        this.ws = null;
        this.currentChatId = null;
    }

    async createChat(title = "New Chat") {
        try {
            const response = await fetch(`${this.baseURL}/api/chat/new`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ title })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error creating chat:', error);
            throw error;
        }
    }

    async sendMessage(chatId, message, mode = "aggregate") {
        try {
            const response = await fetch(`${this.baseURL}/api/chat/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    chat_id: chatId, 
                    message,
                    mode 
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    }

    async getChatHistory(chatId) {
        try {
            const response = await fetch(`${this.baseURL}/api/chat/${chatId}/history`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching chat history:', error);
            throw error;
        }
    }

    async submitRating(chatId, messageId, score) {
        try {
            const response = await fetch(`${this.baseURL}/api/rating`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ chat_id: chatId, message_id: messageId, score })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error submitting rating:', error);
            throw error;
        }
    }

    connectWebSocket(chatId, onMessage) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat/${chatId}`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
        };
        
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                onMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        
        return this.ws;
    }

    disconnectWebSocket() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}