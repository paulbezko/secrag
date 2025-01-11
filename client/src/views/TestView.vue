<template>
  <div id="svg-sankey" style="display: flex; justify-content: center;"></div>
</template>

<script>
import { onMounted } from 'vue';

// Import the ApexSankey library from the local path
import ApexSankey from '../../libraries/apexsankey-main/apexsankey.es.min.js';

export default {
name: 'SankeyChart',
setup() {
  // Define the chart data using your provided JSON
  const data = {
    nodes: [
      { id: 'Net Sales', title: 'Net Sales' },
      { id: 'Cost of Sales', title: 'Cost of Sales' },
      { id: 'Gross Margin', title: 'Gross Margin' },
      { id: 'Operating Expenses', title: 'Operating Expenses' },
      { id: 'Operating Income', title: 'Operating Income' },
      { id: 'Other Income', title: 'Other Income/(Expense), Net' },
      { id: 'Income Before Taxes', title: 'Income Before Provision for Income Taxes' },
      { id: 'Provision for Taxes', title: 'Provision for Income Taxes' },
      { id: 'Net Income', title: 'Net Income' }
    ],
    edges: [
      { source: 'Net Sales', target: 'Cost of Sales', value: 46099.0 },
      { source: 'Net Sales', target: 'Gross Margin', value: 39678.0 },
      { source: 'Gross Margin', target: 'Operating Expenses', value: 14326.0 },
      { source: 'Gross Margin', target: 'Operating Income', value: 25352.0 },
      { source: 'Operating Income', target: 'Other Income', value: 142.0 },
      { source: 'Operating Income', target: 'Income Before Taxes', value: 25494.0 },
      { source: 'Income Before Taxes', target: 'Provision for Taxes', value: 4046.0 },
      { source: 'Income Before Taxes', target: 'Net Income', value: 21448.0 }
    ]
  };

  const graphOptions = {
    nodeWidth: 20,
    fontFamily: 'Quicksand, sans-serif',
    fontWeight: 600,
    height: 600,
  };

  // Render the Sankey chart after the component is mounted
  onMounted(() => {
    // Initialize the ApexSankey chart
    const s = new ApexSankey(document.getElementById('svg-sankey'), graphOptions);
    s.render(data);
  });

  return {
    data,
    graphOptions,
  };
},
};
</script>

<style scoped>
</style>