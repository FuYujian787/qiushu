<script setup>
defineProps({
  icon: { type: String, default: 'book' },
  title: { type: String, default: '暂无内容' },
  subtitle: { type: String, default: '书山有路，待君来寻' },
  action: { type: String, default: '' },
})

const emit = defineEmits(['action'])
</script>

<template>
  <div class="empty-state">
    <div class="empty-icon">
      <svg v-if="icon === 'book'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
        <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
        <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <h3 class="empty-title">{{ title }}</h3>
    <p class="empty-subtitle">{{ subtitle }}</p>
    <button v-if="action" class="empty-action" @click="$emit('action')">{{ action }}</button>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 24px;
  text-align: center;
}

.empty-icon {
  color: var(--text-muted);
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-title {
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.empty-subtitle {
  color: var(--text-muted);
  font-size: 14px;
  line-height: 1.6;
  max-width: 300px;
}

.empty-action {
  margin-top: 20px;
  padding: 10px 24px;
  background: var(--accent-primary);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.empty-action:hover {
  background: var(--accent-primary-hover);
  transform: translateY(-1px);
}
</style>
