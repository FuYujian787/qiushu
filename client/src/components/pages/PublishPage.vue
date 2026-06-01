<template>
  <div class="publish-page">
    <div v-if="!store.isLoggedIn.value" class="empty-state">请先登录</div>
    <div v-else class="publish-card">
      <h2>发布闲置书籍</h2>
      <div class="form-fields">
        <div class="field"><label>书名 <span class="required">*</span></label><input v-model="title" placeholder="请输入书名" class="input-field" /></div>
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
    author: publisher.value,
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
</style>
