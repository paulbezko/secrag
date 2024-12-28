import { config } from "../config";

import axios from "axios";

function getNavbarInfo() {
  return new Promise((resolve, reject) => {
    const token = localStorage.getItem("_u");
    if (token) {
      axios
        .get(`${config.apiUrl}/api/get-user-data`, { params: { token: token } })
        .then((response) => {
          const isSubscribed = response.data.subscription !== "none";
          const subscription = response.data.subscription
            ? response.data.subscription
            : null;
          const subscriptionTokensLeft = response.data.subscription_tokens_left
            ? response.data.subscription_tokens_left
            : null;
          resolve({ isSubscribed, subscription, subscriptionTokensLeft });
        })
        .catch((error) => {
          alert("Error retrieving user data:", error);
          reject(error);
        });
    } else {
      resolve({ isSubscribed: false, subscription: null }); // If no token exists, user is not subscribed
    }
  });
}

export { getNavbarInfo };
