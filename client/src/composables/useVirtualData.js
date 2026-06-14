import { ref } from 'vue'
import api from '@/api'

const books = ref([])
const loading = ref(false)
const loaded = ref(false)

/**
 * 兼容 requestIdleCallback 的降级方案（Safari 不支持）
 */
function requestIdleCallbackShim(callback, options) {
  const start = Date.now()
  return setTimeout(() => {
    callback({
      didTimeout: false,
      timeRemaining: () => Math.max(0, 50 - (Date.now() - start)),
    })
  }, 1)
}

const rIC = window.requestIdleCallback || requestIdleCallbackShim

export function useVirtualData() {
  async function loadBooks() {
    if (loaded.value) return books.value
    if (loading.value) {
      return new Promise((resolve) => {
        const check = setInterval(() => {
          if (loaded.value) {
            clearInterval(check)
            resolve(books.value)
          }
        }, 100)
      })
    }

    loading.value = true
    const startTime = performance.now()

    try {
      const response = await fetch('/mock/books_100k.json')
      const text = await response.text()

      const data = await new Promise((resolve, reject) => {
        const actualChunkSize = 5000
        let allData
        let result = []
        let index = 0

        try {
          allData = JSON.parse(text)
        } catch (e) {
          reject(new Error('JSON 解析失败: ' + e.message))
          return
        }

        function processChunk(deadline) {
          try {
            const endIndex = Math.min(index + actualChunkSize, allData.length)
            for (let i = index; i < endIndex; i++) {
              result.push(allData[i])
            }
            index = endIndex

            if (index >= allData.length) {
              resolve(result)
            } else {
              rIC(processChunk)
            }
          } catch (e) {
            reject(e)
          }
        }
        rIC(processChunk)
      })

      books.value = data
      loaded.value = true
      const elapsed = ((performance.now() - startTime) / 1000).toFixed(2)
      console.log(`[OK] 已加载 ${data.length} 条虚拟书籍 (${elapsed}s)`)
      return data
    } catch (err) {
      console.error('虚拟数据加载失败:', err)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * 搜索书籍 — 合并后端 API 结果（数据库中的真实发布）+ 虚拟数据
   */
  async function searchBooks(query = '', filters = {}) {
    await loadBooks()

    // ── 并行请求：后端API + 本地虚拟数据过滤 ──
    const apiPromise = fetchApiBooks(query, filters)
    const mockPromise = filterMockBooks(query, filters)

    const [apiResults, mockResults] = await Promise.all([apiPromise, mockPromise])

    // ── 合并去重：API 结果优先（真实发布的书在前） ──
    const apiIds = new Set(apiResults.map((b) => b.id))
    const dedupedMock = mockResults.filter((b) => !apiIds.has(b.id))

    return [...apiResults, ...dedupedMock]
  }

  /**
   * 从后端 API 获取书籍（数据库中的真实发布）
   */
  async function fetchApiBooks(query, filters) {
    try {
      const params = { per_page: 100 }
      if (query) params.q = query
      if (filters.category) params.category = filters.category
      if (filters.condition) params.condition = filters.condition
      if (filters.priceMin != null) params.price_min = filters.priceMin
      if (filters.priceMax != null) params.price_max = filters.priceMax
      if (filters.sort) {
        if (filters.sort === 'price_asc') { params.sort = 'price'; params.order = 'asc' }
        else if (filters.sort === 'price_desc') { params.sort = 'price'; params.order = 'desc' }
        else { params.sort = 'created_at'; params.order = 'desc' }
      }

      const res = await api.get('/books', { params })
      if (res.status === 'success' && res.data?.books) {
        return res.data.books
      }
      return []
    } catch (err) {
      console.warn('API 搜索失败，仅使用虚拟数据:', err.message)
      return []
    }
  }

  /**
   * 在已加载的虚拟数据中过滤
   */
  async function filterMockBooks(query, filters) {
    return new Promise((resolve) => {
      setTimeout(() => {
        let results = books.value

        if (query) {
          const q = query.toLowerCase()
          results = results.filter(
            (b) => b.title.toLowerCase().includes(q) || b.author.toLowerCase().includes(q)
          )
        }
        if (filters.category) {
          results = results.filter((b) => b.category === filters.category)
        }
        if (filters.condition) {
          results = results.filter((b) => b.condition === filters.condition)
        }
        if (filters.priceMin !== undefined && filters.priceMin !== null) {
          results = results.filter((b) => b.price >= filters.priceMin)
        }
        if (filters.priceMax !== undefined && filters.priceMax !== null) {
          results = results.filter((b) => b.price <= filters.priceMax)
        }
        if (filters.sort === 'price_asc') {
          results = [...results].sort((a, b) => a.price - b.price)
        } else if (filters.sort === 'price_desc') {
          results = [...results].sort((a, b) => b.price - a.price)
        } else {
          results = [...results].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        }

        resolve(results)
      }, 0)
    })
  }

  function getBookById(id) {
    // First check mock data
    const mockBook = books.value.find((b) => b.id === id)
    if (mockBook) return mockBook
    // Fallback: will be handled by BookDetailView's API call
    return null
  }

  return { books, loading, loaded, loadBooks, searchBooks, getBookById }
}
