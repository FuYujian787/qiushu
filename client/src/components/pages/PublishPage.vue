<template>
  <div class="publish-page">
    <div v-if="!store.isLoggedIn.value" class="empty-state">请先登录</div>
    <div v-else class="publish-card">
      <h2>发布闲置书籍</h2>
      
      <!-- ISBN 查询区域 -->
      <div class="isbn-section">
        <div class="isbn-header">
          <span class="iconify" data-icon="solar:barcode-outline" data-width="18"></span>
          <span>ISBN 扫码识别</span>
        </div>
        <div class="isbn-input-wrap">
          <input 
            v-model="isbnCode" 
            placeholder="输入 ISBN 码自动识别图书信息" 
            class="isbn-input"
            @blur="onIsbnInput"
          />
          <button class="isbn-search-btn" @click="searchByIsbn" :disabled="isbnLoading || !isbnCode.trim()">
            <span class="iconify" data-icon="solar:search-outline" data-width="16"></span>
            {{ isbnLoading ? '识别中...' : '查询' }}
          </button>
        </div>
        <div v-if="isbnError" class="isbn-error">{{ isbnError }}</div>
        <div v-if="isbnResult" class="isbn-result">
          <div class="isbn-result-header">
            <span class="iconify" data-icon="solar:check-circle-outline" data-width="16" style="color: #10b981"></span>
            已识别图书信息
          </div>
          <div class="isbn-book-info">
            <img :src="isbnResult.image" class="isbn-book-cover" />
            <div class="isbn-book-detail">
              <h4>{{ isbnResult.title }}</h4>
              <p class="isbn-author">{{ isbnResult.author }}</p>
              <p class="isbn-publisher">{{ isbnResult.publisher }}</p>
              <p class="isbn-price">定价: ¥{{ isbnResult.price }}</p>
            </div>
          </div>
          <button class="isbn-use-btn" @click="useIsbnInfo">使用此信息</button>
        </div>
      </div>

      <div class="form-fields">
        <div class="field"><label>书名 <span class="required">*</span></label><input v-model="title" placeholder="请输入书名" class="input-field" /></div>
        <div class="field"><label>作者</label><input v-model="author" placeholder="例如：张三" class="input-field" /></div>
        <div class="field"><label>卖价 (¥) <span class="required">*</span></label><input v-model.number="price" type="number" placeholder="0.00" step="0.01" min="0" class="input-field" /></div>
        <div class="field"><label>原价 (¥)</label><input v-model.number="oldPrice" type="number" placeholder="0.00" step="0.01" min="0" class="input-field" /></div>
        <div class="field"><label>出版社 <span class="required">*</span></label><input v-model="publisher" placeholder="例如：高等教育出版社" class="input-field" /></div>
        <div class="field"><label>成色 <span class="required">*</span></label><select v-model="condition" class="input-field"><option value="">请选择</option><option v-for="c in conditions" :key="c" :value="c">{{ c }}</option></select></div>
        <div class="field"><label>分类</label><select v-model="category" class="input-field"><option value="教材">教材</option><option value="考研">考研</option><option value="选修">选修</option><option value="其他">其他</option></select></div>
        <div class="field"><label>书籍图片</label><div class="upload-zone" @click="triggerUpload('img')"><img v-if="imgPreview" :src="imgPreview" class="upload-preview-img" /><p v-else class="upload-text">点击更换图片</p></div><input ref="imgInput" type="file" accept="image/*" class="hidden" @change="onUpload('img', $event)" /></div>
        <div class="field"><label>支付宝收款二维码</label><div class="upload-zone" @click="triggerUpload('alipay')"><img v-if="alipayPreview" :src="alipayPreview" class="upload-preview-img" /><p v-else class="upload-text">点击上传支付宝收款码</p></div><input ref="alipayInput" type="file" accept="image/*" class="hidden" @change="onUpload('alipay', $event)" /></div>
        <div class="field"><label>微信收款二维码</label><div class="upload-zone" @click="triggerUpload('wechat')"><img v-if="wechatPreview" :src="wechatPreview" class="upload-preview-img" /><p v-else class="upload-text">点击上传微信收款码</p></div><input ref="wechatInput" type="file" accept="image/*" class="hidden" @change="onUpload('wechat', $event)" /></div>
      </div>
      <div class="publish-btn" @click="confirmPublish">确认发布</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useStore } from '../../stores/useStore'

const store = useStore()
const conditions = computed(() => store.categoriesData.value?.conditions || ['全新未拆', '九成新', '八成新', '有笔记', '七成新'])

const title = ref('')
const author = ref('')
const price = ref(null)
const oldPrice = ref(null)
const publisher = ref('')
const condition = ref('')
const category = ref('教材')
const imgPreview = ref(null)
const alipayPreview = ref(null)
const wechatPreview = ref(null)
const imgInput = ref(null)
const alipayInput = ref(null)
const wechatInput = ref(null)
const imgData = ref(null)
const alipayData = ref(null)
const wechatData = ref(null)

// ISBN 相关变量
const isbnCode = ref('')
const isbnLoading = ref(false)
const isbnError = ref('')
const isbnResult = ref(null)

// ISBN 校验函数
function isValidIsbn(isbn) {
  isbn = isbn.replace(/[-\s]/g, '')
  if (isbn.length !== 10 && isbn.length !== 13) return false
  
  if (isbn.length === 13) {
    let sum = 0
    for (let i = 0; i < 12; i++) {
      sum += parseInt(isbn[i]) * (i % 2 === 0 ? 1 : 3)
    }
    const checkDigit = (10 - (sum % 10)) % 10
    return checkDigit === parseInt(isbn[12])
  } else {
    let sum = 0
    for (let i = 0; i < 9; i++) {
      sum += parseInt(isbn[i]) * (10 - i)
    }
    const lastChar = isbn[9].toUpperCase()
    const checkDigit = lastChar === 'X' ? 10 : parseInt(lastChar)
    return (sum + checkDigit) % 11 === 0
  }
}

// ISBN 输入处理
function onIsbnInput() {
  isbnError.value = ''
  isbnResult.value = null
}

// 搜索 ISBN
async function searchByIsbn() {
  const isbn = isbnCode.value.replace(/[-\s]/g, '').trim()
  
  if (!isbn) {
    isbnError.value = '请输入 ISBN 码'
    return
  }
  
  if (!isValidIsbn(isbn)) {
    isbnError.value = '请输入有效的 ISBN 码'
    return
  }
  
  isbnLoading.value = true
  isbnError.value = ''
  
  try {
    const response = await fetch(`/api/isbn/search?code=${encodeURIComponent(isbn)}`)
    const data = await response.json()
    
    if (data.success) {
      isbnResult.value = data.data
    } else {
      isbnError.value = data.message || '未找到该图书信息'
    }
  } catch (error) {
    isbnError.value = '查询失败，请稍后重试'
  } finally {
    isbnLoading.value = false
  }
}

// 使用 ISBN 信息填充表单
function useIsbnInfo() {
  if (!isbnResult.value) return
  
  title.value = isbnResult.value.title || ''
  author.value = isbnResult.value.author || ''
  publisher.value = isbnResult.value.publisher || ''
  oldPrice.value = parseFloat(isbnResult.value.price) || null
  
  // 如果有封面图片，使用识别到的图片
  if (isbnResult.value.image) {
    imgPreview.value = isbnResult.value.image
    imgData.value = isbnResult.value.image
  }
  
  isbnResult.value = null
  isbnCode.value = ''
}

function triggerUpload(type) {
  if (type === 'img') imgInput.value?.click()
  else if (type === 'alipay') alipayInput.value?.click()
  else if (type === 'wechat') wechatInput.value?.click()
}

function onUpload(type, e) {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => {
    const data = ev.target.result
    if (type === 'img') { imgData.value = data; imgPreview.value = data }
    else if (type === 'alipay') { alipayData.value = data; alipayPreview.value = data }
    else if (type === 'wechat') { wechatData.value = data; wechatPreview.value = data }
  }
  reader.readAsDataURL(file)
}

function confirmPublish() {
  if (!title.value || !price.value || !publisher.value || !condition.value) {
    alert('请填写完整必填项'); return
  }
  if (isNaN(parseFloat(price.value)) || parseFloat(price.value) <= 0) {
    alert('请输入有效价格'); return
  }
  const op = oldPrice.value ? parseFloat(oldPrice.value).toFixed(1) : (parseFloat(price.value) * 1.5).toFixed(1)
  const newBook = {
    id: Date.now() + Math.floor(Math.random() * 1000),
    title: title.value,
    author: author.value || '未知',
    publisher: publisher.value,
    price: parseFloat(price.value).toFixed(1),
    oldPrice: op,
    condition: condition.value,
    seller: store.currentUser.value.name,
    img: imgData.value || 'R-C.jpg',
    category: category.value,
    isUserPublished: true,
    status: 'active',
    alipayQr: alipayData.value,
    wechatQr: wechatData.value,
  }
  store.publishBook(newBook)
  alert('发布成功！')
  store.navigateTo('procurement')
}
</script>

<style scoped>
.publish-page { display: flex; justify-content: center; }
.empty-state { background: var(--glass-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--glass-border); border-radius: 1.5rem; padding: 2.5rem; text-align: center; color: var(--text-tertiary); font-size: 1.125rem; }
.publish-card { max-width: 36rem; width: 100%; background: var(--glass-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--glass-border); border-radius: 1.5rem; padding: 2rem; box-shadow: var(--glass-shadow); }
.publish-card h2 { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin: 0 0 2rem 0; }
.form-fields { display: flex; flex-direction: column; gap: 1.25rem; }
.field label { display: block; font-size: 0.875rem; font-weight: 500; color: var(--text-primary); margin-bottom: 0.25rem; }
.required { color: #f87171; }
.input-field { width: 100%; padding: 0.75rem 1rem; background: rgba(255,255,255,0.7); border: 1px solid var(--glass-border); border-radius: 0.75rem; outline: none; box-sizing: border-box; transition: all 0.2s; }
.input-field:focus { border-color: var(--lavender-accent-soft); box-shadow: 0 0 0 4px rgba(220,208,255,0.15); }
.upload-zone { border: 2px dashed var(--lavender-primary); border-radius: 0.75rem; padding: 1rem; text-align: center; cursor: pointer; }
.upload-zone:hover { border-color: var(--lavender-accent-soft); background: var(--lavender-accent-mist); }
.upload-preview-img { max-height: 10rem; margin: 0 auto; object-fit: contain; border-radius: 0.5rem; }
.upload-text { font-size: 0.75rem; color: var(--text-tertiary); margin: 0; }
.hidden { display: none; }
.publish-btn { width: 100%; padding: 1rem; background: var(--gradient-brand); color: var(--text-primary); border-radius: 0.75rem; font-weight: 700; text-align: center; cursor: pointer; margin-top: 2rem; box-shadow: 0 4px 12px rgba(155, 142, 196, 0.3); }
.publish-btn:hover { filter: brightness(0.95); }

/* ISBN 区域样式 */
.isbn-section { background: var(--lavender-accent-mist); border-radius: 1rem; padding: 1.5rem; margin-bottom: 2rem; }
.isbn-header { display: flex; align-items: center; gap: 0.5rem; font-weight: 600; color: var(--text-primary); margin-bottom: 1rem; }
.isbn-input-wrap { display: flex; gap: 0.75rem; }
.isbn-input { flex: 1; padding: 0.75rem 1rem; background: rgba(255,255,255,0.8); border: 1px solid var(--glass-border); border-radius: 0.75rem; outline: none; font-size: 0.875rem; }
.isbn-input:focus { border-color: var(--lavender-accent-soft); box-shadow: 0 0 0 4px rgba(220,208,255,0.15); }
.isbn-search-btn { padding: 0.75rem 1.25rem; background: var(--lavender-primary); color: white; border: none; border-radius: 0.75rem; cursor: pointer; font-size: 0.875rem; display: flex; align-items: center; gap: 0.5rem; }
.isbn-search-btn:hover:not(:disabled) { background: var(--lavender-accent-soft); }
.isbn-search-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.isbn-error { color: #ef4444; font-size: 0.75rem; margin-top: 0.75rem; }
.isbn-result { margin-top: 1rem; padding: 1rem; background: rgba(255,255,255,0.6); border-radius: 0.75rem; }
.isbn-result-header { display: flex; align-items: center; gap: 0.5rem; font-weight: 500; color: var(--text-primary); margin-bottom: 1rem; }
.isbn-book-info { display: flex; gap: 1rem; }
.isbn-book-cover { width: 6rem; height: 8rem; object-fit: cover; border-radius: 0.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.isbn-book-detail { flex: 1; }
.isbn-book-detail h4 { margin: 0 0 0.5rem 0; font-size: 1rem; font-weight: 600; color: var(--text-primary); }
.isbn-author, .isbn-publisher { margin: 0.25rem 0; font-size: 0.75rem; color: var(--text-secondary); }
.isbn-price { margin: 0.5rem 0 0 0; font-size: 0.875rem; font-weight: 600; color: var(--lavender-primary); }
.isbn-use-btn { margin-top: 1rem; padding: 0.5rem 1.5rem; background: var(--gradient-brand); color: var(--text-primary); border: none; border-radius: 0.5rem; cursor: pointer; font-size: 0.875rem; font-weight: 500; }
.isbn-use-btn:hover { filter: brightness(0.95); }
</style>
