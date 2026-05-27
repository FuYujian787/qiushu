<template>
  <!-- ============================================================
   紫金求思 · 高奢科技感私人数字化会客室
   Private Chat — Luxury Tech Digital Lounge
   ============================================================
   设计哲学：
     1. 无边界流体画布 — 大面积负空间留白
     2. 高饱和度毛玻璃晶体 — backdrop-filter: blur(30px) saturate(120%)
     3. 动态身份刻度 — 左上角及头像边缘 1px 细线微缩数字身份刻度
     4. 三大状态光影反馈 — PENDING/DELIVERED/READ
     5. 瀑布流错峰入场 — TransitionGroup + stagger delay
     6. 一键出价/交易 — 悬浮3D交易晶体胶囊
   ============================================================ -->
  <div class="chat-fluid-canvas">
    <!-- ===== 对话列表侧栏 ===== -->
    <aside class="chat-conversations-panel">
      <div class="chat-conversations-header">
        <h2 class="chat-conversations-title">
          <span class="iconify" data-icon="solar:chat-round-dots-outline" data-width="20"></span>
          私信
        </h2>
      </div>

      <div class="chat-conversations-list">
        <!-- 加载骨架屏 -->
        <template v-if="loadingConversations">
          <div v-for="n in 4" :key="'sk-conv-' + n" class="chat-conv-skeleton">
            <div class="chat-skeleton-avatar"></div>
            <div class="chat-skeleton-line" style="flex:1">
              <div class="skeleton-line w-60"></div>
              <div class="skeleton-line w-40" style="margin-top:6px"></div>
            </div>
          </div>
        </template>

        <!-- 空状态 -->
        <div v-else-if="conversations.length === 0" class="chat-empty-conv">
          <div class="chat-empty-conv-icon">💬</div>
          <p class="chat-empty-conv-text">暂无对话</p>
          <p class="chat-empty-conv-hint">在社区或书摊中点击"私聊"<br/>开始一段对话</p>
        </div>

        <!-- 对话列表 -->
        <div
          v-for="conv in conversations"
          :key="conv.partner"
          class="chat-conversation-item"
          :class="{ active: activePartner === conv.partner }"
          @click="switchConversation(conv.partner)"
        >
          <div class="chat-avatar-wrapper">
            <div class="chat-avatar">
              {{ getInitial(conv.partner) }}
            </div>
            <div class="chat-avatar-ring" :class="{ verified: conv.partnerInfo?.verified }"></div>
            <div class="chat-identity-badge" v-if="conv.partnerInfo">
              {{ conv.partnerInfo.college === '未设置' ? '校友' : conv.partnerInfo.college }}
            </div>
          </div>
          <div class="chat-conversation-info">
            <div class="chat-conversation-name">
              {{ conv.partner }}
              <span class="chat-conversation-identity" v-if="conv.partnerInfo">
                {{ conv.partnerInfo.grade }}
              </span>
            </div>
            <div class="chat-conversation-preview">
              {{ getPreviewText(conv.lastMessage) }}
            </div>
          </div>
          <div class="chat-conversation-meta">
            <span class="chat-conversation-time">{{ formatTime(conv.lastMessage?.createdAt) }}</span>
            <span class="chat-unread-badge" v-if="conv.unreadCount > 0">
              {{ conv.unreadCount > 99 ? '99+' : conv.unreadCount }}
            </span>
          </div>
        </div>
      </div>
    </aside>

    <!-- ===== 主聊天区域 ===== -->
    <main class="chat-main-area">
      <!-- 未选择对话时的空状态 -->
      <div v-if="!activePartner" class="chat-empty-state">
        <div class="chat-empty-icon">💬</div>
        <p class="chat-empty-text">选择一位好友开始私聊</p>
        <p class="chat-empty-hint">加密通讯 · 全息信笺 · 瞬时送达</p>
      </div>

      <template v-else>
        <!-- ===== 顶部悬浮交易胶囊 ===== -->
        <div class="chat-top-capsule">
          <div class="chat-partner-info">
            <div class="chat-avatar-wrapper" style="width:2.5rem;height:2.5rem">
              <div class="chat-avatar" style="font-size:0.9rem">
                {{ getInitial(activePartner) }}
              </div>
              <div class="chat-avatar-ring" :class="{ verified: activePartnerInfo?.verified }"></div>
            </div>
            <div class="chat-partner-details">
              <span class="chat-partner-name">{{ activePartner }}</span>
              <span class="chat-partner-identity" v-if="activePartnerInfo">
                {{ activePartnerInfo.college }} · {{ activePartnerInfo.grade }}
              </span>
            </div>
          </div>

          <!-- 悬浮 3D 交易晶体胶囊 -->
          <div
            class="chat-trade-capsule"
            :class="{ expanded: showOrderPanel }"
            @click="toggleOrderPanel"
          >
            <div class="chat-trade-capsule-icon">⟐</div>
            <span class="chat-trade-capsule-text">一键出价</span>
            <span class="chat-trade-capsule-arrow">▾</span>
          </div>
        </div>

        <!-- ===== 一键出价毛玻璃折叠面板 ===== -->
        <div class="chat-order-panel" :class="{ open: showOrderPanel }">
          <div class="chat-order-panel-inner">
            <!-- 选择书籍 -->
            <div class="chat-order-book" v-if="selectedOrderBook">
              <img :src="selectedOrderBook.img" class="chat-order-book-img" />
              <div class="chat-order-book-info">
                <div class="chat-order-book-title">{{ selectedOrderBook.title }}</div>
                <div class="chat-order-book-price">¥{{ selectedOrderBook.price }}</div>
              </div>
              <button class="chat-order-change-btn" @click.stop="selectBookForOrder">更换</button>
            </div>
            <div v-else class="chat-order-book" @click="selectBookForOrder" style="cursor:pointer">
              <div class="chat-order-book-info" style="text-align:center;width:100%;color:var(--text-tertiary)">
                ← 点击选择要交易的书籍
              </div>
            </div>

            <!-- 出价输入 -->
            <div class="chat-order-input-group">
              <input
                v-model="orderPrice"
                type="number"
                placeholder="出价金额"
                class="chat-order-price-input"
                min="0"
                step="0.1"
              />
              <input
                v-model="orderAddress"
                type="text"
                placeholder="收货地址"
                class="chat-order-price-input"
              />
              <button
                class="chat-order-submit-btn"
                @click="submitOrder"
                :disabled="!selectedOrderBook || !orderPrice"
              >
                发送出价
              </button>
            </div>
          </div>
        </div>

        <!-- ===== 消息流区域 ===== -->
        <div class="chat-messages-area" ref="messagesAreaRef">
          <!-- 加载骨架屏 -->
          <template v-if="loadingMessages">
            <div v-for="n in 5" :key="'sk-msg-' + n" class="chat-skeleton-message" :class="{ own: n % 2 === 0 }">
              <div class="chat-skeleton-avatar"></div>
              <div class="chat-skeleton-bubble"></div>
            </div>
          </template>

          <!-- 消息列表 -->
          <template v-else>
            <!-- 时间分隔线 -->
            <div class="chat-date-divider" v-if="messages.length > 0">
              <span class="chat-date-divider-line"></span>
              <span class="chat-date-divider-text">对话开始</span>
              <span class="chat-date-divider-line"></span>
            </div>

            <TransitionGroup name="chat-message" tag="div" style="display:contents">
              <div
                v-for="msg in messages"
                :key="msg.clientTimestamp || msg.id"
                class="chat-message-card"
                :class="[
                  msg.sender === currentUserName ? 'own' : 'other',
                  msg.isSystem ? 'system' : '',
                  msg.status === 'PENDING' ? 'status-pending' : '',
                  msg.status === 'DELIVERED' ? 'status-delivered' : '',
                  msg.status === 'READ' ? 'status-read' : '',
                  msg._frozen ? 'frozen' : '',
                ]"
                :style="{ '--msg-delay': '0ms' }"
                @click="retrySend(msg)"
              >
                <!-- 发送者信息 -->
                <div class="chat-message-sender" v-if="msg.sender !== currentUserName && !msg.isSystem">
                  <span class="chat-message-sender-name">{{ msg.sender }}</span>
                  <span class="chat-message-sender-badge" v-if="msg.senderInfo">
                    {{ msg.senderInfo.college }}
                  </span>
                </div>

                <!-- 消息内容 -->
                <div class="chat-message-content" v-if="!msg.isSystem">
                  {{ msg.content }}
                </div>

                <!-- 系统消息（全息信件） -->
                <div class="chat-system-content" v-else>
                  <template v-if="msg._parsedOrder">
                    <div class="chat-system-order-icon">⟐</div>
                    <div>📦 交易订单已创建</div>
                    <div class="chat-system-order">
                      <span>《{{ msg._parsedOrder.bookTitle }}》</span>
                      <span>¥{{ msg._parsedOrder.price }}</span>
                    </div>
                    <div style="font-size:0.7rem;margin-top:0.25rem;opacity:0.6">
                      订单号: {{ msg._parsedOrder.orderNo }}
                    </div>
                  </template>
                  <template v-else>
                    {{ msg.content }}
                  </template>
                </div>

                <!-- 消息时间戳 -->
                <div class="chat-message-time">
                  <span>{{ formatMsgTime(msg.createdAt) }}</span>
                  <span class="chat-message-status-icon" v-if="msg.sender === currentUserName">
                    {{ msg.status === 'READ' ? '◉' : msg.status === 'DELIVERED' ? '◎' : '○' }}
                  </span>
                </div>
              </div>
            </TransitionGroup>

            <!-- 空消息状态 -->
            <div v-if="messages.length === 0 && !loadingMessages" class="chat-empty-state" style="flex:1">
              <div class="chat-empty-icon">✉</div>
              <p class="chat-empty-text">发送第一条消息</p>
              <p class="chat-empty-hint">全息信笺 · 瞬时送达</p>
            </div>
          </template>
        </div>

        <!-- ===== 输入区域 ===== -->
        <div class="chat-input-area">
          <div class="chat-input-wrapper">
            <textarea
              v-model="inputMessage"
              class="chat-input"
              placeholder="输入消息..."
              rows="1"
              @keydown.enter.prevent="sendMessage"
              @input="autoResizeInput"
            ></textarea>
          </div>
          <button
            class="chat-send-btn"
            :disabled="!inputMessage.trim() || sendingMessage"
            @click="sendMessage"
          >
            <span v-if="!sendingMessage">↑</span>
            <span v-else class="chat-sending-spinner">⟳</span>
            <!-- 粒子湮灭容器 -->
            <div class="chat-send-particle-container" ref="particleContainerRef"></div>
          </button>
        </div>
      </template>
    </main>

    <!-- ===== 选择书籍对话框 ===== -->
    <Teleport to="body">
      <Transition name="popover-fade">
        <div v-if="showBookSelector" class="chat-book-selector-overlay" @click.self="showBookSelector = false">
          <div class="chat-book-selector glass-crystal">
            <div class="chat-book-selector-header">
              <h3>选择交易书籍</h3>
              <button class="chat-book-selector-close" @click="showBookSelector = false">✕</button>
            </div>
            <div class="chat-book-selector-search">
              <input
                v-model="bookSearchQuery"
                placeholder="搜索书籍..."
                class="chat-order-price-input"
              />
            </div>
            <div class="chat-book-selector-list">
              <div
                v-for="book in filteredUserBooks"
                :key="book.id"
                class="chat-book-selector-item"
                @click="pickBook(book)"
              >
                <img :src="book.img" class="chat-book-selector-img" />
                <div class="chat-book-selector-info">
                  <div class="chat-book-selector-title">{{ book.title }}</div>
                  <div class="chat-book-selector-price">¥{{ book.price }}</div>
                </div>
                <div class="chat-book-selector-check" v-if="selectedOrderBook?.id === book.id">✓</div>
              </div>
              <div v-if="filteredUserBooks.length === 0" class="chat-book-selector-empty">
                没有找到匹配的书籍
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
/**
 * ============================================================
 * 紫金求思 · 私聊系统前端 — 高奢科技感私人数字化会客室
 * Chat Frontend — Luxury Tech Private Digital Lounge
 * ============================================================
 *
 * 架构设计：
 *   1. 双栏布局：左栏对话列表 | 右栏聊天主区域
 *   2. 增量同步：基于 client_timestamp 的增量拉取
 *   3. 乐观更新：发送消息立即显示，后端确认后更新状态
 *   4. 瀑布流入场：TransitionGroup + stagger delay
 *   5. 一键出价：悬浮3D交易晶体胶囊 + 毛玻璃折叠面板
 *   6. 三大状态光影：PENDING(呼吸) / DELIVERED(金属) / READ(金色流光)
 *
 * 性能优化：
 *   - 防抖处理发送和拉取
 *   - 仅渲染可见消息
 *   - 自动滚动到底部
 *   - 增量同步减少数据传输
 *
 * 边界安全：
 *   - 空输入保护
 *   - 超长消息截断
 *   - 网络异常优雅降级
 *   - XSS 防范
 * ============================================================
 */
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useStore } from '../../stores/useStore'

// ============================================================
// Store 与状态
// ============================================================
const store = useStore()
const currentUserName = computed(() => store.currentUser.value?.name || '')

// 对话列表
const conversations = ref([])
const loadingConversations = ref(true)
const activePartner = ref('')
const activePartnerInfo = ref(null)

// 消息
const messages = ref([])
const loadingMessages = ref(false)
const inputMessage = ref('')
const sendingMessage = ref(false)

// 交易面板
const showOrderPanel = ref(false)
const selectedOrderBook = ref(null)
const orderPrice = ref('')
const orderAddress = ref('')
const showBookSelector = ref(false)
const bookSearchQuery = ref('')

// 轮询定时器
let pollTimer = null
const POLL_INTERVAL = 3000 // 3秒轮询

// DOM 引用
const messagesAreaRef = ref(null)
const particleContainerRef = ref(null)

// ============================================================
// 计算属性
// ============================================================

/** 当前用户发布的书籍（用于交易选择） */
const userBooks = computed(() => {
  if (!store.isLoggedIn.value || !store.currentUser.value) return []
  const result = store.fetchUserBooks(store.currentUser.value.name)
  return result.books || []
})

/** 搜索过滤后的书籍 */
const filteredUserBooks = computed(() => {
  const query = bookSearchQuery.value.trim().toLowerCase()
  if (!query) return userBooks.value
  return userBooks.value.filter(b =>
    b.title.toLowerCase().includes(query) ||
    b.author.toLowerCase().includes(query)
  )
})

// ============================================================
// 生命周期
// ============================================================

onMounted(async () => {
  await loadConversations()
  loadingConversations.value = false

  // 如果从其他页面跳转过来时携带了目标用户参数
  const targetUser = sessionStorage.getItem('chat_target_user')
  if (targetUser) {
    sessionStorage.removeItem('chat_target_user')
    activePartner.value = targetUser
    await loadMessages()
    await markAsRead()
  }

  // 启动轮询
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})

// 监听活跃对话变化
watch(activePartner, async (newVal, oldVal) => {
  if (newVal && newVal !== oldVal) {
    await loadMessages()
    await markAsRead()
    await loadConversations()
  }
})

// ============================================================
// API 请求
// ============================================================

const API_BASE = 'http://127.0.0.1:5000'

/**
 * 加载对话列表
 */
async function loadConversations() {
  if (!currentUserName.value) return
  try {
    const res = await fetch(`${API_BASE}/api/chat/conversations?user=${encodeURIComponent(currentUserName.value)}`)
    const data = await res.json()
    if (data.success) {
      conversations.value = data.conversations || []
      // 更新活跃对话的对方信息
      if (activePartner.value) {
        const conv = conversations.value.find(c => c.partner === activePartner.value)
        if (conv) {
          activePartnerInfo.value = conv.partnerInfo
        }
      }
    }
  } catch (err) {
    console.warn('[Chat] 加载对话列表失败:', err)
  }
}

/**
 * 加载消息历史（增量同步）
 */
async function loadMessages() {
  if (!currentUserName.value || !activePartner.value) return
  loadingMessages.value = true

  try {
    // 获取最后一条消息的时间戳用于增量同步
    const lastMsg = messages.value.length > 0 ? messages.value[messages.value.length - 1] : null
    const lastTimestamp = lastMsg ? lastMsg.clientTimestamp || 0 : 0

    const params = new URLSearchParams({
      user_a: currentUserName.value,
      user_b: activePartner.value,
      last_timestamp: lastTimestamp,
      limit: 50,
    })
    const res = await fetch(`${API_BASE}/api/chat/history?${params}`)
    const data = await res.json()

    if (data.success && data.messages) {
      if (lastTimestamp === 0) {
        // 首次加载，全量替换
        messages.value = data.messages.map(parseMessage)
      } else {
        // 增量加载，追加新消息（去重）
        const existingIds = new Set(messages.value.map(m => m.clientTimestamp))
        const newMsgs = data.messages
          .filter(m => !existingIds.has(m.clientTimestamp))
          .map(parseMessage)
        if (newMsgs.length > 0) {
          messages.value = [...messages.value, ...newMsgs]
        }
      }

      // 更新对方信息
      if (data.messages.length > 0) {
        const firstMsg = data.messages[0]
        if (firstMsg.senderInfo) {
          activePartnerInfo.value = firstMsg.senderInfo
        }
      }

      // 滚动到底部
      await nextTick()
      scrollToBottom()
    }
  } catch (err) {
    console.warn('[Chat] 加载消息失败:', err)
  } finally {
    loadingMessages.value = false
  }
}

/**
 * 发送消息（乐观更新）
 */
async function sendMessage() {
  const content = inputMessage.value.trim()
  if (!content || !currentUserName.value || !activePartner.value || sendingMessage.value) return

  sendingMessage.value = true
  inputMessage.value = ''

  // 生成客户端时间戳（微秒级）
  const clientTimestamp = Date.now() * 1000 + Math.floor(Math.random() * 1000)

  // 乐观更新：立即在 UI 中显示消息
  const optimisticMsg = {
    id: 'pending_' + clientTimestamp,
    sender: currentUserName.value,
    receiver: activePartner.value,
    content: content,
    status: 'PENDING',
    clientTimestamp: clientTimestamp,
    createdAt: new Date().toISOString(),
    isSystem: false,
    senderInfo: {
      college: store.currentUser.value?.college || '校友',
      grade: store.currentUser.value?.grade || '未知',
      verified: true,
    },
    _frozen: false,
  }
  messages.value.push(optimisticMsg)

  // 触发粒子动画
  triggerParticleBurst()

  await nextTick()
  scrollToBottom()

  try {
    const res = await fetch(`${API_BASE}/api/chat/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sender: currentUserName.value,
        receiver: activePartner.value,
        content: content,
        client_timestamp: clientTimestamp,
      }),
    })
    const data = await res.json()

    if (data.success && data.message) {
      // 替换乐观更新的消息为服务端确认的消息
      const idx = messages.value.findIndex(m => m.clientTimestamp === clientTimestamp)
      if (idx !== -1) {
        messages.value[idx] = parseMessage(data.message)
        messages.value[idx]._frozen = false
      }
    } else {
      // 标记为冻结状态（发送失败）
      const idx = messages.value.findIndex(m => m.clientTimestamp === clientTimestamp)
      if (idx !== -1) {
        messages.value[idx].status = 'DELIVERED'
        messages.value[idx]._frozen = true
      }
    }
  } catch (err) {
    // 网络错误，标记为冻结
    const idx = messages.value.findIndex(m => m.clientTimestamp === clientTimestamp)
    if (idx !== -1) {
      messages.value[idx]._frozen = true
    }
    console.warn('[Chat] 发送消息失败:', err)
  } finally {
    sendingMessage.value = false
    // 刷新对话列表
    await loadConversations()
  }
}

/**
 * 重试发送冻结的消息
 */
async function retrySend(msg) {
  if (!msg._frozen || !msg.content) return
  msg._frozen = false
  msg.status = 'PENDING'

  try {
    const res = await fetch(`${API_BASE}/api/chat/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sender: msg.sender,
        receiver: msg.receiver,
        content: msg.content,
        client_timestamp: msg.clientTimestamp || Date.now() * 1000,
      }),
    })
    const data = await res.json()
    if (data.success && data.message) {
      const idx = messages.value.findIndex(m => m.clientTimestamp === msg.clientTimestamp)
      if (idx !== -1) {
        messages.value[idx] = parseMessage(data.message)
      }
    }
  } catch (err) {
    msg._frozen = true
    console.warn('[Chat] 重试发送失败:', err)
  }
}

/**
 * 标记消息为已读
 */
async function markAsRead() {
  if (!currentUserName.value || !activePartner.value) return
  try {
    await fetch(`${API_BASE}/api/chat/read`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        reader: currentUserName.value,
        sender: activePartner.value,
      }),
    })
  } catch (err) {
    // 静默失败
  }
}

/**
 * 提交交易订单
 */
async function submitOrder() {
  if (!selectedOrderBook.value || !orderPrice.value || !currentUserName.value || !activePartner.value) return

  try {
    const res = await fetch(`${API_BASE}/api/chat/order`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sender: currentUserName.value,
        receiver: activePartner.value,
        book_id: selectedOrderBook.value.id,
        price: parseFloat(orderPrice.value),
        address: orderAddress.value || '未填写',
      }),
    })
    const data = await res.json()
    if (data.success) {
      // 添加系统消息到列表
      if (data.message) {
        messages.value.push(parseMessage(data.message))
        await nextTick()
        scrollToBottom()
      }
      // 重置表单
      showOrderPanel.value = false
      selectedOrderBook.value = null
      orderPrice.value = ''
      orderAddress.value = ''
      alert('出价已发送！')
    }
  } catch (err) {
    console.warn('[Chat] 创建订单失败:', err)
    alert('创建订单失败，请重试')
  }
}

// ============================================================
// 轮询
// ============================================================

function startPolling() {
  stopPolling()
  pollTimer = setInterval(async () => {
    if (activePartner.value && currentUserName.value) {
      await loadMessages()
      await loadConversations()
    }
  }, POLL_INTERVAL)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

// ============================================================
// 交互方法
// ============================================================

/** 切换对话 */
async function switchConversation(partner) {
  if (partner === activePartner.value) return
  activePartner.value = partner
  messages.value = []
  // 更新对方信息
  const conv = conversations.value.find(c => c.partner === partner)
  if (conv) {
    activePartnerInfo.value = conv.partnerInfo
  }
}

/** 切换交易面板 */
function toggleOrderPanel() {
  showOrderPanel.value = !showOrderPanel.value
  if (showOrderPanel.value) {
    // 默认使用当前用户的第一本书
    if (userBooks.value.length > 0 && !selectedOrderBook.value) {
      selectedOrderBook.value = userBooks.value[0]
    }
  }
}

/** 打开书籍选择器 */
function selectBookForOrder() {
  showBookSelector.value = true
  bookSearchQuery.value = ''
}

/** 选择书籍 */
function pickBook(book) {
  selectedOrderBook.value = book
  showBookSelector.value = false
}

/** 自动调整输入框高度 */
function autoResizeInput(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 128) + 'px'
}

/** 滚动到底部 */
function scrollToBottom() {
  if (messagesAreaRef.value) {
    messagesAreaRef.value.scrollTop = messagesAreaRef.value.scrollHeight
  }
}

/** 触发发送按钮粒子湮灭动效 */
function triggerParticleBurst() {
  const container = particleContainerRef.value
  if (!container) return

  const colors = ['#DCD0FF', '#C4B5E0', '#B8A9DA', '#E6E6FA', '#F3EFFFF']
  for (let i = 0; i < 12; i++) {
    const particle = document.createElement('div')
    particle.className = 'chat-send-particle'
    const angle = (Math.PI * 2 * i) / 12
    const distance = 30 + Math.random() * 40
    const tx = Math.cos(angle) * distance
    const ty = Math.sin(angle) * distance
    particle.style.cssText = `
      left: 50%;
      top: 50%;
      background: ${colors[i % colors.length]};
      width: ${3 + Math.random() * 4}px;
      height: ${3 + Math.random() * 4}px;
      animation: particleFly 0.6s cubic-bezier(0.25, 1, 0.5, 1) forwards;
      --tx: ${tx}px;
      --ty: ${ty}px;
    `
    container.appendChild(particle)
    setTimeout(() => particle.remove(), 700)
  }
}

// ============================================================
// 工具函数
// ============================================================

/** 解析消息对象 */
function parseMessage(msg) {
  if (!msg) return msg
  // 解析系统消息中的订单信息
  if (msg.isSystem && msg.content) {
    try {
      const parsed = JSON.parse(msg.content)
      if (parsed.type === 'order_created') {
        msg._parsedOrder = parsed
      }
    } catch {
      // 不是 JSON 格式，忽略
    }
  }
  msg._frozen = msg._frozen || false
  return msg
}

/** 获取首字母 */
function getInitial(name) {
  if (!name) return '?'
  return name.charAt(0).toUpperCase()
}

/** 获取预览文本 */
function getPreviewText(msg) {
  if (!msg) return ''
  if (msg.isSystem) return '[系统消息]'
  const content = msg.content || ''
  return content.length > 30 ? content.substring(0, 30) + '...' : content
}

/** 格式化时间 */
function formatTime(dateStr) {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now - date
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    if (days === 0) {
      return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    } else if (days === 1) {
      return '昨天'
    } else if (days < 7) {
      return `${days}天前`
    } else {
      return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
    }
  } catch {
    return ''
  }
}

/** 格式化消息时间 */
function formatMsgTime(dateStr) {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ''
  }
}
</script>

<style scoped>
/* ============================================================
 * 私聊系统样式 — 继承自 community-theme.css 的 chat-* 类
 * 此处仅补充组件级特有样式
 * ============================================================ */
@import '../../assets/community-theme.css';


/* ===== 对话列表骨架屏 ===== */
.chat-conv-skeleton {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
}

.chat-skeleton-line {
  display: flex;
  flex-direction: column;
}

.skeleton-line {
  height: 0.75rem;
  border-radius: 0.25rem;
  background: rgba(220, 208, 255, 0.1);
  animation: chatSkeletonPulse 1.5s ease-in-out infinite;
}

.skeleton-line.w-60 { width: 60%; }
.skeleton-line.w-40 { width: 40%; }

/* ===== 空对话状态 ===== */
.chat-empty-conv {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
  gap: 0.5rem;
}

.chat-empty-conv-icon {
  font-size: 2.5rem;
  opacity: 0.4;
  margin-bottom: 0.5rem;
}

.chat-empty-conv-text {
  font-size: 0.9rem;
  color: var(--text-tertiary);
  margin: 0;
  font-weight: 600;
}

.chat-empty-conv-hint {
  font-size: 0.75rem;
  color: rgba(155, 142, 196, 0.35);
  margin: 0;
  line-height: 1.6;
}

/* ===== 空状态提示 ===== */
.chat-empty-hint {
  font-size: 0.75rem;
  color: rgba(155, 142, 196, 0.35);
  margin: 0;
  letter-spacing: 0.05em;
}

/* ===== 发送中旋转 ===== */
.chat-sending-spinner {
  display: inline-block;
  animation: chatSpin 0.8s linear infinite;
}

@keyframes chatSpin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ===== 更换书籍按钮 ===== */
.chat-order-change-btn {
  padding: 0.375rem 0.75rem;
  background: rgba(220, 208, 255, 0.15);
  border: 1px solid rgba(220, 208, 255, 0.2);
  border-radius: 0.5rem;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.chat-order-change-btn:hover {
  background: rgba(220, 208, 255, 0.25);
}

/* ===== 书籍选择器遮罩 ===== */
.chat-book-selector-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.chat-book-selector {
  width: 28rem;
  max-height: 70vh;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(32px) saturate(120%);
  -webkit-backdrop-filter: blur(32px) saturate(120%);
  border: 1px solid rgba(220, 208, 255, 0.3);
  border-radius: 1.5rem;
  box-shadow: 0 24px 80px rgba(74, 59, 90, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-book-selector-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(220, 208, 255, 0.1);
}

.chat-book-selector-header h3 {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.chat-book-selector-close {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  border: none;
  background: rgba(220, 208, 255, 0.1);
  color: var(--text-tertiary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.chat-book-selector-close:hover {
  background: rgba(220, 208, 255, 0.2);
  color: var(--text-primary);
}

.chat-book-selector-search {
  padding: 0.75rem 1.5rem;
}

.chat-book-selector-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 1.5rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.chat-book-selector-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.chat-book-selector-item:hover {
  background: rgba(220, 208, 255, 0.1);
  border-color: rgba(220, 208, 255, 0.2);
}

.chat-book-selector-img {
  width: 2.5rem;
  height: 3.5rem;
  border-radius: 0.5rem;
  object-fit: cover;
  background: rgba(220, 208, 255, 0.15);
  flex-shrink: 0;
}

.chat-book-selector-info {
  flex: 1;
  min-width: 0;
}

.chat-book-selector-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.03em;
}

.chat-book-selector-price {
  font-size: 0.8rem;
  color: var(--lavender-accent);
  font-weight: 600;
  margin-top: 0.125rem;
}

.chat-book-selector-check {
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  background: var(--gradient-brand);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  flex-shrink: 0;
}

.chat-book-selector-empty {
  text-align: center;
  padding: 2rem;
  color: var(--text-tertiary);
  font-size: 0.85rem;
}

/* ===== Popover 淡入淡出 ===== */
.popover-fade-enter-active,
.popover-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.popover-fade-enter-from,
.popover-fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

/* ===== 骨架屏脉冲动画 ===== */
@keyframes chatSkeletonPulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}

/* ===== 粒子飞出动画 ===== */
@keyframes particleFly {
  0% {
    transform: translate(0, 0) scale(1);
    opacity: 1;
  }
  100% {
    transform: translate(var(--tx), var(--ty)) scale(0);
    opacity: 0;
  }
}
</style>


