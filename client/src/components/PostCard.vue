<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

defineProps({
  post: { type: Object, required: true },
})

const emit = defineEmits(['click'])
const router = useRouter()
const auth = useAuthStore()

const typeColors = {
  '选课求助': { bg: '#E3F2FD', text: '#1565C0' },
  '老师评价': { bg: '#FFF3E0', text: '#E65100' },
  '考试资料': { bg: '#E8F5E9', text: '#2E7D32' },
  '学习笔记': { bg: '#F3E5F5', text: '#7B1FA2' },
  '书评': { bg: '#FCE4EC', text: '#C62828' },
  '求书': { bg: '#FBE9E7', text: '#BF360C' },
  '其他': { bg: '#F5F5F5', text: '#616161' },
}

function getTypeStyle(type) {
  return typeColors[type] || typeColors['其他']
}
</script>

<template>
  <div class="post-card" @click="emit('click', post.id)">
    <div
      class="post-type"
      :style="{ background: getTypeStyle(post.type).bg, color: getTypeStyle(post.type).text }"
    >
      {{ post.type }}
    </div>
    <h3 class="post-title">{{ post.title }}</h3>
    <p class="post-summary">{{ post.content?.slice(0, 100) }}</p>
    <div class="post-meta">
      <span>{{ post.user_name || '匿名' }}</span>
      <span
        v-if="auth.isLoggedIn && post.user_id && auth.currentUser?.id !== post.user_id"
        class="dm-link"
        title="私信 {{ post.user_name }}"
        @click.stop="router.push({ name: 'Messages', query: { user_id: post.user_id, user_name: post.user_name } })"
      >私信</span>
      <span>{{ post.course_name || '综合' }}</span>
      <span>{{ post.reply_count || 0 }} 回复</span>
      <span>{{ post.view_count || 0 }} 浏览</span>
      <span>{{ post.created_at?.slice(0, 10) }}</span>
    </div>
  </div>
</template>

<style scoped>
.post-card {
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 16px 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.post-card:hover { border-color: var(--accent-primary); }

.post-type {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 8px;
}

.post-title {
  font-size: 15px;
  color: var(--text-primary);
  font-weight: 600;
  margin-bottom: 6px;
}

.post-summary {
  color: var(--text-muted);
  font-size: 13px;
  line-height: 1.4;
  margin-bottom: 8px;
}

.post-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
  font-size: 11px;
  color: var(--text-muted);
}

.dm-link {
  color: var(--accent-primary);
  cursor: pointer;
  font-weight: 500;
  transition: opacity 0.15s;
}
.dm-link:hover { opacity: 0.75; text-decoration: underline; }

[data-theme="cyber"] .post-card { border-color: rgba(255,255,255,0.04); }
[data-theme="cyber"] .post-card:hover { border-color: rgba(0,212,255,0.2); }
</style>
