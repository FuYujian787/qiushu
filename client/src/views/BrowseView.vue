<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useVirtualData } from '@/composables/useVirtualData'
import BookCard from '@/components/BookCard.vue'
import BookGrid from '@/components/BookGrid.vue'
import FilterPanel from '@/components/FilterPanel.vue'
import SortDropdown from '@/components/SortDropdown.vue'
import EmptyState from '@/components/EmptyState.vue'
import { ElPagination } from 'element-plus'

const route = useRoute()
const router = useRouter()
const { searchBooks, loading } = useVirtualData()

const results = ref([])
const loadingResults = ref(false)
const filters = ref({ category: '', condition: '', priceMin: null, priceMax: null })
const sort = ref('created_at_desc')
const currentPage = ref(1)
const perPage = 20

const totalPages = computed(() => Math.ceil(results.value.length / perPage))
const totalResults = computed(() => results.value.length)
const paginatedResults = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return results.value.slice(start, start + perPage)
})

const query = computed(() => route.query.q || '')

async function doSearch() {
  loadingResults.value = true
  try {
    let sortField = sort.value
    results.value = await searchBooks(query.value, {
      ...filters.value,
      sort: sortField,
    })
  } finally {
    loadingResults.value = false
  }
}

// Update URL query params when filters change
function syncUrl() {
  const queryParams = { ...route.query }
  if (query.value) queryParams.q = query.value
  if (filters.value.category) queryParams.category = filters.value.category
  if (sort.value !== 'created_at_desc') queryParams.sort = sort.value
  router.replace({ query: queryParams })
}

watch([filters, sort, query], () => {
  currentPage.value = 1
  doSearch()
  syncUrl()
})

onMounted(() => {
  // Restore from URL
  if (route.query.category) filters.value.category = route.query.category
  if (route.query.sort) sort.value = route.query.sort
  doSearch()
})

function goToBook(book) {
  router.push({ name: 'BookDetail', params: { id: book.id } })
}
</script>

<template>
  <div class="browse-page page-enter">
    <div class="page-container">
      <div class="browse-header">
        <h1 class="browse-title">
          {{ query ? `搜索: "${query}"` : '浏览书籍' }}
        </h1>
        <span class="browse-count">共 {{ totalResults }} 本在售</span>
      </div>

      <div class="browse-layout">
        <!-- Sidebar Filters -->
        <aside class="browse-sidebar">
          <FilterPanel v-model="filters" />
        </aside>

        <!-- Main Content -->
        <div class="browse-main">
          <div class="browse-toolbar">
            <SortDropdown v-model="sort" />
          </div>

          <BookGrid
            :items="paginatedResults"
            :loading="loadingResults"
            @book-click="goToBook"
          />

          <EmptyState
            v-if="!loadingResults && paginatedResults.length === 0"
            icon="book"
            title="没有找到匹配的书籍"
            subtitle="试试调整筛选条件或搜索其他关键词"
          />

          <div v-if="totalPages > 1" class="pagination-wrapper">
            <el-pagination
              v-model:current-page="currentPage"
              :total="totalResults"
              :page-size="perPage"
              layout="prev, pager, next"
              background
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.browse-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 24px;
}

.browse-title {
  font-family: var(--font-display);
  font-size: 24px;
  color: var(--text-primary);
  font-weight: 700;
}

.browse-count {
  color: var(--text-muted);
  font-size: 14px;
}

.browse-layout {
  display: flex;
  gap: 24px;
}

.browse-sidebar {
  width: 220px;
  flex-shrink: 0;
}

.browse-main {
  flex: 1;
  min-width: 0;
}

.browse-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

@media (max-width: 768px) {
  .browse-layout {
    flex-direction: column;
  }
  .browse-sidebar {
    width: 100%;
  }
}
</style>
