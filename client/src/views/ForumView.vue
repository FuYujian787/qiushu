<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'
import CategoryNav from '@/components/CategoryNav.vue'
import PostForm from '@/components/PostForm.vue'
import PostList from '@/components/PostList.vue'

const router = useRouter()
const auth = useAuthStore()

const posts = ref([])
const courses = ref([])
const loading = ref(false)
const selectedCourse = ref('')
const selectedType = ref('')
const showPostForm = ref(false)

const postTypes = ['选课求助', '老师评价', '考试资料', '学习笔记', '书评', '求书', '其他']

onMounted(async () => {
  await loadCourses()
  await loadPosts()
})

async function loadCourses() {
  try {
    const res = await api.get('/forum/courses')
    courses.value = res.data || []
  } catch { /* ignore */ }
}

async function loadPosts() {
  loading.value = true
  try {
    const params = {}
    if (selectedCourse.value) params.course_id = selectedCourse.value
    if (selectedType.value) params.type = selectedType.value
    const res = await api.get('/forum/posts', { params })
    posts.value = res.data?.posts || []
  } catch { /* ignore */ }
  finally { loading.value = false }
}

function onSelectCourse(courseId) {
  selectedCourse.value = courseId
  loadPosts()
}

function onSelectType(type) {
  selectedType.value = type
  loadPosts()
}

function onPostClick(postId) {
  router.push({ name: 'PostDetail', params: { id: postId } })
}

function onPosted() {
  showPostForm.value = false
  loadPosts()
}

function startPost() {
  if (!auth.isLoggedIn) {
    router.push({ name: 'Auth', query: { redirect: '/forum' } })
    return
  }
  showPostForm.value = !showPostForm.value
}
</script>

<template>
  <div class="forum-page page-enter">
    <div class="page-container">
      <div class="forum-header">
        <h1 class="page-title">课程论坛</h1>
        <button class="new-post-btn" @click="startPost">
          {{ showPostForm ? '取消' : '发帖' }}
        </button>
      </div>

      <div class="forum-layout">
        <!-- Sidebar: Category Navigation -->
        <aside class="forum-sidebar">
          <CategoryNav
            :courses="courses"
            :selected-course="selectedCourse"
            @select="onSelectCourse"
          />
        </aside>

        <!-- Main Content -->
        <div class="forum-main">
          <!-- Type Filter Chips -->
          <div class="type-filter">
            <button
              :class="['type-chip', { active: !selectedType }]"
              @click="onSelectType('')"
            >全部</button>
            <button
              v-for="type in postTypes"
              :key="type"
              :class="['type-chip', { active: selectedType === type }]"
              @click="onSelectType(type)"
            >{{ type }}</button>
          </div>

          <!-- New Post Form -->
          <PostForm
            v-if="showPostForm"
            :courses="courses"
            @posted="onPosted"
          />

          <!-- Post List -->
          <PostList
            :posts="posts"
            :loading="loading"
            @post-click="onPostClick"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-title {
  font-family: var(--font-display);
  font-size: 24px;
  color: var(--text-primary);
  font-weight: 700;
}

.forum-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.new-post-btn {
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

[data-theme="cyber"] .new-post-btn { background: linear-gradient(135deg, #00D4FF, #A855F7); }

.forum-layout {
  display: flex;
  gap: 24px;
}

.forum-sidebar { width: 200px; flex-shrink: 0; }

.forum-main { flex: 1; min-width: 0; }

.type-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
}

.type-chip {
  padding: 6px 14px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  background: transparent;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.type-chip:hover, .type-chip.active {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

@media (max-width: 768px) {
  .forum-layout { flex-direction: column; }
  .forum-sidebar { width: 100%; }
}
</style>
