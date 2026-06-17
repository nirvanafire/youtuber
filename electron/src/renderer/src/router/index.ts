import { createRouter, createWebHashHistory } from "vue-router";

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: "/",
      component: () => import("../components/AppLayout.vue"),
      children: [
        { path: "", name: "home", component: () => import("../views/HomeView.vue") },
        { path: "downloads", name: "downloads", component: () => import("../views/DownloadView.vue") },
        { path: "settings", name: "settings", component: () => import("../views/SettingsView.vue") },
      ],
    },
  ],
});

export default router;
