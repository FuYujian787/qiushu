<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'

const props = defineProps({
  postId: { type: String, required: true },
})

const emit = defineEmits(['replied'])
const auth = useAuthStore()
const router = useRouter()

const content = ref('')
const submitting = ref(false)

async function submit() {
  if (!content.value.trim()) return
  if (!auth.isLoggedIn) {
    router.push({ name: 'Auth', query: { redirect: `/forum/post/${props.postId}` } })
    return
  }
  submitting.value = true
  try {
    const res = await api.post(`/forum/posts/${props.postId}/reply`, { content: content.value })
    emit('replied', res.data)
    content.value = ''
    ElMessage.success('回复成功')
  } catch (err) {
    ElMessage.error(err.message || '回复失败')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="reply-form">
    <h4 class="form-title">写下你的回复</h4>
    <textarea
      v-model="content"
      placeholder="分享你的想法..."
      class="reply-input"
      rows="3"
    ></textarea>
    <button
      class="reply-submit"
      :disabled="submitting"
      @click="submit"
    >
      {{ submitting ? '提交中...' : '回复' }}
    </button>
  </div>
</template>

<style scoped>
.reply-form {
  margin-top: 20px;
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 20px;
}

.form-title { font-size: 14px; color: var(--text-primary); font-weight: 600; margin-bottom: 10px; }

.reply-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-default);
  border-radius: 8px;
  background: var(--surface-primary);
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  resize: vertical;
  margin-bottom: 12px;
  font-family: var(--font-body);
}

.reply-input:focus { border-color: var(--accent-primary); }

.reply-submit {
  padding: 10px 24px;
  background: var(--accent-primary);
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
  transition: all 0.2s;
}

.reply-submit:disabled { opacity: 0.6; cursor: not-allowed; }

[data-theme="cyber"] .reply-submit { background: linear-gradient(135deg, #00D4FF, #A855F7); }
</style>
