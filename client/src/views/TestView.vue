<template>
  <div style="width: 600px !important">
    <apexchart
      :options="chartOptions"
      :series="chartSeries"
      ref="chart"
    />
    <div class="button-send" @click="changeTheme">Change Theme {{ theme }}</div>
  </div>
</template>

<script>
import VueApexCharts from "vue3-apexcharts";

export default {
  name: 'TradingViewWidget',
  components: {
    apexchart: VueApexCharts,
  },
  data() {
    return {
      theme: "dark",
      chartData: {
        name: "Apple Inc. Revenue by Sector (2024)",
        data: [
          { x: "iPhone", y: 205.52 },
          { x: "Mac", y: 41.68 },
          { x: "iPad", y: 20.47 },
          { x: "Wearables, Home, and, Accessories", y: 42.35 },
          { x: "Services", y: 103.34 },
        ],
      },
      chartOptions: {
        chart: {
          // height: 250,
          type: "treemap",
          fontFamily: "Inter, sans-serif",
          toolbar: {
            show: false,
          }
        },
        resize: {
          enabled: false
        },
        grid: {
          padding: {
            top: -20,
            right: 0,
            bottom: 0,
            left: 0
          }
        },
        dataLabels: {
          enabled: true,
          style: {
            fontSize: "12px",
            fontFamily: "Inter, sans-serif",
            fontWeight: "500",
            colors: ["#F4F6F9"],
          },
        },
        plotOptions: {
          treemap: {
            distributed: true,
          }
        },
        stroke: {
          colors: ["#1a1a1b"],
          width: 5,
        },
        colors: ["#0b2e52"],
      },
    };
  },
  computed: {
    chartSeries() {
      return [
        {
          data: this.chartData.data,
        },
      ];
    },
  },
  methods: {
    changeTheme() {
      this.theme = this.theme === "light" ? "dark" : "light";

      const newOptions = {
        colors: this.theme === "dark" ? ["#0b2e52"] : ["#0b2e52"],
        stroke: {
          colors: this.theme === "light" ? ["#F4F6F9"] : ["#1a1a1b"],
        },
      };

      // Update chart options dynamically
      this.$refs.chart.updateOptions(newOptions);
    },
  },
};
</script>

<style scoped>
/* Style the SVG elements for labels and text in the chart */
.apexcharts-texts tspan {
  white-space: normal;  /* This might not work as expected due to SVG limitations */
  word-wrap: break-word;
}

.apexcharts-label {
  font-size: 14px; /* Example of CSS targeting labels */
  font-family: 'Arial', sans-serif;
  text-anchor: middle;
  fill: #FFFFFF;
}
.button-send {
  white-space: normal;
  word-wrap: break-word;
  max-width: 200px;
  padding: 10px;
  background-color: #007bff;
  color: white;
  border-radius: 5px;
  cursor: pointer;
}
</style>
