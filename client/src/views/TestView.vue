<template>
  <div style="width: 600px !important">
    <ApexChartsWidget :theme="'light'" :params="params" />
  </div>
</template>

<script>
import ApexChartsWidget from "@/components/ApexChartsWidget.vue";

export default {
  name: "TestView",
  components: {
    ApexChartsWidget,
  },
  data() {
    return {
      params: {
        series: [
          {
            name: "Series 1",
            data: [
              { x: "iPhone", y: 201183 },
              { x: "Mac", y: 29984 },
              { x: "iPad", y: 26694 },
              { x: "Wearables, Home and Accessories", y: 37005 },
              { x: "Services", y: 96169 },
              { x: "Americas", y: 158000 },
              { x: "Europe", y: 102000 },
              { x: "Greater China", y: 85000 },
              { x: "Japan", y: 22000 },
              { x: "Rest of Asia Pacific", y: 24000 },
            ],
          },
          {
            name: "Series 2",
            data: [
              { x: "awdawd", y: 20183 },
              { x: "sad", y: 39984 },
              { x: "dasdad", y: 26694 },
              { x: "Wecaecacaarables, Home and Accessories", y: 37005 },
              { x: "Serwadwadvices", y: 96169 },
            ],
          },
          {
            name: "Series 3",
            data: [
              { x: "awdawd", y: 70183 },
              { x: "sad", y: 39984 },
              { x: "dasdad", y: 26694 },
              { x: "Wecaecacaarables, Home and Accessories", y: 37005 },
              { x: "Serwadwadvices", y: 96169 },
            ],
          },
        ],
      },
    };
  },
};
</script>
