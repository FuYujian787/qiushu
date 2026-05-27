<template>
  <div class="notif-page">
    <div v-if="!store.isLoggedIn.value" class="empty-state">请先登录查看消息</div>
    <template v-else>
      <h2 class="page-title">消息通知</h2>
      <div v-if="notifs.length === 0" class="empty-state">
        <div class="empty-icon"><span class="iconify" data-icon="solar:bell-bing-outline" data-width="48"></span></div>
        <p>暂无消息通知</p>
      </div>
      <div v-else class="notif-list">
        <div v-for="n in reversedNotifs" :key="n.time + (n.title || '')" class="notif-item">
          <h4>{{ n.title }}</h4>
          <p class="notif-desc">{{ n.desc }}</p>
          <p class="notif-time">{{ n.time }}</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useStore } from '../../stores/useStore'

const store = useStore()

const notifs = computed(() => {
  if (!store.currentUser.value) return []
  return store.userNotifications.value[store.currentUser.value.name] || []
})

const reversedNotifs = computed(() => {
  return [...notifs.value].reverse()
})

onMounted(() => {
  if (store.currentUser.value) {
    store.markAllRead(store.currentUser.value.name)
  }
})
</script>

<style scoped>
.notif-page {}
.page-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 1.5rem; color: var(--text-primary); }
.empty-state { background: var(--glass-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--glass-border); border-radius: 1.5rem; padding: 2.5rem; text-align: center; color: var(--text-tertiary); }
.empty-icon { margin-bottom: 1rem; }
.empty-icon :deep(.iconify) { color: var(--text-tertiary); }
.empty-state p { font-size: 1.125rem; margin: 0; }
.notif-list { display: flex; flex-direction: column; gap: 1rem; }
.notif-item { background: var(--glass-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--glass-border); border-radius: 1rem; padding: 1.5rem; box-shadow: var(--glass-shadow); }
.notif-item h4 { font-weight: 700; margin: 0; color: var(--text-primary); }
.notif-desc { font-size: 0.875rem; color: var(--text-secondary); margin: 0.5rem 0; }
.notif-time { font-size: 0.75rem; color: var(--text-tertiary); margin: 0; }
</style>
