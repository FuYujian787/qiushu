<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'
import NavBar from '@/components/NavBar.vue'
import AppFooter from '@/components/AppFooter.vue'
import AIChat from '@/components/AIChat.vue'
import CyberBackground from '@/components/CyberBackground.vue'

const router = useRouter()
const auth = useAuthStore()
const { initTheme } = useTheme()

onMounted(async () => {
  initTheme()
  // 尝试自动登录
  const restored = await auth.tryAutoLogin()
  if (!restored && localStorage.getItem('qiu-shu-token')) {
    // 有 token 但已过期
    await auth.fetchProfile()
  }
})
</script>

<template>
  <div class="app-shell">
    <!-- Cyber theme atmospheric background (dark mode only) -->
    <CyberBackground />
    <NavBar />
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <AppFooter />
    <AIChat />
  </div>
</template>

<style>
/* ── Global Reset & Layering ──────────────────────────── */
*,
*::before,
*::after {
  box-sizing: border-box;
}

html {
  background: var(--surface-primary);
  transition: background 0.5s ease;
}

body {
  margin: 0;
  font-family: var(--font-body);
  color: var(--text-primary);
  background: var(--surface-primary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  position: relative;
}

.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  position: relative;
  z-index: 1;
}

.main-content {
  flex: 1;
  margin-top: 64px;
  position: relative;
  z-index: 1;
}

@media (max-width: 768px) {
  .main-content {
    margin-top: 56px;
  }
}

/* 页面过渡动画 */
.page-fade-enter-active {
  animation: pageIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.page-fade-leave-active {
  animation: pageOut 0.25s ease-in both;
}

@keyframes pageIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pageOut {
  from { opacity: 1; transform: translateY(0); }
  to { opacity: 0; transform: translateY(-10px); }
}
</style>
