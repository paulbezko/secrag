const { defineConfig } = require('@vue/cli-service')
const webdata = require('./src/webdata.json');
module.exports = defineConfig({
  devServer: {
    allowedHosts: "all"
  },
  pages: {
    index: {
      entry: 'src/main.js',
      template: 'public/index.html',
      filename: 'index.html',
      title: webdata.projectName,
    },
  },
});
