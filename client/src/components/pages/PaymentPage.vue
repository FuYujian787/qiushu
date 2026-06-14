<template>
  <div class="payment-page">
    <div class="payment-card">
      <div class="payment-header">
        <span class="iconify" data-icon="solar:wallet-money-outline" data-width="64"></span>
        <h2>扫码支付</h2>
      </div>
      <div class="payment-body">
        <p class="payment-total">¥{{ total }}</p>
        <div v-if="sellers.length > 0" class="payment-sellers">
          <p class="payment-seller-label">卖家：</p>
          <span v-for="(s, i) in sellers" :key="s" class="payment-seller-tag">
            {{ s }}
            <button
              v-if="store.isLoggedIn.value && s !== store.currentUser.value?.name"
              class="chat-btn-mini"
              @click.stop="startChat(s)"
              title="私聊卖家"
            >
              💬
            </button>
            <template v-if="i < sellers.length - 1">、</template>
          </span>
        </div>
        <div v-if="alipayQr" class="qr-section">
          <h3><span class="iconify" data-icon="logos:alipay" data-width="24"></span> 支付宝扫码支付</h3>
          <div class="qr-img-wrap"><img :src="alipayQr" class="qr-img" /></div>
        </div>
        <div v-if="wechatQr" class="qr-section">
          <h3><span class="iconify" data-icon="logos:wechat" data-width="24"></span> 微信扫码支付</h3>
          <div class="qr-img-wrap"><img :src="wechatQr" class="qr-img" /></div>
        </div>
        <div v-if="!alipayQr && !wechatQr" class="qr-placeholder">
          <svg width="200" height="200" viewBox="0 0 200 200"><rect width="200" height="200" fill="#f0f0f0"/><text x="100" y="110" text-anchor="middle" fill="#333" font-size="14">卖家未上传收款码</text></svg>
        </div>
        <!-- 场景三：【思辨流转】粒子爆破按钮 -->
        <div class="payment-btn btn-pulse" ref="btnRef" @click="completePayment">
          我已完成支付
          <div v-if="showParticles" class="particle-burst">
            <div
              v-for="p in particles"
              :key="p.id"
              class="particle"
              :style="p.style"
            />
            <div class="ripple-ring" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useStore } from '../../stores/useStore'

const store = useStore()

const total = computed(() => store.cart.reduce((s, i) => s + parseFloat(i.price) * i.qty, 0).toFixed(2))

const alipayQr = computed(() => {
  for (const item of store.cart) {
    if (item.alipayQr) return item.alipayQr
  }
  return null
})

const wechatQr = computed(() => {
  for (const item of store.cart) {
    if (item.wechatQr) return item.wechatQr
  }
  return null
})

const sellers = computed(() => {
  const set = new Set()
  for (const item of store.cart) {
    if (item.seller) set.add(item.seller)
  }
  return [...set]
})

/* ===== 场景三：粒子爆破反馈 ===== */
const showParticles = ref(false)
const particles = ref([])
const btnRef = ref(null)

function completePayment() {
  if (!store.cart.length || !store.currentUser.value) return

  // 触发粒子爆破
  triggerParticles()

  // 延迟执行支付逻辑，让粒子动画先跑
  setTimeout(() => {
    const buyer = store.currentUser.value
    const address = buyer.address || '未设置地址'
    store.placeOrder(buyer.name, address)
    alert('支付成功！')
    store.navigateTo('orders')
  }, 300)
}

function triggerParticles() {
  const colors = [
    'rgba(220, 208, 255, 0.9)',  // 薰衣草淡紫
    'rgba(196, 181, 224, 0.8)',  // 深薰衣草
    'rgba(230, 215, 184, 0.8)',  // 紫金
    'rgba(255, 255, 255, 0.7)',  // 白
  ]

  const list = []
  for (let i = 0; i < 24; i++) {
    const angle = (Math.PI * 2 * i) / 24 + (Math.random() - 0.5) * 0.3
    const distance = 80 + Math.random() * 80
    const tx = Math.cos(angle) * distance
    const ty = Math.sin(angle) * distance
    const size = 4 + Math.random() * 6
    const color = colors[Math.floor(Math.random() * colors.length)]
    const duration = 0.8 + Math.random() * 0.4

    list.push({
      id: i,
      style: {
        width: size + 'px',
        height: size + 'px',
        background: color,
        boxShadow: `0 0 ${size * 2}px ${color}`,
        '--tx': tx + 'px',
        '--ty': ty + 'px',
        animation: `particleFly ${duration}s cubic-bezier(0.25, 1, 0.5, 1) forwards`,
        top: '50%',
        left: '50%',
        marginTop: -(size / 2) + 'px',
        marginLeft: -(size / 2) + 'px',
      },
    })
  }

  particles.value = list
  showParticles.value = true

  // 动画结束后清理
  setTimeout(() => {
    showParticles.value = false
    particles.value = []
  }, 1200)
}

/** 私聊卖家 */
function startChat(sellerName) {
  if (!store.isLoggedIn.value) {
    alert('请先登录')
    return
  }
  sessionStorage.setItem('chat_target_user', sellerName)
  store.navigateTo('chat')
}
</script>

<style scoped>
.payment-page { display: flex; justify-content: center; }
.payment-card { max-width: 28rem; width: 100%; background: var(--glass-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--glass-border); border-radius: 1.5rem; overflow: hidden; box-shadow: var(--glass-shadow-hover); }
.payment-header { background: var(--gradient-brand); padding: 2rem; text-align: center; color: var(--text-primary); }
.payment-header :deep(.iconify) { color: var(--text-primary); }
.payment-header h2 { font-size: 1.25rem; font-weight: 700; margin: 0.5rem 0 0 0; }
.payment-body { padding: 2rem; display: flex; flex-direction: column; align-items: center; }
.payment-total { font-size: 2.25rem; font-weight: 700; color: var(--text-primary); margin: 0 0 1.5rem 0; }
.payment-sellers { margin-bottom: 1.5rem; text-align: center; display: flex; align-items: center; justify-content: center; gap: 0.25rem; flex-wrap: wrap; }
.payment-seller-label { font-size: 0.875rem; color: var(--text-secondary); margin: 0; }
.payment-seller-tag { font-size: 0.875rem; color: var(--text-primary); font-weight: 600; display: inline-flex; align-items: center; gap: 0.25rem; }
.qr-section { margin-bottom: 1.5rem; text-align: center; }
.qr-section h3 { font-size: 1.125rem; font-weight: 700; color: var(--text-primary); margin: 0 0 0.75rem 0; display: flex; align-items: center; justify-content: center; gap: 0.5rem; }
.qr-img-wrap { width: 12rem; height: 12rem; margin: 0 auto; background: white; border: 2px solid var(--glass-border); border-radius: 1rem; overflow: hidden; }
.qr-img { width: 100%; height: 100%; object-fit: contain; }
.qr-placeholder { margin-bottom: 1.5rem; }
.payment-btn { position: relative; width: 100%; padding: 1rem; background: var(--gradient-brand); color: var(--text-primary); border-radius: 1rem; font-weight: 700; text-align: center; cursor: pointer; overflow: hidden; box-shadow: 0 4px 12px rgba(155, 142, 196, 0.3); }
.payment-btn:hover { filter: brightness(0.95); }
</style>
