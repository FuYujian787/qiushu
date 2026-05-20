<template>
  <div class="community-page">
    <div class="community-header">
      <h2>学习社区</h2>
      <div class="new-post-btn" @click="toggleForm">发布新帖</div>
    </div>
    <div v-if="showForm" class="new-post-form">
      <input v-model="newTitle" placeholder="帖子标题" class="post-input" />
      <textarea v-model="newContent" placeholder="分享你的学习心得..." rows="4" class="post-textarea"></textarea>
      <div class="form-actions">
        <div class="action-btn primary-btn" @click="submitPost">发布</div>
        <div class="action-btn cancel-btn" @click="toggleForm">取消</div>
      </div>
    </div>
    <div class="posts-list">
      <div v-for="post in mergedPosts" :key="post.id" class="post-card">
        <h3 class="post-title">{{ post.title }}</h3>
        <p class="post-content">{{ post.content }}</p>
        <div class="post-meta"><span>{{ post.author }}</span><span>{{ post.time }}</span></div>
        <div class="replies-section">
          <div v-for="reply in (postReplies[String(post.id)] || [])" :key="reply.id" class="reply-item">
            <div class="reply-header"><span class="reply-author">{{ reply.author }}</span><span class="reply-time">{{ reply.time }}</span></div>
            <p class="reply-content">{{ reply.content }}</p>
          </div>
        </div>
        <div class="reply-input-area">
          <input v-model="replyInputs[String(post.id)]" placeholder="写下你的回复..." class="reply-input" @keyup.enter="submitReply(String(post.id))" />
          <button class="reply-btn" @click="submitReply(String(post.id))">回复</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { useStore } from '../../stores/useStore'

const store = useStore()
const showForm = ref(false)
const newTitle = ref('')
const newContent = ref('')
const replyInputs = reactive({})

const mergedPosts = computed(() => {
  return [...store.getMergedPosts()].reverse()
})

const postReplies = computed(() => store.postReplies.value)

function toggleForm() {
  showForm.value = !showForm.value
}

function submitPost() {
  if (!store.isLoggedIn.value) { alert('请先登录'); return }
  if (!newTitle.value || !newContent.value) { alert('标题和内容不能为空'); return }
  store.addPost({
    id: Date.now(),
    title: newTitle.value,
    content: newContent.value,
    author: store.currentUser.value.name,
    time: new Date().toLocaleString('zh-CN'),
  })
  newTitle.value = ''
  newContent.value = ''
  showForm.value = false
}

function submitReply(postId) {
  if (!store.isLoggedIn.value) { alert('请先登录'); return }
  const content = replyInputs[postId]
  if (!content?.trim()) { alert('回复内容不能为空'); return }
  store.addReply(postId, {
    id: Date.now() + Math.random(),
    author: store.currentUser.value.name,
    content: content.trim(),
    time: new Date().toLocaleString('zh-CN'),
  })
  replyInputs[postId] = ''
}
</script>

<style scoped>
.community-page {}
.community-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.community-header h2 { font-size: 1.5rem; font-weight: 700; margin: 0; }
.new-post-btn { padding: 0.625rem 1.5rem; background: #7c3aed; color: white; border-radius: 0.75rem; font-weight: 700; cursor: pointer; }
.new-post-btn:hover { background: #6d28d9; }
.new-post-form { background: white; border-radius: 1rem; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.post-input { width: 100%; padding: 0.75rem 1rem; background: #f9fafb; border: 1px solid #f3f4f6; border-radius: 0.75rem; outline: none; box-sizing: border-box; margin-bottom: 1rem; }
.post-input:focus, .post-textarea:focus { border-color: #7c3aed; box-shadow: 0 0 0 4px rgba(124,58,237,0.1); }
.post-textarea { width: 100%; padding: 0.75rem 1rem; background: #f9fafb; border: 1px solid #f3f4f6; border-radius: 0.75rem; outline: none; box-sizing: border-box; margin-bottom: 1rem; resize: vertical; }
.form-actions { display: flex; gap: 1rem; }
.action-btn { flex: 1; padding: 0.75rem; border-radius: 0.75rem; font-weight: 700; text-align: center; cursor: pointer; }
.primary-btn { background: #7c3aed; color: white; }
.primary-btn:hover { background: #6d28d9; }
.cancel-btn { background: #e5e7eb; color: #6b7280; }
.cancel-btn:hover { background: #d1d5db; }
.posts-list { display: flex; flex-direction: column; gap: 1.5rem; }
.post-card { background: white; border-radius: 1rem; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.post-title { font-weight: 700; font-size: 1.125rem; margin: 0 0 0.5rem 0; }
.post-content { font-size: 0.875rem; color: #6b7280; margin: 0 0 0.75rem 0; }
.post-meta { display: flex; justify-content: space-between; font-size: 0.75rem; color: #9ca3af; padding-bottom: 1rem; border-bottom: 1px solid #f3f4f6; margin-bottom: 1rem; }
.replies-section { display: flex; flex-direction: column; gap: 0.75rem; margin-bottom: 1rem; }
.reply-item { background: rgba(250,245,255,0.6); padding: 0.75rem; border-radius: 0.75rem; }
.reply-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem; }
.reply-author { font-size: 0.875rem; font-weight: 500; color: #7c3aed; }
.reply-time { font-size: 0.75rem; color: #9ca3af; }
.reply-content { font-size: 0.875rem; color: #374151; margin: 0; }
.reply-input-area { display: flex; gap: 0.5rem; }
.reply-input { flex: 1; padding: 0.5rem 1rem; background: #f9fafb; border: 1px solid #f3f4f6; border-radius: 0.75rem; font-size: 0.875rem; outline: none; }
.reply-input:focus { border-color: #7c3aed; }
.reply-btn { padding: 0.5rem 1.25rem; background: #7c3aed; color: white; border: none; border-radius: 0.75rem; font-size: 0.875rem; font-weight: 700; cursor: pointer; white-space: nowrap; }
.reply-btn:hover { background: #6d28d9; }
</style>
