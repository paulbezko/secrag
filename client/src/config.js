// src/config.js
const dev = {
  apiUrl: "http://192.168.0.128:5000",
  webUrl: "http://192.168.0.128:8080",
  socketUrl: "http://192.168.0.128:5000",
};

// const dev = {
//   apiUrl: 'http://localhost:5000',
//   webUrl: 'http://localhost:5000',
//   socketUrl: 'http://localhost:5000'
// };

const prod = {
  apiUrl: "https://alpha.secrag.com",
  webUrl: "https://alpha.secrag.com",
  socketUrl: "https://alpha.secrag.com",
};

export const config = process.env.NODE_ENV === "production" ? prod : dev;
