<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import api from '@/api'
import ReplyForm from '@/components/ReplyForm.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const post = ref(null)
const replies = ref([])
const loading = ref(true)

onMounted(async () => {
  const id = route.params.id
  try {
    const res = await api.get(`/forum/posts/${id}`)
    post.value = res.data
    replies.value = res.data?.replies || []
  } catch {
    ElMessage.error('帖子不存在')
    router.push('/forum')
  } finally {
    loading.value = false
  }
})

function onReplied(newReply) {
  replies.value.push(newReply)
  if (post.value) {
    post.value.reply_count = (post.value.reply_count || 0) + 1
  }
}

function goBack() { router.back() }

function getPostTypeClass(type) {
  const map = {
    '选课求助': 'type-blue',
    '老师评价': 'type-orange',
    '考试资料': 'type-green',
    '学习笔记': 'type-purple',
    '书评': 'type-red',
    '求书': 'type-deeporange',
    '其他': 'type-gray',
  }
  return map[type] || 'type-gray'
}
</script>

<template>
  <div class="post-detail-page page-enter">
    <div class="page-container">
      <button class="back-btn" @click="goBack">← 返回论坛</button>

      <div v-if="loading" class="loading">加载中...</div>

      <div v-else-if="post" class="post-detail">
        <!-- Post Head -->
        <div class="post-head">
          <h1 class="post-title">{{ post.title }}</h1>
          <div class="post-meta">
            <span :class="['post-type-badge', getPostTypeClass(post.type)]">
              {{ post.type }}
            </span>
            <span>{{ post.user_name || '匿名' }}</span>
            <span
              v-if="auth.isLoggedIn && post.user_id && auth.currentUser?.id !== post.user_id"
              class="dm-inline"
              @click="router.push({ name: 'Messages', query: { user_id: post.user_id, user_name: post.user_name } })"
            >💬 私信</span>
            <span v-if="post.course_name">{{ post.course_name }}</span>
            <span>{{ post.created_at?.slice(0, 10) }}</span>
            <span>{{ post.view_count || 0 }} 次浏览</span>
          </div>
        </div>

        <!-- Post Body -->
        <div class="post-body">
          <p>{{ post.content }}</p>
        </div>

        <!-- Replies Section -->
        <div class="replies-section">
          <h3>回复（{{ replies.length }}）</h3>

          <div v-if="replies.length === 0" class="no-replies">
            暂无回复，来写下第一条回复吧
          </div>

          <div v-for="reply in replies" :key="reply.id" class="reply-item">
            <div class="reply-header">
              <span class="reply-author">{{ reply.user_name || '匿名' }}</span>
              <span
                v-if="auth.isLoggedIn && reply.user_id && auth.currentUser?.id !== reply.user_id"
                class="dm-inline"
                @click="router.push({ name: 'Messages', query: { user_id: reply.user_id, user_name: reply.user_name } })"
              >💬 私信</span>
              <span class="reply-time">{{ reply.created_at?.slice(0, 10) }}</span>
            </div>
            <p class="reply-content">{{ reply.content }}</p>
          </div>

          <!-- Reply Form -->
          <ReplyForm
            :post-id="route.params.id"
            @replied="onReplied"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.back-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 14px;
  cursor: pointer;
  margin-bottom: 20px;
  padding: 4px 0;
  transition: color 0.2s;
}

.back-btn:hover { color: var(--accent-primary); }

.post-head {
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 24px;
  margin-bottom: 20px;
}

.post-title {
  font-family: var(--font-display);
  font-size: 22px;
  color: var(--text-primary);
  font-weight: 700;
  margin-bottom: 12px;
  line-height: 1.4;
}

.post-meta {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  font-size: 12px;
  color: var(--text-muted);
}

.post-type-badge {
  padding: 2px 10px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 11px;
}

.type-blue { background: #E3F2FD; color: #1565C0; }
.type-orange { background: #FFF3E0; color: #E65100; }
.type-green { background: #E8F5E9; color: #2E7D32; }
.type-purple { background: #F3E5F5; color: #7B1FA2; }
.type-red { background: #FCE4EC; color: #C62828; }
.type-deeporange { background: #FBE9E7; color: #BF360C; }
.type-gray { background: #F5F5F5; color: #616161; }

.post-body {
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 24px;
  margin-bottom: 24px;
  line-height: 1.7;
  color: var(--text-primary);
  font-size: 14px;
}

.replies-section { margin-top: 24px; }
.replies-section h3 { font-size: 16px; color: var(--text-primary); margin-bottom: 16px; font-weight: 600; }

.reply-item {
  padding: 16px;
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  margin-bottom: 8px;
}

.reply-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.reply-author { font-weight: 600; font-size: 13px; color: var(--text-primary); }
.dm-inline {
  font-size: 11px;
  color: var(--accent-primary);
  cursor: pointer;
  font-weight: 500;
  transition: opacity 0.15s;
  white-space: nowrap;
}
.dm-inline:hover { opacity: 0.75; text-decoration: underline; }
.reply-time { font-size: 11px; color: var(--text-muted); }
.reply-content { font-size: 14px; color: var(--text-secondary); line-height: 1.6; }

.no-replies { color: var(--text-muted); padding: 24px; text-align: center; font-size: 13px; }

.loading { text-align: center; padding: 40px; color: var(--text-muted); }
</style>
