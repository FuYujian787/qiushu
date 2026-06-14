<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'
import WishGrid from '@/components/WishGrid.vue'
import WishForm from '@/components/WishForm.vue'

const router = useRouter()
const auth = useAuthStore()

const wishes = ref([])
const loading = ref(false)
const showForm = ref(false)

onMounted(async () => {
  await loadWishes()
})

async function loadWishes() {
  loading.value = true
  try {
    const res = await api.get('/wishes')
    wishes.value = res.data?.wishes || []
  } catch { /* ignore */ }
  finally { loading.value = false }
}

function onHaveBook(title) {
  if (!auth.isLoggedIn) {
    router.push({ name: 'Auth', query: { redirect: '/publish' } })
    return
  }
  router.push({ name: 'Publish', query: { title } })
}

function onPosted() {
  showForm.value = false
  loadWishes()
}
</script>

<template>
  <div class="wishes-page page-enter">
    <div class="page-container">
      <div class="wishes-header">
        <h1 class="page-title">求书许愿墙</h1>
        <button class="wish-btn" @click="showForm = !showForm">
          {{ showForm ? '取消' : '发布求书' }}
        </button>
      </div>

      <!-- Wish Form -->
      <WishForm
        v-if="showForm"
        @posted="onPosted"
      />

      <!-- Wish Grid -->
      <WishGrid
        :wishes="wishes"
        :loading="loading"
        @have-book="onHaveBook"
      />
    </div>
  </div>
</template>

<style scoped>
.wishes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-family: var(--font-display);
  font-size: 24px;
  color: var(--text-primary);
  font-weight: 700;
}

.wish-btn {
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

[data-theme="cyber"] .wish-btn { background: linear-gradient(135deg, #00D4FF, #A855F7); }
</style>
