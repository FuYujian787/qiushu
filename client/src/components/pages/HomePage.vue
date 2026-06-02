<template>
  <div class="home-page">
    <div class="top-grid">
      <div class="card official-zone apple-liquid-card stagger-item stagger-1">
        <div class="card-header">
          <h3 class="apple-text-gradient font-serif-display">
            <span class="iconify" data-icon="solar:verified-check-outline" data-width="20"></span>
            官方专区
          </h3>
          <span class="more-link">
            查看更多
            <span class="iconify" data-icon="solar:alt-arrow-right-outline" data-width="14"></span>
          </span>
        </div>
        <div class="publisher-grid">
          <div v-for="(pub, idx) in publishers" :key="pub.name" class="pub-item apple-liquid-card" :class="'bg-' + pub.color + '-50'">
            <span class="iconify" :data-icon="pub.icon" :data-width="32" :style="{ color: pub.color + '-400' }"></span>
            <span class="pub-name">{{ pub.name }}</span>
          </div>
        </div>
      </div>
      <div class="card community-zone apple-liquid-card stagger-item stagger-2">
        <h3 class="apple-text-gradient font-serif-display">
          <span class="iconify" data-icon="solar:users-group-two-rounded-outline" data-width="20"></span>
          学习社区
        </h3>
        <div class="topic-grid">
          <div v-for="(post, idx) in homePosts" :key="post.id" class="topic-item apple-liquid-nav-item" @click="goCommunity">
            <span class="iconify topic-dot" data-icon="solar:circle-small-outline" data-width="10"></span>
            <span class="topic-title">{{ post.title }}</span>
          </div>
        </div>
      </div>
    </div>
    <div class="bottom-grid">
      <div class="card smart-list apple-liquid-card stagger-item stagger-3">
        <h3 class="apple-text-gradient font-serif-display">
          <span class="iconify" data-icon="solar:lightbulb-bolt-outline" data-width="20"></span>
          智慧购书清单
        </h3>
        <div class="book-list">
          <div v-for="book in smartBooks" :key="book.name" class="book-row apple-cart-item" @click="goProcurement">
            <span class="book-name">{{ book.name }}</span>
            <span class="match-badge apple-match-badge">
              <span class="iconify" data-icon="solar:books-outline" data-width="14"></span>
              已匹配 {{ book.matchCount }} 本
            </span>
          </div>
        </div>
      </div>
      <div class="card hot-books apple-liquid-card stagger-item stagger-4">
        <h3 class="apple-text-gradient font-serif-display">
          <span class="iconify" data-icon="solar:fire-outline" data-width="20"></span>
          热门书本
        </h3>
        <div class="hot-list">
          <div
            v-for="book in randomBooks"
            :key="book.id"
            class="hot-item apple-product-card"
            @click="openDetail(book.id)"
            @mousemove="onHotMove($event, book.id)"
            @mouseleave="onHotLeave($event, book.id)"
          >
            <div class="hot-img apple-product-image-container">
              <img :src="book.img" :alt="book.title" class="hot-img-inner card-content-layer" />
            </div>
            <div class="hot-info card-content-layer">
              <h4 class="hot-title">{{ book.title }}</h4>
              <p class="hot-condition">{{ book.condition }}</p>
              <p class="hot-price apple-price-tag">
                <span class="iconify" data-icon="solar:dollar-minimalistic-outline" data-width="11"></span>
                {{ book.price }}
              </p>
              <p class="hot-seller" v-if="book.seller">
                <span class="iconify" data-icon="solar:user-outline" data-width="11"></span>
                {{ book.seller }}
                <button
                  v-if="store.isLoggedIn.value && book.seller !== store.currentUser.value?.name"
                  class="chat-btn-mini"
                  @click.stop="startChat(book.seller)"
                  title="私聊卖家"
                >
                  <span class="iconify" data-icon="solar:chat-dots-outline" data-width="14"></span>
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from '../../stores/useStore'

const store = useStore()

const publishers = computed(() => store.categoriesData.value?.homePublishers || [])
const smartBooks = computed(() => store.categoriesData.value?.smartBooks || [])
const randomBooks = computed(() => store.getRandomProducts(4))
const homePosts = computed(() => store.getMergedPosts().slice(0, 4))

function goCommunity() { store.navigateTo('community') }
function goProcurement() { store.navigateTo('procurement') }
function openDetail(id) { store.navigateTo('bookDetail', id) }

/* ===== 场景一扩展：热门书本 3D 悬停 ===== */
function onHotMove(e, id) {
  const el = e.currentTarget
  const rect = el.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const centerX = rect.width / 2
  const centerY = rect.height / 2

  const rotateY = ((x - centerX) / centerX) * 6
  const rotateX = ((centerY - y) / centerY) * 6

  el.style.transform = `perspective(600px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`
}

function onHotLeave(e, id) {
  const el = e.currentTarget
  el.style.transform = 'perspective(600px) rotateX(0deg) rotateY(0deg)'
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
.home-page { display: flex; flex-direction: column; gap: 1.5rem; }
.top-grid, .bottom-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1.5rem; }
.card {
  background: var(--glass-bg-card);
  backdrop-filter: blur(28px) saturate(1.4);
  -webkit-backdrop-filter: blur(28px) saturate(1.4);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-md), var(--shadow-glow), inset 0 1px 0 rgba(255,255,255,0.55);
  position: relative;
}
.official-zone { grid-column: span 2; }
.community-zone { grid-column: span 3; background: rgba(243, 239, 255, 0.6); border: 1px solid rgba(220, 208, 255, 0.3); }
.smart-list { grid-column: span 3; padding: 1.5rem; }
.hot-books { grid-column: span 2; padding: 1.5rem; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.card-header h3, .card h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 1.5rem 0;
  letter-spacing: -0.01em;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.card-header h3 { margin: 0; }
.more-link {
  font-size: 0.75rem;
  color: var(--text-caption);
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.2rem;
  transition: color 0.2s;
}
.more-link:hover { color: var(--lavender-accent); }
.publisher-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.pub-item {
  padding: 1rem;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1px solid rgba(255,255,255,0.3);
}
.pub-item:nth-child(1) { background: rgba(243, 239, 255, 0.8); }
.pub-item:nth-child(2) { background: rgba(220, 208, 255, 0.15); }
.pub-item:nth-child(3) { background: rgba(243, 239, 255, 0.5); }
.pub-item:nth-child(4) { background: rgba(255, 255, 255, 0.6); }
.pub-name { font-size: 0.875rem; font-weight: 500; margin-top: 0.5rem; }
.topic-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem 2rem; }
.topic-item { display: flex; align-items: center; gap: 0.75rem; cursor: pointer; }
.topic-dot { flex-shrink: 0; color: var(--lavender-accent-soft); }
.topic-title { font-size: 0.875rem; color: var(--text-secondary); }
.topic-title:hover { color: var(--lavender-accent); }
.book-list { display: flex; flex-direction: column; gap: 0.75rem; }
.book-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem;
  background: rgba(243, 239, 255, 0.6);
  border-radius: 12px;
  border: 1px solid rgba(220, 208, 255, 0.3);
  cursor: pointer;
  transition: all 0.2s ease;
}
.book-row:hover { border-color: var(--lavender-accent-soft); }
.book-name { font-size: 1.125rem; font-weight: 600; color: var(--text-primary); }
.match-badge {
  padding: 0.375rem 1rem;
  background: linear-gradient(135deg, #DCD0FF, #C4B5E0);
  color: var(--text-primary);
  font-size: 0.75rem;
  font-weight: 700;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}
.hot-list { display: flex; flex-direction: column; gap: 1rem; }
.hot-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.3);
  cursor: pointer;
  will-change: transform;
  transition: transform 0.1s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.hot-item:hover { background: rgba(255, 255, 255, 0.5); }
.hot-img {
  width: 4rem;
  aspect-ratio: 3 / 4;
  background: linear-gradient(135deg, rgba(255,255,255,0.4), rgba(220,210,240,0.3));
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
}
.hot-img-inner { width: 100%; height: 100%; object-fit: cover; }
.hot-info {}
.hot-title {
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.3;
}
.hot-condition {
  font-size: 0.75rem;
  color: var(--text-caption);
  margin: 0.25rem 0;
  font-weight: 400;
}
.hot-price {
  color: var(--text-primary);
  font-weight: 600;
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
  margin: 0.375rem 0 0 0;
  font-size: 0.85rem;
  letter-spacing: -0.02em;
  display: flex;
  align-items: center;
  gap: 0.15rem;
}
.hot-seller {
  font-size: 0.7rem;
  color: var(--text-caption);
  margin: 0.25rem 0 0 0;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.chat-btn-mini {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  margin-left: 0.4rem;
  background: rgba(108,63,192,0.08);
  border: 1px solid rgba(108,63,192,0.15);
  border-radius: 6px;
  cursor: pointer;
  padding: 0;
  color: var(--lavender-accent);
  transition: all 0.2s;
}
.chat-btn-mini:hover { background: rgba(108,63,192,0.15); border-color: rgba(108,63,192,0.3); }
</style>
