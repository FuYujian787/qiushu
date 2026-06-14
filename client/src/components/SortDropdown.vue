<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: 'created_at_desc' },
})

const emit = defineEmits(['update:modelValue'])

const options = [
  { value: 'created_at_desc', label: '最新发布' },
  { value: 'price_asc', label: '价格从低到高' },
  { value: 'price_desc', label: '价格从高到低' },
]

const current = ref(props.modelValue)

watch(current, (val) => emit('update:modelValue', val))
</script>

<template>
  <div class="sort-dropdown">
    <span class="sort-label">排序：</span>
    <select v-model="current" class="sort-select">
      <option v-for="opt in options" :key="opt.value" :value="opt.value">
        {{ opt.label }}
      </option>
    </select>
  </div>
</template>

<style scoped>
.sort-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-label {
  font-size: 13px;
  color: var(--text-muted);
  white-space: nowrap;
}

.sort-select {
  padding: 8px 12px;
  border: 1px solid var(--border-default);
  border-radius: 8px;
  background: var(--surface-secondary);
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
  cursor: pointer;
  font-family: var(--font-body);
}

.sort-select:focus {
  border-color: var(--accent-primary);
}
</style>
