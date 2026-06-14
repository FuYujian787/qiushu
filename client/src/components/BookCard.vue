<script setup>
import { computed } from 'vue'

const props = defineProps({
  book: { type: Object, required: true },
})

const emit = defineEmits(['click'])

const conditionColor = computed(() => {
  const map = {
    '全新': { bg: '#E8F5E9', text: '#2E7D32' },
    '良好': { bg: '#FFF8E1', text: '#F57F17' },
    '有笔记': { bg: '#FCE4EC', text: '#C62828' },
    '旧': { bg: '#F5F5F5', text: '#616161' },
  }
  return map[props.book.condition] || { bg: '#F5F5F5', text: '#616161' }
})

// Resolve the cover image URL from either format:
// - Mock data: "images/book_1.jpg" → "/mock/images/book_1.jpg"
// - DB records: "/mock/images/book_5.jpg" or "/static/uploads/xxx.jpg"
const coverSrc = computed(() => {
  const img = props.book.image || props.book.cover_image
  if (!img) {
    return '/mock/images/_5_鱼鱼何包蛋_来自小红书网页版.jpg'
  }
  if (img.startsWith('/')) return img
  if (img.startsWith('images/')) return `/mock/${img}`
  return `/mock/${img}`
})

const priceColor = computed(() => {
  return document.documentElement.getAttribute('data-theme') === 'cyber' ? '#00D4FF' : '#C41E3A'
})

// Handle image load failure — fallback to another random cover
function onImgError(e) {
  e.target.src = '/mock/images/_5_鱼鱼何包蛋_来自小红书网页版.jpg'
}
</script>

<template>
  <div class="book-card" @click="$emit('click')">
    <!-- Cover — always uses real book cover image -->
    <div class="book-cover">
      <img
        :src="coverSrc"
        :alt="book.title"
        class="cover-img"
        loading="lazy"
        @error="onImgError"
      />
      <span class="condition-badge" :style="{ background: conditionColor.bg, color: conditionColor.text }">
        {{ book.condition }}
      </span>
      <span v-if="book.status === '预定了'" class="reserved-badge">已预定</span>
    </div>

    <!-- Info -->
    <div class="book-info">
      <h3 class="book-title">{{ book.title }}</h3>
      <p class="book-author">{{ book.author }}</p>
      <div class="book-footer">
        <span class="book-price" :style="{ color: priceColor }">
          <span class="price-symbol">¥</span>{{ book.price }}
          <span v-if="book.original_price" class="original-price">¥{{ book.original_price }}</span>
        </span>
        <span class="book-seller">{{ book.seller }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.book-card {
  background: var(--surface-secondary);
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  border: 1px solid var(--border-default);
}

.book-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-lg);
}

.book-cover {
  position: relative;
  aspect-ratio: 3/4;
  overflow: hidden;
  background: var(--surface-tertiary);
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.book-card:hover .cover-img {
  transform: scale(1.04);
}

.condition-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.reserved-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  background: rgba(255, 152, 0, 0.9);
  color: #fff;
  animation: pulse-reserved 2s ease-in-out infinite;
}

@keyframes pulse-reserved {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.book-info {
  padding: 12px 14px 14px;
}

.book-title {
  font-family: var(--font-display);
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 700;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 4px;
}

.book-author {
  color: var(--text-muted);
  font-size: 12px;
  margin-bottom: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.book-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.book-price {
  font-family: var(--font-mono);
  font-size: 18px;
  font-weight: 600;
}

.price-symbol {
  font-size: 12px;
}

.original-price {
  font-size: 12px;
  color: var(--text-muted);
  text-decoration: line-through;
  margin-left: 6px;
}

.book-seller {
  color: var(--text-muted);
  font-size: 11px;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
