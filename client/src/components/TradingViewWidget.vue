<template>
  <div class="widget-container">
    <div class="widget-container-child" ref="container">
      <div class="tradingview-widget-container__widget"></div>
    </div>
  </div>
</template>

<script>
import { onMounted, ref, watch, } from 'vue';

export default {
  name: 'TradingViewWidget',
  props: {
    ticker: {
      type: String,
      required: true,
    },
    theme: {
      type: String,
      default: 'light',
    },
  },
  setup(props) {
    const container = ref(null);

    // Function to update the widget based on the ticker symbol
    const loadWidget = () => {
      const script = document.createElement('script');
      script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-symbol-overview.js';
      script.type = 'text/javascript';
      script.async = true;
      script.innerHTML = `{
        "symbols": [
          ["${props.ticker}|1M"]
        ],
        "chartOnly": false,
        "width": "100%",
        "height": "400",
        "locale": "en",
        "backgroundColor": ${props.theme === 'dark' ? '"#1a1a1b"' : '"#F4F6F9"'},
        "gridColor": ${props.theme === 'dark' ? '"#2d2d30"' : '"#D1D5DB"'},
        "colorTheme": ${props.theme === 'dark' ? '"dark"' : '"light"'},
        "autosize": true,
        "showVolume": true,
        "showMA": false,
        "hideDateRanges": false,
        "hideMarketStatus": false,
        "hideSymbolLogo": true,
        "scalePosition": "left",
        "scaleMode": "Normal",
        "fontFamily": "-apple-system, BlinkMacSystemFont, Trebuchet MS, Roboto, Ubuntu, sans-serif",
        "fontSize": "10",
        "noTimeScale": false,
        "valuesTracking": "1",
        "changeMode": "price-and-percent",
        "chartType": "area",
        "maLineColor": "#2962FF",
        "maLineWidth": 1,
        "maLength": 9,
        "headerFontSize": "small",
        "lineWidth": 2,
        "lineType": 0,
        "dateRanges": ["1d|1", "1m|30", "3m|60", "12m|1D", "60m|1W", "all|1M"]
      }`;

      // Clear any existing widget before appending a new one
      if (container.value) {
        container.value.innerHTML = '';
        container.value.appendChild(script);
      }
    };

    // Load widget when the component is mounted
    onMounted(() => {
      loadWidget();
    });

    // Watch for changes in the ticker prop and reload the widget
    watch([() => props.ticker, () => props.theme], loadWidget);

    return {
      container,
    };
  },
};
</script>
