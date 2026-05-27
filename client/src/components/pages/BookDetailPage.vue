<template>
  <div class="detail-page">
    <div v-if="!book" class="empty-state">书籍未找到</div>
    <div v-else class="detail-layout">
      <!-- 场景一：【知识的引力】书籍封面 3D 悬停 -->
      <div
        class="detail-image book-card-3d"
        ref="coverRef"
        @mousemove="onCoverMove"
        @mouseleave="onCoverLeave"
      >
        <div class="detail-img-wrap">
          <img :src="book.img" class="detail-img card-content-layer" />
        </div>
        <div class="card-glass-flare" :style="flareStyle" />
      </div>

      <div class="detail-info">
        <h1 class="detail-title">{{ book.title }}</h1>
        <p class="detail-author">
          {{ book.author }} · {{ book.seller }}
          <button
            v-if="store.isLoggedIn.value && book.seller !== store.currentUser.value?.name"
            class="chat-btn-mini"
            @click.stop="startChat(book.seller)"
            title="私聊卖家"
          >
            💬
          </button>
        </p>
        <div class="detail-price">
          <span class="current-price">¥{{ book.price }}</span>
          <span class="old-price">原价 ¥{{ book.oldPrice }}</span>
        </div>
        <div class="detail-actions">
          <div class="detail-btn primary" @click="addAndGo">加入购物车</div>
          <div class="detail-btn dark" @click="buyNow">立即购买</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useStore } from '../../stores/useStore'

const store = useStore()

const book = computed(() => {
  return store.productCache.value.find(p => p.id === store.bookDetailId.value)
})

function addAndGo() {
  if (book.value) {
    store.addToCart(book.value)
    alert('已加入购物车')
  }
}

function buyNow() {
  if (book.value) {
    store.addToCart(book.value)
    store.navigateTo('cart')
  }
}

/* ===== 场景一：3D 悬停微交互 ===== */
const coverRef = ref(null)
const flareStyle = ref({})

function onCoverMove(e) {
  const el = coverRef.value
  if (!el) return
  const rect = el.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const centerX = rect.width / 2
  const centerY = rect.height / 2

  // 计算 3D 旋转角度（最大 ±8 度）
  const rotateY = ((x - centerX) / centerX) * 8
  const rotateX = ((centerY - y) / centerY) * 8

  el.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`

  // 玻璃高光跟随鼠标
  flareStyle.value = {
    '--flare-x': `${(x / rect.width) * 100}%`,
    '--flare-y': `${(y / rect.height) * 100}%`,
  }
}

function onCoverLeave() {
  if (coverRef.value) {
    coverRef.value.style.transform = 'perspective(800px) rotateX(0deg) rotateY(0deg)'
  }
  flareStyle.value = {}
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
.detail-page {}
.empty-state { text-align: center; padding: 3rem; color: var(--text-tertiary); }
.detail-layout { display: grid; grid-template-columns: repeat(12, 1fr); gap: 2.5rem; max-width: 72rem; margin: 0 auto; }
.detail-image { grid-column: span 4; }
.detail-img-wrap { background: var(--glass-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--glass-border); padding: 1.5rem; border-radius: 2.5rem; box-shadow: var(--glass-shadow); }
.detail-img { aspect-ratio: 3/4; border-radius: 1.5rem; overflow: hidden; width: 100%; object-fit: cover; }
.detail-info { grid-column: span 8; background: var(--glass-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--glass-border); border-radius: 2.5rem; padding: 2.5rem; box-shadow: var(--glass-shadow); }
.detail-title { font-size: 1.875rem; font-weight: 700; color: var(--text-primary); margin: 0; }
.detail-author { color: var(--text-tertiary); margin-top: 0.5rem; font-size: 0.875rem; }
.detail-price { margin-top: 1.5rem; display: flex; align-items: center; gap: 1rem; }
.current-price { font-size: 2.25rem; font-weight: 900; color: var(--lavender-accent); }
.old-price { font-size: 0.875rem; color: var(--text-tertiary); text-decoration: line-through; }
.detail-actions { margin-top: 2rem; display: flex; gap: 1rem; }
.detail-btn { flex: 1; padding: 1rem; border-radius: 1rem; font-weight: 700; text-align: center; cursor: pointer; }
.detail-btn.primary { background: var(--gradient-brand); color: var(--text-primary); box-shadow: 0 4px 12px rgba(155, 142, 196, 0.3); }
.detail-btn.primary:hover { filter: brightness(0.95); }
.detail-btn.dark { background: var(--text-primary); color: white; }
.detail-btn.dark:hover { filter: brightness(1.2); }
</style>
