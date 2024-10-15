import { reactive } from "vue";
import { io } from "socket.io-client";

export const state = reactive({
  connected: false,
  fooEvents: [],
  barEvents: [],
  aiTokenEvents: [],
  LLMResponseEvents: []
});

// "undefined" means the URL will be computed from the `window.location` object
// const URL = process.env.NODE_ENV === "production" ? undefined : "http://localhost:5000";
import {config} from '@/config';
export const socket = io(config.webUrl);
