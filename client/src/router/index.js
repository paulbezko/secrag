import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    component: () => import("../views/HomeView.vue"),
  },
  {
    path: "/terms-and-conditions",
    component: () => import("../views/TermsAndConditionsView.vue"),
  },
  {
    path: "/:pathMatch(.*)",
    component: () => import("../views/404View.vue"),
  },
];

// Route declarations
const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
