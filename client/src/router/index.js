import { createRouter, createWebHistory } from 'vue-router'

/**
 * 获取存储的 token（优先使用 Pinia store，降级到 localStorage）
 * 注意：在 router 文件中不能直接使用 useAuthStore()（Pinia 尚未安装），
 * 但可以通过直接读取 pinia state 或 localStorage 实现。
 * 这里使用统一常量与 stores/auth.js 保持一致。
 */
const AUTH_TOKEN_KEY = 'qiu-shu-token'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: '首页', requiresAuth: false },
  },
  {
    path: '/auth',
    name: 'Auth',
    component: () => import('@/views/AuthView.vue'),
    meta: { title: '登录 / 注册', requiresAuth: false },
  },
  {
    path: '/browse',
    name: 'Browse',
    component: () => import('@/views/BrowseView.vue'),
    meta: { title: '浏览书籍', requiresAuth: false },
  },
  {
    path: '/book/:id',
    name: 'BookDetail',
    component: () => import('@/views/BookDetailView.vue'),
    meta: { title: '书籍详情', requiresAuth: false },
  },
  {
    path: '/publish',
    name: 'Publish',
    component: () => import('@/views/PublishView.vue'),
    meta: { title: '发布书籍', requiresAuth: true },
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('@/views/OrdersView.vue'),
    meta: { title: '订单管理', requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { title: '个人中心', requiresAuth: true },
  },
  {
    path: '/forum',
    name: 'Forum',
    component: () => import('@/views/ForumView.vue'),
    meta: { title: '课程论坛', requiresAuth: false },
  },
  {
    path: '/forum/post/:id',
    name: 'PostDetail',
    component: () => import('@/views/PostDetailView.vue'),
    meta: { title: '帖子详情', requiresAuth: false },
  },
  {
    path: '/wishes',
    name: 'Wishes',
    component: () => import('@/views/WishesView.vue'),
    meta: { title: '求书许愿墙', requiresAuth: false },
  },
  {
    path: '/exchange',
    name: 'Exchange',
    component: () => import('@/views/ExchangeView.vue'),
    meta: { title: '以书换书', requiresAuth: false },
  },
  {
    path: '/tree',
    name: 'Tree',
    component: () => import('@/views/TreeView.vue'),
    meta: { title: '知识传承树', requiresAuth: false },
  },
  {
    path: '/messages',
    name: 'Messages',
    component: () => import('@/views/MessagesView.vue'),
    meta: { title: '消息', requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || '求书 · 書緣'} — 浙江大学二手书交易平台`

  const token = localStorage.getItem(AUTH_TOKEN_KEY)
  if (to.meta.requiresAuth && !token) {
    next({ name: 'Auth', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

// 页面入场动画
router.afterEach(() => {
  const main = document.querySelector('.page-enter')
  if (main) {
    main.style.animation = 'none'
    main.offsetHeight // trigger reflow
    main.style.animation = ''
  }
})

export default router
