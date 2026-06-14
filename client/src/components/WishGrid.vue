<script setup>
import WishCard from './WishCard.vue'

defineProps({
  wishes: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['have-book'])
</script>

<template>
  <div class="wish-grid">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="wishes.length === 0" class="empty">
      <p>还没有求书帖，快来许愿吧 ✨</p>
    </div>
    <div v-else class="grid">
      <WishCard
        v-for="wish in wishes"
        :key="wish.id"
        :wish="wish"
        @have-book="emit('have-book', $event)"
      />
    </div>
  </div>
</template>

<style scoped>
.grid { display: flex; flex-direction: column; gap: 12px; }

.loading, .empty { text-align: center; padding: 40px; color: var(--text-muted); font-size: 14px; }
</style>
