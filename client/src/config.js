// src/config.js
const dev = {
  apiUrl: 'http://localhost:5000',
  webUrl: 'http://localhost:8080',
  socketUrl: 'http://localhost:8080' 
};

const prod = {
  apiUrl: 'https://secrag.com',
  webUrl: 'https://secrag.com',
  socketUrl: 'https://secrag.com'
};

// const prod = {
//   apiUrl: 'https://collab-skeltal.onrender.com',
//   webUrl: 'https://collab-skeltal.onrender.com'
// };

export const config = process.env.NODE_ENV === 'production' ? prod : dev;