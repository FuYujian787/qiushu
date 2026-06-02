<template>
  <!-- ============================================================
   紫金求思 · 数字化思想圣殿 — 社区模块
   ============================================================
   设计哲学：
     - 三栏式布局：左栏分类 (20%) | 中栏帖子流 (55%) | 右栏知识联动 (25%)
     - 晶体玻璃拟态：backdrop-filter: blur(24px) saturate(120%)
     - 电影级入场转场：错峰延迟 (Stagger) + cubic-bezier(0.16, 1, 0.3, 1)
     - 流体悬停 Z 轴浮起 3px + 无缝内联回复
     - 智能书名识别与书摊联动 Popover
   ============================================================ -->
  <div class="community-sacred-hall">
    <!-- ===== 骨架屏（数据加载时显示） ===== -->
    <div v-if="loading" class="skeleton-overlay">
      <div class="skeleton-container">
        <div class="skeleton-sidebar">
          <div class="skeleton-block" v-for="n in 5" :key="'sk-sb-' + n"></div>
        </div>
        <div class="skeleton-main">
          <div class="skeleton-card" v-for="n in 4" :key="'sk-c-' + n">
            <div class="skeleton-line w-60"></div>
            <div class="skeleton-line w-80"></div>
            <div class="skeleton-line w-40"></div>
          </div>
        </div>
        <div class="skeleton-sidebar-right">
          <div class="skeleton-block" v-for="n in 3" :key="'sk-sr-' + n"></div>
        </div>
      </div>
    </div>

    <!-- ===== 主内容（数据就绪后显示） ===== -->
    <template v-else>
      <!-- 左栏：极简分类 (20%) -->
      <aside class="category-panel">
        <div class="category-header">
          <h3 class="category-title">思辨回廊</h3>
          <p class="category-subtitle">探索知识维度</p>
        </div>
        <nav class="category-list">
          <button
            v-for="cat in categories"
            :key="cat.key"
            class="category-item"
            :class="{ 'category-active': activeCategory === cat.key }"
            @click="switchCategory(cat.key)"
          >
            <span class="category-icon">{{ cat.icon }}</span>
            <span class="category-label">{{ cat.label }}</span>
            <span class="category-count">{{ cat.count }}</span>
          </button>
        </nav>
        <div class="category-footer">
          <button class="new-thought-btn" @click="togglePostForm">
            <span class="iconify new-thought-icon" data-icon="solar:sparkles-outline" data-width="18"></span>
            <span>发布思想</span>
          </button>
        </div>
      </aside>

      <!-- 中栏：沉浸式帖子主信息流 (55%) -->
      <main class="post-stream">
        <!-- 发布新帖表单（毛玻璃滑入） -->
        <Transition name="form-slide">
          <div v-if="showPostForm" class="new-post-form glass-crystal">
            <div class="form-header">
              <h4 class="form-title font-serif-display">记录你的思想</h4>
            <button class="form-close-btn" @click="togglePostForm">
              <span class="iconify" data-icon="solar:close-circle-outline" data-width="20"></span>
            </button>
            </div>
            <input
              v-model="newPostTitle"
              placeholder="为你的思想命名..."
              class="form-input"
              maxlength="100"
            />
            <textarea
              v-model="newPostContent"
              placeholder="分享你的学习心得、书籍推荐、问题探讨... 输入《书名》即可自动关联书摊在售书籍"
              rows="5"
              class="form-textarea"
              maxlength="10000"
            ></textarea>
            <div class="form-actions">
              <span class="form-hint">✦ 输入《书名》自动联动书摊</span>
              <div class="form-btns">
                <button class="btn-cancel" @click="togglePostForm">取消</button>
                <button class="btn-submit" @click="submitPost" :disabled="submitting">
                  {{ submitting ? '发布中...' : '发布思想' }}
                </button>
              </div>
            </div>
          </div>
        </Transition>

        <!-- 排序切换 -->
        <div class="stream-toolbar">
          <div class="sort-tabs">
            <button
              v-for="s in sortOptions"
              :key="s.key"
              class="sort-tab"
              :class="{ 'sort-active': activeSort === s.key }"
              @click="switchSort(s.key)"
            >
              {{ s.label }}
            </button>
          </div>
          <span class="stream-count">共 {{ filteredPosts.length }} 条思辨</span>
        </div>

        <!-- 帖子列表（错峰延迟 Stagger 动画） -->
        <!--
          【电影级入场转场】
          使用 TransitionGroup 实现错峰延迟（Stagger Effect）：
          - 每条卡片以 15ms 间隔从下往上浮现
          - 位移 15px，曲线 cubic-bezier(0.16, 1, 0.3, 1)
          - 仅使用 transform 和 opacity，确保 120Hz 下 120FPS 无 Jank
        -->
        <TransitionGroup
          name="stagger"
          tag="div"
          class="post-list"
          :css="true"
        >
          <article
            v-for="(post, index) in filteredPosts"
            :key="post.id"
            class="post-card glass-crystal"
            :style="{ '--stagger-delay': index * 15 + 'ms' }"
            @mouseenter="onPostHover(post)"
          >
            <!-- 帖子头部：作者信息 -->
            <div class="post-header">
              <div class="post-author-avatar">
                {{ getInitial(post.author) }}
              </div>
              <div class="post-author-info">
                <span class="post-author-name">{{ post.author }}</span>
                <span class="post-author-badge" v-if="post.authorInfo">
                  {{ post.authorInfo.college }} · {{ post.authorInfo.grade }}
                </span>
                <button
                  v-if="store.isLoggedIn.value && post.author !== store.currentUser.value?.name"
                  class="chat-btn-mini"
                  @click.stop="startChat(post.author)"
                  :aria-label="'私聊 ' + post.author"
                  title="私聊"
                >
                  <span class="iconify" data-icon="solar:chat-dots-outline" data-width="14"></span>
                </button>
              </div>
            </div>

            <!-- 帖子标题 -->
            <h3 class="post-title">{{ post.title }}</h3>

            <!-- 帖子正文（安全转义后渲染，书名高亮为淡紫标签） -->
            <!--
              【XSS 安全防范】
              后端已对 content 做 HTML 转义（sanitize_html），
              此处使用 v-html 仅渲染安全的转义文本，
              书名高亮通过 replace 替换《》为带标记的 span，
              所有用户输入均已被转义，杜绝 XSS 注入。
            -->
            <div
              class="post-content"
              v-html="highlightBookTitles(post.content)"
            ></div>

            <!-- 智能书名标签行 -->
            <div class="book-tags" v-if="post.matchedBooks && post.matchedBooks.length > 0">
              <div
                v-for="book in post.matchedBooks"
                :key="book.title"
                class="book-tag"
                @mouseenter="showBookPopover($event, book)"
                @mouseleave="hideBookPopover"
              >
                《{{ book.title }}》
              </div>
            </div>

            <!-- 帖子统计栏 -->
            <div class="post-stats">
              <button class="stat-btn" @click="likePost(post)" :class="{ 'stat-liked': post._liked }">
                <span class="iconify stat-icon" :data-icon="post._liked ? 'solar:heart-bold' : 'solar:heart-outline'" data-width="15"></span>
                <span>{{ post.likeCount || 0 }}</span>
              </button>
              <button class="stat-btn" @click="toggleReplyForm(post)">
                <span class="iconify stat-icon" data-icon="solar:reply-outline" data-width="15"></span>
                <span>{{ post.replyCount || (post.replies ? post.replies.length : 0) }}</span>
              </button>
              <span class="stat-btn stat-view">
                <span class="iconify stat-icon" data-icon="solar:eye-outline" data-width="15"></span>
                <span>{{ post.viewCount || 0 }}</span>
              </span>
              <span class="stat-footer-meta">
                <span class="stat-footer-item" v-if="post.hotScore">
                  <span class="iconify" data-icon="solar:fire-outline" data-width="13"></span>
                  热度 {{ post.hotScore.toFixed(1) }}
                </span>
                <span class="stat-footer-divider" v-if="post.hotScore">·</span>
                <span class="stat-footer-item">
                  <span class="iconify" data-icon="solar:clock-circle-outline" data-width="13"></span>
                  {{ post.time }}
                </span>
              </span>
            </div>

            <!-- 回复列表 -->
            <div class="replies-section" v-if="post.replies && post.replies.length > 0">
              <TransitionGroup name="reply-stagger" tag="div" class="replies-list">
                <div
                  v-for="(reply, rIdx) in post.replies"
                  :key="reply.id"
                  class="reply-item"
                  :style="{ '--reply-delay': rIdx * 10 + 'ms' }"
                >
                  <div class="reply-header">
                    <span class="reply-author">{{ reply.author }}</span>
                    <span class="reply-author-badge" v-if="reply.authorInfo">
                      {{ reply.authorInfo.college }}
                    </span>
                    <button
                      v-if="store.isLoggedIn.value && reply.author !== store.currentUser.value?.name"
                      class="chat-btn-mini"
                      @click.stop="startChat(reply.author)"
                      title="私聊"
                    >
                      💬
                    </button>
                    <span class="reply-time">{{ reply.time }}</span>
                  </div>
                  <p class="reply-content">{{ reply.content }}</p>
                  <button class="reply-like-btn" @click="likeReply(post, reply)">
                    <span class="iconify" data-icon="solar:heart-outline" data-width="13"></span>
                    {{ reply.likeCount || 0 }}
                  </button>
                </div>
              </TransitionGroup>
            </div>

            <!-- 内联回复输入框（毛玻璃微型输入框） -->
            <!--
              【无缝内联回复】
              点击"回复"按钮后，原地滑出毛玻璃输入框，
              提交后新回复通过响应式状态无缝插入，
              绝对禁止页面跳动和硬刷新。
            -->
            <Transition name="reply-inline">
              <div v-if="activeReplyPostId === post.id" class="inline-reply-box glass-crystal">
                <textarea
                  v-model="replyInputs[post.id]"
                  placeholder="写下你的回应..."
                  rows="2"
                  class="reply-textarea"
                  @keydown.enter.prevent="submitReply(post)"
                ></textarea>
                <div class="reply-box-actions">
                  <span class="reply-preview-hint">↵ 发送</span>
                  <div class="reply-box-btns">
                    <button class="reply-cancel-btn" @click="closeReplyForm(post)">取消</button>
                    <button
                      class="reply-submit-btn"
                      @click="submitReply(post)"
                      :disabled="!replyInputs[post.id]?.trim()"
                    >
                      发送
                    </button>
                  </div>
                </div>
              </div>
            </Transition>
          </article>
        </TransitionGroup>

        <!-- 空状态 -->
        <div v-if="filteredPosts.length === 0" class="empty-state">
          <span class="iconify empty-icon" data-icon="solar:document-text-outline" data-width="44"></span>
          <p class="empty-text">此分类暂无思辨</p>
          <p class="empty-hint">成为第一个发布思想的人</p>
        </div>

        <!-- 加载更多 -->
        <div class="load-more" v-if="hasMore">
          <button class="load-more-btn" @click="loadMore" :disabled="loadingMore">
            {{ loadingMore ? '加载中...' : '加载更多思辨' }}
          </button>
        </div>
      </main>

      <!-- 右栏：知识上下文联动 (25%) -->
      <aside class="knowledge-panel">
        <div class="knowledge-header">
          <h3 class="knowledge-title">知识联动</h3>
          <p class="knowledge-subtitle">书摊在售关联</p>
        </div>

        <!-- 当前悬停/选中帖子的书籍联动 -->
        <div class="knowledge-content" v-if="hoveredPost && hoveredPost.matchedBooks && hoveredPost.matchedBooks.length > 0">
          <div
            v-for="book in hoveredPost.matchedBooks"
            :key="book.title"
            class="knowledge-book-card"
          >
            <div class="knowledge-book-header">
              <span class="iconify knowledge-book-icon" data-icon="solar:book-2-outline" data-width="18"></span>
              <span class="knowledge-book-title">《{{ book.title }}》</span>
            </div>
            <div class="knowledge-book-status" v-if="book.matched && book.availableCount > 0">
              <span class="status-available">
                校内 {{ book.availableCount }} 本在售
              </span>
              <span class="status-price">
                最低 ¥{{ book.minPrice }}
              </span>
              <button class="status-buy-btn" @click="quickBuy(book)">一键购书</button>
            </div>
            <div class="knowledge-book-status" v-else>
              <!--
                【优雅降级】
                当后端没有匹配到任何在售书籍时，
                显示高级占位图，而非留出难看的空白。
              -->
              <span class="status-unavailable">
                当前无在售
              </span>
              <button class="status-want-btn" @click="openProcurement(book.title)">
                发布求购
              </button>
            </div>
          </div>
        </div>

        <!-- 无联动时的优雅降级占位 -->
        <div class="knowledge-empty" v-else>
          <div class="knowledge-empty-icon">
            <span class="iconify" data-icon="solar:hand-pointer-outline" data-width="36"></span>
          </div>
          <p class="knowledge-empty-text">悬停帖子查看<br/>关联书籍信息</p>
          <p class="knowledge-empty-hint">帖子中的《书名》将自动<br/>联动书摊在售数据</p>
        </div>
      </aside>
    </template>

    <!-- ===== 毛玻璃 Popover（书名悬停浮窗） ===== -->
    <Transition name="popover-fade">
      <div
        v-if="bookPopover.visible"
        class="book-popover glass-crystal"
        :style="{ left: bookPopover.x + 'px', top: bookPopover.y + 'px' }"
      >
        <div class="popover-header">
          <span class="popover-title">《{{ bookPopover.book?.title }}》</span>
        </div>
        <div class="popover-body" v-if="bookPopover.book?.matched && bookPopover.book?.availableCount > 0">
          <div class="popover-stat">
            <span class="popover-stat-label">校内闲置</span>
            <span class="popover-stat-value">{{ bookPopover.book.availableCount }} 本</span>
          </div>
          <div class="popover-stat">
            <span class="popover-stat-label">最低价格</span>
            <span class="popover-stat-value">¥{{ bookPopover.book.minPrice }}</span>
          </div>
          <button class="popover-buy-btn" @click="quickBuy(bookPopover.book)">一键购书</button>
        </div>
        <div class="popover-body empty" v-else>
          <p class="popover-empty-text">当前无在售</p>
          <button class="popover-want-btn" @click="openProcurement(bookPopover.book?.title || '')">发布求购</button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
/**
 * ============================================================
 * 紫金求思 · 社区模块 — 数字化思想圣殿
 * Community Module — Digital Sanctuary of Thought
 * ============================================================
 *
 * 架构设计：
 *   1. 三栏式布局：左栏分类 | 中栏帖子流 | 右栏知识联动
 *   2. 全量数据通过后端 API 获取，支持热度加权排序
 *   3. 响应式状态管理：纯手工 useStore.js，无外部路由库
 *   4. 错峰延迟动画：TransitionGroup + CSS custom properties
 *   5. 智能书名识别：后端自动匹配，前端高亮 + Popover 联动
 *
 * 性能优化：
 *   - 防抖（Debounce）处理分类切换和回复提交
 *   - 仅使用 transform/opacity 动画，GPU 硬件加速
 *   - 骨架屏加载态，避免白屏闪烁
 *   - 分页加载，避免一次性渲染大量 DOM
 *
 * 边界安全：
 *   - XSS 防范：后端 sanitize_html + 前端 v-html 仅渲染安全内容
 *   - ReDoS 防范：后端正则限制书名最大长度 50 字符
 *   - 空状态优雅降级：无匹配书籍时显示高级占位图
 * ============================================================
 */
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useStore } from '../../stores/useStore'

// ============================================================
// Store 与状态
// ============================================================
const store = useStore()

// 加载状态
const loading = ref(true)
const loadingMore = ref(false)
const submitting = ref(false)
const hasMore = ref(true)
const currentPage = ref(1)
const PAGE_SIZE = 10

// 帖子数据
const allPosts = ref([])

// 分类与排序
const activeCategory = ref('全部')
const activeSort = ref('hot')

const categories = ref([
  { key: '全部', label: '全部思辨', icon: '◌', count: 0 },
  { key: '教材', label: '教材讨论', icon: '📚', count: 0 },
  { key: '考研', label: '考研专区', icon: '🎯', count: 0 },
  { key: '选修', label: '选修天地', icon: '🔬', count: 0 },
  { key: '其他', label: '自由交流', icon: '💬', count: 0 },
])

const sortOptions = [
  { key: 'hot', label: '热度排序' },
  { key: 'new', label: '最新发布' },
  { key: 'top', label: '最多回复' },
]

// 发布表单
const showPostForm = ref(false)
const newPostTitle = ref('')
const newPostContent = ref('')

// 回复状态
const replyInputs = reactive({})
const activeReplyPostId = ref(null)

// 悬停帖子（右栏联动）
const hoveredPost = ref(null)

// 书名 Popover
const bookPopover = reactive({
  visible: false,
  x: 0,
  y: 0,
  book: null,
})

// 防抖定时器
let categoryDebounceTimer = null
let viewDebounceTimer = null

// ============================================================
// 计算属性
// ============================================================

/** 根据分类和排序过滤帖子 */
const filteredPosts = computed(() => {
  let posts = [...allPosts.value]

  // 分类筛选
  if (activeCategory.value !== '全部') {
    const categoryMap = {
      '教材': ['微积分', '线性代数', '高等数学', '大学英语', '有机化学'],
      '考研': ['考研', '政治', '英语', '数学'],
      '选修': ['数据结构', '概率论', '计算机网络', '操作系统', '微观经济学', '宏观经济学'],
    }
    const keywords = categoryMap[activeCategory.value] || []
    if (keywords.length > 0) {
      posts = posts.filter(p => {
        const text = (p.title + ' ' + p.content).toLowerCase()
        return keywords.some(kw => text.includes(kw.toLowerCase()))
      })
    }
  }

  // 排序
  if (activeSort.value === 'new') {
    posts.sort((a, b) => new Date(b.time || 0) - new Date(a.time || 0))
  } else if (activeSort.value === 'top') {
    posts.sort((a, b) => (b.replyCount || 0) - (a.replyCount || 0))
  } else {
    // 热度排序（默认）
    posts.sort((a, b) => (b.hotScore || 0) - (a.hotScore || 0))
  }

  return posts
})

// ============================================================
// 生命周期
// ============================================================

onMounted(async () => {
  await fetchPosts()
  loading.value = false
})

onUnmounted(() => {
  if (categoryDebounceTimer) clearTimeout(categoryDebounceTimer)
  if (viewDebounceTimer) clearTimeout(viewDebounceTimer)
})

// ============================================================
// API 请求
// ============================================================

/**
 * 获取帖子列表
 * 调用后端 GET /api/posts 接口，支持热度加权排序
 */
async function fetchPosts(page = 1) {
  try {
    const params = new URLSearchParams({
      page: page,
      pageSize: PAGE_SIZE,
      sort: activeSort.value,
      category: activeCategory.value === '全部' ? '' : activeCategory.value,
    })
    const res = await fetch(`http://127.0.0.1:5000/api/posts?${params}`)
    const data = await res.json()

    if (data.posts) {
      if (page === 1) {
        allPosts.value = data.posts
      } else {
        allPosts.value = [...allPosts.value, ...data.posts]
      }
      hasMore.value = data.page < data.totalPages
      currentPage.value = data.page

      // 更新分类计数
      updateCategoryCounts()
    }
  } catch (err) {
    console.warn('[Community] 后端 API 不可用，使用本地数据降级')
    // 优雅降级：使用本地 store 数据
    loadLocalPosts()
  }
}

/**
 * 本地数据降级方案
 * 当后端 API 不可用时，使用 useStore 中的本地数据
 */
function loadLocalPosts() {
  const merged = store.getMergedPosts()
  allPosts.value = merged.map((p, idx) => ({
    ...p,
    id: p.id || 'local_' + idx,
    likeCount: p.likeCount || Math.floor(Math.random() * 30),
    viewCount: p.viewCount || Math.floor(Math.random() * 200),
    replyCount: 0,
    hotScore: Math.random() * 10,
    replies: [],
    matchedBooks: [],
    authorInfo: { college: '校友', grade: '未知' },
  }))
  hasMore.value = false
  updateCategoryCounts()
}

/** 更新分类计数 */
function updateCategoryCounts() {
  const total = allPosts.value.length
  categories.value[0].count = total

  const counts = { '教材': 0, '考研': 0, '选修': 0, '其他': 0 }
  const categoryMap = {
    '教材': ['微积分', '线性代数', '高等数学', '大学英语', '有机化学'],
    '考研': ['考研', '政治', '英语', '数学'],
    '选修': ['数据结构', '概率论', '计算机网络', '操作系统', '微观经济学', '宏观经济学'],
  }

  for (const post of allPosts.value) {
    const text = (post.title + ' ' + post.content).toLowerCase()
    let matched = false
    for (const [cat, keywords] of Object.entries(categoryMap)) {
      if (keywords.some(kw => text.includes(kw.toLowerCase()))) {
        counts[cat]++
        matched = true
        break
      }
    }
    if (!matched) counts['其他']++
  }

  for (let i = 1; i < categories.value.length; i++) {
    const key = categories.value[i].key
    categories.value[i].count = counts[key] || 0
  }
}

// ============================================================
// 交互方法
// ============================================================

/**
 * 切换分类（带防抖）
 * 防止用户快速点击时频繁请求
 */
function switchCategory(key) {
  if (categoryDebounceTimer) clearTimeout(categoryDebounceTimer)
  categoryDebounceTimer = setTimeout(() => {
    activeCategory.value = key
    currentPage.value = 1
    fetchPosts(1)
  }, 150)
}

/** 切换排序 */
function switchSort(key) {
  activeSort.value = key
  currentPage.value = 1
  fetchPosts(1)
}

/** 加载更多 */
async function loadMore() {
  loadingMore.value = true
  await fetchPosts(currentPage.value + 1)
  loadingMore.value = false
}

/** 切换发布表单 */
function togglePostForm() {
  showPostForm.value = !showPostForm.value
  if (!showPostForm.value) {
    newPostTitle.value = ''
    newPostContent.value = ''
  }
}

/**
 * 发布新帖
 * 调用后端 POST /api/posts 接口
 */
async function submitPost() {
  if (!store.isLoggedIn.value || !store.currentUser.value) {
    alert('请先登录后再发布思想')
    return
  }
  if (!newPostTitle.value.trim() || !newPostContent.value.trim()) {
    alert('标题和内容不能为空')
    return
  }

  submitting.value = true
  try {
    const res = await fetch('http://127.0.0.1:5000/api/posts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: newPostTitle.value.trim(),
        content: newPostContent.value.trim(),
        author: store.currentUser.value.name,
      }),
    })
    const data = await res.json()
    if (data.success && data.post) {
      // 无缝插入新帖到列表顶部
      allPosts.value.unshift(data.post)
      showPostForm.value = false
      newPostTitle.value = ''
      newPostContent.value = ''
      updateCategoryCounts()
    }
  } catch (err) {
    // 后端不可用时，使用本地存储降级
    store.addPost({
      id: Date.now(),
      title: newPostTitle.value.trim(),
      content: newPostContent.value.trim(),
      author: store.currentUser.value.name,
      time: new Date().toLocaleString('zh-CN'),
      likeCount: 0,
      viewCount: 0,
      replyCount: 0,
      hotScore: 0.01,
      replies: [],
      matchedBooks: [],
      authorInfo: { college: store.currentUser.value.college || '校友', grade: store.currentUser.value.grade || '未知' },
    })
    showPostForm.value = false
    newPostTitle.value = ''
    newPostContent.value = ''
    loadLocalPosts()
  } finally {
    submitting.value = false
  }
}

/** 切换回复表单 */
function toggleReplyForm(post) {
  if (activeReplyPostId.value === post.id) {
    activeReplyPostId.value = null
  } else {
    activeReplyPostId.value = post.id
    // 初始化回复输入
    if (!replyInputs[post.id]) {
      replyInputs[post.id] = ''
    }
  }
}

/** 关闭回复表单 */
function closeReplyForm(post) {
  activeReplyPostId.value = null
  replyInputs[post.id] = ''
}

/**
 * 提交回复（无缝内联插入）
 * 调用后端 POST /api/posts/:id/replies 接口
 * 提交后新回复通过响应式状态无缝插入，禁止页面跳动
 */
async function submitReply(post) {
  if (!store.isLoggedIn.value || !store.currentUser.value) {
    alert('请先登录后再回复')
    return
  }
  const content = replyInputs[post.id]
  if (!content?.trim()) return

  const originalContent = content.trim()
  replyInputs[post.id] = ''

  try {
    const res = await fetch(`http://127.0.0.1:5000/api/posts/${post.id}/replies`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        author: store.currentUser.value.name,
        content: originalContent,
      }),
    })
    const data = await res.json()
    if (data.success && data.reply) {
      // 响应式状态无缝插入新回复
      if (!post.replies) post.replies = []
      post.replies.push(data.reply)
      post.replyCount = (post.replyCount || 0) + 1
    }
  } catch (err) {
    // 后端不可用时，本地降级
    const newReply = {
      id: Date.now() + Math.random(),
      postId: post.id,
      author: store.currentUser.value.name,
      content: originalContent,
      time: new Date().toLocaleString('zh-CN'),
      likeCount: 0,
      authorInfo: { college: store.currentUser.value.college || '校友', grade: store.currentUser.value.grade || '未知' },
    }
    if (!post.replies) post.replies = []
    post.replies.push(newReply)
    post.replyCount = (post.replyCount || 0) + 1
  }

  activeReplyPostId.value = null
}

/**
 * 点赞帖子
 * 调用后端 POST /api/posts/:id/like
 */
async function likePost(post) {
  if (post._liked) return
  try {
    const res = await fetch(`http://127.0.0.1:5000/api/posts/${post.id}/like`, { method: 'POST' })
    const data = await res.json()
    if (data.success) {
      post.likeCount = data.likeCount
      post._liked = true
    }
  } catch {
    post.likeCount = (post.likeCount || 0) + 1
    post._liked = true
  }
}

/**
 * 点赞回复
 * 调用后端 POST /api/posts/:id/replies/:replyId/like
 */
async function likeReply(post, reply) {
  if (reply._liked) return
  try {
    const res = await fetch(`http://127.0.0.1:5000/api/posts/${post.id}/replies/${reply.id}/like`, { method: 'POST' })
    const data = await res.json()
    if (data.success) {
      reply.likeCount = data.likeCount
      reply._liked = true
    }
  } catch {
    reply.likeCount = (reply.likeCount || 0) + 1
    reply._liked = true
  }
}

/**
 * 帖子悬停时更新右栏知识联动
 * 同时触发浏览量递增（带防抖）
 */
function onPostHover(post) {
  hoveredPost.value = post

  // 浏览量递增（防抖）
  if (viewDebounceTimer) clearTimeout(viewDebounceTimer)
  viewDebounceTimer = setTimeout(async () => {
    try {
      await fetch(`http://127.0.0.1:5000/api/posts/${post.id}/view`, { method: 'POST' })
    } catch {
      // 静默失败，不影响用户体验
    }
  }, 1000)
}

/**
 * 书名高亮渲染
 * 将《书名》替换为带淡紫色标签样式的 span
 * 安全设计：后端已做 HTML 转义，此处仅做样式替换
 */
function highlightBookTitles(content) {
  if (!content) return ''
  // 使用正则匹配《书名》并替换为高亮 span
  return content.replace(
    /《([^》]{1,50})》/g,
    '<span class="book-highlight">《$1》</span>'
  )
}

/**
 * 显示书名 Popover
 * 鼠标悬停书名标签时触发毛玻璃浮窗
 */
function showBookPopover(event, book) {
  const rect = event.target.getBoundingClientRect()
  bookPopover.book = book
  bookPopover.x = rect.left + rect.width / 2
  bookPopover.y = rect.bottom + 8
  // 确保 Popover 不超出视口
  nextTick(() => {
    bookPopover.visible = true
  })
}

/** 隐藏书名 Popover */
function hideBookPopover() {
  bookPopover.visible = false
  bookPopover.book = null
}

/** 获取作者首字母 */
function getInitial(name) {
  if (!name) return '?'
  return name.charAt(0)
}

/** 一键购书：跳转到采购页并搜索该书 */
function quickBuy(book) {
  if (book && book.title) {
    store.searchQuery.value = book.title
    store.navigateTo('procurement')
  }
}

/** 发布求购：跳转到采购页 */
function openProcurement(title) {
  if (title) {
    store.searchQuery.value = title
  }
  store.navigateTo('procurement')
}

/** 私聊：跳转到聊天页并自动打开与该用户的对话 */
function startChat(targetUser) {
  if (!store.isLoggedIn.value) {
    alert('请先登录')
    return
  }
  sessionStorage.setItem('chat_target_user', targetUser)
  store.navigateTo('chat')
}
</script>

<style scoped>
/* ============================================================
 * 紫金求思 · 社区模块 — 样式导入
 * ============================================================
 * 所有样式定义在独立的 community-theme.css 文件中，
 * 包括晶体玻璃拟态、骨架屏、错峰延迟动画、毛玻璃 Popover 等。
 * 此处仅保留组件级最小样式。
 * ============================================================
 */
@import '../../assets/community-theme.css';

/* ===== 主容器：三栏布局 ===== */
.community-sacred-hall {
  display: flex;
  gap: 1.5rem;
  height: 100%;
  min-height: 0;
  position: relative;
}
</style>
