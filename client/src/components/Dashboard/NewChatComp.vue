<template>
  <div v-if="windowLoaded" class="flex-column width-100 center gap-1 padding-sidebar-dashboard height-100" style="height: 100dvh; padding-bottom: 1rem; max-width: 140rem; overflow: hidden;">
    <div class="absolute" v-if="newChatLoading">
      <div class="z-20 flex-column center gap-1 card relative">
        <div class="text-2 text-bold" style="box-sizing: border-box; white-space: nowrap;">Creating the Chat</div>
        <div class="flex-row center gap-1">
          <div class="text-3" style="box-sizing: border-box; white-space: nowrap;">{{ newChatLoadingMessage }}</div>
          <SpinnerCompInside :customClass="'text-3'"></SpinnerCompInside>
        </div>
      </div>
      <div class="backdrop z-17"></div>
    </div>
    <div class="flex-column center gap-2 width-100" style="padding: 2rem; max-width: 40rem;">
      <div class="subheading">Create a new Chat</div>
      <div class="flex-column gap-1 center width-100">
        <div class="text-3 text-center">Choose what to select the company by</div>
        <div class="flex-column gap-1 relative width-100">
          <div class="flex-row gap-1 width-100">
            <div class="button button-card" :class="{ active: selectedType === 'Name' }" @click="selectType('Name')">Name</div>
            <div class="button button-card" :class="{ active: selectedType === 'Ticker' }" @click="selectType('Ticker')">Ticker</div>
            <div class="button button-card" :class="{ active: selectedType === 'CIK' }" @click="selectType('CIK')">CIK</div>
          </div>
          <input 
            type="text"
            class="input width-100"
            v-model="optionInput" 
            @input="filterOptions" 
            @focus="showSuggestions = true" 
            :placeholder="'Input ' + selectedType" 
            :class="{ 'selected-option': selectedOption !== '' }"
          />
          <div v-if="showSuggestions && filteredOptionsVisible.length > 0" class="suggestions-container">
            <div v-for="option in filteredOptionsVisible.slice(0, 10)" :key="option" class="suggestion-item" @mousedown="selectOptionFromSuggestion(option)">
              {{ option }}
            </div>
          </div>
        </div>
      </div>
      
      <div class="flex-column center gap-1 width-100">
        <div class="text-3 text-center" style="max-width: 24rem;">Select remaining parameters</div>
        <select 
          class="input"
          @change="selectYear($event.target.value)" 
          v-model="selectedYear" 
          :class="{ 'input-disabled': selectedTicker === '' , 'selected-option': selectedYear !== '' }" 
          :disabled="selectedTicker === ''"
        >
          <option value="" disabled hidden selected>Select Year</option>
          <option v-for="option in yearOptions" :key="option" class="text-inter text-4" :value="option">
            {{ option }}
          </option>
        </select>
        <select class="input" @change="selectFiling($event.target.value)" v-model="selectedFiling" :class="{ 'input-disabled': selectedYear === '', 'selected-option': selectedFiling !== '' }" :disabled="selectedYear === ''">
          <option value="" disabled hidden selected>Select Filing</option>
          <option v-for="option in filingOptions" :key="option" class="text-inter text-4" :value="option">
            {{ option }}
          </option>
        </select>
      </div>
      <div
        class="button button-primary flex-row gap-1 width-100" 
        :class="{ 'button-disabled': (!selectedTicker || !selectedYear || !selectedFiling)}" 
        @click="createChat()"
        :disabled="(!selectedTicker || !selectedYear || !selectedFiling)">
        Create Chat
      </div>
      <div v-if="error && selectedNewFiling === ''" class="text-4 text-error text-center flex-row gap-05 center"><div class="fa-solid fa-triangle-exclamation text-error"></div>{{ error }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NewChatComp',

  props: {
    type: {
      type: String,
      required: true,
      validator(value) {
        return ['preview', 'full'].includes(value);
      },
    },
  },

  data() {
    return {
      windowLoaded: true,
    };
  },

  mounted() {   
  },

  methods: {
  },
};
</script>