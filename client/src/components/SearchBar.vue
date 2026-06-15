<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const emit = defineEmits(['search'])
const router = useRouter()
const query = ref('')
const showModal = ref(false)

function handleSearch() {
  if (query.value.trim()) {
    router.push({ name: 'Browse', query: { q: query.value.trim() } })
    query.value = ''
    showModal.value = false
  }
}

function handleKeydown(e) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    showModal.value = true
  }
  if (e.key === 'Escape') {
    showModal.value = false
  }
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>

<template>
  <div class="search-bar-wrapper">
    <!-- Desktop Search Bar -->
    <div class="search-bar" @click="showModal = true">
      <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
        <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span class="search-placeholder">搜索书名、作者、关键词...</span>
      <div class="search-shortcut">
        <kbd>⌘</kbd><kbd>K</kbd>
      </div>
    </div>

    <!-- Search Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content">
          <form @submit.prevent="handleSearch" class="modal-search">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
              <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <input
              v-model="query"
              placeholder="搜索书名、作者、关键词..."
              class="modal-input"
              autofocus
              ref="modalInput"
            />
            <button type="submit" class="modal-submit">搜索</button>
          </form>
          <div class="modal-hints">
            <div class="hint-item"><span class="hint-tag">分类</span>数学 · 计算机 · 外语 · 经管 · 理工 · 人文 · 其他</div>
            <div class="hint-item"><span class="hint-tag">书况</span>全新 · 良好 · 有笔记 · 旧</div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.search-bar-wrapper {
  width: 100%;
  max-width: 600px;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all 0.3s;
}

.search-bar:hover {
  border-color: var(--border-strong);
}

.search-bar:focus-within,
.search-bar:hover {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--accent-primary-light);
}

.search-icon {
  color: var(--text-muted);
  flex-shrink: 0;
}

.search-placeholder {
  flex: 1;
  color: var(--text-muted);
  font-size: 15px;
}

.search-shortcut {
  display: flex;
  align-items: center;
  gap: 4px;
}

.search-shortcut kbd {
  padding: 2px 6px;
  background: var(--surface-tertiary);
  border: 1px solid var(--border-default);
  border-radius: 4px;
  font-size: 11px;
  font-family: var(--font-mono);
  color: var(--text-muted);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  z-index: 2000;
  display: flex;
  justify-content: center;
  padding-top: 120px;
}

.modal-content {
  width: 100%;
  max-width: 560px;
  background: var(--surface-secondary);
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--shadow-lg);
  height: fit-content;
}

[data-theme="cyber"] .modal-content {
  border: 1px solid rgba(0, 212, 255, 0.15);
}

.modal-search {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--surface-primary);
  border: 1px solid var(--border-default);
  border-radius: 12px;
}

.modal-search:focus-within {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--accent-primary-light);
}

.modal-input {
  flex: 1;
  border: none;
  background: none;
  outline: none;
  font-size: 16px;
  color: var(--text-primary);
  font-family: var(--font-body);
}

.modal-submit {
  padding: 8px 20px;
  background: var(--accent-primary);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

[data-theme="cyber"] .modal-submit {
  background: linear-gradient(135deg, #00D4FF, #A855F7);
}

.modal-hints {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hint-item {
  font-size: 13px;
  color: var(--text-muted);
}

.hint-tag {
  display: inline-block;
  padding: 2px 8px;
  background: var(--surface-tertiary);
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-right: 8px;
}

@media (max-width: 768px) {
  .modal-overlay { padding-top: 60px; padding-inline: 16px; }
}
</style>
