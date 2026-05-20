<template>
  <div class="app-container">
    <TheSidebar v-if="showSidebar" />
    <main class="main-area" :class="{ 'full-width': !showSidebar }">
      <ThePageHeader v-if="showSidebar" />
      <div class="page-content">
        <LoginPage v-if="store.currentPage.value === 'login'" />
        <RegisterPage v-else-if="store.currentPage.value === 'register'" />
        <HomePage v-else-if="store.currentPage.value === 'home'" />
        <ProcurementPage v-else-if="store.currentPage.value === 'procurement'" />
        <CartPage v-else-if="store.currentPage.value === 'cart'" />
        <OrderPage v-else-if="store.currentPage.value === 'orders'" />
        <NotificationPage v-else-if="store.currentPage.value === 'notifications'" />
        <CommunityPage v-else-if="store.currentPage.value === 'community'" />
        <ProfilePage v-else-if="store.currentPage.value === 'profile'" />
        <PublishPage v-else-if="store.currentPage.value === 'publish'" />
        <BookDetailPage v-else-if="store.currentPage.value === 'bookDetail'" />
        <PaymentPage v-else-if="store.currentPage.value === 'payment'" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useStore } from './stores/useStore'
import TheSidebar from './components/TheSidebar.vue'
import ThePageHeader from './components/ThePageHeader.vue'
import LoginPage from './components/pages/LoginPage.vue'
import RegisterPage from './components/pages/RegisterPage.vue'
import HomePage from './components/pages/HomePage.vue'
import ProcurementPage from './components/pages/ProcurementPage.vue'
import CartPage from './components/pages/CartPage.vue'
import OrderPage from './components/pages/OrderPage.vue'
import NotificationPage from './components/pages/NotificationPage.vue'
import CommunityPage from './components/pages/CommunityPage.vue'
import ProfilePage from './components/pages/ProfilePage.vue'
import PublishPage from './components/pages/PublishPage.vue'
import BookDetailPage from './components/pages/BookDetailPage.vue'
import PaymentPage from './components/pages/PaymentPage.vue'

const store = useStore()
const authPages = ['login', 'register']
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
      store.currentPage.value = 'home'
      return
    }
  }
  store.currentPage.value = 'login'
})
</script>

<style>
body {
  margin: 0;
  padding: 0;
  background-color: #f3f2f7;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
</style>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
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
</style>
