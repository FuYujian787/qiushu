<template>
  <div class="seller-dashboard" v-if="statsLoaded">
    <!-- 呼吸渐变边框动画 -->
    <div class="dashboard-inner">
      <div class="dashboard-header">
        <span class="iconify" data-icon="ph:storefront-duotone" data-width="22" style="color: var(--lavender-accent);"></span>
        <h4 class="dashboard-title">我的求是书摊</h4>
      </div>
      <div class="dashboard-stats">
        <div class="stat-item">
          <div class="stat-icon-wrap">
            <span class="iconify" data-icon="ph:book-duotone" data-width="24" style="color: #8A2BE2;"></span>
          </div>
          <div class="stat-info">
            <span class="stat-label">一共卖出</span>
            <span class="stat-value lilac-gradient">{{ sellerStats.total_books_sold }}</span>
            <span class="stat-unit">本</span>
          </div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <div class="stat-icon-wrap">
            <span class="iconify" data-icon="ph:wallet-duotone" data-width="24" style="color: #7B68EE;"></span>
          </div>
          <div class="stat-info">
            <span class="stat-label">一共赚了</span>
            <span class="stat-value lilac-gradient">¥{{ sellerStats.total_earnings }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useStore } from '../stores/useStore'

const store = useStore()
const statsLoaded = ref(false)
const sellerStats = ref({ total_books_sold: 0, total_earnings: 0.00 })

// 当前登录用户作为卖家名
const sellerName = computed(() => {
  if (store.isLoggedIn.value && store.currentUser.value) {
    return store.currentUser.value.name
  }
  return ''
})

onMounted(() => {
  loadSellerStats()
})

function loadSellerStats() {
  if (!sellerName.value) {
    statsLoaded.value = false
    return
  }
  try {
    const data = store.fetchSellerStats(sellerName.value)
    if (data.success) {
      sellerStats.value = {
        total_books_sold: data.total_books_sold ?? 0,
        total_earnings: data.total_earnings ?? 0.00,
      }
      statsLoaded.value = true
    }
  } catch (e) {
    statsLoaded.value = false
  }
}
</script>

<style scoped>
.seller-dashboard {
  padding: 0 2.5rem;
  flex-shrink: 0;
}

.dashboard-inner {
  background: var(--glass-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 1.25rem;
  padding: 1rem 1.5rem;
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
  position: relative;
  /* 淡紫色呼吸渐变边框动画 */
  animation: lavender-breath 3s ease-in-out infinite;
}

@keyframes lavender-breath {
  0%, 100% {
    box-shadow: 0 0 8px rgba(220, 208, 255, 0.3), 0 0 20px rgba(155, 142, 196, 0.1);
  }
  50% {
    box-shadow: 0 0 14px rgba(220, 208, 255, 0.5), 0 0 30px rgba(155, 142, 196, 0.2);
  }
}

.dashboard-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.dashboard-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: 0.05em;
}

.dashboard-stats {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 1rem;
  align-items: center;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.stat-icon-wrap {
  width: 2.5rem;
  height: 2.5rem;
  background: rgba(243, 239, 255, 0.8);
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.stat-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 800;
  line-height: 1;
}

.stat-unit {
  font-size: 0.8rem;
  color: var(--text-tertiary);
  font-weight: 500;
}

.lilac-gradient {
  background: linear-gradient(135deg, #8A2BE2, #7B68EE);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-divider {
  width: 1px;
  height: 3rem;
  background: var(--glass-border);
}
</style>