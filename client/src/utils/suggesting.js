import { interfacing } from './interfacing.js';
import { messaging } from './messaging.js';

export const suggesting = {

  getPremadeSuggestions(ctx) {
    if (ctx.view === 'profile') {
      ctx.inputMode = 'default';
      ctx.userProfileUpdated = false;
      ctx.organicSuggestions = [];
      ctx.premadeSuggestionsShown = true;
      ctx.premadeSuggestions = [
        { label: 'Save changes', action: () => (ctx.updateUserProfile()) },
        { label: 'Back', action: () => (ctx.view = 'chat', this.getPremadeSuggestions(ctx), ctx.$nextTick(() => {setTimeout(() => {interfacing.chatScrollToBottom();}, 100)})) },
      ];
    }
    
    else if (ctx.premadeSuggestionsTopic === 'more_authenticated_1') {
      ctx.premadeSuggestions =  [
      ...(!ctx.userIsSubscribed ? [] : [{ label: 'Manage Subscription', action: () => console.log('Redirect to stripe here') }]),
        { label: 'Sign Out', action: ctx.signOut },
        { label: 'More', action: () => (ctx.premadeSuggestionsTopic = 'more_authenticated_2', this.getPremadeSuggestions(ctx)) },
        { label: 'Back', action: () => (ctx.premadeSuggestionsTopic = '', this.getPremadeSuggestions(ctx)) },
      ]
    }

    else if (ctx.premadeSuggestionsTopic === 'more_authenticated_2') {
      ctx.premadeSuggestions =  [
        { label: 'Delete Account', action: () => console.log('DELETE ACCOUNT') },
        { label: 'Back', action: () => (ctx.premadeSuggestionsTopic = 'more_authenticated_1', this.getPremadeSuggestions(ctx)) },
      ];
    }

    else if (ctx.premadeSuggestionsTopic === 'more_anonymous') {
      ctx.premadeSuggestions =  [
        { label: 'Pricing', action: () => messaging.sendMessage(ctx, "I'd like to know more about the pricing") },
        { label: 'Contact', action: () => messaging.sendMessage(ctx, "I'd like to contact you") },
        { label: 'T&C', action: () => ctx.$router.push('/terms-and-conditions') },
        { label: 'Back', action: () => (ctx.premadeSuggestionsTopic = '', this.getPremadeSuggestions(ctx)) },
      ];
    }

    else if (ctx.userStatus === 'anonymous' || ctx.userStatus === null) {
      ctx.premadeSuggestions =  [
        { label: 'Profile', action: async () => (await ctx.getUserProfile(localStorage.getItem('_u')), ctx.view = 'profile', this.getPremadeSuggestions(ctx)) },
        { label: 'Sign Up', action: () => messaging.sendMessage(ctx, "I'd like to sign up") },
        { label: 'Sign In', action: () => messaging.sendMessage(ctx, "I'd like to sign in") },
        { label: 'More', action: () => (ctx.premadeSuggestionsTopic = 'more_anonymous', this.getPremadeSuggestions(ctx)) },
      ];
    }

    else if (ctx.userStatus === 'verified') {
      ctx.premadeSuggestions =  [];
    }

    else if (ctx.userStatus === 'registered') {
      ctx.premadeSuggestions =  [
        { label: 'Subscribe', action: () => console.log('Redirect to stripe here') },
        { label: 'Profile', action: async () => (await ctx.getUserProfile(localStorage.getItem('_u')), ctx.view = 'profile', this.getPremadeSuggestions(ctx)) },
        { label: 'More', action: () => (ctx.premadeSuggestionsTopic = 'more_authenticated_1', this.getPremadeSuggestions(ctx)) },
      ];
    }

    else {
      ctx.premadeSuggestions =  [];
    }
  }
}