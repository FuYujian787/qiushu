<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'

const emit = defineEmits(['posted'])
const auth = useAuthStore()
const router = useRouter()

const form = ref({ title: '', author: '', isbn: '', reason: '' })

async function submit() {
  if (!form.value.title.trim()) {
    ElMessage.warning('请输入书名')
    return
  }
  if (!auth.isLoggedIn) {
    router.push({ name: 'Auth', query: { redirect: '/wishes' } })
    return
  }
  try {
    await api.post('/wishes', form.value)
    ElMessage.success('求书帖已发布')
    form.value = { title: '', author: '', isbn: '', reason: '' }
    emit('posted')
  } catch (err) {
    ElMessage.error(err.message || '发布失败')
  }
}
</script>

<template>
  <div class="wish-form-card">
    <h3 class="form-title">发布求书帖</h3>
    <input
      v-model="form.title"
      placeholder="书名 *"
      class="input"
    />
    <div class="form-row">
      <input v-model="form.author" placeholder="作者（选填）" class="input" />
      <input v-model="form.isbn" placeholder="ISBN（选填）" class="input" />
    </div>
    <textarea
      v-model="form.reason"
      placeholder="求书理由（选填）"
      class="input textarea"
      rows="3"
    ></textarea>
    <button class="submit-btn" @click="submit">发布求书</button>
  </div>
</template>

<style scoped>
.wish-form-card {
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 24px;
  margin-bottom: 24px;
}

.form-title { font-size: 15px; font-weight: 600; color: var(--text-primary); margin-bottom: 12px; }

.input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-default);
  border-radius: 8px;
  background: var(--surface-primary);
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  margin-bottom: 10px;
  font-family: var(--font-body);
}

.input:focus { border-color: var(--accent-primary); }

.form-row { display: flex; gap: 10px; }

.textarea { resize: vertical; }

.submit-btn {
  padding: 10px 24px;
  background: var(--accent-primary);
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
}

[data-theme="cyber"] .submit-btn { background: linear-gradient(135deg, #00D4FF, #A855F7); }
</style>
