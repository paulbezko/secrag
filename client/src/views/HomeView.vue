<template>
  <div class="flex-column center width-100" style="padding-inline: 2rem;">
    <NavbarComp :authenticated=isAuthenticated :subscribed=isSubscribed />
    <div class="flex-row width-100 gap-8 center" style="padding-inline: 0rem; height: calc(100vh - 6rem)">
      <div class="flex-column gap-4 center" style="max-width: 52rem;">
        <div class="heading fade-in delay-1">{{ heroHeading }}</div>
        <div class="text-1 fade-in delay-2">{{ heroSubheading }}</div>
        <div class="flex-row width-100 gap-2 switch-row-to-column" style="justify-content: start;">
          <router-link to="/signup" class="button button-primary fade-in delay-3">Get Started -></router-link>
          <a href="#about" class="button button-secondary fade-in delay-4">Learn More</a>
        </div>
      </div>
      <div class="flex-column center width-100 show-on-large" style="max-width: 52rem">
        <div class="relative width-100" style="height: 60rem" >
          <img src="../assets/home/hero 1.png" class="absolute shadow fade-in delay-4" style="top: 42.5%; left: 42.5%; max-width: 70%; z-index: 4; transform: translate(-50%, -50%)">
          <img src="../assets/home/hero 2.png" class="absolute shadow fade-in delay-3" style="top: 47.5%; left: 47.5%; max-width: 70%; z-index: 3; transform: translate(-50%, -50%)">
          <img src="../assets/home/hero 3.png" class="absolute shadow fade-in delay-2" style="top: 52.5%; left: 52.5%; max-width: 70%; z-index: 2; transform: translate(-50%, -50%)">
          <img src="../assets/home/hero 4.png" class="absolute shadow fade-in delay-1" style="top: 57.5%; left: 57.5%; max-width: 70%; z-index: 1; transform: translate(-50%, -50%)">
        </div>
      </div>
    </div>
    <div id="about" class="flex-column width-100 center gap-4" style="padding-inline: 0rem;">
      <div class="heading text-center fade-in">The SEC Filing Problem</div>
      <div class="flex-row gap-4 center fade-in">
        <div class="text-2 text-center" style="max-width: 50rem;">For investors, analysts, and legal professionals, deciphering complex SEC filings can be <b style="color: var(--color-red);">overwhelming</b>.</div>
        <img src="../assets/home/face_with_monocle_3d 1.png" class="fade-in" style="width: 10rem; height: 10rem;">
      </div>
      <div class="flex-row gap-4 center fade-in">
        <div class="text-2 text-center" style="max-width: 50rem;">Extracting key insights from lengthy documents often requires <b style="color: var(--color-red);">hours</b> of manual effort and expertise.</div>
        <img src="../assets/home/hourglass_done_3d 1.png" class="fade-in" style="width: 10rem; height: 10rem;">
      </div>
      <div class="flex-row gap-4 center fade-in">
        <div class="text-2 text-center" style="max-width: 50rem;">It's easy to <b style="color: var(--color-red);">miss critical information</b>, and traditional search tools don’t provide the contextual understanding needed to make informed decisions quickly.</div>
        <img src="../assets/home/money_with_wings_3d 1.png" class="fade-in" style="width: 10rem; height: 10rem;">
      </div>
    </div>
    <div class="flex-column width-100 center gap-8" style="max-width: 88rem; padding-top: 20rem; padding-inline: 0rem;">
      <div class="heading text-center fade-in">Our Simple, Two-Step Solution</div>
      <div class="flex-row switch-row-to-column gap-4 center width-100 fade-in">
        <div class="flex-column vertical-line gap-2 width-100">
          <div class="subheading">Step 1: Find the Filing You Need</div>
          <div class="text-2"><b style="color: var(--color-green);">Easily</b> search our comprehensive library of SEC filings and select the document you want to explore. Whether it’s a recent filing or a historical one, everything is at your fingertips, ready to be <b style="color: var(--color-green);">analyzed in seconds.</b></div>
        </div>
        <img src="../assets/home/card_index_dividers_3d 1.png" class="fade-in" style="width: 15rem; height: 15rem;">
      </div>
      <div class="flex-row switch-row-to-column gap-4 center width-100 fade-in">
        <div class="flex-column vertical-line gap-2 width-100">
          <div class="subheading">Step 2: Get Instant Answers with AI</div>
          <div class="text-2">Ask our advanced AI-powered model any question about the filing and <b style="color: var(--color-green);">get detailed, clear insights immediately.</b> No more sifting through pages—just direct answers to the key information you’re looking for, all in <b style="color: var(--color-green);">real time.</b></div>
        </div>
        <img src="../assets/home/bookmark_tabs_3d 1.png" class="fade-in" style="width: 15rem; height: 15rem;">
      </div>
      <div class="flex-row switch-row-to-column gap-4 center width-100 fade-in">
        <div class="flex-column vertical-line gap-2 width-100">
          <div class="subheading">Why This Works:</div>
          <ul class="text-2">
            <li><b style="color: var(--color-green);">Fast Access:</b> No manual searching. Instant results.</li>
            <li><b style="color: var(--color-green);">Clear Insights:</b> Get precise answers without the overwhelm.</li>
            <li><b style="color: var(--color-green);">User-Friendly:</b> Navigate filings and interact with AI effortlessly.</li>
          </ul>
        </div>
        <img src="../assets/home/stopwatch_3d 1.png" class="fade-in" style="width: 15rem; height: 15rem;">
      </div>
    </div>
    <div class="flex-column center gap-4 fade-in" style="padding-top: 20rem; padding-inline: 0rem;">
      <div class="text-2 text-center">~ We provide access to filings for any public company. No matter which one you're looking for, we have it. ~</div>
      <div class="flex-row width-100 show-on-large">
        <div class="flex-row width-100 space-between">
          <img src="../assets/home/logos/image 6.png" class="fade-in delay-1" style="object-fit: contain;">
          <img src="../assets/home/logos/image 7.png" class="fade-in delay-2" style="object-fit: contain;">
          <img src="../assets/home/logos/image 8.png" class="fade-in delay-3" style="object-fit: contain;">
          <img src="../assets/home/logos/image 9.png" class="fade-in delay-4" style="object-fit: contain;">
          <img src="../assets/home/logos/image 10.png" class="fade-in delay-1" style="object-fit: contain;">
          <img src="../assets/home/logos/image 11.png" class="fade-in delay-2" style="object-fit: contain;">
          <img src="../assets/home/logos/image 14.png" class="fade-in delay-3" style="object-fit: contain;">
          <img src="../assets/home/logos/image 15.png" class="fade-in delay-4" style="object-fit: contain;">
          <img src="../assets/home/logos/image 16.png" class="fade-in delay-1" style="object-fit: contain;">
        </div>
      </div>
      <div class="flex-column width-100 show-on-small">
        <div class="flex-row width-100 space-between">
          <img src="../assets/home/logos/image 6.png" class="fade-in delay-1" style="object-fit: contain;">
          <img src="../assets/home/logos/image 7.png" class="fade-in delay-2" style="object-fit: contain;">
          <img src="../assets/home/logos/image 8.png" class="fade-in delay-3" style="object-fit: contain;">
          <img src="../assets/home/logos/image 9.png" class="fade-in delay-4" style="object-fit: contain;">
        </div>
        <div class="flex-row width-100 space-between">
          <img src="../assets/home/logos/image 10.png" class="fade-in delay-1" style="object-fit: contain;">
          <img src="../assets/home/logos/image 11.png" class="fade-in delay-2" style="object-fit: contain;">
          <img src="../assets/home/logos/image 14.png" class="fade-in delay-3" style="object-fit: contain;">
          <img src="../assets/home/logos/image 15.png" class="fade-in delay-4" style="object-fit: contain;">
          <img src="../assets/home/logos/image 16.png" class="fade-in delay-1" style="object-fit: contain;">
        </div>
      </div>
    </div>
    <div class="flex-column center gap-4" style="max-width: 70rem; padding-top: 20rem; padding-inline: 0rem;">
      <div class="heading text-center fade-in">Start Your Journey to Smarter Filings</div>
      <div class="text-1 text-center fade-in">Get more from SEC filings with the plan that fits your workflow.</div>
      <div class="flex-column gap-2 width-100">
        <div class="flex-row card width-100 gap-4 fade-in" style="padding: 1rem;">
          <div class="card-nested width-100 flex-column center" :class="{ active: subscriptionIsYearly }" @click="selectSubscriptionYearly" style="cursor: pointer">
            <b class="text-1">Yearly</b>
            <div class="text-2 text-center flex-row gap-05" style="align-items: baseline;"><div class="text-1">20%</div> Off</div>
          </div>
          <div class="card-nested width-100 flex-column center" :class="{ active: !subscriptionIsYearly }" @click="selectSubscriptionMonthly" style="cursor: pointer">
            <b class="text-1">Monthly</b>
          </div>
        </div>
        <div class="flex-row gap-2 width-100 show-on-large fade-in">
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
            <router-link to="/signup" class="button button-secondary">Join {{ subscriptionItems.Basic.name }}</router-link>
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
            <router-link to="/signup" class="button button-primary">Join {{ subscriptionItems.Premium.name }}</router-link>
          </div>
        </div>
        <div class="flex-row gap-2 show-on-small fade-in">
          <div class="flex-row card width-100 gap-4" style="padding: 1rem;">
            <div class="card-nested width-100 flex-column center" :class="{ active: subscriptionIsBasic }" @click="selectSubscriptionBasic" style="cursor: pointer">
              <b class="text-1" style="color: var(--color-blue)">{{ subscriptionItems.Basic.name }}</b>
            </div>
            <div class="card-nested width-100 flex-column center" :class="{ active: !subscriptionIsBasic }" @click="selectSubscriptionPremium" style="cursor: pointer">
              <b class="text-1" style="color: var(--color-yellow)">{{ subscriptionItems.Premium.name }}</b>
            </div>
          </div>
        </div>
        <div class="card flex-column center gap-1 width-100 show-on-small fade-in" style="padding-top: 3rem;">
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
          <router-link to="/signup" v-if="subscriptionIsBasic" class="button button-secondary">Join {{ subscriptionItems.Basic.name }}</router-link>
          <router-link to="/signup" v-if="!subscriptionIsBasic" class="button button-primary">Join {{ subscriptionItems.Premium.name }}</router-link>
        </div>
      </div>
    </div>
    <div id="faq" class="flex-column gap-4" style="max-width: 112rem; padding-top: 20rem; padding-inline: 0rem;">
      <div class="heading text-center fade-in">Frequently Asked Questions</div>
      <div class="width-100 vertical-line flex-column fade-in">
        <div v-for="(faq, index) in faqItems" :key="index">
          <div class="faq-question text-2 flex-row space-between gap-2" :class="{ open: faq.open }" @click="toggleFAQAnswer(index)">
            {{ faq.question }}<span class="text-2">{{ faq.open ? '-' : '+' }}</span>
          </div>
          <div class="faq-answer text-3" :class="{ open: faq.open }" :style="{ maxHeight: faq.open ? faq.height : '0' }">
            <div class="vertical-line">{{ faq.answer }}</div>
            <div style="height: 2rem"></div>
          </div>
        </div>
      </div>
    </div>
    <div id="contact" class="flex-column gap-4 text-left width-100" style="max-width: 112rem; padding-top: 20rem; padding-inline: 0rem;">
      <div class="flex-column gap-2">
        <div class="heading fade-in">Contact Us</div>
        <div class="text-1 fade-in">Got a question or a remark? <a href="mailto:secrag.info@gmail.com?subject=Question%20or%20Remark&body=Hi%20there%2C" class="text-link text-bold">Send us a message!</a></div>
      </div>
      <div class="flex-column text-4 gap-05" style="padding-bottom: 2rem;">
        <div style="text-align: justify; color: var(--color-grey-semidark)">The information provided through this platform is for informational and educational purposes only and is not intended as financial, legal, or professional advice. The platform uses AI to retrieve and summarize information from publicly available SEC filings; however, it may not always capture the complete context of the documents. Users are encouraged to review the original filings and consult with a qualified professional for any investment or business decisions. The platform and its creators are not responsible for any inaccuracies, omissions, or actions taken based on the content provided. Use of this platform is at your own risk.</div>
        <div class="text-4" style="text-align: justify; color: var(--color-grey-semidark)">The complete Terms and Conditions for use of this platform are available <router-link class="text-4 text-link" style="color: var(--color-grey-semidark); text-decoration: underline;" to="/terms-and-conditions">here</router-link>.</div>
        <div class="text-4" style="text-align: justify; color: var(--color-grey-semidark)">© {{ new Date().getFullYear() }} {{ projectName }}. All rights reserved.</div>
      </div>
    </div>
  </div>
</template>

<script>
// import getNavbarInfo from '../main.js'
import webdata from '../webdata.json'
import NavbarComp from '../components/NavbarComp.vue';
import { mapState } from 'vuex';
export default {
  
  components: {
    NavbarComp
  },
  data() { return {
    // pageLoaded: false,
    subscription: '',
    projectName: webdata.projectName,
    heroHeading: webdata.heroHeading,
    heroSubheading: webdata.heroSubheading,
    faqItems: webdata.faqItems,
    subscriptionItems: webdata.subscriptionItems,
    subscriptionIsYearly: true,
    subscriptionIsBasic: true
  }},
  computed: {
    ...mapState(['isAuthenticated', 'isSubscribed']),
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
    // this.pageLoaded = false
    // getNavbarInfo().then(data => {this.subscription = data.subscription; this.pageLoaded = true;})

    const observer = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target); // Once visible, stop observing
        }
      });
    }, {
      threshold: 0.2, // 20% of the element is in view
    });

    // Select all elements that need the fade-in effect
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach(el => observer.observe(el));

    // Open the first FAQ
    this.faqItems[0].open = true;
    this.$nextTick(() => {
      const answerElement = this.$el.querySelectorAll('.faq-answer')[0];
      this.faqItems[0].height = answerElement.scrollHeight + 'px';
    });
  },
  methods: {
    // isAuthenticated() {return localStorage.getItem('_u') !== null},
    // isSubscribed() {return this.subscription},
    toggleFAQAnswer(index) {
      // Logic for FAQ handling
      this.faqItems.forEach((faq, i) => {if (i !== index) {faq.open = false; faq.height = '0';}});
      const faq = this.faqItems[index];
      faq.open = !faq.open;
      if (faq.open) {
        this.$nextTick(() => {
          const answerElement = this.$el.querySelectorAll('.faq-answer')[index];
          faq.height = answerElement.scrollHeight + 'px';
        })} else {faq.height = '0'}
    },
    selectSubscriptionYearly() {this.subscriptionIsYearly = true;},
    selectSubscriptionMonthly() {this.subscriptionIsYearly = false;},
    selectSubscriptionBasic() {this.subscriptionIsBasic = true;},
    selectSubscriptionPremium() {this.subscriptionIsBasic = false;},
  }
}



</script>

<style scoped>
.fade-in {
  opacity: 0;
  transform: translateY(4rem);
  transition: opacity 1s ease-out, transform 1s ease-out;
}

.fade-in.visible {
  opacity: 1;
  transform: translateY(0);
}

.fade-in.delay-1 {
  transition-delay: 0.2s;
}

.fade-in.delay-2 {
  transition-delay: 0.4s;
}

.fade-in.delay-3 {
  transition-delay: 0.6s;
}

.fade-in.delay-4 {
  transition-delay: 0.8s;
}
</style>