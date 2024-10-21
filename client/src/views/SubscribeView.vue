<template>
  <div class="flex-column center width-100 gap-8" style="min-height: 100vh; justify-content: start; padding-inline: 4rem; padding-bottom: 4rem;">
    <SpinnerComp v-if="showSpinner"></SpinnerComp>
    <NavbarComp :authenticated="true" :subscribed="false"/>
      <div class="flex-column center gap-4" style="max-width: 70rem;">
      <div class="heading text-center">Start Your Journey to Smarter Filings</div>
      <div class="text-2 text-center">Get more from SEC filings with the plan that fits your workflow.</div>
      <div class="flex-column gap-2 width-100">
        <div class="flex-row card width-100 gap-4" style="padding: 1rem;">
          <div class="card-nested width-100 flex-column center" :class="{ active: subscriptionIsYearly }" @click="selectSubscriptionYearly" style="cursor: pointer">
            <b class="text-1">Yearly</b>
            <div class="text-2 text-center flex-row gap-05" style="align-items: baseline;"><div class="text-1">20%</div> Off</div>
          </div>
          <div class="card-nested width-100 flex-column center" :class="{ active: !subscriptionIsYearly }" @click="selectSubscriptionMonthly" style="cursor: pointer">
            <b class="text-1">Monthly</b>
          </div>
        </div>
        <div class="flex-row gap-2 width-100 show-on-large">
          <div class="flex-column card center gap-1 width-100">
            <div class="text-2 flex-row" style="align-items: baseline;">
              <div class="flex-row gap-05" style="align-items: baseline;">
                <b style="font-size: var(--subheading)">€</b>
                <b style="font-size: var(--heading);">{{ subscriptionIsYearly ? subscriptionItemsWithAnnual.Basic.priceAnnual : subscriptionItems.Basic.priceMonthly }}</b>
              </div>/mo
            </div>
            <div class="text-1">{{ subscriptionItems.Basic.name }}</div>
            <hr class="width-100" style="border-top: 1px solid var(--color-grey)">
            <div class="flex-column gap-1">
              <div v-for="(feature, index) in subscriptionItems.Basic.features" :key="index">
                <div class="flex-row gap-1 text-3">
                  <div class="fa-solid fa-square-check text-2" style="color: var(--color-blue)"></div>
                  {{ feature }}
                </div>
              </div>
            </div>
            <hr class="width-100" style="border-top: 1px solid var(--color-grey)">
            <div class="button button-secondary" @click="subscribe('basic')">Join {{ subscriptionItems.Basic.name }}</div>
          </div>
          <div class="flex-column card center gap-1 width-100">
            <div class="text-2 flex-row" style="align-items: baseline;">
              <div class="flex-row gap-05" style="align-items: baseline;">
                <b style="font-size: var(--subheading)">€</b>
                <b style="font-size: var(--heading);">{{ subscriptionIsYearly ? subscriptionItemsWithAnnual.Premium.priceAnnual : subscriptionItems.Premium.priceMonthly }}</b>
              </div>/mo
            </div>
            <div class="text-1">{{ subscriptionItems.Premium.name }}</div>
            <hr class="width-100" style="border-top: 1px solid var(--color-grey)">
            <div class="flex-column gap-1">
              <div v-for="(feature, index) in subscriptionItems.Premium.features" :key="index">
                <div class="flex-row gap-1 text-3">
                  <div class="fa-solid fa-square-check text-2" style="color: var(--color-blue)"></div>
                  {{ feature }}
                </div>
              </div>
            </div>
            <hr class="width-100" style="border-top: 1px solid var(--color-grey)">
            <div class="button button-primary" @click="subscribe('premium')">Join {{ subscriptionItems.Premium.name }}</div>
          </div>
        </div>
        <div class="flex-row gap-2 show-on-small">
          <div class="flex-row card width-100 gap-4" style="padding: 1rem;">
            <div class="card-nested width-100 flex-column center" :class="{ active: subscriptionIsBasic }" @click="selectSubscriptionBasic">
              <b class="text-1" style="color: var(--color-blue)">{{ subscriptionItems.Basic.name }}</b>
            </div>
            <div class="card-nested width-100 flex-column center" :class="{ active: !subscriptionIsBasic }" @click="selectSubscriptionPremium">
              <b class="text-1" style="color: var(--color-yellow)">{{ subscriptionItems.Premium.name }}</b>
            </div>
          </div>
        </div>
        <div class="card flex-column center gap-1 width-100 show-on-small" style="padding-top: 3rem;">
          <div class="text-2 flex-row" style="align-items: baseline;">
              <div class="flex-row gap-05" style="align-items: baseline;">
                <b style="font-size: var(--heading)">€</b>
                <b style="font-size: var(--heading);">{{ subscriptionIsBasic ? (subscriptionIsYearly ? subscriptionItemsWithAnnual.Basic.priceAnnual : subscriptionItems.Basic.priceMonthly) : (subscriptionIsYearly ? subscriptionItemsWithAnnual.Premium.priceAnnual : subscriptionItems.Premium.priceMonthly) }}</b>
              </div>/mo
            </div>
          <hr class="width-100" style="border-top: 1px solid var(--color-grey)">
          <div class="flex-column gap-1">
            <div v-for="(feature, index) in (subscriptionIsBasic ? subscriptionItems.Basic.features : subscriptionItems.Premium.features)" :key="index">
              <div class="flex-row gap-1 text-2" style="align-items: center;">
                <div class="fa-solid fa-square-check text-2" style="color: var(--color-blue)"></div>
                {{ feature }}
              </div>
            </div>
          </div>
          <hr class="width-100" style="border-top: 1px solid var(--color-grey)">
          <div v-if="subscriptionIsBasic" class="button button-secondary" @click="subscribe('basic')">Join {{ subscriptionItems.Basic.name }}</div>
          <div v-if="!subscriptionIsBasic" class="button button-primary" @click="subscribe('premium')">Join {{ subscriptionItems.Premium.name }}</div>
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
import webdata from '../webdata.json'

export default {
  components: {
    NavbarComp,
    SpinnerComp
  },
  data() {return {
    stripePromise: null, 
    showSpinner: false,
    subscriptionItems: webdata.subscriptionItems,
    subscriptionIsYearly: true,
    periodType: 'yearly',
    subscriptionIsBasic: false,
    subscriptionType: 'basic',
    projectName: webdata.projectName,
  }},
  computed: {
    subscriptionItemsWithAnnual() {
      return {
        "Basic": {
          ...this.subscriptionItems.Basic,
          priceAnnual: (this.subscriptionItems.Basic.priceMonthly * 0.8)
        },
        "Premium": {
          ...this.subscriptionItems.Premium,
          priceAnnual: (this.subscriptionItems.Premium.priceMonthly * 0.8)
        }
      };
    }
  },
  mounted() {
    this.initializeStripe()
  },
  methods: {
    async initializeStripe() {
      try {this.stripePromise = loadStripe(webdata.stripeKey)} 
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

    selectSubscriptionYearly() {this.subscriptionIsYearly = true; this.periodType = 'yearly'},
    selectSubscriptionMonthly() {this.subscriptionIsYearly = false; this.periodType = 'monthly'},
    selectSubscriptionBasic() {this.subscriptionIsBasic = true;},
    selectSubscriptionPremium() {this.subscriptionIsBasic = false;},
  }
}
</script>