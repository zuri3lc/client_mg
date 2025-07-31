import { createRouter, createWebHistory } from "vue-router"
import { useAuthStore } from '@/stores/auth';
import AppLayout from '@/components/AppLayout.vue'
import LoginView from "@/views/LoginView.vue"
import HomeView from '@/views/HomeView.vue'
import RegisterView from '@/views/RegisterView.vue';
import NewClientView from '@/views/NewClientView.vue';
import ClientDetailView from "@/views/ClientDetailView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/login",
      name: "login",
      component: LoginView
    },
    {
      path: "/register",
      name: "register",
      component: RegisterView
    },
    {
      path: "/",
      component: AppLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: "",
          name: "home",
          component: HomeView
        },
        {
          path: "/client/new",
          name: "new-client",
          component: NewClientView
        },
        {
          path: "/client/:id",
          name: "client-detail",
          component: ClientDetailView
        }
      ]

    }

  ]
});

// NavigationGuard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = !!authStore.token;

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: "login" });
  } else if (to.name === "login" && isAuthenticated) {
    next({ name: "home" });
  } else {
    next();
  }
});

export default router;  