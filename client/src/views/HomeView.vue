<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useVirtualData } from '@/composables/useVirtualData'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'
import HeroSection from '@/components/HeroSection.vue'
import BookGrid from '@/components/BookGrid.vue'
import RecommendSection from '@/components/RecommendSection.vue'

const router = useRouter()
const { loadBooks } = useVirtualData()
const auth = useAuthStore()

const featuredBooks = ref([])
const loadingFeatured = ref(true)

onMounted(async () => {
  // 并行加载：数据库真实发布 + 虚拟数据
  const [apiBooks, allMockBooks] = await Promise.all([
    fetchApiRecent(),
    loadBooks(),
  ])

  // 数据库中的真实书籍排在最前面
  const apiIds = new Set(apiBooks.map((b) => b.id))
  const dedupedMock = allMockBooks.filter((b) => !apiIds.has(b.id))
  // 随机抽样填充到 8 本
  const randomMock = dedupedMock.sort(() => Math.random() - 0.5).slice(0, Math.max(0, 8 - apiBooks.length))

  featuredBooks.value = [...apiBooks.slice(0, 8), ...randomMock]
  loadingFeatured.value = false
})

async function fetchApiRecent() {
  try {
    const res = await api.get('/books', { params: { sort: 'created_at', order: 'desc', per_page: 8 } })
    return res.data?.books || []
  } catch {
    return []
  }
}

function goToBook(book) {
  router.push({ name: 'BookDetail', params: { id: book.id } })
}
</script>

<template>
  <div class="home-page">
    <HeroSection />

    <!-- Personalized / Hot Recommendations -->
    <section class="page-container">
      <RecommendSection />
    </section>

    <!-- Recently Listed Books -->
    <section class="featured-section page-container">
      <div class="section-header">
        <h2 class="section-title">最近上架</h2>
        <router-link to="/browse" class="section-link">浏览全部 →</router-link>
      </div>
      <BookGrid
        :items="featuredBooks"
        :loading="loadingFeatured"
        @book-click="goToBook"
      />
    </section>
  </div>
</template>

<style scoped>
.featured-section {
  padding-top: 0;
  padding-bottom: 48px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title {
  font-family: var(--font-display);
  font-size: 22px;
  color: var(--text-primary);
  font-weight: 700;
}

.section-link {
  color: var(--accent-primary);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
}

.section-link:hover { text-decoration: underline; }
</style>
