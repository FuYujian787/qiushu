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
          <div v-for="book in randomBooks" :key="book.id" class="hot-item" @click="openDetail(book.id)">
            <div class="hot-img"><img :src="book.img" :alt="book.title" class="hot-img-inner" /></div>
            <div class="hot-info">
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
</script>

<style scoped>
.home-page { display: flex; flex-direction: column; gap: 2rem; }
.top-grid, .bottom-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 2rem; }
.card { background: white; border-radius: 1.5rem; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.official-zone { grid-column: span 2; }
.community-zone { grid-column: span 3; background: #faf5ff; border: 1px solid #f3e8ff; }
.smart-list { grid-column: span 3; padding: 2rem; }
.hot-books { grid-column: span 2; padding: 2rem; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.card-header h3, .card h3 { font-size: 1.125rem; font-weight: 700; color: #374151; margin: 0 0 1.5rem 0; }
.card-header h3 { margin: 0; }
.more-link { font-size: 0.75rem; color: #a78bfa; cursor: pointer; }
.publisher-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.pub-item { padding: 1rem; border-radius: 1rem; display: flex; flex-direction: column; align-items: center; }
.pub-item:nth-child(1) { background: #faf5ff; }
.pub-item:nth-child(2) { background: #eff6ff; }
.pub-item:nth-child(3) { background: #fef2f2; }
.pub-item:nth-child(4) { background: #f9fafb; }
.pub-name { font-size: 0.875rem; font-weight: 500; margin-top: 0.5rem; }
.topic-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem 2rem; }
.topic-item { display: flex; align-items: center; gap: 0.75rem; cursor: pointer; }
.topic-dot { width: 0.5rem; height: 0.5rem; border-radius: 50%; background: #a78bfa; flex-shrink: 0; }
.topic-title { font-size: 0.875rem; color: #6b7280; }
.topic-title:hover { color: #7c3aed; }
.book-list { display: flex; flex-direction: column; gap: 1rem; }
.book-row { display: flex; align-items: center; justify-content: space-between; padding: 1.5rem; background: #faf5ff; border-radius: 1rem; border: 1px solid #f3e8ff; cursor: pointer; }
.book-row:hover { border-color: #d8b4fe; }
.book-name { font-size: 1.125rem; font-weight: 700; color: #374151; }
.match-badge { padding: 0.375rem 1rem; background: #7c3aed; color: white; font-size: 0.75rem; font-weight: 700; border-radius: 9999px; }
.hot-list { display: flex; flex-direction: column; gap: 1.5rem; }
.hot-item { display: flex; align-items: center; gap: 1rem; padding: 1rem; border-radius: 1rem; cursor: pointer; }
.hot-item:hover { background: #f9fafb; }
.hot-img { width: 4rem; height: 5rem; background: #f3f4f6; border-radius: 0.5rem; overflow: hidden; flex-shrink: 0; }
.hot-img-inner { width: 100%; height: 100%; object-fit: cover; }
.hot-info {}
.hot-title { font-weight: 700; color: #374151; margin: 0; font-size: 0.875rem; }
.hot-condition { font-size: 0.75rem; color: #9ca3af; margin: 0.25rem 0; }
.hot-price { color: #7c3aed; font-weight: 700; margin: 0.5rem 0 0 0; }
</style>
