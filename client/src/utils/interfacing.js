
export const interfacing = {

  observeSize(ctx) {
    // Ensure ResizeObserver is only created once
    if (ctx.resizeObserver) return;
  
    // Create a ResizeObserver to handle layout changes
    ctx.resizeObserver = new ResizeObserver((entries) => {
      for (let entry of entries) {
        if (entry.target.id === 'dashboard') {
          requestAnimationFrame(() => {
            // Update the chat height and check screen width only if the dashboard's size changes
            interfacing.updateChatHeight(ctx);
            interfacing.checkScreenWidth(ctx);
          });
        }
      }
    });
  
    // Safely observe the dashboard element
    const dashboard = document.getElementById('dashboard');
    if (dashboard) {
      ctx.resizeObserver.observe(dashboard);
    } else {
      console.warn("Dashboard element not found. Ensure 'dashboard' ID is correctly set in the DOM.");
    }
  
    // Immediately adjust layout during initialization
    interfacing.updateChatHeight(ctx);
    interfacing.checkScreenWidth(ctx);
  },

  checkScreenWidth(ctx) {
    if (window.innerWidth <= 796) {ctx.isMobile = true; ctx.premadeSuggestionsShown = false} 
    else {ctx.isMobile = false; ctx.premadeSuggestionsShown = true}
  },

  updateChatHeight(ctx) {
    const headerHeight = document.getElementById('header').offsetHeight;
    const footerHeight = document.getElementById('footer').offsetHeight;
    ctx.chatContainerHeight = window.innerHeight - footerHeight - headerHeight;
  },

  chatScrollToBottom() {
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.scrollTo({top: chatContainer.scrollHeight, behavior: 'smooth'});
  },

  updateTextareaHeight(ctx) {
    const textarea = document.getElementById('textarea');
    if (!textarea) return;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    this.updateChatHeight(ctx);
  },

}