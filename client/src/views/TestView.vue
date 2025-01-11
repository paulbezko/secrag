<template>
  <div></div>
</template>

<script>
export default {
  data() {
    return {
      chartData: ` {'type': 'multi_dimentional_treemap', 'params': {'series': [{'name': 'Assets 2024 (in millions)', 'data': [{'x': 'Current Assets', 'y': 152987.0}, {'x': 'Non-Current Assets', 'y': 211993.0}]}, {'name': 'Liabilities 2024 (in millions)', 'data': [{'x': 'Current Liabilities', 'y': 176392.0}, {'x': 'Non-Current Liabilities', 'y': 131638.0}]}, {'name': "Shareholders' Equity 2024 (in millions)", 'data': [{'x': 'Common stock and additional paid-in capital', 'y': 83276.0}, {'x': 'Accumulated deficit', 'y': -19154.0}, {'x': 'Accumulated other comprehensive loss', 'y': -7172.0}]}]}}`
    };
  },
  mounted() {
    let correctedData = ""; // Define correctedData outside the try block
    try {
      // 1. Replace single quotes with double quotes
      correctedData = this.chartData.replace(/'/g, '"');

      // 2. Fix embedded single quotes (e.g., Shareholders' Equity)
      correctedData = correctedData.replace(/"([a-zA-Z\s]+)'([a-zA-Z\s]+)"/g, '"$1\'$2"');

      // 3. Parse the JSON
      const parsedData = JSON.parse(correctedData);

      // Log the result
      console.log(parsedData);
    } catch (error) {
      // Log the specific error and the corrected string for debugging
      console.error("Error parsing chartData:", error);
      console.error("Corrected JSON string:", correctedData); // correctedData is now accessible here
    }
  }
};
</script>
