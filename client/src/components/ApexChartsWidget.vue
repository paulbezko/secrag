<template>
  <apexchart
    :options="chartOptions"
    :series="chartSeries"
    ref="chart"
  />
</template>

<script>
import VueApexCharts from "vue3-apexcharts";

export default {
  name: 'ApexChartsWidget',
  props: {
    params: {
      type: Object,
      required: true,
    },
    theme: {
      type: String,
      default: 'light',
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
        },
        resize: {
          enabled: false,
        },
        grid: {
          padding: {
            top: -20,
            right: 0,
            bottom: 0,
            left: 0,
          },
        },
        dataLabels: {
          enabled: true,
          style: {
            fontSize: "12px",
            fontFamily: "Inter, sans-serif",
            fontWeight: "500",
            colors: ["#F4F6F9"],
            theme: 'dark'
          },
        },
        plotOptions: {
          treemap: {
            distributed: true,
          },
        },
        stroke: {
          colors: [this.theme === 'dark' ? '#1a1a1b' : '#F4F6F9'],
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
          data: this.params.data,
        },
      ];
    },
  },
};
</script>