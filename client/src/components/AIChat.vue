<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useChat } from '@/composables/useChat'

const auth = useAuthStore()
const {
  isOpen,
  messages,
  input,
  loading,
  chatBodyRef,
  open,
  close,
  sendMessage,
  scrollToBottom,
} = useChat()

onMounted(() => {
  scrollToBottom()
})
</script>

<template>
  <!-- Chat FAB (Floating Action Button) -->
  <button v-if="!isOpen" class="chat-fab" @click="open" :title="'AI 求书小助手'">
    <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
      <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.17L4 17.17V4h16v12z"/>
    </svg>
  </button>

  <!-- Chat Window -->
  <div v-if="isOpen" class="chat-window">
    <div class="chat-header">
      <span class="chat-title">🤖 求书小助手</span>
      <button class="chat-close" @click="close" title="关闭">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <path d="M6 18L18 6M6 6l12 12" stroke-linecap="round"/>
        </svg>
      </button>
    </div>

    <div ref="chatBodyRef" class="chat-body">
      <div v-for="(msg, i) in messages" :key="i" :class="['msg', msg.role]">
        <div class="msg-content">{{ msg.content }}</div>
      </div>
      <div v-if="loading" class="msg assistant">
        <div class="msg-content typing">
          <span>.</span><span>.</span><span>.</span>
        </div>
      </div>
    </div>

    <div class="chat-input-area">
      <input
        v-model="input"
        @keyup.enter="sendMessage()"
        placeholder="问我关于书籍、课程的任何问题..."
        :disabled="!auth.isLoggedIn"
        class="chat-input"
      />
      <button
        @click="sendMessage()"
        :disabled="loading || !auth.isLoggedIn"
        class="chat-send"
        title="发送"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.chat-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--accent-primary);
  color: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(196, 30, 58, 0.3);
  z-index: 1001;
  transition: all 0.3s;
}

[data-theme="cyber"] .chat-fab {
  background: linear-gradient(135deg, #00D4FF, #A855F7);
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
}

.chat-fab:hover { transform: scale(1.1); }

.chat-window {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 360px;
  max-height: 520px;
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
  z-index: 1001;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

[data-theme="cyber"] .chat-window {
  background: rgba(15, 10, 40, 0.95);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(0, 212, 255, 0.2);
  box-shadow: 0 0 40px rgba(0, 212, 255, 0.1), 0 8px 32px rgba(0, 0, 0, 0.5);
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: var(--accent-primary);
  color: #fff;
}

[data-theme="cyber"] .chat-header {
  background: linear-gradient(135deg, rgba(0, 180, 220, 0.35), rgba(130, 60, 220, 0.35));
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
}

[data-theme="cyber"] .chat-title {
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
}

.chat-title { font-size: 14px; font-weight: 600; }

.chat-close {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  padding: 4px;
  opacity: 0.8;
}

.chat-close:hover { opacity: 1; }

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 360px;
}

.msg { display: flex; }

.msg.user { justify-content: flex-end; }

.msg-content {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.msg.assistant .msg-content {
  background: var(--surface-tertiary);
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
}

.msg.user .msg-content {
  background: var(--accent-primary);
  color: #fff;
  border-bottom-right-radius: 4px;
}

[data-theme="cyber"] .msg.assistant .msg-content {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(0, 212, 255, 0.12);
  color: #E8E8F0;
}

[data-theme="cyber"] .msg.user .msg-content {
  background: linear-gradient(135deg, #0088CC, #7C3AED);
  box-shadow: 0 2px 12px rgba(0, 212, 255, 0.2);
}

[data-theme="cyber"] .chat-body {
  background: transparent;
}

.typing span {
  animation: blink 1.4s infinite both;
  font-size: 20px;
  line-height: 0;
}

.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
  0%, 80%, 100% { opacity: 0; }
  40% { opacity: 1; }
}

.chat-input-area {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--border-default);
}

.chat-input {
  flex: 1;
  border: 1px solid var(--border-default);
  border-radius: 20px;
  padding: 8px 14px;
  font-size: 13px;
  background: var(--surface-primary);
  color: var(--text-primary);
  outline: none;
  font-family: var(--font-body);
}

.chat-input:focus { border-color: var(--accent-primary); }

[data-theme="cyber"] .chat-input-area {
  border-top-color: rgba(0, 212, 255, 0.15);
}

[data-theme="cyber"] .chat-input {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(0, 212, 255, 0.15);
  color: #E8E8F0;
}

[data-theme="cyber"] .chat-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

[data-theme="cyber"] .chat-input:focus {
  border-color: rgba(0, 212, 255, 0.5);
  box-shadow: 0 0 12px rgba(0, 212, 255, 0.08);
}

.chat-send {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--accent-primary);
  color: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.chat-send:disabled { opacity: 0.5; cursor: not-allowed; }
.chat-send:hover:not(:disabled) { transform: scale(1.1); }

[data-theme="cyber"] .chat-send { background: linear-gradient(135deg, #00D4FF, #A855F7); }

@media (max-width: 480px) {
  .chat-window { left: 12px; right: 12px; width: auto; bottom: 12px; }
}
</style>
