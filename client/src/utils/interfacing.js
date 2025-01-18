
export const interfacing = {

  observeSize(ctx) {
    if (ctx.resizeObserver) return;
  
    ctx.resizeObserver = new ResizeObserver((entries) => {
      for (let entry of entries) {
        if (entry.target.id === 'dashboard') {
          requestAnimationFrame(() => {
            interfacing.updateChatHeight(ctx);
            interfacing.checkScreenWidth(ctx);
            console.log('page loaded');
            ctx.pageLoaded = true;
          });
        }
      }
    });
  
    const dashboard = document.getElementById('dashboard');
    ctx.resizeObserver.observe(dashboard);

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
    setTimeout(() => {chatContainer.scrollTo({top: chatContainer.scrollHeight, behavior: 'smooth'});}, 100);
  },

  updateTextareaHeight(ctx) {
    const textarea = document.getElementById('textarea');
    if (!textarea) return;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    this.updateChatHeight(ctx);
  },

}