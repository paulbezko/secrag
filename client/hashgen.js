// generateHash.js
const fs = require('fs');

// Generate a timestamp
const timestamp = Date.now();

// Read the index.html file
fs.readFile('public/template.html', 'utf8', (err, data) => {
  if (err) throw err;

  // Replace {{hash}} with the generated timestamp
  const result = data.replace('{{hash}}', timestamp);

  // Write the updated content back to index.html
  fs.writeFile('public/index.html', result, 'utf8', (err) => {
    if (err) throw err;
    console.log(`Timestamp ${timestamp} added to index.html`);
  });
});