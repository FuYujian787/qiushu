<template>
  <div class="cart-page">
    <div class="cart-layout">
      <div class="cart-items-section">
        <h3>我的购物车</h3>
        <div id="cartItems">
          <div v-for="item in store.cart" :key="item.id" class="cart-item">
            <div class="cart-item-img"><img :src="item.img" class="cart-img" /></div>
            <div class="cart-item-info">
              <h4>{{ item.title }}</h4>
              <p class="cart-item-price">¥{{ item.price }} x {{ item.qty }}</p>
              <p class="cart-item-seller" v-if="item.seller">
                卖家：{{ item.seller }}
                <button
                  v-if="store.isLoggedIn.value && item.seller !== store.currentUser.value?.name"
                  class="chat-btn-mini"
                  @click.stop="startChat(item.seller)"
                  title="私聊卖家"
                >
                  💬
                </button>
              </p>
            </div>
            <div class="cart-item-remove" @click="removeItem(item.id)">删除</div>
          </div>
          <div v-if="store.cart.length === 0" class="cart-empty">购物车为空</div>
        </div>
      </div>
      <div class="cart-summary">
        <h3>订单摘要</h3>
        <div class="summary-line"><span>商品总价</span><span>¥{{ total }}</span></div>
        <div class="summary-total"><span>应付总额</span><span class="total-price">¥{{ total }}</span></div>
        <div class="checkout-btn" @click="goPayment">去支付</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from '../../stores/useStore'

const store = useStore()
const total = computed(() => store.cart.reduce((s, i) => s + parseFloat(i.price) * i.qty, 0).toFixed(2))

function removeItem(id) {
  store.removeFromCart(id)
}

function goPayment() {
  store.navigateTo('payment')
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
.cart-page {}
.cart-layout { display: flex; flex-direction: row; gap: 2rem; }
.cart-items-section { flex-grow: 1; background: var(--glass-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--glass-border); border-radius: 1.5rem; padding: 2rem; box-shadow: var(--glass-shadow); }
.cart-items-section h3, .cart-summary h3 { font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin: 0 0 1.5rem 0; }
.cart-item { display: flex; align-items: center; padding: 1.5rem 0; border-bottom: 1px solid var(--glass-border); }
.cart-item-img { width: 6rem; height: 8rem; background: rgba(255,255,255,0.3); border-radius: 0.75rem; overflow: hidden; }
.cart-img { width: 100%; height: 100%; object-fit: cover; }
.cart-item-info { margin-left: 1.5rem; flex-grow: 1; }
.cart-item-info h4 { font-weight: 700; margin: 0; color: var(--text-primary); }
.cart-item-price { font-size: 0.875rem; color: var(--text-tertiary); margin: 0.25rem 0 0 0; }
.cart-item-seller { font-size: 0.75rem; color: var(--text-tertiary); margin: 0.25rem 0 0 0; display: flex; align-items: center; }
.cart-item-remove { color: #f87171; cursor: pointer; font-size: 0.875rem; }
.cart-empty { text-align: center; padding: 3rem; color: var(--text-tertiary); }
.cart-summary { width: 24rem; background: var(--glass-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--glass-border); border-radius: 1.5rem; padding: 2rem; box-shadow: var(--glass-shadow); flex-shrink: 0; }
.summary-line { display: flex; justify-content: space-between; margin-bottom: 1rem; font-size: 0.875rem; color: var(--text-secondary); }
.summary-total { border-top: 1px solid var(--glass-border); padding-top: 1.5rem; display: flex; justify-content: space-between; align-items: center; }
.total-price { font-size: 1.875rem; font-weight: 700; color: var(--lavender-accent); }
.checkout-btn { width: 100%; padding: 1rem; background: var(--gradient-brand); color: var(--text-primary); border-radius: 1rem; font-weight: 700; text-align: center; cursor: pointer; margin-top: 1.5rem; box-shadow: 0 4px 12px rgba(155, 142, 196, 0.3); }
.checkout-btn:hover { filter: brightness(0.95); }
</style>
