<template>
  <div class="home-page">
    <div class="top-grid">
      <div class="card ai-chat-zone apple-liquid-card stagger-item stagger-1">
        <div class="card-header">
          <h3 class="apple-text-gradient font-serif-display">
            <span class="iconify" data-icon="solar:chat-square-code-outline" data-width="20"></span>
            AI 学习助手
          </h3>
          <span class="ai-status">
            <span class="ai-dot"></span>
            在线
          </span>
        </div>
        <div class="chat-messages" ref="chatMsgs">
          <div class="chat-msg ai-msg">
            <span class="msg-avatar">
              <span class="iconify" data-icon="solar:robot-outline" data-width="18"></span>
            </span>
            <div class="msg-bubble">
              你好！我是紫金AI助手，可以帮你解答学习问题、推荐书籍、规划学习路径。试试问我吧～
            </div>
          </div>
          <div v-for="(msg, i) in chatHistory" :key="i" :class="['chat-msg', msg.role === 'user' ? 'user-msg' : 'ai-msg']">
            <span class="msg-avatar" v-if="msg.role === 'ai'">
              <span class="iconify" data-icon="solar:robot-outline" data-width="18"></span>
            </span>
            <div class="msg-bubble">{{ msg.content }}</div>
            <span class="msg-avatar" v-if="msg.role === 'user'">
              <span class="iconify" data-icon="solar:user-circle-outline" data-width="18"></span>
            </span>
          </div>
          <div v-if="chatLoading" class="chat-msg ai-msg">
            <span class="msg-avatar">
              <span class="iconify" data-icon="solar:robot-outline" data-width="18"></span>
            </span>
            <div class="msg-bubble typing-dots">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
        <div class="chat-input-area">
          <input
            v-model="chatInput"
            class="chat-text-input"
            placeholder="输入你的问题，如：推荐一本线性代数教材..."
            @keydown.enter="sendChat"
            :disabled="chatLoading"
          />
          <button class="chat-send-btn" @click="sendChat" :disabled="chatLoading || !chatInput.trim()">
            <span class="iconify" data-icon="solar:plain-3-linear" data-width="18"></span>
          </button>
        </div>
      </div>
      <div class="card community-zone apple-liquid-card stagger-item stagger-2">
        <h3 class="apple-text-gradient font-serif-display">
          <span class="iconify" data-icon="solar:users-group-two-rounded-outline" data-width="20"></span>
          学习社区
        </h3>
        <div class="topic-grid">
          <div v-for="(post, idx) in homePosts" :key="post.id" class="topic-item apple-liquid-nav-item" @click="goCommunity">
            <span class="iconify topic-dot" data-icon="solar:circle-small-outline" data-width="10"></span>
            <span class="topic-title">{{ post.title }}</span>
          </div>
        </div>
      </div>
    </div>
    <div class="bottom-grid">
      <div class="card smart-list apple-liquid-card stagger-item stagger-3">
        <h3 class="apple-text-gradient font-serif-display">
          <span class="iconify" data-icon="solar:lightbulb-bolt-outline" data-width="20"></span>
          智慧购书清单
        </h3>
        <div class="book-list">
          <div v-for="book in smartBooks" :key="book.name" class="book-row apple-cart-item" @click="goProcurement">
            <span class="book-name">{{ book.name }}</span>
            <span class="match-badge apple-match-badge">
              <span class="iconify" data-icon="solar:books-outline" data-width="14"></span>
              已匹配 {{ book.matchCount }} 本
            </span>
          </div>
        </div>
      </div>
      <div class="card hot-books apple-liquid-card stagger-item stagger-4">
        <h3 class="apple-text-gradient font-serif-display">
          <span class="iconify" data-icon="solar:fire-outline" data-width="20"></span>
          热门书本
        </h3>
        <div class="hot-list">
          <div
            v-for="book in randomBooks"
            :key="book.id"
            class="hot-item apple-product-card"
            @click="openDetail(book.id)"
            @mousemove="onHotMove($event, book.id)"
            @mouseleave="onHotLeave($event, book.id)"
          >
            <div class="hot-img apple-product-image-container">
              <img :src="book.img" :alt="book.title" class="hot-img-inner card-content-layer" />
            </div>
            <div class="hot-info card-content-layer">
              <h4 class="hot-title">{{ book.title }}</h4>
              <p class="hot-condition">{{ book.condition }}</p>
              <p class="hot-price apple-price-tag">
                <span class="iconify" data-icon="solar:dollar-minimalistic-outline" data-width="11"></span>
                {{ book.price }}
              </p>
              <p class="hot-seller" v-if="book.seller">
                <span class="iconify" data-icon="solar:user-outline" data-width="11"></span>
                {{ book.seller }}
                <button
                  v-if="store.isLoggedIn.value && book.seller !== store.currentUser.value?.name"
                  class="chat-btn-mini"
                  @click.stop="startChat(book.seller)"
                  title="私聊卖家"
                >
                  <span class="iconify" data-icon="solar:chat-dots-outline" data-width="14"></span>
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, nextTick } from 'vue'
import { useStore } from '../../stores/useStore'

const store = useStore()

const smartBooks = computed(() => store.categoriesData.value?.smartBooks || [])
const randomBooks = computed(() => store.getRandomProducts(4))
const homePosts = computed(() => store.getMergedPosts().slice(0, 4))

/* ===== AI 聊天 ===== */
const chatInput = ref('')
const chatHistory = ref([])
const chatLoading = ref(false)
const chatMsgs = ref(null)

// 本地知识库回复
const aiResponses = {
  '线性代数': '推荐《线性代数及其应用》（David C. Lay），浙江大学线性代数课程常用教材。在求是书摊有多个卖家提供，价格约15-30元。',
  '微积分': '浙大微积分常用《高等数学》（同济版），上册定价49.80元。书摊上有九成新的二手书，性价比很高！',
  '英语': '大学英语教材推荐《新视野大学英语》系列，书摊上流通量很大。另外还有《考研英语词汇》等备考资料。',
  '数据结构': '经典教材《数据结构（C语言版）》（严蔚敏），计算机学院必修课。二手市场流通频繁，容易淘到有笔记的版本。',
  '考研': '考研复习用书推荐：政治用《肖秀荣考研政治》，数学用《张宇考研数学》，英语用《考研真相》。书摊上这些书很常见。',
  '教材': '在求是书摊可以按分类浏览教材。你也可以在智慧购书清单中输入课程名称，系统会自动匹配对应的二手书。',
  'default': '这是个好问题！建议你在求是书摊按分类浏览，或使用智慧购书清单功能。如果你在找特定的教材或参考书，告诉我课程名称，我可以帮你推荐。'
}

function getAiReply(query) {
  const q = query.toLowerCase()
  for (const [keyword, reply] of Object.entries(aiResponses)) {
    if (q.includes(keyword)) return reply
  }
  return aiResponses.default
}

async function sendChat() {
  const msg = chatInput.value.trim()
  if (!msg || chatLoading.value) return

  chatHistory.value.push({ role: 'user', content: msg })
  chatInput.value = ''
  chatLoading.value = true

  await nextTick()
  if (chatMsgs.value) {
    chatMsgs.value.scrollTop = chatMsgs.value.scrollHeight
  }

  // 模拟延迟
  await new Promise(r => setTimeout(r, 600 + Math.random() * 800))
  const reply = getAiReply(msg)
  chatHistory.value.push({ role: 'ai', content: reply })
  chatLoading.value = false

  await nextTick()
  if (chatMsgs.value) {
    chatMsgs.value.scrollTop = chatMsgs.value.scrollHeight
  }
}

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

/** 私聊卖家 */
function startChat(sellerName) {
  if (!store.isLoggedIn.value) {
    alert('请先登录')
    return
  }
  sessionStorage.setItem('chat_target_user', sellerName)
  store.navigateTo('chat')
}
</script>

<style scoped>
.home-page { display: flex; flex-direction: column; gap: 1.5rem; }
.top-grid, .bottom-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1.5rem; }
.card {
  background: var(--glass-bg-card);
  backdrop-filter: blur(28px) saturate(1.4);
  -webkit-backdrop-filter: blur(28px) saturate(1.4);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-md), var(--shadow-glow), inset 0 1px 0 rgba(255,255,255,0.55);
  position: relative;
}
.ai-chat-zone { grid-column: span 2; display: flex; flex-direction: column; }
.community-zone { grid-column: span 3; background: rgba(243, 239, 255, 0.6); border: 1px solid rgba(220, 208, 255, 0.3); }
.smart-list { grid-column: span 3; padding: 1.5rem; }
.hot-books { grid-column: span 2; padding: 1.5rem; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.card-header h3, .card h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 1.5rem 0;
  letter-spacing: -0.01em;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.card-header h3 { margin: 0; }

/* ===== AI 聊天样式 ===== */
.ai-status {
  font-size: 0.75rem;
  color: #10b981;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.ai-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #10b981;
  animation: dotPulse 2s ease-in-out infinite;
}
@keyframes dotPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  max-height: 220px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-right: 4px;
  margin-bottom: 1rem;
}
.chat-messages::-webkit-scrollbar { width: 4px; }
.chat-messages::-webkit-scrollbar-thumb { background: rgba(180, 160, 220, 0.4); border-radius: 2px; }

.chat-msg {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
}
.user-msg { justify-content: flex-end; }
.msg-avatar {
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(220, 208, 255, 0.3);
  color: var(--lavender-accent);
}
.msg-bubble {
  font-size: 0.8rem;
  line-height: 1.55;
  padding: 0.6rem 0.85rem;
  border-radius: 14px;
  max-width: 85%;
}
.ai-msg .msg-bubble {
  background: rgba(243, 239, 255, 0.7);
  border: 1px solid rgba(220, 208, 255, 0.3);
  border-radius: 4px 14px 14px 14px;
  color: var(--text-primary);
}
.user-msg .msg-bubble {
  background: linear-gradient(135deg, rgba(220, 208, 255, 0.6), rgba(196, 181, 224, 0.4));
  border: 1px solid rgba(180, 160, 220, 0.4);
  border-radius: 14px 4px 14px 14px;
  color: var(--text-primary);
}

.typing-dots {
  display: flex;
  gap: 4px;
  padding: 0.75rem 0.85rem;
}
.typing-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--lavender-accent-soft);
  animation: dotBounce 1.4s ease-in-out infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes dotBounce {
  0%, 80%, 100% { transform: translateY(0); opacity: 0.3; }
  40% { transform: translateY(-6px); opacity: 1; }
}

.chat-input-area {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  border-top: 1px solid rgba(220, 208, 255, 0.2);
  padding-top: 0.75rem;
}
.chat-text-input {
  flex: 1;
  padding: 0.6rem 0.85rem;
  border: 1px solid rgba(220, 208, 255, 0.4);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.5);
  font-family: inherit;
  font-size: 0.8rem;
  color: var(--text-primary);
  outline: none;
  transition: border-color 0.2s;
}
.chat-text-input::placeholder { color: var(--text-caption); }
.chat-text-input:focus { border-color: var(--lavender-accent-soft); }
.chat-text-input:disabled { opacity: 0.5; }

.chat-send-btn {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #DCD0FF, #C4B5E0);
  color: #4a3f6b;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}
.chat-send-btn:hover:not(:disabled) {
  transform: scale(1.08);
  box-shadow: 0 4px 12px rgba(155, 142, 196, 0.3);
}
.chat-send-btn:disabled { opacity: 0.4; cursor: default; }

.topic-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem 2rem; }
.topic-item { display: flex; align-items: center; gap: 0.75rem; cursor: pointer; }
.topic-dot { flex-shrink: 0; color: var(--lavender-accent-soft); }
.topic-title { font-size: 0.875rem; color: var(--text-secondary); }
.topic-title:hover { color: var(--lavender-accent); }
.book-list { display: flex; flex-direction: column; gap: 0.75rem; }
.book-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem;
  background: rgba(243, 239, 255, 0.6);
  border-radius: 12px;
  border: 1px solid rgba(220, 208, 255, 0.3);
  cursor: pointer;
  transition: all 0.2s ease;
}
.book-row:hover { border-color: var(--lavender-accent-soft); }
.book-name { font-size: 1.125rem; font-weight: 600; color: var(--text-primary); }
.match-badge {
  padding: 0.375rem 1rem;
  background: linear-gradient(135deg, #DCD0FF, #C4B5E0);
  color: var(--text-primary);
  font-size: 0.75rem;
  font-weight: 700;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}
.hot-list { display: flex; flex-direction: column; gap: 1rem; }
.hot-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.3);
  cursor: pointer;
  will-change: transform;
  transition: transform 0.1s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.hot-item:hover { background: rgba(255, 255, 255, 0.5); }
.hot-img {
  width: 4rem;
  aspect-ratio: 3 / 4;
  background: linear-gradient(135deg, rgba(255,255,255,0.4), rgba(220,210,240,0.3));
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
}
.hot-img-inner { width: 100%; height: 100%; object-fit: cover; }
.hot-info {}
.hot-title {
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.3;
}
.hot-condition {
  font-size: 0.75rem;
  color: var(--text-caption);
  margin: 0.25rem 0;
  font-weight: 400;
}
.hot-price {
  color: var(--text-primary);
  font-weight: 600;
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
  margin: 0.375rem 0 0 0;
  font-size: 0.85rem;
  letter-spacing: -0.02em;
  display: flex;
  align-items: center;
  gap: 0.15rem;
}
.hot-seller {
  font-size: 0.7rem;
  color: var(--text-caption);
  margin: 0.25rem 0 0 0;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.chat-btn-mini {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  margin-left: 0.4rem;
  background: rgba(108,63,192,0.08);
  border: 1px solid rgba(108,63,192,0.15);
  border-radius: 6px;
  cursor: pointer;
  padding: 0;
  color: var(--lavender-accent);
  transition: all 0.2s;
}
.chat-btn-mini:hover { background: rgba(108,63,192,0.15); border-color: rgba(108,63,192,0.3); }
</style>
