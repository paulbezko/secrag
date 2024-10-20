// src/config.js
const dev = {
  apiUrl: 'http://localhost:5000',
  webUrl: 'http://localhost:8080',
  socketUrl: 'http://localhost:5000' 
};

// const prod = {
//   apiUrl: 'http://localhost:5000',
//   webUrl: 'http://localhost:5000'
// };

const prod = {
  apiUrl: 'https://secrag.com',
  webUrl: 'https://secrag.com',
  socketUrl: 'https://secrag.com'
};

export const config = process.env.NODE_ENV === 'production' ? prod : dev;