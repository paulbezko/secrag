<template>
  <div class="display display-flex-column center">
    <SpinnerComp v-if="showSpinner"></SpinnerComp>
    <div class="display-margin display-flex-column">
      <NavbarComp :authenticated="true" :subscribed="false"/>
      <div class="display-flex-column height-100 flex-1 center width-100">
        <div class="display-flex-column gap-2 center width-100">
          <div class="heading-2 text-center">Subscribe to SkelTal</div>
          
          <div class="display-flex-column gap-2 width-100 height-100 card-subscription">
            <div class="slider-parent">
              <div id="slider-yearly" @click="handleClickPeriod('yearly')" class="slider-child display-flex-column">
                <div class="text-2">Pay Yearly</div>
                <div class="text-3">2 months free</div>
              </div>
              <div id="slider-monthly" @click="handleClickPeriod('monthly')" class="slider-child text-3 slider-child-active">
                <div class="text-2">Pay Monthly</div>
              </div>
            </div>
            <div class="display-flex-row gap-2 width-100 center show-on-large">
              <div class="card card-subscribe display-flex-column center" style="position: relative">
                <div class="tooltip display-flex-row center position-absolute text-3 gap-05" style="top: -15px"><div class="fa-solid fa-fire text-3"></div>Most Popular</div>
                <div class="heading-2 display-flex-row" style="align-items: baseline;">{{ priceBasic }}<div class="text-2 bold">/mo</div></div>
                <div class="text-2 bold">Basic</div>
                <div class="text-3 text-center">The most basic stuff, you know</div>
                <div class="line"></div>
                <div class="display-flex-column gap-1" style="align-items: start; padding-block: 1rem;">
                  <div class="text-2 display-flex-row center gap-1"><div class="fa-solid fa-circle-check text-1 color-green"></div>Item 1</div>
                  <div class="text-2 display-flex-row center gap-1"><div class="fa-solid fa-circle-check text-1 color-green"></div>Item 2 longer</div>
                  <div class="text-2 display-flex-row center gap-1"><div class="fa-solid fa-circle-check text-1 color-green"></div>Item 3 even longer</div>
                  <div class="text-2 display-flex-row center gap-1"><div class="fa-solid fa-circle-check text-1 color-green"></div>Item 4 shorter</div>
                </div>
                <button class="button button-cta" @click="subscribe('basic')">Subscribe Basic</button>
              </div>
              <div class="card card-subscribe display-flex-column center">
                <div class="heading-2 display-flex-row" style="align-items: baseline;">{{ pricePremium }}<div class="text-2 bold">/mo</div></div>
                <div class="text-2 bold">Premium</div>
                <div class="text-3 text-center">The more premium stuff, you know</div>
                <div class="line"></div>
                <div class="display-flex-column gap-1" style="align-items: start; padding-block: 1rem;">
                  <div class="text-2 display-flex-row center gap-1"><div class="fa-solid fa-circle-check text-1 color-green"></div>Item 1</div>
                  <div class="text-2 display-flex-row center gap-1"><div class="fa-solid fa-circle-check text-1 color-green"></div>Item 2 longer</div>
                  <div class="text-2 display-flex-row center gap-1"><div class="fa-solid fa-circle-check text-1 color-green"></div>Item 3 even longer</div>
                  <div class="text-2 display-flex-row center gap-1"><div class="fa-solid fa-circle-check text-1 color-green"></div>Item 4 shorter</div>
                </div>
                <button class="button button-secondary" @click="subscribe('premium')">Subscribe Premium</button>
              </div>
            </div>

            <div class="display-flex-column gap-2 show-on-small">
              <div class="display-flex-row gap-2 width-100 height-100 center">
                <div id="card-basic" @click="handleClickSubscription('basic')" class="card card-subscribe-small display-flex-column center card-clickable card-clickable-active flex-1" style="position: relative">
                  <div class="tooltip display-flex-row center position-absolute text-3 gap-05" style="top: -15px"><div class="fa-solid fa-fire text-3"></div>Most Popular</div>
                  <div class="heading-2 display-flex-row" style="align-items: baseline;">{{ priceBasic }}<div class="text-2 bold">/mo</div></div>
                  <div class="text-2 bold">Basic</div>
                  <div class="text-3 text-center">The most basic stuff, you know</div>
                </div>
                <div id="card-premium" @click="handleClickSubscription('premium')" class="card card-subscribe-small display-flex-column center card-clickable flex-1">
                  <div class="heading-2 display-flex-row" style="align-items: baseline;">{{ pricePremium }}<div class="text-2 bold">/mo</div></div>
                  <div class="text-2 bold">Premium</div>
                  <div class="text-3 text-center">The more premium stuff, you know</div>
                </div>
              </div>
              <div class="card">
                <div class="display-flex-column gap-1" style="align-items: start; padding-block: 1rem;">
                  <div class="text-2 display-flex-row center gap-1"><div class="fa-solid fa-circle-check text-1 color-green"></div>Item 1</div>
                  <div class="text-2 display-flex-row center gap-1"><div class="fa-solid fa-circle-check text-1 color-green"></div>Item 2 longer</div>
                  <div class="text-2 display-flex-row center gap-1"><div class="fa-solid fa-circle-check text-1 color-green"></div>Item 3 even longer</div>
                  <div class="text-2 display-flex-row center gap-1"><div class="fa-solid fa-circle-check text-1 color-green"></div>Item 4 shorter</div>
                </div>
              </div>
              <button class="button button-cta" style="width: 100%; border-radius: 2rem;" @click="subscribe(subscriptionType)">Subscribe to {{ subscriptionType }}</button>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NavbarComp from '../components/NavbarComp.vue';
import { loadStripe } from '@stripe/stripe-js';
import { config } from '@/config';
import axios from 'axios';
import SpinnerComp from '@/components/SpinnerComp.vue';

export default {
  components: {
    NavbarComp,
    SpinnerComp
  },
  data() {return {
    stripePromise: null, 
    subscriptionType: 'basic',
    priceBasic: 20,
    pricePremium: 40,
    periodType: 'monthly',
    showSpinner: false
  }},
  mounted() {
    this.initializeStripe()
  },
  methods: {
    async initializeStripe() {
      try {this.stripePromise = loadStripe('pk_test_51PtWwQGjSxKJrDncatm1lbb4MnM0umSDHU41hWh12HuIlkNwyl29qKdisowDY7UZazwI4HUnIDhLh9j17upYBTsA002jNz2GUG')} 
      catch (error) {console.error('Error initializing Stripe:', error)}
    },

    async subscribe(subscriptionType) {
      this.showSpinner = true

      let stripe, response
      stripe = await this.stripePromise;
      response = await axios.post(`${config.apiUrl}/api/subscribe`, {
        token: localStorage.getItem('_u'),
        operation: 'subscribe',
        subscriptionType: subscriptionType,
        periodType: this.periodType
      })

      stripe.redirectToCheckout({sessionId: response.data.sessionId})
    },
    handleClickPeriod(type) {
      const yearlySlider = document.getElementById('slider-yearly');
      const monthlySlider = document.getElementById('slider-monthly');

      yearlySlider.classList.remove('slider-child-active');
      monthlySlider.classList.remove('slider-child-active');

      if (type === 'yearly') {
        this.periodType = 'yearly'
        this.priceBasic = 17
        this.pricePremium = 33
        yearlySlider.classList.add('slider-child-active');
      } else if (type === 'monthly') {
        this.periodType = 'monthly'
        this.priceBasic = 20
        this.pricePremium = 40
        monthlySlider.classList.add('slider-child-active');
      }
    },
    handleClickSubscription(type) {
      const basicSubscription = document.getElementById('card-basic');
      const premiumSubscription = document.getElementById('card-premium');

      basicSubscription.classList.remove('card-clickable-active');
      premiumSubscription.classList.remove('card-clickable-active');

      if (type === 'basic') {
        this.subscriptionType = 'basic'
        basicSubscription.classList.add('card-clickable-active');
      } else if (type === 'premium') {
        this.subscriptionType = 'premium'
        premiumSubscription.classList.add('card-clickable-active');
      }
    },
  }
}
</script>