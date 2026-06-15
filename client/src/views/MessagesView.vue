<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

// ==================== State ====================
const conversations = ref([])
const activeConvId = ref(null)
const messages = ref([])
const newMsgText = ref('')
const loadingConv = ref(false)
const loadingMsgs = ref(false)
const sending = ref(false)
const chatContainer = ref(null)
const pollTimer = ref(null)
const unreadTotal = ref(0)

// Image upload state
const pendingImages = ref([])       // { file, previewUrl } — 待发送的图片
const uploading = ref(false)
const fileInput = ref(null)
const lightboxImage = ref(null)     // 灯箱预览的图片 URL

// Order card state
const loadingOrderCard = ref(false)

// ==================== Computed ====================
const activeConv = computed(() =>
  conversations.value.find(c => c.id === activeConvId.value) || null
)

const peerName = computed(() => {
  if (!activeConv.value) return ''
  return activeConv.value.peer_name || '书友'
})

const peerId = computed(() => {
  if (!activeConv.value) return ''
  return activeConv.value.peer_id || ''
})

const hasOrderContext = computed(() => {
  return activeConv.value?.order_id ? true : false
})

// ==================== Load Conversations ====================
async function loadConversations() {
  try {
    const res = await api.get('/messages/conversations')
    conversations.value = res.data || []
    unreadTotal.value = conversations.value.reduce((sum, c) => sum + (c.unread_count || 0), 0)
  } catch { /* ignore */ }
}

// ==================== Load Messages ====================
async function loadMessages(convId) {
  if (!convId) return
  loadingMsgs.value = true
  try {
    const res = await api.get(`/messages/conversations/${convId}`)
    messages.value = res.data?.messages || []
    await api.put(`/messages/conversations/${convId}/read`)
    const conv = conversations.value.find(c => c.id === convId)
    if (conv) conv.unread_count = 0
    unreadTotal.value = conversations.value.reduce((sum, c) => sum + (c.unread_count || 0), 0)
  } catch {
    messages.value = []
  }
  loadingMsgs.value = false
  await nextTick()
  scrollToBottom()
}

// ==================== Select Conversation ====================
async function selectConv(conv) {
  activeConvId.value = conv.id
  pendingImages.value = []  // 切换会话时清空待发送图片
  await loadMessages(conv.id)
}

// Check if any pending image is still uploading
const hasUploadingImages = computed(() =>
  pendingImages.value.some(img => !img.url)
)

// ==================== Send Text Message ====================
async function sendMessage() {
  const text = newMsgText.value.trim()
  const hasImages = pendingImages.value.length > 0

  if ((!text && !hasImages) || !activeConvId.value || sending.value) return

  // Guard: don't send images that haven't finished uploading
  if (hasUploadingImages.value) {
    ElMessage.warning('请等待图片上传完成后再发送')
    return
  }

  sending.value = true
  try {
    // 先发送所有待发送图片
    if (hasImages) {
      for (const img of pendingImages.value) {
        await api.post('/messages', {
          conversation_id: activeConvId.value,
          message_type: 'image',
          image_url: img.url,
          content: '',
        })
      }
      // 刷新消息列表
      await refreshMessages()
      pendingImages.value = []
    }

    // 发送文字消息
    if (text) {
      const res = await api.post('/messages', {
        conversation_id: activeConvId.value,
        message_type: 'text',
        content: text,
      })
      messages.value.push(res.data)
      newMsgText.value = ''
    }

    // 更新侧边栏会话预览
    updateConvPreview(text || '[图片]')

    await nextTick()
    scrollToBottom()
  } catch (err) {
    ElMessage.error(err.message || '发送失败')
  }
  sending.value = false
}

function updateConvPreview(preview) {
  const conv = conversations.value.find(c => c.id === activeConvId.value)
  if (conv) {
    conv.last_message = preview.slice(0, 200)
    conv.last_message_at = new Date().toISOString()
    conversations.value.sort((a, b) => {
      const ta = a.last_message_at ? new Date(a.last_message_at).getTime() : 0
      const tb = b.last_message_at ? new Date(b.last_message_at).getTime() : 0
      return tb - ta
    })
  }
}

async function refreshMessages() {
  try {
    const res = await api.get(`/messages/conversations/${activeConvId.value}`)
    messages.value = res.data?.messages || []
  } catch { /* ignore */ }
}

// ==================== Image Upload & Paste ====================
function triggerFileInput() {
  fileInput.value?.click()
}

async function onFileSelected(e) {
  const files = Array.from(e.target.files || [])
  await processFiles(files)
  // Reset input so the same file can be re-selected
  e.target.value = ''
}

async function processFiles(files) {
  for (const file of files) {
    if (!file.type.startsWith('image/')) {
      ElMessage.warning(`文件 "${file.name}" 不是图片格式`)
      continue
    }
    if (file.size > 5 * 1024 * 1024) {
      ElMessage.warning(`图片 "${file.name}" 超过 5MB 限制`)
      continue
    }
    // 生成本地预览
    const previewUrl = URL.createObjectURL(file)
    pendingImages.value.push({ file, previewUrl, url: null })
  }
  // 上传到服务器
  await uploadPendingImages()
}

async function uploadPendingImages() {
  for (const img of pendingImages.value) {
    if (img.url) continue  // 已上传的跳过
    try {
      const formData = new FormData()
      formData.append('image', img.file)
      const res = await api.post('/messages/upload-image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      img.url = res.data.url
    } catch (err) {
      ElMessage.error(err.message || '图片上传失败')
      // 移除上传失败的图片
      const idx = pendingImages.value.indexOf(img)
      if (idx >= 0) pendingImages.value.splice(idx, 1)
      if (img.previewUrl) URL.revokeObjectURL(img.previewUrl)
    }
  }
}

function removePendingImage(idx) {
  const img = pendingImages.value[idx]
  if (img?.previewUrl) URL.revokeObjectURL(img.previewUrl)
  pendingImages.value.splice(idx, 1)
}

// Ctrl+V 粘贴图片
function onPaste(e) {
  const items = e.clipboardData?.items
  if (!items) return

  const imageFiles = []
  for (const item of items) {
    if (item.type.startsWith('image/')) {
      const file = item.getAsFile()
      if (file) imageFiles.push(file)
    }
  }
  if (imageFiles.length > 0) {
    e.preventDefault()
    processFiles(imageFiles)
  }
}

// ==================== Lightbox ====================
function openLightbox(url) {
  lightboxImage.value = url
}
function closeLightbox() {
  lightboxImage.value = null
}
function onLightboxKeydown(e) {
  if (e.key === 'Escape') closeLightbox()
}

// ==================== Order Card ====================
async function sendOrderCard() {
  if (!activeConv.value?.order_id || loadingOrderCard.value) return
  loadingOrderCard.value = true
  try {
    const res = await api.get(`/messages/order-card/${activeConv.value.order_id}`)
    const orderData = res.data
    const cardJson = JSON.stringify(orderData)

    const sendRes = await api.post('/messages', {
      conversation_id: activeConvId.value,
      message_type: 'order_card',
      content: cardJson,
    })
    messages.value.push(sendRes.data)
    updateConvPreview('[订单卡片]')

    await nextTick()
    scrollToBottom()
  } catch (err) {
    ElMessage.error(err.message || '发送订单卡片失败')
  }
  loadingOrderCard.value = false
}

// ==================== Keyboard ====================
function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// ==================== Scroll ====================
function scrollToBottom() {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// ==================== Create/Find Conversation ====================
async function startChat(peerUserId, peerUserName, bookId, bookTitle, orderId) {
  try {
    const body = { user_id: peerUserId }
    if (orderId) body.order_id = orderId
    if (bookId) body.book_id = bookId
    const res = await api.post('/messages/conversations', body)
    // 重新拉取以获取完整字段（peer_name、unread_count 等）
    await loadConversations()
    const conv = conversations.value.find(c => c.id === res.data.id)
    if (conv) {
      await selectConv(conv)
    }
  } catch (err) {
    ElMessage.error(err.message || '创建会话失败')
  }
}

// ==================== Format Time ====================
function formatTime(isoStr) {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  const now = new Date()
  const isToday = d.toDateString() === now.toDateString()
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  if (isToday) return `${hh}:${mm}`
  return `${d.getMonth() + 1}/${d.getDate()} ${hh}:${mm}`
}

function parseOrderCard(content) {
  try { return JSON.parse(content) } catch { return null }
}

function statusClass(status) {
  const map = {
    '待确认': 'status-pending',
    '已确认': 'status-confirmed',
    '已完成': 'status-done',
    '已取消': 'status-cancelled',
  }
  return map[status] || ''
}

// ==================== Init ====================
onMounted(async () => {
  if (!auth.isLoggedIn) {
    router.push({ name: 'Auth', query: { redirect: '/messages' } })
    return
  }

  if (!auth.currentUser) {
    await auth.fetchProfile()
  }

  await loadConversations()

  const qUserId = route.query.user_id
  if (qUserId) {
    await startChat(
      qUserId, route.query.user_name,
      route.query.book_id, route.query.book_title, route.query.order_id,
    )
  } else if (conversations.value.length > 0) {
    selectConv(conversations.value[0])
  }

  // Poll every 30s
  pollTimer.value = setInterval(async () => {
    await loadConversations()
    if (activeConvId.value) {
      try {
        const res = await api.get(`/messages/conversations/${activeConvId.value}`)
        const newMsgs = res.data?.messages || []
        const currentIds = new Set(messages.value.map(m => m.id))
        const hasNew = newMsgs.some(m => !currentIds.has(m.id))
        if (hasNew || newMsgs.length !== messages.value.length) {
          messages.value = newMsgs
          await api.put(`/messages/conversations/${activeConvId.value}/read`)
          await nextTick()
          scrollToBottom()
        }
      } catch { /* ignore */ }
    }
  }, 30000)

  // Listen for paste globally on the chat panel
  document.addEventListener('paste', onPaste)
})

onUnmounted(() => {
  if (pollTimer.value) clearInterval(pollTimer.value)
  document.removeEventListener('paste', onPaste)
  // Clean up any remaining object URLs
  pendingImages.value.forEach(img => {
    if (img.previewUrl) URL.revokeObjectURL(img.previewUrl)
  })
})

watch(() => route.query.user_id, async (newUserId) => {
  if (newUserId) {
    await loadConversations()
    await startChat(
      newUserId, route.query.user_name,
      route.query.book_id, route.query.book_title, route.query.order_id,
    )
  }
})
</script>

<template>
  <div class="messages-page page-enter">
    <div class="messages-layout">
      <!-- ============ Left Panel: Conversation List ============ -->
      <div class="conv-panel">
        <div class="conv-panel-header">
          <h2 class="panel-title">消息</h2>
          <span v-if="unreadTotal > 0" class="unread-total-badge">{{ unreadTotal }}</span>
        </div>

        <div class="conv-list">
          <div v-if="conversations.length === 0 && !loadingConv" class="conv-empty">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
              <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <p>暂无消息</p>
            <p class="sub">浏览书籍时可联系卖家开始对话</p>
          </div>

          <div
            v-for="conv in conversations" :key="conv.id"
            :class="['conv-item', { active: conv.id === activeConvId }]"
            @click="selectConv(conv)"
          >
            <div class="conv-avatar">{{ (conv.peer_name || '书友')[0] }}</div>
            <div class="conv-body">
              <div class="conv-top">
                <span class="conv-name">{{ conv.peer_name }}</span>
                <span class="conv-time">{{ formatTime(conv.last_message_at || conv.created_at) }}</span>
              </div>
              <div class="conv-bottom">
                <span class="conv-preview">{{ conv.last_message || '开始对话吧' }}</span>
                <span v-if="conv.unread_count > 0" class="conv-unread">{{ conv.unread_count }}</span>
              </div>
              <div v-if="conv.book_title" class="conv-context">📚 {{ conv.book_title }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- ============ Right Panel: Chat Window ============ -->
      <div class="chat-panel">
        <!-- No conversation selected -->
        <div v-if="!activeConvId" class="chat-empty">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="64" height="64">
            <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <p>选择一个会话开始聊天</p>
        </div>

        <!-- Active chat -->
        <template v-else>
          <!-- Chat header -->
          <div class="chat-header">
            <div class="chat-header-left">
              <div class="chat-avatar">{{ peerName[0] }}</div>
              <div>
                <div class="chat-peer-name">{{ peerName }}</div>
                <div v-if="activeConv?.book_title" class="chat-context-hint">📚 {{ activeConv.book_title }}</div>
              </div>
            </div>
            <!-- 分享订单按钮 -->
            <button
              v-if="hasOrderContext"
              class="share-order-btn"
              :disabled="loadingOrderCard"
              @click="sendOrderCard"
            >
              📋 {{ loadingOrderCard ? '发送中...' : '分享订单' }}
            </button>
          </div>

          <!-- Messages -->
          <div ref="chatContainer" class="chat-messages">
            <div v-if="loadingMsgs" class="chat-loading">加载中...</div>
            <div v-else-if="messages.length === 0" class="chat-loading">发送第一条消息开始对话吧</div>
            <template v-else>
              <template v-for="msg in messages" :key="msg.id">
                <!-- ===== TEXT message bubble ===== -->
                <div
                  v-if="msg.message_type === 'text' || !msg.message_type"
                  :class="['msg-bubble', msg.sender_id === auth.currentUser?.id ? 'msg-mine' : 'msg-theirs']"
                >
                  <div class="msg-content">{{ msg.content }}</div>
                  <div class="msg-time">{{ formatTime(msg.created_at) }}</div>
                </div>

                <!-- ===== IMAGE message bubble ===== -->
                <div
                  v-else-if="msg.message_type === 'image'"
                  :class="['msg-bubble', 'msg-image-bubble', msg.sender_id === auth.currentUser?.id ? 'msg-mine' : 'msg-theirs']"
                >
                  <div class="img-wrapper" @click="openLightbox(msg.image_url)">
                    <img
                      :src="msg.image_url"
                      alt="聊天图片"
                      class="chat-image"
                      loading="lazy"
                      @error="e => e.target.style.display = 'none'"
                    />
                    <div class="img-overlay">
                      <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" width="20" height="20">
                        <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </div>
                  </div>
                  <div v-if="msg.content" class="msg-content img-caption">{{ msg.content }}</div>
                  <div class="msg-time">{{ formatTime(msg.created_at) }}</div>
                </div>

                <!-- ===== ORDER CARD message bubble ===== -->
                <div
                  v-else-if="msg.message_type === 'order_card'"
                  :class="['msg-bubble', msg.sender_id === auth.currentUser?.id ? 'msg-mine' : 'msg-theirs']"
                >
                  <div class="order-card">
                    <div class="order-card-header">📦 订单信息</div>
                    <div class="order-card-body">
                      <div class="order-card-row" v-if="parseOrderCard(msg.content)?.book_title">
                        <span class="oc-label">书名</span>
                        <span class="oc-value">{{ parseOrderCard(msg.content).book_title }}</span>
                      </div>
                      <div class="order-card-row" v-if="parseOrderCard(msg.content)?.book_price">
                        <span class="oc-label">价格</span>
                        <span class="oc-price">¥{{ parseOrderCard(msg.content).book_price }}</span>
                      </div>
                      <div class="order-card-row" v-if="parseOrderCard(msg.content)?.status">
                        <span class="oc-label">状态</span>
                        <span :class="['oc-status', statusClass(parseOrderCard(msg.content).status)]">
                          {{ parseOrderCard(msg.content).status }}
                        </span>
                      </div>
                      <div class="order-card-row" v-if="parseOrderCard(msg.content)?.buyer_name">
                        <span class="oc-label">买家</span>
                        <span class="oc-value">{{ parseOrderCard(msg.content).buyer_name }}</span>
                      </div>
                      <div class="order-card-row" v-if="parseOrderCard(msg.content)?.seller_name">
                        <span class="oc-label">卖家</span>
                        <span class="oc-value">{{ parseOrderCard(msg.content).seller_name }}</span>
                      </div>
                    </div>
                    <div
                      class="order-card-footer"
                      @click="router.push({ name: 'Orders' })"
                    >
                      查看订单详情 →
                    </div>
                  </div>
                  <div class="msg-time">{{ formatTime(msg.created_at) }}</div>
                </div>
              </template>
            </template>
          </div>

          <!-- Input area -->
          <div class="chat-input-area">
            <!-- Image preview strip -->
            <div v-if="pendingImages.length > 0" class="image-preview-strip">
              <div v-for="(img, i) in pendingImages" :key="i" class="preview-item">
                <img :src="img.previewUrl" alt="预览" class="preview-thumb" />
                <div v-if="!img.url" class="preview-uploading">上传中...</div>
                <button class="preview-remove" @click="removePendingImage(i)">×</button>
              </div>
            </div>

            <div class="input-row">
              <!-- 📎 File attach button -->
              <button class="attach-btn" title="发送图片" @click="triggerFileInput">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                  <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
              <input
                ref="fileInput"
                type="file"
                accept="image/*"
                multiple
                style="display:none"
                @change="onFileSelected"
              />

              <textarea
                v-model="newMsgText"
                class="chat-input"
                placeholder="输入消息... (Enter 发送, Shift+Enter 换行, Ctrl+V 粘贴图片)"
                rows="2"
                @keydown="onKeydown"
              ></textarea>
              <button
                class="send-btn"
                :disabled="(!newMsgText.trim() && pendingImages.length === 0) || sending || hasUploadingImages"
                @click="sendMessage"
              >
                {{ sending ? '发送中...' : '发送' }}
              </button>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- ===== Lightbox overlay ===== -->
    <Teleport to="body">
      <div
        v-if="lightboxImage"
        class="lightbox-overlay"
        @click="closeLightbox"
        @keydown="onLightboxKeydown"
      >
        <button class="lightbox-close" @click="closeLightbox">✕</button>
        <img :src="lightboxImage" alt="图片预览" class="lightbox-img" @click.stop />
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.messages-page {
  min-height: calc(100vh - 64px);
  padding-top: 64px;
  background: var(--surface-primary);
}

/* 暗色模式：让 CyberBackground 四层背景透出 */
[data-theme="cyber"] .messages-page {
  background: transparent;
}

.messages-layout {
  display: flex;
  height: calc(100vh - 64px);
  max-width: 1200px;
  margin: 0 auto;
}

/* ========== Left Panel ========== */
.conv-panel {
  width: 340px;
  flex-shrink: 0;
  border-right: 1px solid var(--border-default);
  background: var(--surface-secondary);
  display: flex;
  flex-direction: column;
}

.conv-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-default);
  flex-shrink: 0;
}

.panel-title {
  font-family: var(--font-display);
  font-size: 20px;
  color: var(--text-primary);
  margin: 0;
}

.unread-total-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 22px;
  height: 22px;
  border-radius: 11px;
  background: var(--accent-primary);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  padding: 0 6px;
}

.conv-list { flex: 1; overflow-y: auto; }

.conv-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--text-muted);
  text-align: center;
}
.conv-empty p { margin: 8px 0; font-size: 14px; }
.conv-empty .sub { font-size: 12px; opacity: 0.7; }

.conv-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 20px;
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid var(--border-default);
}
.conv-item:hover { background: var(--surface-tertiary); }
.conv-item.active { background: var(--accent-primary-light); }

.conv-avatar {
  width: 44px; height: 44px;
  border-radius: 50%;
  background: var(--accent-primary-light);
  color: var(--accent-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  flex-shrink: 0;
}
[data-theme="cyber"] .conv-avatar {
  background: rgba(0,212,255,0.12);
  color: #00D4FF;
  border: 1px solid rgba(0,212,255,0.3);
}

.conv-body { flex: 1; min-width: 0; }
.conv-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.conv-name { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.conv-time { font-size: 11px; color: var(--text-muted); flex-shrink: 0; }
.conv-bottom { display: flex; justify-content: space-between; align-items: center; }
.conv-preview {
  font-size: 12px; color: var(--text-muted);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 190px;
}
.conv-unread {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 18px; height: 18px; border-radius: 9px;
  background: var(--accent-primary); color: #fff;
  font-size: 10px; font-weight: 600;
}
.conv-context { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

/* ========== Right Panel ========== */
.chat-panel {
  flex: 1; display: flex; flex-direction: column;
  min-width: 0; min-height: 0;
  background: var(--surface-primary);
}

.chat-empty {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  flex: 1; color: var(--text-muted); gap: 16px;
}
.chat-empty p { font-size: 15px; }

.chat-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 24px;
  border-bottom: 1px solid var(--border-default);
  background: var(--surface-secondary);
  flex-shrink: 0;
}

.chat-header-left { display: flex; align-items: center; gap: 12px; }

.chat-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--accent-primary-light); color: var(--accent-primary);
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: 600;
}
[data-theme="cyber"] .chat-avatar {
  background: rgba(0,212,255,0.12); color: #00D4FF;
  border: 1px solid rgba(0,212,255,0.3);
}

.chat-peer-name { font-size: 16px; font-weight: 600; color: var(--text-primary); }
.chat-context-hint { font-size: 12px; color: var(--text-muted); margin-top: 2px; }

/* 分享订单按钮 */
.share-order-btn {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 6px 14px;
  border: 1px solid var(--accent-primary); border-radius: 8px;
  background: transparent; color: var(--accent-primary);
  font-size: 13px; font-weight: 500; cursor: pointer;
  transition: all 0.2s;
}
.share-order-btn:hover:not(:disabled) { background: var(--accent-primary-light); }
.share-order-btn:disabled { opacity: 0.5; cursor: not-allowed; }
[data-theme="cyber"] .share-order-btn:hover:not(:disabled) {
  box-shadow: 0 0 12px rgba(0,212,255,0.15);
}

/* ========== Messages ========== */
.chat-messages {
  flex: 1; min-height: 0; overflow-y: auto;
  padding: 20px 24px;
  display: flex; flex-direction: column; gap: 16px;
}

.chat-loading { text-align: center; color: var(--text-muted); padding: 40px; font-size: 13px; }

.msg-bubble { max-width: 70%; display: flex; flex-direction: column; }
.msg-mine { align-self: flex-end; }
.msg-theirs { align-self: flex-start; }

.msg-content {
  padding: 10px 16px; border-radius: 16px;
  font-size: 14px; line-height: 1.55;
  white-space: pre-wrap; word-break: break-word;
}
.msg-mine .msg-content {
  background: var(--accent-primary); color: #fff;
  border-bottom-right-radius: 4px;
}
.msg-theirs .msg-content {
  background: var(--surface-secondary); color: var(--text-primary);
  border-bottom-left-radius: 4px;
  border: 1px solid var(--border-default);
}
[data-theme="cyber"] .msg-mine .msg-content {
  background: linear-gradient(135deg, #00D4FF, #A855F7);
}

.msg-time { font-size: 10px; color: var(--text-muted); margin-top: 4px; padding: 0 4px; }
.msg-mine .msg-time { text-align: right; }

/* ========== Image Message Bubble ========== */
.msg-image-bubble { max-width: 300px; }

.img-wrapper {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  background: var(--surface-tertiary);
}
.img-wrapper:hover .img-overlay { opacity: 1; }

.chat-image {
  display: block;
  width: 100%;
  max-width: 280px;
  max-height: 280px;
  object-fit: cover;
  border-radius: 12px;
}

.img-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  border-radius: 12px;
}

.img-caption {
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-muted);
  background: none !important;
  border: none !important;
  padding: 0 4px !important;
}

/* ========== Order Card Message ========== */
.order-card {
  width: 300px;
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: 10px;
  overflow: hidden;
  border-left: 3px solid var(--accent-primary);
}
[data-theme="cyber"] .order-card {
  background: rgba(255,255,255,0.03);
  border-left-color: #00D4FF;
}

.order-card-header {
  padding: 10px 14px;
  font-size: 13px; font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-default);
}

.order-card-body {
  padding: 10px 14px;
  display: flex; flex-direction: column; gap: 6px;
}

.order-card-row {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 12px;
}

.oc-label { color: var(--text-muted); }
.oc-value { color: var(--text-primary); font-weight: 500; }
.oc-price { color: var(--accent-primary); font-weight: 700; font-family: var(--font-mono); font-size: 14px; }

.oc-status {
  padding: 2px 8px; border-radius: 4px;
  font-size: 11px; font-weight: 600;
}
.status-pending { background: #FFF8E1; color: #F57F17; }
.status-confirmed { background: #E3F2FD; color: #1565C0; }
.status-done { background: #E8F5E9; color: #2E7D32; }
.status-cancelled { background: #F5F5F5; color: #9E9E9E; }
[data-theme="cyber"] .status-pending { background: rgba(255,152,0,0.15); color: #FFB74D; }
[data-theme="cyber"] .status-confirmed { background: rgba(33,150,243,0.15); color: #64B5F6; }
[data-theme="cyber"] .status-done { background: rgba(76,175,80,0.15); color: #81C784; }
[data-theme="cyber"] .status-cancelled { background: rgba(158,158,158,0.15); color: #BDBDBD; }

.order-card-footer {
  padding: 8px 14px;
  text-align: center;
  font-size: 12px; font-weight: 500;
  color: var(--accent-primary);
  cursor: pointer;
  border-top: 1px solid var(--border-default);
  transition: background 0.15s;
}
.order-card-footer:hover { background: var(--accent-primary-light); }

/* ========== Input Area ========== */
.chat-input-area {
  border-top: 1px solid var(--border-default);
  background: var(--surface-secondary);
  flex-shrink: 0;
  padding: 12px 24px;
}

/* Image preview strip */
.image-preview-strip {
  display: flex; gap: 8px; margin-bottom: 10px; flex-wrap: wrap;
}

.preview-item {
  position: relative;
  width: 80px; height: 80px;
  border-radius: 8px; overflow: hidden;
  border: 1px solid var(--border-default);
  background: var(--surface-tertiary);
}

.preview-thumb {
  width: 100%; height: 100%;
  object-fit: cover;
}

.preview-uploading {
  position: absolute; inset: 0;
  background: rgba(0,0,0,0.5);
  color: #fff; font-size: 10px;
  display: flex; align-items: center; justify-content: center;
}

.preview-remove {
  position: absolute; top: 2px; right: 2px;
  width: 20px; height: 20px; border-radius: 50%;
  background: rgba(0,0,0,0.6); color: #fff;
  border: none; font-size: 14px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  line-height: 1;
}
.preview-remove:hover { background: rgba(220,38,38,0.9); }

/* Input row */
.input-row {
  display: flex; align-items: flex-end; gap: 10px;
}

.attach-btn {
  width: 38px; height: 38px;
  border: 1px solid var(--border-default);
  border-radius: 10px;
  background: var(--surface-primary);
  color: var(--text-muted);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}
.attach-btn:hover {
  color: var(--accent-primary);
  border-color: var(--accent-primary);
}

.chat-input {
  flex: 1;
  border: 1px solid var(--border-default);
  border-radius: 12px;
  padding: 10px 14px;
  font-size: 14px;
  color: var(--text-primary);
  background: var(--surface-primary);
  resize: none; outline: none;
  font-family: var(--font-body);
  line-height: 1.5;
  transition: border-color 0.2s;
}
.chat-input:focus { border-color: var(--accent-primary); }

.send-btn {
  padding: 10px 22px;
  background: var(--accent-primary); color: #fff;
  border: none; border-radius: 12px;
  font-size: 14px; font-weight: 600;
  cursor: pointer; transition: all 0.2s; white-space: nowrap;
}
.send-btn:hover:not(:disabled) { background: var(--accent-primary-hover); }
.send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
[data-theme="cyber"] .send-btn { background: linear-gradient(135deg, #00D4FF, #A855F7); }

/* ========== Lightbox ========== */
.lightbox-overlay {
  position: fixed; inset: 0;
  z-index: 9999;
  background: rgba(0,0,0,0.92);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
}
.lightbox-close {
  position: absolute; top: 20px; right: 20px;
  width: 44px; height: 44px; border-radius: 50%;
  background: rgba(255,255,255,0.15); color: #fff;
  border: none; font-size: 22px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.2s;
  z-index: 1;
}
.lightbox-close:hover { background: rgba(255,255,255,0.25); }
.lightbox-img {
  max-width: 90vw; max-height: 90vh;
  object-fit: contain; border-radius: 8px;
  cursor: default;
}

/* ========== Responsive ========== */
@media (max-width: 768px) {
  .conv-panel { width: 100%; flex-shrink: 1; }
  .chat-panel {
    display: none;
    position: fixed; top: 56px; left: 0; right: 0; bottom: 0;
    z-index: 100; background: var(--surface-primary);
  }
  .chat-panel.active-mobile { display: flex; }
  .order-card { width: 260px; }
  .chat-image { max-width: 220px; max-height: 220px; }
}
</style>
