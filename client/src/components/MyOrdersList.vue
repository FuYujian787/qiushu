<script setup>
defineProps({
  orders: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['order-click'])

function getStatusClass(status) {
  const map = {
    '待确认': 'pending',
    '已确认': 'confirmed',
    '已完成': 'done',
    '已取消': 'cancelled',
  }
  return map[status] || ''
}
</script>

<template>
  <div class="my-orders-list">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="orders.length === 0" class="empty">
      <p>暂无订单</p>
    </div>
    <div v-else class="order-list">
      <div
        v-for="order in orders"
        :key="order.id"
        class="order-item"
        @click="emit('order-click', order)"
      >
        <div class="order-main">
          <span class="order-title">{{ order.book_title || '未知书籍' }}</span>
          <span :class="['order-status', getStatusClass(order.status)]">{{ order.status }}</span>
        </div>
        <div class="order-meta">
          <span>¥{{ order.book_price || 0 }}</span>
          <span v-if="order.buyer_name">买家: {{ order.buyer_name }}</span>
          <span v-if="order.seller_name">卖家: {{ order.seller_name }}</span>
          <span>{{ order.created_at?.slice(0, 10) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.order-list { display: flex; flex-direction: column; gap: 8px; }

.order-item {
  padding: 14px 16px;
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.order-item:hover { border-color: var(--accent-primary); }

.order-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.order-title { font-size: 14px; color: var(--text-primary); font-weight: 600; }

.order-status {
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.order-status.pending { background: #FFF3E0; color: #E65100; }
.order-status.confirmed { background: #E3F2FD; color: #1565C0; }
.order-status.done { background: #E8F5E9; color: #2E7D32; }
.order-status.cancelled { background: #F5F5F5; color: #9E9E9E; }

[data-theme="cyber"] .order-status.pending { background: rgba(255,152,0,0.12); color: #FF9800; }
[data-theme="cyber"] .order-status.confirmed { background: rgba(0,212,255,0.12); color: #00D4FF; }
[data-theme="cyber"] .order-status.done { background: rgba(168,85,247,0.12); color: #A855F7; }
[data-theme="cyber"] .order-status.cancelled { background: rgba(255,255,255,0.04); color: #5A6080; }

.order-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-muted);
}

.loading, .empty { text-align: center; padding: 40px; color: var(--text-muted); font-size: 14px; }
</style>
