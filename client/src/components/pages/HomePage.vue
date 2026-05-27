<template>
  <div class="home-page">
    <div class="top-grid">
      <div class="card official-zone">
        <div class="card-header"><h3>官方专区</h3><span class="more-link">查看更多</span></div>
        <div class="publisher-grid">
          <div v-for="pub in publishers" :key="pub.name" class="pub-item" :class="'bg-' + pub.color + '-50'">
            <span class="iconify" :data-icon="pub.icon" :data-width="32" :style="{ color: pub.color + '-400' }"></span>
            <span class="pub-name">{{ pub.name }}</span>
          </div>
        </div>
      </div>
      <div class="card community-zone">
        <h3>学习社区</h3>
        <div class="topic-grid">
          <div v-for="post in homePosts" :key="post.id" class="topic-item" @click="goCommunity">
            <span class="topic-dot"></span>
            <span class="topic-title">{{ post.title }}</span>
          </div>
        </div>
      </div>
    </div>
    <div class="bottom-grid">
      <div class="card smart-list">
        <h3>智慧购书清单</h3>
        <div class="book-list">
          <div v-for="book in smartBooks" :key="book.name" class="book-row" @click="goProcurement">
            <span class="book-name">{{ book.name }}</span>
            <span class="match-badge">已匹配 {{ book.matchCount }} 本</span>
          </div>
        </div>
      </div>
      <div class="card hot-books">
        <h3>热门书本</h3>
        <div class="hot-list">
          <div
            v-for="book in randomBooks"
            :key="book.id"
            class="hot-item book-card-3d"
            @click="openDetail(book.id)"
            @mousemove="onHotMove($event, book.id)"
            @mouseleave="onHotLeave($event, book.id)"
          >
            <div class="hot-img"><img :src="book.img" :alt="book.title" class="hot-img-inner card-content-layer" /></div>
            <div class="hot-info card-content-layer">
              <h4 class="hot-title">{{ book.title }}</h4>
              <p class="hot-condition">{{ book.condition }}</p>
              <p class="hot-price">¥{{ book.price }}</p>
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
</script>

<style scoped>
.home-page { display: flex; flex-direction: column; gap: 2rem; }
.top-grid, .bottom-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 2rem; }
.card { background: var(--glass-bg); border-radius: 1.5rem; padding: 1.5rem; backdrop-filter: blur(16px); border: 1px solid var(--glass-border); box-shadow: var(--glass-shadow); }
.official-zone { grid-column: span 2; }
.community-zone { grid-column: span 3; background: rgba(243, 239, 255, 0.6); border: 1px solid rgba(220, 208, 255, 0.3); }
.smart-list { grid-column: span 3; padding: 2rem; }
.hot-books { grid-column: span 2; padding: 2rem; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.card-header h3, .card h3 { font-size: 1.125rem; font-weight: 700; color: var(--text-primary); margin: 0 0 1.5rem 0; }
.card-header h3 { margin: 0; }
.more-link { font-size: 0.75rem; color: var(--lavender-accent-soft); cursor: pointer; }
.publisher-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.pub-item { padding: 1rem; border-radius: 1rem; display: flex; flex-direction: column; align-items: center; }
.pub-item:nth-child(1) { background: rgba(243, 239, 255, 0.8); }
.pub-item:nth-child(2) { background: rgba(220, 208, 255, 0.15); }
.pub-item:nth-child(3) { background: rgba(243, 239, 255, 0.5); }
.pub-item:nth-child(4) { background: rgba(255, 255, 255, 0.6); }
.pub-name { font-size: 0.875rem; font-weight: 500; margin-top: 0.5rem; }
.topic-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem 2rem; }
.topic-item { display: flex; align-items: center; gap: 0.75rem; cursor: pointer; }
.topic-dot { width: 0.5rem; height: 0.5rem; border-radius: 50%; background: var(--lavender-accent-soft); flex-shrink: 0; }
.topic-title { font-size: 0.875rem; color: var(--text-secondary); }
.topic-title:hover { color: var(--lavender-accent); }
.book-list { display: flex; flex-direction: column; gap: 1rem; }
.book-row { display: flex; align-items: center; justify-content: space-between; padding: 1.5rem; background: rgba(243, 239, 255, 0.6); border-radius: 1rem; border: 1px solid rgba(220, 208, 255, 0.3); cursor: pointer; }
.book-row:hover { border-color: var(--lavender-accent-soft); }
.book-name { font-size: 1.125rem; font-weight: 700; color: var(--text-primary); }
.match-badge { padding: 0.375rem 1rem; background: linear-gradient(135deg, #DCD0FF, #C4B5E0); color: var(--text-primary); font-size: 0.75rem; font-weight: 700; border-radius: 9999px; }
.hot-list { display: flex; flex-direction: column; gap: 1.5rem; }
.hot-item { display: flex; align-items: center; gap: 1rem; padding: 1rem; border-radius: 1rem; cursor: pointer; will-change: transform; transition: transform 0.1s cubic-bezier(0.25, 0.8, 0.25, 1); }
.hot-item:hover { background: rgba(255, 255, 255, 0.5); }
.hot-img { width: 4rem; height: 5rem; background: rgba(255, 255, 255, 0.3); border-radius: 0.5rem; overflow: hidden; flex-shrink: 0; }
.hot-img-inner { width: 100%; height: 100%; object-fit: cover; }
.hot-info {}
.hot-title { font-weight: 700; color: var(--text-primary); margin: 0; font-size: 0.875rem; }
.hot-condition { font-size: 0.75rem; color: var(--text-tertiary); margin: 0.25rem 0; }
.hot-price { color: var(--lavender-accent); font-weight: 700; margin: 0.5rem 0 0 0; }
</style>
