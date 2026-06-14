<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'

const props = defineProps({
  courses: { type: Array, default: () => [] },
})

const emit = defineEmits(['posted'])
const auth = useAuthStore()
const router = useRouter()

const postTypes = ['选课求助', '老师评价', '考试资料', '学习笔记', '书评', '求书', '其他']
const form = ref({ title: '', content: '', type: '其他', course_id: '' })

function submit() {
  if (!auth.isLoggedIn) {
    router.push({ name: 'Auth', query: { redirect: '/forum' } })
    return
  }
  if (!form.value.title.trim()) {
    ElMessage.warning('请输入帖子标题')
    return
  }

  api.post('/forum/posts', form.value).then(() => {
    ElMessage.success('发布成功')
    form.value = { title: '', content: '', type: '其他', course_id: '' }
    emit('posted')
  }).catch((err) => {
    ElMessage.error(err.message || '发布失败')
  })
}
</script>

<template>
  <div class="post-form">
    <h3 class="form-title">发布新帖</h3>
    <input
      v-model="form.title"
      placeholder="帖子标题"
      class="input title-input"
    />
    <div class="form-row">
      <select v-model="form.type" class="input select">
        <option v-for="t in postTypes" :key="t" :value="t">{{ t }}</option>
      </select>
      <select v-model="form.course_id" class="input select">
        <option value="">选择课程（可选）</option>
        <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
    </div>
    <textarea
      v-model="form.content"
      placeholder="帖子内容..."
      class="input textarea"
      rows="4"
    ></textarea>
    <button class="submit-btn" @click="submit">发布</button>
  </div>
</template>

<style scoped>
.post-form {
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 20px;
  margin-bottom: 20px;
}

.form-title { font-size: 15px; color: var(--text-primary); font-weight: 600; margin-bottom: 12px; }

.input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-default);
  border-radius: 8px;
  background: var(--surface-primary);
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  font-family: var(--font-body);
}

.input:focus { border-color: var(--accent-primary); }

.title-input { font-size: 16px; margin-bottom: 10px; }

.form-row { display: flex; gap: 10px; margin-bottom: 10px; }
.select { flex: 1; }

.textarea { resize: vertical; margin-bottom: 12px; }

.submit-btn {
  padding: 8px 24px;
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
