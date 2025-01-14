<template>
  <div class="widget-container">
    <div class="widget-container-child">
      <apexchart
        :options="chartOptions"
        :series="chartSeries"
        ref="chart"
      />
    </div>
  </div>
</template>

<script>
import VueApexCharts from "vue3-apexcharts";

export default {
  name: "ApexChartsWidget",
  props: {
    params: {
      type: [Object, String],
      required: true,
    },
    theme: {
      type: String,
      default: "light",
    },
  },
  components: {
    apexchart: VueApexCharts,
  },
  data() {
    return {
      chartOptions: {
        chart: {
          type: "treemap",
          fontFamily: "Inter, sans-serif",
          toolbar: {
            show: false,
          },
          background: "transparent",
        },
        theme: {
          mode: this.theme,
        },
        grid: {
          padding: {
            top: -20,
            right: 0,
            bottom: 0,
            left: 0,
          },
        },
        states: {
          hover: {
            filter: {
              type: 'none'
            }
          },
          active: {
            filter: {
              type: 'none'
            }
          }
        },
        dataLabels: {
          enabled: true,
          style: {
            fontSize: "12px",
            fontFamily: "Inter, sans-serif",
            fontWeight: "500",
            colors: [this.theme === "dark" ? "#F4F6F9" : "#1a1a1b"],
          },
          formatter: function (text, op) {
            const total = op.w.globals.seriesTotals.reduce((a, b) => a + b, 0);
            const value = op.value;
            const percentage = ((value / total) * 100).toFixed(2);
            return [`${text}`, `$${value}`, `${percentage}%`];
          },
          textAnchor: "middle",
          offsetY: -6,
        },
        tooltip: {
          enabled: false,
          custom({ series, seriesIndex, dataPointIndex, w }) {
            const total = w.globals.seriesTotals.reduce((a, b) => a + b, 0);
            const value = series[seriesIndex][dataPointIndex];
            const percentage = ((value / total) * 100).toFixed(2);

            return `
              <div style="padding: 10px; background-color: #121212; color: #fff; font-family: Inter, sans-serif; box-shadow: none;">
                $${value}<br>
                ${percentage}%
              </div>`;
          },
        },
        plotOptions: {
          treemap: {
            enableShades: true,
            distributed: false,
          },
        },
        stroke: {
          colors: [this.theme === "dark" ? "#1a1a1b" : "#F4F6F9"],
          width: 5,
        },
        colors: this.theme === "dark" 
          ? ["#2a3b54", "#404045", "#8a7300"] 
          : ["#4a90e2", "#D1D5DB", "#ffd54f"],
      },
    };
  },
  computed: {
    chartSeries() {
      const parsedParams = typeof this.params === "string" ? JSON.parse(this.params) : this.params;
      return parsedParams.series;
    },
  },
};
</script>

<style scoped>
.widget-container-child {
  position: relative;
  margin: -10px;
  margin-bottom: -20px;
}
</style>
