<template>
  <div class="cart-page">
    <div class="cart-layout">
      <div class="cart-items-section">
        <h3>
          <span class="iconify" data-icon="solar:cart-large-2-outline" data-width="22"></span>
          我的购物车
        </h3>
        <div id="cartItems">
          <div v-for="item in store.cart" :key="item.id" class="cart-item">
            <div class="cart-item-img"><img :src="item.img" class="cart-img" /></div>
            <div class="cart-item-info">
              <h4>{{ item.title }}</h4>
              <p class="cart-item-price">
                <span class="iconify" data-icon="solar:dollar-minimalistic-outline" data-width="12"></span>
                {{ item.price }} x {{ item.qty }}
              </p>
              <p class="cart-item-seller" v-if="item.seller">
                <span class="iconify" data-icon="solar:user-outline" data-width="12"></span>
                {{ item.seller }}
                <button
                  v-if="store.isLoggedIn.value && item.seller !== store.currentUser.value?.name"
                  class="chat-btn-mini"
                  @click.stop="startChat(item.seller)"
                  title="私聊卖家"
                >
                  <span class="iconify" data-icon="solar:chat-dots-outline" data-width="14"></span>
                </button>
              </p>
            </div>
            <div class="cart-item-remove" @click="removeItem(item.id)">
              <span class="iconify" data-icon="solar:trash-bin-trash-outline" data-width="17"></span>
              删除
            </div>
          </div>
          <div v-if="store.cart.length === 0" class="cart-empty">
            <span class="iconify empty-icon" data-icon="solar:cart-large-2-outline" data-width="44"></span>
            <p>购物车为空</p>
          </div>
        </div>
      </div>
      <div class="cart-summary">
        <h3>
          <span class="iconify" data-icon="solar:bill-list-outline" data-width="20"></span>
          订单摘要
        </h3>
        <div class="summary-line">
          <span>
            <span class="iconify" data-icon="solar:tag-outline" data-width="14"></span>
            商品总价
          </span>
          <span class="apple-price-mono">¥{{ total }}</span>
        </div>
        <div class="summary-total">
          <span>应付总额</span>
          <span class="total-price">¥{{ total }}</span>
        </div>
        <div class="checkout-btn" @click="goPayment">
          <span class="iconify" data-icon="solar:card-outline" data-width="18"></span>
          去支付
        </div>
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
.cart-layout { display: flex; flex-direction: row; gap: 1.5rem; }
.cart-items-section {
  flex-grow: 1;
  background: var(--glass-bg-card);
  backdrop-filter: blur(28px) saturate(1.4);
  -webkit-backdrop-filter: blur(28px) saturate(1.4);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: var(--shadow-md), var(--shadow-glow), inset 0 1px 0 rgba(255,255,255,0.55);
}
.cart-items-section h3, .cart-summary h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 1.5rem 0;
  letter-spacing: -0.01em;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.cart-item { display: flex; align-items: center; padding: 1.5rem 0; border-bottom: 1px solid var(--glass-border); }
.cart-item-img { width: 6rem; aspect-ratio: 3/4; background: linear-gradient(135deg, rgba(255,255,255,0.4), rgba(220,210,240,0.3)); border-radius: 4px; overflow: hidden; }
.cart-img { width: 100%; height: 100%; object-fit: cover; }
.cart-item-info { margin-left: 1.5rem; flex-grow: 1; }
.cart-item-info h4 { font-weight: 600; margin: 0; color: var(--text-primary); }
.cart-item-price {
  font-size: 0.875rem;
  color: var(--text-caption);
  margin: 0.25rem 0 0 0;
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
  display: flex;
  align-items: center;
  gap: 0.2rem;
}
.cart-item-seller {
  font-size: 0.75rem;
  color: var(--text-caption);
  margin: 0.25rem 0 0 0;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}
.chat-btn-mini {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  background: rgba(108,63,192,0.08);
  border: 1px solid rgba(108,63,192,0.15);
  border-radius: 6px;
  cursor: pointer;
  padding: 0;
  color: var(--lavender-accent);
  transition: all 0.2s;
}
.chat-btn-mini:hover { background: rgba(108,63,192,0.15); border-color: rgba(108,63,192,0.3); }
.cart-item-remove {
  color: #f87171;
  cursor: pointer;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.4rem 0.7rem;
  border-radius: 8px;
  transition: all 0.2s;
}
.cart-item-remove:hover { background: rgba(248,113,113,0.08); }
.cart-empty {
  text-align: center;
  padding: 3rem;
  color: var(--text-tertiary);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.8rem;
}
.cart-empty .empty-icon { opacity: 0.35; }
.cart-summary {
  width: 24rem;
  background: var(--glass-bg-card);
  backdrop-filter: blur(28px) saturate(1.4);
  -webkit-backdrop-filter: blur(28px) saturate(1.4);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: var(--shadow-md), var(--shadow-glow), inset 0 1px 0 rgba(255,255,255,0.55);
  flex-shrink: 0;
}
.summary-line {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
}
.summary-line span:first-child {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}
.summary-total {
  border-top: 1px solid var(--glass-border);
  padding-top: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.total-price {
  font-size: 1.875rem;
  font-weight: 700;
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}
.checkout-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #6c3fc0 0%, #af52de 100%);
  color: #fff;
  border: none;
  border-radius: 14px;
  font-weight: 700;
  text-align: center;
  cursor: pointer;
  margin-top: 1.5rem;
  box-shadow: 0 4px 16px rgba(108, 63, 192, 0.3);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}
.checkout-btn:hover { filter: brightness(1.08); transform: translateY(-1px); }
</style>
