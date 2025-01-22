<template>
  <div class="widget-container">
    <div class="widget-container-child">
      <div ref="chartContainer" style="width: 100%; height: 400px;"></div>
    </div>
  </div>
</template>

<script>
import { createChart } from 'lightweight-charts';

export default {
  name: 'LightweightChart',
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

  mounted() {
    const chartContainer = this.$refs.chartContainer;
    const chart = createChart(chartContainer, {
      width: chartContainer.clientWidth,
      height: chartContainer.clientHeight,
      layout: {
        background: {
          'type': 'solid',
          'color': 'transparent',
        },
        textColor: this.theme === 'dark' ? "#F4F6F9" : "#1a1a1b"
      },

      grid: {
        vertLines: {
          color: 'transparent',
        },
        horzLines: {
          color: 'transparent',
        },
      },
      timeScale: {
        rightOffset: 0,
        barSpacing: 6,
      }
    });

    const areaSeries = chart.addAreaSeries(
      {
        lineColor: this.theme === 'dark' ? '#1f4a75' : "#6c98c4",
        topColor: this.theme === 'dark' ? '#1f4a75' : "#6c98c4",
        bottomColor: this.theme === 'dark' ? "#1a1a1b" : "#F4F6F9"
      }
    );

    chart.timeScale().fitContent();
    chart.timeScale().applyOptions({borderColor: "transparent"});
    chart.priceScale("right").applyOptions({borderColor: "transparent"});
    areaSeries.setData(this.params.series[0].data);

    const resizeObserver = new ResizeObserver(() => {
      chart.resize(chartContainer.clientWidth, chartContainer.clientHeight);
    });

    resizeObserver.observe(chartContainer);
  },
};
</script>

<style scoped>
.widget-container table {
  margin-block: 0 !important;
}

.widget-container-child {
  width: 100%; 
  height: 400px;
}

.widget-container-child * {
  border: none;
  /* overflow: hidden; */
}

.widget-container-child td {
  margin: -1px;
}

canvas {
  background-color: #132d4a !important;
}
</style>
<style>
.widget-container-child table {
  margin: -1px !important;
}
</style>