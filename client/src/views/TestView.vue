<template>
  <div style="width: 600px !important">
    <!-- Render the user's message content -->
    <div class="message-content">
      <div v-for="(part, index) in splitMessage" :key="index">
        <div v-if="part.type === 'text'" v-html="part.content"></div>
        <ApexChartsWidget v-else-if="part.type === 'treemap'" :theme="'light'" :params="part.params"/>
        <TradingViewWidget v-else-if="part.type === 'pricechart'" :params="part.params"/>
      </div>
    </div>
  </div>
</template>

<script>
import ApexChartsWidget from "@/widgets/ApexChartsWidget.vue";
import TradingViewWidget from "@/widgets/TradingViewWidget.vue"; // Assume this exists for 'pricechart'

export default {
  name: "TestView",
  components: {
    ApexChartsWidget,
    TradingViewWidget, // Add TradingViewWidget if you have it
  },
  data() {
    return {
      message: {
        "role": "assistant",
        "content": "Here is the widget: [SP_PLT]Let me know if there is anything else I can help you with.",
        "widgets": [
          {
            "id": "SP_PLT",
            "type": "treemap", // Can be 'treemap' or 'pricechart'
            "params": {
              "series": [
                {
                  "name": "TICKERS",
                  "data": [
                    { "x": "AAPL", "y": 100 },
                    { "x": "MSFT", "y": 50 },
                    { "x": "GOOG", "y": 25 },
                  ],
                },
                {
                  "name": "PRICE",
                  "data": [
                    { "x": "AAPL", "y": 100 },
                    { "x": "MSFT", "y": 50 },
                    { "x": "GOOG", "y": 25 },
                  ],
                },
              ],
            },
          },
        ],
      },
    };
  },
  computed: {
    splitMessage() {
      const content = this.message.content;
      const widgets = this.message.widgets;
      const parts = [];
      let lastIndex = 0;

      widgets.forEach((widget) => {
        const placeholder = `[${widget.id}]`;
        const idx = content.indexOf(placeholder, lastIndex);
        if (idx > lastIndex) {parts.push({ type: 'text', content: content.substring(lastIndex, idx) });}
        parts.push({ type: widget.type, params: widget.params });
        lastIndex = idx + placeholder.length;
      });

      if (lastIndex < content.length) {parts.push({ type: 'text', content: content.substring(lastIndex) });}
      return parts;
    },
  },
};
</script>

<style scoped>
/* Optional styling for the message content */
.message-content {
  font-size: 16px;
  margin-bottom: 20px;
  color: white;
}
</style>
