<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const router = useRouter()
const auth = useAuthStore()
const matched = ref([])
const loading = ref(false)

onMounted(async () => {
  if (!auth.isLoggedIn) return
  await loadMatches()
})

async function loadMatches() {
  loading.value = true
  try {
    const res = await api.get('/courses/match')
    matched.value = res.data || []
  } catch { /* silently ignore */ }
  finally { loading.value = false }
}

function goToBook(book) {
  router.push({ name: 'BookDetail', params: { id: book.id } })
}

function goToCourse(courseId) {
  router.push({ name: 'Forum', query: { course_id: courseId } })
}

defineExpose({ loadMatches })
</script>

<template>
  <div v-if="loading" class="loading">正在为你匹配教材...</div>
  <div v-else-if="matched.length === 0" class="empty-match">
    <p>暂未添加课程，或暂无匹配的在售教材</p>
    <p class="hint">添加课程后，系统将自动匹配对应教材的二手书</p>
  </div>
  <div v-else class="course-book-match">
    <div v-for="item in matched" :key="item.course.id" class="match-card">
      <div class="match-header">
        <span class="course-name" @click="goToCourse(item.course.id)">
          📚 {{ item.course.name }}
        </span>
        <span class="match-badge">{{ item.available_count }} 本在售</span>
      </div>
      <div class="required-book">
        <span class="required-label">教材:</span>
        <span class="required-title">{{ item.required_book.book_title }}</span>
        <span v-if="item.required_book.book_author" class="required-author">{{ item.required_book.book_author }}</span>
      </div>
      <div class="available-list">
        <div
          v-for="book in item.available_books"
          :key="book.id"
          class="available-item"
          @click="goToBook(book)"
        >
          <span class="av-title">{{ book.title }}</span>
          <span class="av-condition">{{ book.condition }}</span>
          <span class="av-price">¥{{ book.price }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.course-book-match { display: flex; flex-direction: column; gap: 16px; }

.match-card {
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 20px;
  transition: all 0.2s;
}

.match-card:hover { border-color: var(--accent-primary); }

.match-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.course-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--accent-primary);
  cursor: pointer;
}

.course-name:hover { text-decoration: underline; }

.match-badge {
  padding: 2px 10px;
  border-radius: 12px;
  background: var(--accent-primary-light);
  color: var(--accent-primary);
  font-size: 12px;
  font-weight: 600;
}

[data-theme="cyber"] .match-badge {
  background: rgba(0, 212, 255, 0.12);
  color: #00D4FF;
}

.required-book {
  display: flex;
  gap: 8px;
  align-items: baseline;
  margin-bottom: 10px;
  font-size: 13px;
}

.required-label { color: var(--text-muted); }
.required-title { color: var(--text-primary); font-weight: 500; }
.required-author { color: var(--text-muted); font-size: 12px; }

.available-list { display: flex; flex-direction: column; gap: 6px; }

.available-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: var(--surface-tertiary);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
}

.available-item:hover { background: var(--accent-primary-light); }

[data-theme="cyber"] .available-item:hover { background: rgba(0,212,255,0.06); }

.av-title { flex: 1; font-size: 13px; color: var(--text-primary); }
.av-condition { font-size: 11px; color: var(--text-muted); padding: 1px 6px; background: var(--surface-secondary); border-radius: 4px; }
.av-price { font-family: var(--font-mono); font-size: 14px; color: var(--accent-primary); font-weight: 600; }

.loading, .empty-match { text-align: center; padding: 32px; color: var(--text-muted); }
.hint { font-size: 12px; margin-top: 4px; }
</style>
