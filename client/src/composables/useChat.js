import { ref, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

/**
 * AI 对话助手组合式函数
 *
 * 管理对话窗口状态、消息列表、发送/接收消息逻辑。
 * 用于 AIChat 组件和全局对话状态共享。
 */
export function useChat() {
  const auth = useAuthStore()

  const isOpen = ref(false)
  const messages = ref([
    {
      role: 'assistant',
      content: '你好！我是求书小助手 🤖\n\n有什么关于二手书、课程教材的问题可以问我~',
    },
  ])
  const input = ref('')
  const loading = ref(false)
  const chatBodyRef = ref(null)

  /** 切换对话窗口 */
  function toggle() {
    isOpen.value = !isOpen.value
    if (isOpen.value) {
      nextTick(() => scrollToBottom())
    }
  }

  /** 打开对话窗口 */
  function open() {
    isOpen.value = true
    nextTick(() => scrollToBottom())
  }

  /** 关闭对话窗口 */
  function close() {
    isOpen.value = false
  }

  /** 发送消息 */
  async function sendMessage(msg) {
    const text = (msg || input.value).trim()
    if (!text || loading.value || !auth.isLoggedIn) return

    messages.value.push({ role: 'user', content: text })
    input.value = ''
    loading.value = true

    try {
      const history = messages.value.slice(0, -1).map((m) => ({
        role: m.role,
        content: m.content,
      }))

      const res = await api.post('/ai/chat', {
        message: text,
        history,
      })
      messages.value.push({ role: 'assistant', content: res.data.reply })
    } catch {
      messages.value.push({
        role: 'assistant',
        content: '抱歉，AI 服务暂时不可用，请稍后再试~',
      })
    } finally {
      loading.value = false
      await nextTick()
      scrollToBottom()
    }
  }

  /** 滚动到对话底部 */
  function scrollToBottom() {
    if (chatBodyRef.value) {
      chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
    }
  }

  /** 清空对话历史 */
  function clearHistory() {
    messages.value = [
      {
        role: 'assistant',
        content: '你好！我是求书小助手 🤖\n\n有什么关于二手书、课程教材的问题可以问我~',
      },
    ]
  }

  return {
    isOpen,
    messages,
    input,
    loading,
    chatBodyRef,
    toggle,
    open,
    close,
    sendMessage,
    scrollToBottom,
    clearHistory,
  }
}
