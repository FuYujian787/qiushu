<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['update:modelValue'])

const filters = ref({ ...props.modelValue })

const categories = ['数学', '计算机', '外语', '经管', '理工', '人文', '其他']
const conditions = ['全新', '良好', '有笔记', '旧']
const priceOptions = [
  { label: '全部', min: null, max: null },
  { label: '20元以下', min: 0, max: 20 },
  { label: '20-40元', min: 20, max: 40 },
  { label: '40-60元', min: 40, max: 60 },
  { label: '60元以上', min: 60, max: null },
]

// 必须 emit 新对象（不能传同一引用），否则 v-model 的 ref 比较 Object.is 判定值未变，父组件 watch 不触发
watch(filters, (val) => emit('update:modelValue', { ...val }), { deep: true })

function clearFilters() {
  filters.value = { category: '', condition: '', priceMin: null, priceMax: null }
}
</script>

<template>
  <div class="filter-panel">
    <div class="filter-header">
      <h3>筛选</h3>
      <button class="clear-btn" @click="clearFilters">清除</button>
    </div>

    <div class="filter-section">
      <h4>分类</h4>
      <div class="filter-options">
        <button
          v-for="cat in categories"
          :key="cat"
          :class="['filter-chip', { active: filters.category === cat }]"
          @click="filters.category = filters.category === cat ? '' : cat"
        >
          {{ cat }}
        </button>
      </div>
    </div>

    <div class="filter-section">
      <h4>书况</h4>
      <div class="filter-options">
        <button
          v-for="cond in conditions"
          :key="cond"
          :class="['filter-chip', { active: filters.condition === cond }]"
          @click="filters.condition = filters.condition === cond ? '' : cond"
        >
          {{ cond }}
        </button>
      </div>
    </div>

    <div class="filter-section">
      <h4>价格区间</h4>
      <div class="filter-options">
        <button
          v-for="opt in priceOptions"
          :key="opt.label"
          :class="['filter-chip', { active: filters.priceMin === opt.min && filters.priceMax === opt.max }]"
          @click="filters.priceMin = opt.min; filters.priceMax = opt.max"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.filter-panel {
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 20px;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-header h3 {
  font-family: var(--font-display);
  font-size: 16px;
  color: var(--text-primary);
}

.clear-btn {
  background: none;
  border: none;
  color: var(--accent-primary);
  font-size: 13px;
  cursor: pointer;
  font-weight: 500;
}

.clear-btn:hover { text-decoration: underline; }

.filter-section {
  margin-bottom: 20px;
}

.filter-section h4 {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 10px;
  font-weight: 600;
}

.filter-options {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.filter-chip {
  padding: 6px 14px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  background: transparent;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-chip:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.filter-chip.active {
  background: var(--accent-primary);
  color: #fff;
  border-color: var(--accent-primary);
}

[data-theme="cyber"] .filter-chip.active {
  background: linear-gradient(135deg, #00D4FF, #A855F7);
  border-color: transparent;
}
</style>
