class ChatUI {
    constructor() {
        this.api = new ChatAPI();
        this.currentChatId = null;
        this.synthMessageId = null;
        this.providerStatus = {};
    }

    initialize() {
        this.bindEvents();
        this.loadChatHistory();
        this.applyTheme();
        this.setupModeSelector();
    }

    bindEvents() {
        // Message form
        document.getElementById('messageForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSendMessage();
        });

        // New chat button
        document.getElementById('newChatBtn').addEventListener('click', () => {
            this.createNewChat();
        });

        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', () => {
            this.toggleTheme();
        });

        // Rating buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-like') || e.target.classList.contains('btn-dislike')) {
                this.handleRating(e.target.dataset.score);
            }
        });

        // Mode selector
        document.getElementById('responseMode').addEventListener('change', (e) => {
            this.handleModeChange(e.target.value);
        });
    }

    setupModeSelector() {
        this.handleModeChange('aggregate');
    }

    handleModeChange(mode) {
        const singleModelSelect = document.getElementById('singleModelSelect');
        if (mode === 'single') {
            singleModelSelect.style.display = 'block';
        } else {
            singleModelSelect.style.display = 'none';
        }
    }

    async createNewChat() {
        try {
            const chat = await this.api.createChat();
            this.currentChatId = chat.id;
            this.loadChat(chat.id);
            this.clearProviderStreams();
            this.hideRatingButtons();
            this.updateChatTitle(chat.title);
        } catch (error) {
            this.showError('Failed to create new chat');
        }
    }

    async handleSendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        if (!message) return;

        // Clear input
        input.value = '';

        // Add user message to UI
        this.addUserMessage(message);

        try {
            const mode = document.getElementById('responseMode').value;
            let requestData = {
                chat_id: this.currentChatId,
                message: message,
                mode: mode
            };

            if (mode === 'single') {
                const selectedModel = document.getElementById('singleModelSelect').value;
                requestData.mode = 'single';
                // We'll handle the model selection in the frontend display
            }

            // Send message and get chat ID
            const response = await this.api.sendMessage(
                this.currentChatId, 
                message, 
                mode
            );
            this.currentChatId = response.chat_id;
            
            // Connect WebSocket for streaming
            this.setupStreaming(mode);
            
        } catch (error) {
            this.showError('Failed to send message');
        }
    }

    setupStreaming(mode) {
        this.api.connectWebSocket(this.currentChatId, (data) => {
            this.handleStreamEvent(data, mode);
        });

        // Create provider containers based on mode
        this.createProviderContainers(mode);
    }

    createProviderContainers(mode) {
        const container = document.getElementById('providerStreams');
        container.innerHTML = '';

        this.providerStatus = {};

        if (mode === 'single') {
            const selectedModel = document.getElementById('singleModelSelect').value;
            this.createProviderSection(selectedModel);
        } else if (mode === 'multiple') {
            const providers = ['openai', 'groq', 'deepseek', 'gemini'];
            providers.forEach(provider => this.createProviderSection(provider));
        } else { // aggregate
            const providers = ['openai', 'groq', 'deepseek', 'gemini', 'synth'];
            providers.forEach(provider => this.createProviderSection(provider));
        }
    }

    createProviderSection(provider) {
        const container = document.getElementById('providerStreams');
        const section = document.createElement('div');
        section.className = 'provider-section';
        section.innerHTML = `
            <div class="provider-header">
                <span>${provider}</span>
                <span class="status-indicator" id="${provider}-status">streaming</span>
            </div>
            <div class="provider-response ${provider === 'synth' ? 'synth-response' : ''}" 
                 id="${provider}-response"></div>
        `;
        container.appendChild(section);
        this.providerStatus[provider] = 'streaming';
    }

    handleStreamEvent(data, mode) {
        const { type, provider, token, done } = data;
        
        if (type === 'provider') {
            this.updateProviderResponse(provider, token, done);
        } else if (type === 'synth') {
            this.updateSynthResponse(token, done, mode);
        }
    }

    updateProviderResponse(provider, token, done) {
        let container = document.getElementById(`${provider}-response`);
        let status = document.getElementById(`${provider}-status`);
        
        if (!container) {
            this.createProviderSection(provider);
            container = document.getElementById(`${provider}-response`);
            status = document.getElementById(`${provider}-status`);
        }

        if (!container.textContent && token) {
            container.textContent = token;
        } else if (token) {
            container.textContent += token;
        }

        if (done) {
            container.classList.remove('streaming');
            if (status) {
                status.textContent = 'complete';
                status.classList.add('status-complete');
            }
            this.providerStatus[provider] = 'complete';
        } else {
            container.classList.add('streaming');
            if (status) {
                status.textContent = 'streaming';
                status.classList.remove('status-complete', 'status-error');
            }
        }

        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    }

    updateSynthResponse(token, done, mode) {
        let container = document.getElementById('synth-response');
        let status = document.getElementById('synth-status');
        
        if (!container) {
            this.createProviderSection('synth');
            container = document.getElementById('synth-response');
            status = document.getElementById('synth-status');
        }

        if (!container.textContent && token) {
            container.textContent = token;
        } else if (token) {
            container.textContent += token;
        }

        if (done) {
            container.classList.remove('streaming');
            if (status) {
                status.textContent = 'complete';
                status.classList.add('status-complete');
            }
            this.providerStatus['synth'] = 'complete';
            this.synthMessageId = this.generateMessageId();
            this.showRatingButtons();
            
            // Add synthesized message to chat in aggregate mode
            if (mode === 'aggregate') {
                this.addAssistantMessage(container.textContent, true);
            }
        } else {
            container.classList.add('streaming');
            if (status) {
                status.textContent = 'streaming';
                status.classList.remove('status-complete', 'status-error');
            }
        }

        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    }

    addUserMessage(content) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        messageDiv.textContent = content;
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addAssistantMessage(content, isSynthesized = false) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message assistant ${isSynthesized ? 'synthesized' : ''}`;
        messageDiv.textContent = content;
        if (isSynthesized) {
            messageDiv.dataset.messageId = this.synthMessageId;
        }
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showRatingButtons() {
        document.getElementById('ratingButtons').style.display = 'block';
    }

    hideRatingButtons() {
        document.getElementById('ratingButtons').style.display = 'none';
    }

    async handleRating(score) {
        if (!this.currentChatId || !this.synthMessageId) return;

        try {
            await this.api.submitRating(this.currentChatId, this.synthMessageId, parseInt(score));
            this.hideRatingButtons();
            this.showSuccess('Rating submitted!');
        } catch (error) {
            this.showError('Failed to submit rating');
        }
    }

    async loadChatHistory() {
        try {
            // In a real app, you'd fetch the list of chats from the API
            // For now, we'll just show a placeholder
            const historyContainer = document.getElementById('chatHistory');
            historyContainer.innerHTML = '<div class="chat-item">No chats yet</div>';
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    async loadChat(chatId) {
        try {
            const history = await this.api.getChatHistory(chatId);
            this.renderChat(history);
        } catch (error) {
            this.showError('Failed to load chat');
        }
    }

    renderChat(history) {
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.innerHTML = '';

        history.messages.forEach(message => {
            if (message.is_user) {
                this.addUserMessage(message.content);
            } else {
                this.addAssistantMessage(message.content);
            }
        });
    }

    clearProviderStreams() {
        document.getElementById('providerStreams').innerHTML = '';
        this.providerStatus = {};
    }

    updateChatTitle(title) {
        document.getElementById('currentChatTitle').textContent = title;
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Update toggle button
        const toggleBtn = document.getElementById('themeToggle');
        toggleBtn.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    }

    applyTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        
        const toggleBtn = document.getElementById('themeToggle');
        toggleBtn.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    }

    showError(message) {
        // Simple error display - could be enhanced with a proper notification system
        console.error('Error:', message);
        alert(`Error: ${message}`);
    }

    showSuccess(message) {
        // Simple success display
        console.log('Success:', message);
    }

    generateMessageId() {
        return 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
}