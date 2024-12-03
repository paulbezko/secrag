import { reactive } from "vue";
import { io } from "socket.io-client";

export const state = reactive({
  connected: false,
  fooEvents: [],
  barEvents: [],
  aiTokenEvents: [],
  LLMResponseEvents: []
});


import {config} from '@/config';
export const socket = io(config.socketUrl, {transports: ['websocket', 'polling']});