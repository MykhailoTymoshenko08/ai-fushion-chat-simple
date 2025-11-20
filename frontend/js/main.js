// Main application entry point
document.addEventListener('DOMContentLoaded', () => {
    const chatUI = new ChatUI();
    chatUI.initialize();
    
    // Create initial chat
    chatUI.createNewChat();
});