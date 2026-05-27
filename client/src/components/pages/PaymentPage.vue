<template>
  <div class="payment-page">
    <div class="payment-card">
      <div class="payment-header">
        <span class="iconify" data-icon="solar:wallet-money-outline" data-width="64"></span>
        <h2>扫码支付</h2>
      </div>
      <div class="payment-body">
        <p class="payment-total">¥{{ total }}</p>
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
        <div class="payment-btn" @click="completePayment">我已完成支付</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
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

function completePayment() {
  if (!store.cart.length || !store.currentUser.value) return
  const buyer = store.currentUser.value
  const address = buyer.address || '未设置地址'
  store.placeOrder(buyer.name, address)
  alert('支付成功！')
  store.navigateTo('orders')
}
</script>

<style scoped>
.payment-page { display: flex; justify-content: center; }
.payment-card { max-width: 28rem; width: 100%; background: white; border-radius: 1.5rem; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.12); }
.payment-header { background: #7c3aed; padding: 2rem; text-align: center; color: white; }
.payment-header :deep(.iconify) { color: white; }
.payment-header h2 { font-size: 1.25rem; font-weight: 700; margin: 0.5rem 0 0 0; }
.payment-body { padding: 2rem; display: flex; flex-direction: column; align-items: center; }
.payment-total { font-size: 2.25rem; font-weight: 700; margin: 0 0 1.5rem 0; }
.qr-section { margin-bottom: 1.5rem; text-align: center; }
.qr-section h3 { font-size: 1.125rem; font-weight: 700; color: #374151; margin: 0 0 0.75rem 0; display: flex; align-items: center; justify-content: center; gap: 0.5rem; }
.qr-img-wrap { width: 12rem; height: 12rem; margin: 0 auto; background: white; border: 2px solid #e5e7eb; border-radius: 1rem; overflow: hidden; }
.qr-img { width: 100%; height: 100%; object-fit: contain; }
.qr-placeholder { margin-bottom: 1.5rem; }
.payment-btn { width: 100%; padding: 1rem; background: #7c3aed; color: white; border-radius: 1rem; font-weight: 700; text-align: center; cursor: pointer; }
.payment-btn:hover { background: #6d28d9; }
</style>
