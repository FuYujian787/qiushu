<script setup>
import PostCard from './PostCard.vue'

defineProps({
  posts: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['post-click'])
</script>

<template>
  <div class="post-list">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="posts.length === 0" class="empty">
      <p>暂无帖子</p>
    </div>
    <div v-else class="list">
      <PostCard
        v-for="post in posts"
        :key="post.id"
        :post="post"
        @click="emit('post-click', $event)"
      />
    </div>
  </div>
</template>

<script>
export default { name: 'PostList' }
</script>

<style scoped>
.list { display: flex; flex-direction: column; gap: 12px; }

.loading, .empty { text-align: center; padding: 40px; color: var(--text-muted); font-size: 14px; }
</style>
