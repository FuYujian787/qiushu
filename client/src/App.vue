<template>
  <div class="app-container">
    <StarCanvas />
    <a href="#main-content" class="skip-to-content">跳到主要内容</a>
    <Transition name="sidebar-fade">
      <TheSidebar v-if="showSidebar" />
    </Transition>
    <main class="main-area" :class="{ 'full-width': !showSidebar }" id="main-content" tabindex="-1">
      <ThePageHeader v-if="showSidebar" />
      <div class="page-content">
        <Transition name="page-enter" mode="out-in" @before-enter="onBeforeEnter">
          <LoginPage v-if="store.currentPage.value === 'login'" key="login" />
          <RegisterPage v-else-if="store.currentPage.value === 'register'" key="register" />
          <WelcomePage v-else-if="store.currentPage.value === 'welcome'" key="welcome" />
          <HomePage v-else-if="store.currentPage.value === 'home'" key="home" />
          <ProcurementPage v-else-if="store.currentPage.value === 'procurement'" key="procurement" />
          <StallPage v-else-if="store.currentPage.value === 'stall'" key="stall" />
          <CartPage v-else-if="store.currentPage.value === 'cart'" key="cart" />
          <OrderPage v-else-if="store.currentPage.value === 'orders'" key="orders" />
          <NotificationPage v-else-if="store.currentPage.value === 'notifications'" key="notifications" />
          <CommunityPage v-else-if="store.currentPage.value === 'community'" key="community" />
          <ProfilePage v-else-if="store.currentPage.value === 'profile'" key="profile" />
          <PublishPage v-else-if="store.currentPage.value === 'publish'" key="publish" />
          <BookDetailPage v-else-if="store.currentPage.value === 'bookDetail'" key="bookDetail" />
          <PaymentPage v-else-if="store.currentPage.value === 'payment'" key="payment" />
          <ChatPage v-else-if="store.currentPage.value === 'chat'" key="chat" />
        </Transition>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useStore } from './stores/useStore'
import StarCanvas from './components/StarCanvas.vue'
import TheSidebar from './components/TheSidebar.vue'
import ThePageHeader from './components/ThePageHeader.vue'
import LoginPage from './components/pages/LoginPage.vue'
import RegisterPage from './components/pages/RegisterPage.vue'
import HomePage from './components/pages/HomePage.vue'
import ProcurementPage from './components/pages/ProcurementPage.vue'
import StallPage from './components/pages/StallPage.vue'
import CartPage from './components/pages/CartPage.vue'
import OrderPage from './components/pages/OrderPage.vue'
import NotificationPage from './components/pages/NotificationPage.vue'
import CommunityPage from './components/pages/CommunityPage.vue'
import ProfilePage from './components/pages/ProfilePage.vue'
import PublishPage from './components/pages/PublishPage.vue'
import BookDetailPage from './components/pages/BookDetailPage.vue'
import PaymentPage from './components/pages/PaymentPage.vue'
import ChatPage from './components/pages/ChatPage.vue'
import WelcomePage from './components/pages/WelcomePage.vue'

const store = useStore()
const authPages = ['login', 'register', 'welcome']
const showSidebar = computed(() => !authPages.includes(store.currentPage.value))

onMounted(async () => {
  store.initFromLocal()
  const [userRes, postRes, catRes] = await Promise.all([
    fetch('/data/users.json'),
    fetch('/data/community-posts.json'),
    fetch('/data/categories.json'),
  ])
  store.users.value = await userRes.json()
  store.communityPosts.value = await postRes.json()
  store.categoriesData.value = await catRes.json()
  store.generateProducts(store.categoriesData.value)

  const savedName = localStorage.getItem(store.KEYS.loggedInUser)
  if (savedName) {
    const user = store.users.value.find(u => u.name === savedName)
    if (user) {
      store.login(user)
      store.currentPage.value = store.hasSeenWelcome.value ? 'home' : 'welcome'
      return
    }
  }
  store.currentPage.value = 'login'
})

let prevRoute = ''
function onBeforeEnter(el) {
  prevRoute = store.currentPage.value
}
</script>

<style>
/* 全局背景已统一由 apple-liquid-glass.css 管理 */
</style>

<style>
/* ========== 全局私聊按钮样式 ========== */
.chat-btn-mini {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border: none;
  border-radius: 50%;
  background: linear-gradient(135deg, #DCD0FF, #C4B5E0);
  color: #4a3f6b;
  font-size: 0.75rem;
  cursor: pointer;
  margin-left: 0.5rem;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  box-shadow: 0 2px 8px rgba(155, 142, 196, 0.25);
  vertical-align: middle;
  line-height: 1;
}
.chat-btn-mini:hover {
  transform: scale(1.15);
  box-shadow: 0 4px 16px rgba(155, 142, 196, 0.4);
  background: linear-gradient(135deg, #E8DFFF, #D4C8F0);
}
.chat-btn-mini:active {
  transform: scale(0.95);
}
</style>

<style scoped>

.app-container {
  display: flex;
  height: 100vh;
  height: 100dvh;
  overflow: hidden;
}

.skip-to-content {
  position: absolute;
  top: -100%;
  left: 0.5rem;
  z-index: 1000;
  padding: 0.75rem 1.25rem;
  background: var(--color-primary, #6c3fc0);
  color: #fff;
  font-weight: 600;
  font-size: 0.875rem;
  border-radius: 0 0 0.75rem 0.75rem;
  text-decoration: none;
  transition: top 0.2s var(--ease-out);
}

.skip-to-content:focus {
  top: 0;
  outline: var(--focus-ring-width) solid var(--focus-ring-color);
  outline-offset: var(--focus-ring-offset);
}

.main-area {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.main-area.full-width {
  width: 100%;
}
.page-content {
  flex-grow: 1;
  overflow-y: auto;
  padding: 2.5rem;
}

@media (max-width: 768px) {
  .page-content {
    padding: 1rem;
  }
}

/* ===== 页面切换动画 ===== */
.page-enter-enter-active,
.page-enter-leave-active {
  transition: opacity 0.25s var(--ease-out), transform 0.25s var(--ease-out);
}

.page-enter-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.page-enter-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* ===== 侧栏渐入动画 ===== */
.sidebar-fade-enter-active,
.sidebar-fade-leave-active {
  transition: opacity 0.3s var(--ease-out), transform 0.3s var(--ease-out);
}

.sidebar-fade-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.sidebar-fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
