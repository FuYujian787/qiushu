<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

defineProps({
  wish: { type: Object, required: true },
})

const emit = defineEmits(['have-book'])
const router = useRouter()
const auth = useAuthStore()

function daysSince(dateStr) {
  if (!dateStr) return 0
  const d = new Date(dateStr)
  const now = new Date()
  return Math.floor((now - d) / (1000 * 60 * 60 * 24))
}
</script>

<template>
  <div class="wish-card">
    <div class="wish-main">
      <div class="wish-head">
        <h3 class="wish-title">{{ wish.title }}</h3>
        <span :class="['wish-status', wish.status]">{{ wish.status }}</span>
      </div>
      <p v-if="wish.author" class="wish-author">作者: {{ wish.author }}</p>
      <p v-if="wish.reason" class="wish-reason">"{{ wish.reason }}"</p>
      <div class="wish-meta">
        <span class="wish-user">{{ wish.user_name || '匿名书友' }}</span>
        <span class="wish-days">已等待 {{ daysSince(wish.created_at) }} 天</span>
      </div>
      <div v-if="wish.matched_books?.length" class="matched-section">
        <span class="matched-label">📖 已有匹配书籍:</span>
        <div class="matched-books">
          <span
            v-for="book in wish.matched_books"
            :key="book.id"
            class="matched-book-chip"
          >
            {{ book.title }} ¥{{ book.price }}
          </span>
        </div>
      </div>
    </div>
    <div class="wish-action">
      <button
        v-if="auth.isLoggedIn && auth.currentUser?.id !== wish.user_id"
        class="dm-btn"
        title="私信联系"
        @click.stop="router.push({ name: 'Messages', query: { user_id: wish.user_id, user_name: wish.user_name } })"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        私信
      </button>
      <button class="have-btn" @click.stop="emit('have-book', wish.title)">
        我有这本
      </button>
    </div>
  </div>
</template>

<style scoped>
.wish-card {
  display: flex;
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 20px;
  gap: 16px;
  position: relative;
  overflow: hidden;
  transition: all 0.2s;
}

/* 左边框独特样式 */
.wish-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  border-right: 3px dashed var(--accent-primary);
}

[data-theme="cyber"] .wish-card::before {
  border-right: 1px solid;
  border-color: var(--accent-primary);
  box-shadow: 0 0 8px var(--accent-primary);
}

.wish-card:hover { border-color: var(--accent-primary); }

.wish-main { flex: 1; min-width: 0; }

.wish-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.wish-title {
  font-size: 16px;
  color: var(--text-primary);
  font-weight: 600;
}

.wish-status {
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.wish-status.求购中 { background: rgba(184, 134, 11, 0.1); color: #B8860B; }
.wish-status.已匹配 { background: #E8F5E9; color: #2E7D32; }
.wish-status.已关闭 { background: #F5F5F5; color: #9E9E9E; }

[data-theme="cyber"] .wish-status.求购中 { background: rgba(255, 215, 0, 0.12); color: #FFD700; }
[data-theme="cyber"] .wish-status.已匹配 { background: rgba(168, 85, 247, 0.12); color: #A855F7; }

.wish-author { font-size: 13px; color: var(--text-muted); margin-bottom: 6px; }
.wish-reason { color: var(--text-secondary); font-size: 13px; line-height: 1.5; margin-bottom: 10px; }
.wish-meta { display: flex; gap: 12px; font-size: 12px; color: var(--text-muted); }
.wish-days { color: var(--accent-primary); font-weight: 600; }

.matched-section { margin-top: 10px; }
.matched-label { font-size: 12px; color: var(--text-muted); }
.matched-books { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; }
.matched-book-chip {
  padding: 2px 8px;
  background: var(--accent-primary-light);
  color: var(--accent-primary);
  border-radius: 4px;
  font-size: 11px;
}

[data-theme="cyber"] .matched-book-chip { background: rgba(0,212,255,0.08); color: #00D4FF; }

.wish-action { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }

.dm-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 14px;
  border: 1px solid var(--border-default);
  border-radius: 8px;
  background: var(--surface-tertiary);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.dm-btn:hover { border-color: var(--accent-primary); color: var(--accent-primary); }
[data-theme="cyber"] .dm-btn:hover { border-color: #00D4FF; color: #00D4FF; box-shadow: 0 0 10px rgba(0,212,255,0.12); }

.have-btn {
  padding: 8px 20px;
  border: 1px solid var(--accent-primary);
  border-radius: 8px;
  background: transparent;
  color: var(--accent-primary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.have-btn:hover { background: var(--accent-primary); color: #fff; }

[data-theme="cyber"] .have-btn { border-color: #00D4FF; color: #00D4FF; }
[data-theme="cyber"] .have-btn:hover { background: #00D4FF; color: #09051A; }
</style>
