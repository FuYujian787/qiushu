<script setup>
defineProps({
  courses: { type: Array, default: () => [] },
  selectedCourse: { type: String, default: '' },
})

const emit = defineEmits(['select'])
</script>

<template>
  <nav class="category-nav">
    <h3 class="nav-title">课程分区</h3>
    <div class="nav-list">
      <button
        :class="['nav-item', { active: !selectedCourse }]"
        @click="emit('select', '')"
      >
        全部课程
      </button>
      <button
        v-for="course in courses"
        :key="course.id"
        :class="['nav-item', { active: selectedCourse === course.id }]"
        @click="emit('select', course.id)"
      >
        {{ course.name }}
      </button>
    </div>
  </nav>
</template>

<style scoped>
.category-nav {
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 16px;
}

.nav-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.nav-list { display: flex; flex-direction: column; gap: 2px; }

.nav-item {
  width: 100%;
  padding: 8px 12px;
  border: none;
  background: none;
  border-radius: 6px;
  text-align: left;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  font-family: var(--font-body);
}

.nav-item:hover { background: var(--surface-tertiary); color: var(--accent-primary); }

.nav-item.active {
  background: var(--accent-primary-light);
  color: var(--accent-primary);
  font-weight: 600;
}

[data-theme="cyber"] .nav-item.active {
  background: rgba(0, 212, 255, 0.1);
  color: #00D4FF;
}
</style>
