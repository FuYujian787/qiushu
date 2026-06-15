<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({
  title: '',
  author: '',
  isbn: '',
  category: '',
  original_price: '',
  price: '',
  condition: '良好',
  description: '',
  accept_exchange: false,
})
const images = ref([])
const imagePreviewUrls = ref([])
const loading = ref(false)

const categories = ['数学', '计算机', '外语', '经管', '理工', '人文', '其他']
const conditions = ['全新', '良好', '有笔记', '旧']

async function handleImageUpload(e) {
  const files = Array.from(e.target.files || [])
  for (const file of files) {
    if (file.size > 2 * 1024 * 1024) {
      ElMessage.warning('单张图片不能超过 2MB')
      continue
    }
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      ElMessage.warning('仅支持 JPG/PNG/WebP 格式')
      continue
    }
    if (images.value.length >= 5) {
      ElMessage.warning('最多上传 5 张图片')
      break
    }
    images.value.push(file)
    imagePreviewUrls.value.push(URL.createObjectURL(file))
  }
}

function removeImage(index) {
  images.value.splice(index, 1)
  URL.revokeObjectURL(imagePreviewUrls.value[index])
  imagePreviewUrls.value.splice(index, 1)
}

async function handleSubmit() {
  if (!form.title) {
    ElMessage.warning('请输入书名')
    return
  }
  if (!form.price) {
    ElMessage.warning('请输入售价')
    return
  }

  loading.value = true
  try {
    const formData = new FormData()
    Object.entries(form).forEach(([k, v]) => formData.append(k, v))
    images.value.forEach((img) => formData.append('images', img))

    const res = await api.post('/books', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    ElMessage.success('发布成功！')
    router.push({ name: 'BookDetail', params: { id: res.data.id } })
  } catch (err) {
    ElMessage.error(err.message || '发布失败')
  } finally {
    loading.value = false
  }
}

async function handleAiPrice() {
  if (!form.title) { ElMessage.warning('请先输入书名'); return }
  try {
    const res = await api.post('/ai/price', {
      title: form.title,
      author: form.author,
      isbn: form.isbn,
      condition: form.condition,
      original_price: form.original_price || undefined,
    })
    if (res.data) {
      form.price = Math.round((res.data.min + res.data.max) / 2)
      const sourceLabel = res.data.source === 'local_estimate' ? '（本地估算）' :
                          res.data.source === 'fallback' ? '（保守估计）' :
                          res.data.source === 'ai' ? '（AI 分析）' : ''
      ElMessage({
        message: `建议 ¥${res.data.min} - ¥${res.data.max}${sourceLabel}：${res.data.reason || ''}`,
        type: 'info',
        duration: 6000,
      })
    }
  } catch {
    ElMessage.error('AI 定价服务暂时不可用，可参考同类书籍手动填写价格')
  }
}
</script>

<template>
  <div class="publish-page page-enter">
    <div class="page-container">
      <h1 class="page-title">发布书籍</h1>
      <p class="page-subtitle">让闲置教材找到新的主人</p>

      <form @submit.prevent="handleSubmit" class="publish-form">
        <div class="form-grid">
          <div class="form-left">
            <div class="field">
              <label>书名 <span class="req">*</span></label>
              <input v-model="form.title" placeholder="请输入书名" class="input" />
            </div>
            <div class="field">
              <label>作者</label>
              <input v-model="form.author" placeholder="请输入作者" class="input" />
            </div>
            <div class="field">
              <label>ISBN</label>
              <input v-model="form.isbn" placeholder="978xxxxxxxxxx（选填）" class="input" />
            </div>
            <div class="field-row">
              <div class="field">
                <label>分类</label>
                <select v-model="form.category" class="input">
                  <option value="">选择分类</option>
                  <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
                </select>
              </div>
              <div class="field">
                <label>书况</label>
                <select v-model="form.condition" class="input">
                  <option v-for="c in conditions" :key="c" :value="c">{{ c }}</option>
                </select>
              </div>
            </div>
            <div class="field-row">
              <div class="field">
                <label>原价</label>
                <input v-model="form.original_price" type="number" step="0.1" placeholder="0.00" class="input" />
              </div>
              <div class="field">
                <label>售价 <span class="req">*</span></label>
                <input v-model="form.price" type="number" step="0.1" placeholder="0.00" class="input" />
              </div>
            </div>
            <button type="button" class="ai-price-btn" @click="handleAiPrice">
              <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
              AI 建议价格
            </button>
          </div>

          <div class="form-right">
            <div class="field">
              <label>描述</label>
              <textarea v-model="form.description" rows="4" placeholder="描述书籍状况、使用痕迹等" class="input textarea"></textarea>
            </div>
            <div class="field">
              <label>图片（最多 5 张，单张 ≤2MB）</label>
              <div class="image-upload-area">
                <label v-if="images.length < 5" class="upload-btn">
                  <input type="file" accept="image/jpeg,image/png,image/webp" multiple @change="handleImageUpload" hidden />
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24">
                    <path d="M12 4v16m8-8H4" stroke-linecap="round"/>
                  </svg>
                </label>
                <div v-for="(url, i) in imagePreviewUrls" :key="i" class="image-preview">
                  <img :src="url" alt="" />
                  <button type="button" class="remove-img" @click="removeImage(i)">×</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 以书换书选项 -->
        <div class="exchange-option">
          <label class="checkbox-label">
            <input type="checkbox" v-model="form.accept_exchange" class="checkbox-input" />
            <span class="checkbox-text">
              <span class="checkbox-title">🔄 接受以书换书</span>
              <span class="checkbox-desc">开启后，其他用户可以用他们的书来换你这本书</span>
            </span>
          </label>
        </div>

        <div class="form-submit">
          <button type="submit" class="submit-btn" :disabled="loading">
            {{ loading ? '发布中...' : '发布书籍' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.page-title {
  font-family: var(--font-display);
  font-size: 28px;
  color: var(--text-primary);
  font-weight: 700;
}

.page-subtitle {
  color: var(--text-muted);
  font-size: 14px;
  margin-bottom: 32px;
}

.publish-form {
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 32px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}

.req { color: var(--accent-primary); }

.field { margin-bottom: 16px; }

.field label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 6px;
  font-weight: 500;
}

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
  transition: border-color 0.2s;
}

.input:focus { border-color: var(--accent-primary); }

.textarea { resize: vertical; min-height: 100px; }

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.ai-price-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: var(--accent-primary-light);
  border: 1px solid var(--accent-primary);
  border-radius: 8px;
  color: var(--accent-primary);
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  margin-top: 4px;
}

[data-theme="cyber"] .ai-price-btn {
  background: rgba(0,212,255,0.08);
  border-color: #00D4FF;
  color: #00D4FF;
}

.image-upload-area {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.upload-btn {
  width: 100px;
  height: 120px;
  border: 2px dashed var(--border-default);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-muted);
  transition: all 0.2s;
}

.upload-btn:hover { border-color: var(--accent-primary); color: var(--accent-primary); }

.image-preview {
  position: relative;
  width: 100px;
  height: 120px;
  border-radius: 8px;
  overflow: hidden;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-img {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(0,0,0,0.6);
  color: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.form-submit {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-default);
  text-align: center;
}

.submit-btn {
  padding: 14px 48px;
  background: var(--accent-primary);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: var(--accent-primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(196,30,58,0.3);
}

.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }

[data-theme="cyber"] .submit-btn {
  background: linear-gradient(135deg, #00D4FF, #A855F7);
}

/* Exchange option */
.exchange-option {
  margin-top: 16px;
  padding: 0;
}
.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  cursor: pointer;
  padding: 14px 18px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--surface-primary);
  transition: all 0.2s;
}
.checkbox-label:hover {
  border-color: var(--accent-primary);
}
.checkbox-input {
  margin-top: 2px;
  width: 18px;
  height: 18px;
  accent-color: var(--accent-primary);
  cursor: pointer;
  flex-shrink: 0;
}
.checkbox-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.checkbox-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}
.checkbox-desc {
  font-size: 12px;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .form-grid { grid-template-columns: 1fr; }
}
</style>
