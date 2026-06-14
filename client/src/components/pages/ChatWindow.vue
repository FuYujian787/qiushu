<template>
  <!--
    ============================================================
    紫金求思 · 私聊系统 — 高奢科技感私人数字化会客室
    ChatWindow.vue — 全栈高端化重构版

    设计哲学：
      - 无边界流体画布（Borderless Fluid Canvas）
      - 高饱和度毛玻璃晶体（backdrop-filter: blur(30px) saturate(120%)）
      - 发丝级发光边框（1px solid rgba(220, 208, 255, 0.25)）
      - 动态身份刻度（ZJU.MED.2024 / VERIFIED）
      - 乐观更新与文字"能量湮灭"动效
      - 三大状态光影反馈（PENDING 呼吸 / DELIVERED 金属 / READ 金色流光）
      - 优雅降级"冰封结晶"（断网/超时不弹 Alert）
      - 悬浮 3D 交易晶体胶囊 + 一键出价毛玻璃折叠面板
      - 增量时间戳同步 + 瀑布流错峰补写
    ============================================================
  -->
  <div class="chat-fluid-canvas">
    <!-- ===== 左栏：对话列表 ===== -->
    <aside class="chat-conversations-panel">
      <div class="chat-conversations-header">
        <h2 class="chat-conversations-title">
          <span>◈</span>
          私信
        </h2>
      </div>

      <!-- 对话列表 -->
      <div class="chat-conversations-list">
        <div
          v-for="conv in conversations"
          :key="conv.partner"
          :class="['chat-conversation-item', { active: activePartner === conv.partner }]"
          @click="switchConversation(conv.partner)"
        >
          <!-- 头像 + 身份刻度 -->
          <div class="chat-avatar-wrapper">
            <div class="chat-avatar">
              {{ (conv.partner || '?')[0] }}
            </div>
            <div
              :class="['chat-avatar-ring', { verified: conv.partnerInfo?.verified }]"
            />
            <span class="chat-identity-badge">
              {{ formatIdentityBadge(conv.partnerInfo) }}
            </span>
          </div>

          <!-- 对话信息 -->
          <div class="chat-conversation-info">
            <div class="chat-conversation-name">
              {{ conv.partner }}
              <span class="chat-conversation-identity">
                {{ conv.partnerInfo?.college || '校友' }}
              </span>
            </div>
            <div class="chat-conversation-preview">
              {{ conv.lastMessage?.content || '暂无消息' }}
            </div>
          </div>

          <!-- 元信息 -->
          <div class="chat-conversation-meta">
            <span class="chat-conversation-time">
              {{ formatTime(conv.lastMessage?.createdAt) }}
            </span>
            <span
              v-if="conv.unreadCount > 0"
              class="chat-unread-badge"
            >
              {{ conv.unreadCount > 99 ? '99+' : conv.unreadCount }}
            </span>
          </div>
        </div>

        <!-- 空状态 -->
        <div
          v-if="conversations.length === 0 && !loadingConversations"
          class="chat-empty-state"
          style="padding: 2rem 0;"
        >
          <div class="chat-empty-icon">◈</div>
          <div class="chat-empty-text">暂无对话</div>
        </div>
      </div>
    </aside>

    <!-- ===== 右栏：主聊天区域 ===== -->
    <div class="chat-main-area">
      <!-- 未选择对话时的空状态 -->
      <template v-if="!activePartner">
        <div class="chat-empty-state">
          <div class="chat-empty-icon">✧</div>
          <div class="chat-empty-text">选择一个对话开始交流</div>
        </div>
      </template>

      <!-- 已选择对话 -->
      <template v-else>
        <!-- ===== 顶部悬浮交易胶囊 ===== -->
        <div class="chat-top-capsule">
          <div class="chat-partner-info">
            <div class="chat-avatar-wrapper" style="width: 2.5rem; height: 2.5rem;">
              <div class="chat-avatar" style="font-size: 0.9rem;">
                {{ (activePartner || '?')[0] }}
              </div>
              <div
                :class="['chat-avatar-ring', { verified: activePartnerInfo?.verified }]"
              />
            </div>
            <div class="chat-partner-details">
              <span class="chat-partner-name">{{ activePartner }}</span>
              <span class="chat-partner-identity">
                {{ formatIdentityString(activePartnerInfo) }}
              </span>
            </div>
          </div>

          <!-- 悬浮 3D 交易晶体胶囊 -->
          <div
            :class="['chat-trade-capsule', { expanded: showOrderPanel }]"
            @click="toggleOrderPanel"
          >
            <div class="chat-trade-capsule-icon">📦</div>
            <span class="chat-trade-capsule-text">
              {{ relatedBook ? relatedBook.title : '交易' }}
            </span>
            <span class="chat-trade-capsule-arrow">▾</span>
          </div>
        </div>

        <!-- ===== 一键出价毛玻璃折叠面板 ===== -->
        <div :class="['chat-order-panel', { open: showOrderPanel }]">
          <div class="chat-order-panel-inner">
            <!-- 关联书籍信息 -->
            <div v-if="relatedBook" class="chat-order-book">
              <div class="chat-order-book-img" />
              <div class="chat-order-book-info">
                <div class="chat-order-book-title">{{ relatedBook.title }}</div>
                <div class="chat-order-book-price">
                  参考价 ¥{{ relatedBook.price }}
                </div>
              </div>
            </div>

            <!-- 出价输入 -->
            <div class="chat-order-input-group">
              <span style="font-size: 0.85rem; color: var(--text-secondary);">¥</span>
              <input
                v-model="orderPrice"
                type="number"
                step="0.1"
                min="0"
                placeholder="输入出价金额"
                class="chat-order-price-input"
              />
              <button
                class="chat-order-submit-btn"
                :disabled="sendingOrder"
                @click="submitOrder"
              >
                {{ sendingOrder ? '发送中...' : '一键出价' }}
              </button>
            </div>
          </div>
        </div>

        <!-- ===== 消息流区域 ===== -->
        <div
          ref="messagesContainer"
          class="chat-messages-area"
          @scroll="onMessagesScroll"
        >
          <!-- 加载骨架屏 -->
          <div v-if="loadingMessages" class="chat-skeleton">
            <div
              v-for="n in 4"
              :key="'skel-' + n"
              :class="['chat-skeleton-message', { own: n % 2 === 0 }]"
            >
              <div class="chat-skeleton-avatar" />
              <div class="chat-skeleton-bubble" />
            </div>
          </div>

          <!-- 消息列表（瀑布流错峰入场） -->
          <TransitionGroup
            v-else
            name="chat-message"
            tag="div"
            style="display: flex; flex-direction: column; gap: 0.75rem;"
          >
            <!-- 时间分隔线 -->
            <div
              v-for="(item, idx) in displayMessages"
              :key="item.key || item.id"
              class="chat-message-wrapper"
              :style="{ '--stagger-delay': `${(idx % 5) * 20}ms` }"
            >
              <!-- 日期分隔线 -->
              <div
                v-if="shouldShowDateDivider(item, idx)"
                class="chat-date-divider"
              >
                <span class="chat-date-divider-line" />
                <span class="chat-date-divider-text">
                  {{ formatDateDivider(item.createdAt) }}
                </span>
                <span class="chat-date-divider-line" />
              </div>

              <!-- 系统消息（全息信件） -->
              <div
                v-if="item.isSystem"
                class="chat-message-card system"
              >
                <div class="chat-system-content">
                  <template v-if="item.systemData?.type === 'order_created'">
                    <div>✦ 订单已创建 ✦</div>
                    <div class="chat-system-order">
                      📋 {{ item.systemData.bookTitle }}
                      · ¥{{ item.systemData.price }}
                    </div>
                  </template>
                  <template v-else>
                    {{ item.content }}
                  </template>
                </div>
                <div class="chat-message-time">
                  {{ formatTime(item.createdAt) }}
                </div>
              </div>

              <!-- 普通消息卡片 -->
              <div
                v-else
                :class="[
                  'chat-message-card',
                  item.sender === currentUserName ? 'own' : 'other',
                  'status-' + (item.status || 'delivered').toLowerCase(),
                  item.frozen ? 'frozen' : '',
                ]"
                :title="item.frozen ? '双击重新发送' : ''"
                @dblclick="item.frozen && retrySendMessage(item)"
              >
                <!-- 发送者信息（仅对方消息显示） -->
                <div
                  v-if="item.sender !== currentUserName"
                  class="chat-message-sender"
                >
                  <span class="chat-message-sender-name">{{ item.sender }}</span>
                  <span
                    v-if="item.senderInfo"
                    class="chat-message-sender-badge"
                  >
                    {{ formatIdentityBadge(item.senderInfo) }}
                  </span>
                </div>

                <!-- 消息内容 -->
                <div class="chat-message-content">{{ item.content }}</div>

                <!-- 时间戳 + 状态 -->
                <div class="chat-message-time">
                  <span>{{ formatTime(item.createdAt) }}</span>
                  <!-- 状态图标 -->
                  <span
                    v-if="item.sender === currentUserName"
                    class="chat-message-status-icon"
                  >
                    <template v-if="item.status === 'PENDING'">◌</template>
                    <template v-else-if="item.status === 'DELIVERED'">◈</template>
                    <template v-else-if="item.status === 'READ'">◆</template>
                  </span>
                </div>
              </div>
            </div>
          </TransitionGroup>
        </div>

        <!-- ===== 输入区域 ===== -->
        <div class="chat-input-area">
          <div class="chat-input-wrapper">
            <textarea
              ref="inputRef"
              v-model="inputText"
              class="chat-input"
              placeholder="输入消息..."
              rows="1"
              @keydown.enter.exact.prevent="sendMessage"
              @input="autoResizeInput"
            />
          </div>
          <button
            class="chat-send-btn"
            :disabled="!inputText.trim() || sendingMessage"
            @click="sendMessage"
          >
            <span v-if="!sendingMessage">↑</span>
            <span v-else style="font-size: 0.7rem;">◌</span>

            <!-- 粒子湮灭动效容器 -->
            <div
              v-if="showParticleBurst"
              class="chat-send-particle-container"
            >
              <div
                v-for="p in particles"
                :key="p.id"
                class="chat-send-particle"
                :style="{
                  left: p.x + 'px',
                  top: p.y + 'px',
                  '--tx': p.tx + 'px',
                  '--ty': p.ty + 'px',
                  background: p.color,
                  animation: `particleFly 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) forwards`,
                }"
              />
            </div>
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
/**
 * ============================================================
 * ChatWindow.vue — Script 逻辑层
 * ============================================================
 *
 * 核心交互：
 *   1. 对话列表加载与切换
 *   2. 乐观更新：消息零延迟上屏，虚拟节点替换
 *   3. 文字"能量湮灭"粒子动效
 *   4. 三大状态光影反馈（PENDING / DELIVERED / READ）
 *   5. 优雅降级"冰封结晶"（断网/超时）
 *   6. 悬浮 3D 交易晶体胶囊 + 一键出价
 *   7. 增量时间戳同步 + 瀑布流错峰补写
 *   8. 自动滚动到底部
 *   9. 已读回执
 * ============================================================
 */
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useStore } from '../../stores/useStore'

// ============================================================
// Store
// ============================================================
const store = useStore()
const currentUserName = computed(() => store.currentUser.value?.name || '')

// ============================================================
// 对话列表状态
// ============================================================
const conversations = ref([])
const loadingConversations = ref(false)
const activePartner = ref('')
const activePartnerInfo = ref(null)

// ============================================================
// 消息状态
// ============================================================
const messages = ref([])           // 当前对话的消息列表
const loadingMessages = ref(false)
const inputText = ref('')
const sendingMessage = ref(false)
const inputRef = ref(null)

// ============================================================
// 增量同步状态
// ============================================================
const lastTimestamp = ref(0)       // 最后一条消息的微秒级时间戳
const hasMoreHistory = ref(true)   // 是否还有更多历史消息
const isLoadingMore = ref(false)   // 是否正在加载更多历史

// ============================================================
// 交易面板状态
// ============================================================
const showOrderPanel = ref(false)
const relatedBook = ref(null)
const orderPrice = ref(0)
const sendingOrder = ref(false)

// ============================================================
// 粒子动效状态
// ============================================================
const showParticleBurst = ref(false)
const particles = ref([])
let particleIdCounter = 0

// ============================================================
// 定时器/动画帧管理（组件销毁时清理）
// ============================================================
let pollTimer = null              // 轮询定时器
let frozenCheckTimer = null       // 冰封检测定时器
let animationFrameId = null       // 动画帧 ID
const pendingTimeouts = new Set() // 所有待清理的 setTimeout

/**
 * 安全设置超时（自动追踪以便组件销毁时清理）
 */
function safeSetTimeout(fn, delay) {
  const id = setTimeout(() => {
    pendingTimeouts.delete(id)
    fn()
  }, delay)
  pendingTimeouts.add(id)
  return id
}

// ============================================================
// 计算属性
// ============================================================

/**
 * 用于渲染的消息列表（包含系统消息解析）
 */
const displayMessages = computed(() => {
  return messages.value.map(msg => {
    // 解析系统消息的 JSON content
    if (msg.isSystem && typeof msg.content === 'string') {
      try {
        const parsed = JSON.parse(msg.content)
        return { ...msg, systemData: parsed }
      } catch (e) {
        return msg
      }
    }
    return msg
  })
})

// ============================================================
// 辅助函数
// ============================================================

/**
 * 生成客户端微秒级时间戳
 */
function generateClientTimestamp() {
  return Date.now() * 1000 + Math.floor(Math.random() * 1000)
}

/**
 * 生成临时消息 ID（用于乐观更新）
 */
function generateTempId() {
  return 'temp_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8)
}

/**
 * 格式化身份徽章（如 "ZJU.MED.2024"）
 */
function formatIdentityBadge(info) {
  if (!info) return 'ALUMNI'
  const college = info.college || ''
  const grade = info.grade || ''
  // 提取学院缩写
  const collegeAbbr = college.replace(/[学院系部]/g, '').slice(0, 3).toUpperCase() || 'ZJU'
  // 提取年级数字
  const gradeNum = grade.replace(/[^0-9]/g, '').slice(0, 4) || ''
  const verified = info.verified ? 'VERIFIED' : 'UNVERIFIED'
  if (gradeNum) {
    return `${collegeAbbr}.${gradeNum}/${verified}`
  }
  return `${collegeAbbr}/${verified}`
}

/**
 * 格式化身份字符串（如 "计算机学院 · 大二 · 已认证"）
 */
function formatIdentityString(info) {
  if (!info) return '校友'
  const parts = []
  if (info.college) parts.push(info.college)
  if (info.grade) parts.push(info.grade)
  if (info.verified) parts.push('已认证')
  return parts.join(' · ') || '校友'
}

/**
 * 格式化时间
 */
function formatTime(dateStr) {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now - date
    const hours = Math.floor(diff / 3600000)

    if (hours < 1) {
      const mins = Math.floor(diff / 60000)
      return mins <= 1 ? '刚刚' : `${mins}分钟前`
    }
    if (hours < 24) {
      return `${hours}小时前`
    }
    // 显示具体时间
    const h = date.getHours().toString().padStart(2, '0')
    const m = date.getMinutes().toString().padStart(2, '0')
    return `${h}:${m}`
  } catch (e) {
    return ''
  }
}

/**
 * 格式化日期分隔线
 */
function formatDateDivider(dateStr) {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const msgDate = new Date(date.getFullYear(), date.getMonth(), date.getDate())
    const diff = (today - msgDate) / 86400000

    if (diff === 0) return '今天'
    if (diff === 1) return '昨天'
    if (diff < 7) return `${Math.floor(diff)}天前`

    const m = (date.getMonth() + 1).toString().padStart(2, '0')
    const d = date.getDate().toString().padStart(2, '0')
    return `${m}月${d}日`
  } catch (e) {
    return ''
  }
}

/**
 * 判断是否需要显示日期分隔线
 */
function shouldShowDateDivider(item, idx) {
  if (idx === 0) return true
  const prev = displayMessages.value[idx - 1]
  if (!prev || !item.createdAt || !prev.createdAt) return false
  try {
    const curr = new Date(item.createdAt)
    const prevDate = new Date(prev.createdAt)
    return curr.toDateString() !== prevDate.toDateString()
  } catch (e) {
    return false
  }
}

/**
 * 自动调整输入框高度
 */
function autoResizeInput() {
  if (inputRef.value) {
    inputRef.value.style.height = 'auto'
    inputRef.value.style.height = Math.min(inputRef.value.scrollHeight, 128) + 'px'
  }
}

// ============================================================
// 对话列表加载
// ============================================================

/**
 * 加载对话列表
 */
async function loadConversations() {
  if (!currentUserName.value) return
  loadingConversations.value = true
  try {
    const data = await store.fetchConversations(currentUserName.value)
    if (data.success && data.conversations) {
      conversations.value = data.conversations
    }
  } catch (e) {
    // 静默失败，不弹 Alert
    console.warn('[Chat] 加载对话列表失败:', e.message)
  } finally {
    loadingConversations.value = false
  }
}

// ============================================================
// 对话切换
// ============================================================

/**
 * 切换对话
 */
async function switchConversation(partner) {
  if (partner === activePartner.value) return

  activePartner.value = partner
  showOrderPanel.value = false

  // 查找对方信息
  const conv = conversations.value.find(c => c.partner === partner)
  activePartnerInfo.value = conv?.partnerInfo || null

  // 重置消息状态
  messages.value = []
  lastTimestamp.value = 0
  hasMoreHistory.value = true
  inputText.value = ''

  // 加载历史消息
  await loadMessages()

  // 标记已读
  markAsRead(partner)

  // 滚动到底部
  safeSetTimeout(() => scrollToBottom(), 100)
}

/**
 * 加载消息（增量同步）
 */
async function loadMessages(append = false) {
  if (!currentUserName.value || !activePartner.value) return

  if (append) {
    isLoadingMore.value = true
  } else {
    loadingMessages.value = true
  }

  try {
    const data = await store.fetchChatHistory(
      currentUserName.value,
      activePartner.value,
      lastTimestamp.value,
      30
    )

    if (data.success && data.messages) {
      const newMessages = data.messages

      if (append) {
        // 增量追加（去重）
        const existingIds = new Set(messages.value.map(m => m.id))
        const uniqueNew = newMessages.filter(m => !existingIds.has(m.id))
        messages.value = [...messages.value, ...uniqueNew]
      } else {
        // 全量替换
        messages.value = newMessages
      }

      // 更新最后时间戳
      if (newMessages.length > 0) {
        const last = newMessages[newMessages.length - 1]
        lastTimestamp.value = last.clientTimestamp || 0
      }

      hasMoreHistory.value = data.hasMore || false
    }
  } catch (e) {
    console.warn('[Chat] 加载消息失败:', e.message)
  } finally {
    loadingMessages.value = false
    isLoadingMore.value = false
  }
}

/**
 * 加载更多历史消息（滚动到顶部时触发）
 */
async function loadMoreHistory() {
  if (isLoadingMore.value || !hasMoreHistory.value || messages.value.length === 0) return

  // 使用第一条消息的时间戳作为基准
  const firstMsg = messages.value[0]
  const beforeTimestamp = firstMsg.clientTimestamp || 0

  try {
    isLoadingMore.value = true
    const data = await store.fetchChatHistory(
      currentUserName.value,
      activePartner.value,
      0,  // 从头拉取
      30
    )

    if (data.success && data.messages) {
      // 过滤掉已有的消息
      const existingIds = new Set(messages.value.map(m => m.id))
      const olderMessages = data.messages.filter(
        m => !existingIds.has(m.id) && (m.clientTimestamp || 0) < beforeTimestamp
      )

      if (olderMessages.length > 0) {
        messages.value = [...olderMessages, ...messages.value]
      }

      hasMoreHistory.value = olderMessages.length >= 30
    }
  } catch (e) {
    console.warn('[Chat] 加载更多历史失败:', e.message)
  } finally {
    isLoadingMore.value = false
  }
}

// ============================================================
// 发送消息（乐观更新 + 粒子湮灭动效）
// ============================================================

/**
 * 发送消息
 * 核心流程：
 *   1. 生成临时 ID 和客户端时间戳
 *   2. 触发粒子湮灭动效
 *   3. 乐观更新：消息零延迟上屏
 *   4. 异步发送到后端
 *   5. 成功后替换临时 ID 为真实 ID
 *   6. 失败后标记为"冰封结晶"状态
 */
async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || !currentUserName.value || !activePartner.value || sendingMessage.value) return

  sendingMessage.value = true

  // ---- 1. 生成乐观更新数据 ----
  const tempId = generateTempId()
  const clientTs = generateClientTimestamp()
  const now = new Date().toISOString()

  const optimisticMsg = {
    id: tempId,
    key: tempId,
    sender: currentUserName.value,
    receiver: activePartner.value,
    content: text,
    status: 'PENDING',
    clientTimestamp: clientTs,
    createdAt: now,
    isSystem: false,
    senderInfo: {
      college: store.currentUser.value?.college || '未设置',
      grade: store.currentUser.value?.grade || '未知',
      verified: true,
    },
    frozen: false,
  }

  // ---- 2. 触发粒子湮灭动效 ----
  triggerParticleBurst()

  // ---- 3. 乐观更新：消息零延迟上屏 ----
  messages.value.push(optimisticMsg)
  inputText.value = ''

  // 重置输入框高度
  if (inputRef.value) {
    inputRef.value.style.height = 'auto'
  }

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  // ---- 4. 异步发送到后端 ----
  try {
    const data = await store.sendChatMessage({
      sender: currentUserName.value,
      receiver: activePartner.value,
      content: text,
      clientTimestamp: clientTs,
    })

    if (data.success && data.message) {
      // ---- 5. 替换临时 ID 为真实 ID ----
      const realMsg = data.message
      const idx = messages.value.findIndex(m => m.id === tempId)
      if (idx !== -1) {
        // 无缝替换：保留 DOM 节点，仅更新数据
        messages.value[idx] = {
          ...realMsg,
          key: tempId,  // 保持 key 不变，防止 DOM 销毁重建
          status: 'DELIVERED',
        }
      }

      // 更新最后时间戳
      lastTimestamp.value = realMsg.clientTimestamp || clientTs

      // 标记已读
      safeSetTimeout(() => markAsRead(activePartner.value), 500)
    }
  } catch (e) {
    // ---- 6. 失败：标记为"冰封结晶" ----
    console.warn('[Chat] 发送消息失败:', e.message)
    const idx = messages.value.findIndex(m => m.id === tempId)
    if (idx !== -1) {
      messages.value[idx].frozen = true
      messages.value[idx].status = 'PENDING'
    }
  } finally {
    sendingMessage.value = false
  }
}

/**
 * 重新发送冰封消息
 */
async function retrySendMessage(frozenMsg) {
  if (!frozenMsg || !frozenMsg.frozen) return

  // 取消冰封状态
  frozenMsg.frozen = false
  frozenMsg.status = 'PENDING'

  try {
    const data = await store.sendChatMessage({
      sender: currentUserName.value,
      receiver: activePartner.value,
      content: frozenMsg.content,
      clientTimestamp: frozenMsg.clientTimestamp || generateClientTimestamp(),
    })

    if (data.success && data.message) {
      const realMsg = data.message
      const idx = messages.value.findIndex(m => m.id === frozenMsg.id)
      if (idx !== -1) {
        messages.value[idx] = {
          ...realMsg,
          key: frozenMsg.key || frozenMsg.id,
          status: 'DELIVERED',
        }
      }
    }
  } catch (e) {
    // 再次失败，恢复冰封
    frozenMsg.frozen = true
    console.warn('[Chat] 重发失败:', e.message)
  }
}

// ============================================================
// 粒子湮灭动效
// ============================================================

/**
 * 触发粒子湮灭动效
 * 输入框内的文字瞬间解构为微小淡紫粒子向中心凝聚
 */
function triggerParticleBurst() {
  const btn = document.querySelector('.chat-send-btn')
  if (!btn) return

  const rect = btn.getBoundingClientRect()
  const centerX = rect.width / 2
  const centerY = rect.height / 2

  // 生成 12 个粒子
  const newParticles = []
  for (let i = 0; i < 12; i++) {
    const angle = (Math.PI * 2 * i) / 12
    const radius = 20 + Math.random() * 15
    newParticles.push({
      id: particleIdCounter++,
      x: centerX + Math.cos(angle) * radius,
      y: centerY + Math.sin(angle) * radius,
      tx: Math.cos(angle + Math.PI) * (30 + Math.random() * 20),
      ty: Math.sin(angle + Math.PI) * (30 + Math.random() * 20),
      color: `rgba(220, 208, 255, ${0.5 + Math.random() * 0.4})`,
    })
  }

  particles.value = newParticles
  showParticleBurst.value = true

  // 400ms 后清除粒子
  safeSetTimeout(() => {
    showParticleBurst.value = false
    particles.value = []
  }, 450)
}

// ============================================================
// 已读回执
// ============================================================

/**
 * 标记消息为已读
 */
async function markAsRead(sender) {
  if (!currentUserName.value || !sender) return
  try {
    const data = await store.markChatRead(currentUserName.value, sender)
    if (data.success && data.markedCount > 0) {
      // 更新本地消息状态
      let updated = false
      messages.value.forEach(msg => {
        if (msg.sender === sender && msg.status === 'DELIVERED') {
          msg.status = 'READ'
          updated = true
        }
      })
      // 如果更新了，触发响应式
      if (updated) {
        messages.value = [...messages.value]
      }
    }
  } catch (e) {
    // 静默失败
  }
}

// ============================================================
// 交易面板
// ============================================================

/**
 * 切换交易面板
 */
function toggleOrderPanel() {
  showOrderPanel.value = !showOrderPanel.value
}

/**
 * 提交订单
 */
async function submitOrder() {
  if (!currentUserName.value || !activePartner.value || !relatedBook.value) return
  const price = parseFloat(orderPrice.value)
  if (isNaN(price) || price <= 0) return

  sendingOrder.value = true
  try {
    const data = await store.createChatOrder({
      sender: currentUserName.value,
      receiver: activePartner.value,
      book_id: relatedBook.value.id,
      price: price,
      address: store.currentUser.value?.address || '',
    })

    if (data.success && data.message) {
      // 将系统消息插入聊天流
      const sysMsg = {
        ...data.message,
        key: 'sys_' + Date.now(),
      }
      messages.value.push(sysMsg)
      showOrderPanel.value = false

      await nextTick()
      scrollToBottom()
    }
  } catch (e) {
    console.warn('[Chat] 创建订单失败:', e.message)
  } finally {
    sendingOrder.value = false
  }
}

// ============================================================
// 滚动控制
// ============================================================

const messagesContainer = ref(null)

/**
 * 滚动到底部
 */
function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

/**
 * 消息区域滚动事件（用于加载更多历史）
 */
let scrollHandlerTimer = null
function onMessagesScroll() {
  if (scrollHandlerTimer) {
    cancelAnimationFrame(scrollHandlerTimer)
  }
  scrollHandlerTimer = requestAnimationFrame(() => {
    if (!messagesContainer.value) return
    const { scrollTop } = messagesContainer.value
    // 滚动到顶部 100px 范围内时加载更多
    if (scrollTop < 100 && hasMoreHistory.value && !isLoadingMore.value) {
      loadMoreHistory()
    }
  })
}

// ============================================================
// 轮询新消息
// ============================================================

/**
 * 启动轮询（每 3 秒检查新消息）
 */
function startPolling() {
  stopPolling()
  pollTimer = setInterval(async () => {
    if (!activePartner.value || !currentUserName.value) return
    try {
      const data = await store.fetchChatHistory(
        currentUserName.value,
        activePartner.value,
        lastTimestamp.value,
        10
      )
      if (data.success && data.messages && data.messages.length > 0) {
        // 去重追加
        const existingIds = new Set(messages.value.map(m => m.id))
        const newMsgs = data.messages.filter(m => !existingIds.has(m.id))
        if (newMsgs.length > 0) {
          messages.value = [...messages.value, ...newMsgs]
          // 更新最后时间戳
          const last = newMsgs[newMsgs.length - 1]
          lastTimestamp.value = last.clientTimestamp || 0
          // 标记已读
          markAsRead(activePartner.value)
          await nextTick()
          scrollToBottom()
        }
      }
    } catch (e) {
      // 静默失败
    }
  }, 3000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

// ============================================================
// 冰封检测（断网/超时）
// ============================================================

/**
 * 启动冰封检测
 * 检查是否有 PENDING 状态超过 3 秒的消息
 */
function startFrozenCheck() {
  stopFrozenCheck()
  frozenCheckTimer = setInterval(() => {
    const now = Date.now()
    let changed = false
    messages.value.forEach(msg => {
      if (msg.status === 'PENDING' && !msg.frozen) {
        // 检查是否超过 3 秒
        const msgTime = new Date(msg.createdAt).getTime()
        if (now - msgTime > 3000) {
          msg.frozen = true
          changed = true
        }
      }
    })
    if (changed) {
      messages.value = [...messages.value]
    }
  }, 1000)
}

function stopFrozenCheck() {
  if (frozenCheckTimer) {
    clearInterval(frozenCheckTimer)
    frozenCheckTimer = null
  }
}

// ============================================================
// 生命周期
// ============================================================

onMounted(async () => {
  await loadConversations()

  // 检查是否有从其他页面跳转时传入的对话对方
  if (store.chatPartner.value) {
    const partner = store.chatPartner.value
    // 清除 store 中的 partner 状态，避免重复跳转
    store.setChatPartner(null)
    // 如果对话列表已加载且有该对话，直接切换
    if (conversations.value.some(c => c.partner === partner)) {
      await switchConversation(partner)
    } else {
      // 否则手动设置 activePartner 并加载消息
      activePartner.value = partner
      activePartnerInfo.value = { college: '校友', grade: '', verified: false }
      await loadMessages()
      await nextTick()
      scrollToBottom()
    }
  }

  startPolling()
  startFrozenCheck()
})

onUnmounted(() => {
  stopPolling()
  stopFrozenCheck()
  // 清理所有待处理的 setTimeout
  pendingTimeouts.forEach(id => clearTimeout(id))
  pendingTimeouts.clear()
  // 清理动画帧
  if (scrollHandlerTimer) {
    cancelAnimationFrame(scrollHandlerTimer)
  }
})

// ============================================================
// 监听对话切换
// ============================================================

watch(activePartner, (newPartner, oldPartner) => {
  if (newPartner !== oldPartner) {
    // 标记旧对话已读
    if (oldPartner) {
      markAsRead(oldPartner)
    }
  }
})
</script>

<style scoped>
/* ============================================================
 * ChatWindow.vue — 私有样式
 * 全局样式已在 theme.css 中定义
 * 此处仅补充 scoped 的微调样式
 * ============================================================
 */

/* 粒子湮灭动效关键帧 */
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

/* 消息包装器 — 错峰延迟 */
.chat-message-wrapper {
  animation-delay: var(--stagger-delay, 0ms);
}

/* 输入框占位符颜色 */
.chat-input::placeholder {
  color: rgba(155, 142, 196, 0.35);
}

/* 发送按钮加载状态 */
.chat-send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 交易胶囊展开状态 */
.chat-trade-capsule.expanded {
  background: rgba(220, 208, 255, 0.2);
  border-color: rgba(220, 208, 255, 0.4);
}

/* 数字输入框去除默认箭头 */
.chat-order-price-input::-webkit-outer-spin-button,
.chat-order-price-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.chat-order-price-input[type='number'] {
  -moz-appearance: textfield;
}

/* 消息卡片过渡动画 */
.chat-message-enter-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: var(--stagger-delay, 0ms);
}

.chat-message-enter-from {
  opacity: 0;
  transform: translateY(15px) scale(0.97);
}

.chat-message-leave-active {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.chat-message-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

/* 冰封结晶悬停提示 */
.chat-message-card.frozen {
  cursor: pointer;
  position: relative;
}

.chat-message-card.frozen::before {
  content: '❄';
  position: absolute;
  top: -0.375rem;
  right: -0.375rem;
  font-size: 0.7rem;
  opacity: 0.6;
  pointer-events: none;
}

/* 系统消息全息信件图标 */
.chat-message-card.system::before {
  content: '✧';
  position: absolute;
  top: -0.5rem;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.8rem;
  color: rgba(220, 208, 255, 0.4);
  pointer-events: none;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .chat-conversations-panel {
    width: 100%;
    min-width: unset;
    border-right: none;
    border-bottom: 1px solid rgba(220, 208, 255, 0.12);
  }

  .chat-fluid-canvas {
    flex-direction: column;
  }

  .chat-message-card {
    max-width: 85%;
  }
}
</style>
