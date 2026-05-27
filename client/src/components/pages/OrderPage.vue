<template>
  <div class="order-page">
    <div v-if="!store.isLoggedIn.value" class="empty-state">请先登录</div>
    <template v-else>
      <h2 class="page-title">我的订单</h2>
      <div v-if="userOrders.length === 0" class="empty-state">
        <div class="empty-icon"><span class="iconify" data-icon="solar:bill-list-outline" data-width="48"></span></div>
        <p>暂无订单记录</p>
      </div>
      <div v-else class="order-list">
        <div v-for="o in userOrders" :key="o.id" class="order-item">
          <div class="order-info">
            <h4>{{ o.title }}</h4>
            <p class="order-meta">{{ o.id }} · {{ o.date }}</p>
          </div>
          <div class="order-status">¥{{ o.price }} ({{ o.status }})</div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from '../../stores/useStore'

const store = useStore()
const userOrders = computed(() => {
  if (!store.currentUser.value) return []
  return store.orders.value.filter(o => o.buyer === store.currentUser.value.name)
})
</script>

<style scoped>
.order-page {}
.page-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 1.5rem; color: var(--text-primary); }
.empty-state { background: var(--glass-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--glass-border); border-radius: 1.5rem; padding: 2.5rem; text-align: center; color: var(--text-tertiary); }
.empty-icon { margin-bottom: 1rem; }
.empty-icon :deep(.iconify) { color: var(--text-tertiary); }
.empty-state p { font-size: 1.125rem; margin: 0; }
.order-list { display: flex; flex-direction: column; gap: 1rem; }
.order-item { background: var(--glass-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--glass-border); border-radius: 1.5rem; padding: 1.5rem; box-shadow: var(--glass-shadow); display: flex; justify-content: space-between; align-items: center; }
.order-info h4 { font-weight: 700; margin: 0; color: var(--text-primary); }
.order-meta { font-size: 0.75rem; color: var(--text-tertiary); margin: 0.25rem 0 0 0; }
.order-status { color: var(--lavender-accent); font-weight: 700; }
</style>
