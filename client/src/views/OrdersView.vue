<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()
const auth = useAuthStore()
const orders = ref([])
const loading = ref(false)
const activeTab = ref('all')

const tabs = [
  { key: 'all', label: '全部' },
  { key: 'buy', label: '买入' },
  { key: 'sell', label: '卖出' },
]

onMounted(async () => {
  await loadOrders()
})

async function loadOrders() {
  loading.value = true
  try {
    const res = await api.get('/orders', { params: { role: activeTab.value } })
    orders.value = res.data || []
  } catch (err) {
    ElMessage.error('加载订单失败')
  } finally {
    loading.value = false
  }
}

async function confirmOrder(orderId) {
  try {
    await api.post(`/orders/${orderId}/confirm`)
    ElMessage.success('订单已确认')
    await loadOrders()
  } catch (err) {
    ElMessage.error(err.message || '操作失败')
  }
}

async function completeOrder(orderId) {
  try {
    await api.post(`/orders/${orderId}/complete`)
    ElMessage.success('交易已完成')
    await loadOrders()
  } catch (err) {
    ElMessage.error(err.message || '操作失败')
  }
}

async function cancelOrder(orderId) {
  try {
    await ElMessageBox.confirm('确定取消此订单？')
    await api.post(`/orders/${orderId}/cancel`)
    ElMessage.success('订单已取消')
    await loadOrders()
  } catch {
    // cancelled
  }
}

function contactPeer(order) {
  const isBuyer = order.buyer_id === auth.userId
  const peerId = isBuyer ? order.seller_id : order.buyer_id
  const peerName = isBuyer ? order.seller_name : order.buyer_name

  router.push({
    name: 'Messages',
    query: {
      user_id: peerId,
      user_name: peerName,
      book_id: order.book_id,
      book_title: order.book_title,
      order_id: order.id,
    },
  })
}

function getStatusClass(status) {
  const map = {
    '待确认': 'status-pending',
    '已确认': 'status-confirmed',
    '已完成': 'status-done',
    '已取消': 'status-cancelled',
  }
  return map[status] || ''
}
</script>

<template>
  <div class="orders-page page-enter">
    <div class="page-container">
      <h1 class="page-title">订单管理</h1>

      <div class="order-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          :class="['tab', { active: activeTab === tab.key }]"
          @click="activeTab = tab.key; loadOrders()"
        >
          {{ tab.label }}
        </button>
      </div>

      <div v-if="loading" class="loading">加载中...</div>

      <div v-else-if="orders.length === 0" class="empty">
        <p>暂无订单</p>
      </div>

      <div v-else class="order-list">
        <div v-for="order in orders" :key="order.id" class="order-card">
          <div class="order-header">
            <span class="order-book">{{ order.book_title || '未知书籍' }}</span>
            <span :class="['order-status', getStatusClass(order.status)]">{{ order.status }}</span>
          </div>
          <div class="order-body">
            <div class="order-info">
              <p>价格：¥{{ order.book_price }}</p>
              <p>卖家：{{ order.seller_name }}</p>
              <p>买家：{{ order.buyer_name }}</p>
              <p>下单时间：{{ order.created_at?.slice(0, 10) }}</p>
            </div>
          </div>
          <div class="order-actions" v-if="order.status === '待确认'">
            <button
              v-if="order.seller_id === auth.userId"
              class="btn-confirm"
              @click="confirmOrder(order.id)"
            >
              确认订单
            </button>
            <button class="btn-contact" @click="contactPeer(order)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              联系{{ order.seller_id === auth.userId ? '买家' : '卖家' }}
            </button>
            <button class="btn-cancel" @click="cancelOrder(order.id)">取消</button>
          </div>
          <div class="order-actions" v-else-if="order.status === '已确认'">
            <button class="btn-confirm" @click="completeOrder(order.id)">确认完成</button>
            <button class="btn-contact" @click="contactPeer(order)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              联系{{ order.seller_id === auth.userId ? '买家' : '卖家' }}
            </button>
          </div>
          <div class="order-actions" v-else-if="order.status === '已完成'">
            <button class="btn-contact" @click="contactPeer(order)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              联系{{ order.seller_id === auth.userId ? '买家' : '卖家' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-title {
  font-family: var(--font-display);
  font-size: 24px;
  color: var(--text-primary);
  font-weight: 700;
  margin-bottom: 24px;
}

.order-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 24px;
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  padding: 4px;
  width: fit-content;
}

.tab {
  padding: 8px 20px;
  border: none;
  background: none;
  border-radius: 6px;
  font-size: 14px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.tab.active {
  background: var(--accent-primary);
  color: #fff;
}

[data-theme="cyber"] .tab.active {
  background: linear-gradient(135deg, #00D4FF, #A855F7);
}

.order-card {
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 20px;
  margin-bottom: 12px;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.order-book {
  font-weight: 600;
  font-size: 15px;
  color: var(--text-primary);
}

.order-status {
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.status-pending { background: #FFF8E1; color: #F57F17; }
.status-confirmed { background: #E3F2FD; color: #1565C0; }
.status-done { background: #E8F5E9; color: #2E7D32; }
.status-cancelled { background: #F5F5F5; color: #9E9E9E; }

.order-info p {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.order-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-default);
}

.btn-confirm, .btn-cancel {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-confirm {
  background: var(--accent-primary);
  color: #fff;
}

.btn-confirm:hover { opacity: 0.9; }

[data-theme="cyber"] .btn-confirm {
  background: linear-gradient(135deg, #00D4FF, #A855F7);
}

.btn-cancel {
  background: transparent;
  border: 1px solid var(--border-default);
  color: var(--text-secondary);
}

.btn-contact {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
  border: 1px solid var(--accent-primary);
  border-radius: 6px;
  background: transparent;
  color: var(--accent-primary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-contact:hover {
  background: var(--accent-primary-light);
}

.loading, .empty {
  text-align: center;
  padding: 40px;
  color: var(--text-muted);
}
</style>
