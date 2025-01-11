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
    params: {
      type: Object,
      required: true
    }
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


<!-- 
{'multi_dimentional_treemap': {'series': [{'name': 'Q1 2024 Income Statement (in $ million)', 'data': [{'x': 'Net Sales - Products', 'y': 96458.0}, {'x': 'Net Sales - Services', 'y': 23117.0}, {'x': 'Total Net Sales', 'y': 119575.0}, {'x': 'Cost of Sales - Products', 'y': 58440.0}, {'x': 'Cost of Sales - Services', 'y': 6280.0}, {'x': 'Total Cost of Sales', 'y': 64720.0}, {'x': 'Gross Margin', 'y': 54855.0}, {'x': 'Operating Expenses - R&D', 'y': 7696.0}, {'x': 'Operating Expenses - SG&A', 'y': 6786.0}, {'x': 'Total Operating Expenses', 'y': 14482.0}, {'x': 'Operating Income', 'y': 40373.0}, {'x': 'Net Income', 'y': 33916.0}]}, {'name': 'Q2 2024 Income Statement (in $ million)', 'data': [{'x': 'Net Sales - Products', 'y': 66886.0}, {'x': 'Net Sales - Services', 'y': 23867.0}, {'x': 'Total Net Sales', 'y': 90753.0}, {'x': 'Cost of Sales - Products', 'y': 42424.0}, {'x': 'Cost of Sales - Services', 'y': 6058.0}, {'x': 'Total Cost of Sales', 'y': 48482.0}, {'x': 'Gross Margin', 'y': 42271.0}, {'x': 'Operating Expenses - R&D', 'y': 7903.0}, {'x': 'Operating Expenses - SG&A', 'y': 6468.0}, {'x': 'Total Operating Expenses', 'y': 14371.0}, {'x': 'Operating Income', 'y': 27900.0}, {'x': 'Net Income', 'y': 23636.0}]}]}}
-->