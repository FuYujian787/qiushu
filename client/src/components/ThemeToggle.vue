<script setup>
import { useTheme } from '@/composables/useTheme'

const { theme, toggle } = useTheme()
</script>

<template>
  <button class="theme-toggle" @click="toggle" :title="theme === 'paper' ? '切换赛博模式' : '切换书韵模式'">
    <!-- 书韵模式: 太阳/月亮的图标 -->
    <svg v-if="theme === 'paper'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
      <path d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
      <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </button>
</template>

<style scoped>
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border-default);
  border-radius: 50%;
  background: var(--surface-secondary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s;
}

.theme-toggle:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
  box-shadow: 0 0 12px var(--accent-primary-light);
}

[data-theme="cyber"] .theme-toggle:hover {
  box-shadow: 0 0 16px rgba(0, 212, 255, 0.3);
}
</style>
