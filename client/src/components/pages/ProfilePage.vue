<template>
  <div class="profile-page">
    <!-- ===== 1. Hero 英雄卡片 ===== -->
    <section class="profile-hero">
      <div class="hero-avatar-ring" @click="triggerFileInput">
        <div class="hero-avatar-inner">
          <img :src="currentAvatarSrc || store.DEFAULT_AVATAR" class="hero-avatar-img" />
          <div class="hero-avatar-overlay">
            <span class="iconify" data-icon="solar:camera-outline" data-width="24"></span>
            <span class="hero-avatar-hint">更换头像</span>
          </div>
        </div>
        <div class="hero-ring-glow"></div>
      </div>
      <input ref="fileInput" type="file" accept="image/*" class="hidden-input" @change="onAvatarChange" />

      <h1 class="hero-name">{{ user.name }}</h1>

      <div class="hero-level-badge" :class="'level-' + userLevel.key">
        <span class="iconify" :data-icon="userLevel.icon" data-width="16"></span>
        <span>{{ userLevel.label }}</span>
      </div>

      <div class="hero-badges">
        <span class="hero-badge">
          <span class="iconify" data-icon="solar:buildings-outline" data-width="14"></span>
          {{ user.college }}
        </span>
        <span class="hero-badge-divider"></span>
        <span class="hero-badge">
          <span class="iconify" data-icon="solar:bookmark-outline" data-width="14"></span>
          {{ user.grade }}
        </span>
      </div>
    </section>

    <!-- ===== 2. 数据仪表盘 ===== -->
    <section class="profile-stats">
      <div class="stat-card" @click="store.navigateTo('publish')">
        <div class="stat-card-icon stat-icon-publish">
          <span class="iconify" data-icon="solar:book-2-outline" data-width="22"></span>
        </div>
        <span class="stat-card-value apple-price-mono">{{ stats.booksPublished }}</span>
        <span class="stat-card-label">已发布</span>
      </div>
      <div class="stat-card">
        <div class="stat-card-icon stat-icon-sold">
          <span class="iconify" data-icon="solar:cart-check-outline" data-width="22"></span>
        </div>
        <span class="stat-card-value apple-price-mono">{{ stats.booksSold }}</span>
        <span class="stat-card-label">已售出</span>
      </div>
      <div class="stat-card">
        <div class="stat-card-icon stat-icon-earn">
          <span class="iconify" data-icon="solar:dollar-minimalistic-outline" data-width="22"></span>
        </div>
        <span class="stat-card-value apple-price-mono">¥{{ stats.earnings }}</span>
        <span class="stat-card-label">收益</span>
      </div>
      <div class="stat-card" @click="store.navigateTo('community')">
        <div class="stat-card-icon stat-icon-post">
          <span class="iconify" data-icon="solar:chat-square-outline" data-width="22"></span>
        </div>
        <span class="stat-card-value apple-price-mono">{{ stats.postsCount }}</span>
        <span class="stat-card-label">思想</span>
      </div>
    </section>

    <!-- ===== 3. 会员等级进度 ===== -->
    <section class="level-progress-card" v-if="nextLevel">
      <div class="level-progress-header">
        <span class="level-progress-current">{{ userLevel.label }}</span>
        <span class="level-progress-arrow">→</span>
        <span class="level-progress-next">{{ nextLevel.label }}</span>
      </div>
      <div class="level-progress-bar-track">
        <div class="level-progress-bar-fill" :style="{ width: levelProgressPercent + '%' }"></div>
        <div class="level-progress-bar-glow"></div>
      </div>
      <p class="level-progress-hint">{{ levelProgressHint }}</p>
    </section>

    <!-- ===== 4. 我的服务 ===== -->
    <section class="services-section">
      <h3 class="section-title">
        <span class="iconify" data-icon="solar:widget-3-outline" data-width="18"></span>
        我的服务
      </h3>
      <div class="services-grid">
        <button class="service-card" @click="store.navigateTo('orders')">
          <div class="service-icon-wrap service-icon-orders">
            <span class="iconify" data-icon="solar:clipboard-list-outline" data-width="22"></span>
          </div>
          <span class="service-label">我的订单</span>
          <span class="service-badge" v-if="orderCount > 0">{{ orderCount }}</span>
        </button>
        <button class="service-card" @click="store.navigateTo('cart')">
          <div class="service-icon-wrap service-icon-cart">
            <span class="iconify" data-icon="solar:cart-large-2-outline" data-width="22"></span>
          </div>
          <span class="service-label">购物车</span>
          <span class="service-badge" v-if="cartCount > 0">{{ cartCount }}</span>
        </button>
        <button class="service-card" @click="store.navigateTo('notifications')">
          <div class="service-icon-wrap service-icon-notif">
            <span class="iconify" data-icon="solar:bell-outline" data-width="22"></span>
          </div>
          <span class="service-label">消息通知</span>
          <span class="service-badge service-badge-dot" v-if="unreadNotifCount > 0"></span>
        </button>
        <button class="service-card" @click="store.navigateTo('community')">
          <div class="service-icon-wrap service-icon-community">
            <span class="iconify" data-icon="solar:people-nearby-outline" data-width="22"></span>
          </div>
          <span class="service-label">学习社区</span>
        </button>
        <button class="service-card" @click="store.navigateTo('publish')">
          <div class="service-icon-wrap service-icon-publish2">
            <span class="iconify" data-icon="solar:upload-square-outline" data-width="22"></span>
          </div>
          <span class="service-label">发布闲置</span>
        </button>
        <button class="service-card" @click="store.navigateTo('chat')">
          <div class="service-icon-wrap service-icon-chat">
            <span class="iconify" data-icon="solar:chat-round-dots-outline" data-width="22"></span>
          </div>
          <span class="service-label">我的私聊</span>
        </button>
      </div>
    </section>

    <!-- ===== 5. 最近动态 ===== -->
    <section class="activity-section" v-if="recentActivities.length > 0">
      <h3 class="section-title">
        <span class="iconify" data-icon="solar:history-outline" data-width="18"></span>
        最近动态
      </h3>
      <div class="activity-list">
        <div
          class="activity-item"
          v-for="(act, idx) in recentActivities"
          :key="idx"
          @click="act.action ? act.action() : null"
          :class="{ 'activity-clickable': act.action }"
        >
          <div class="activity-icon" :class="'activity-' + act.type">
            <span class="iconify" :data-icon="act.icon" data-width="17"></span>
          </div>
          <div class="activity-body">
            <p class="activity-text">{{ act.text }}</p>
            <span class="activity-time">{{ act.time }}</span>
          </div>
          <span class="activity-arrow" v-if="act.action">
            <span class="iconify" data-icon="solar:alt-arrow-right-outline" data-width="16"></span>
          </span>
        </div>
      </div>
    </section>

    <!-- ===== 5.5 教务信息（浙大学生专属） ===== -->
    <section class="edu-section" v-if="showEduSection">
      <h3 class="section-title">
        <span class="iconify" data-icon="solar:book-open-outline" data-width="18"></span>
        浙大教务
        <span class="edu-source-badge edu-source-badge--cas" v-if="eduDataSrc === 'cas'">CAS认证</span>
      </h3>

      <!-- 学籍卡片 -->
      <div class="edu-student-card">
        <div class="edu-student-row">
          <span class="edu-label">学号</span>
          <span class="edu-value apple-price-mono">{{ eduStudent.student_id }}</span>
        </div>
        <div class="edu-student-row">
          <span class="edu-label">专业</span>
          <span class="edu-value">{{ eduStudent.department }}</span>
        </div>
        <div class="edu-student-row">
          <span class="edu-label">班级</span>
          <span class="edu-value">{{ eduStudent.class_name }}</span>
        </div>
        <div class="edu-student-row">
          <span class="edu-label">校区</span>
          <span class="edu-value">{{ eduStudent.campus }}</span>
        </div>
      </div>

      <!-- 成绩概览 -->
      <div class="edu-grades-summary" v-if="eduGrades.gpa_overall > 0">
        <div class="edu-gpa-card">
          <span class="edu-gpa-value">{{ eduGrades.gpa_overall }}</span>
          <span class="edu-gpa-label">综合绩点</span>
        </div>
        <div class="edu-gpa-card">
          <span class="edu-gpa-value">{{ eduGrades.average_score }}</span>
          <span class="edu-gpa-label">平均分</span>
        </div>
        <div class="edu-gpa-card">
          <span class="edu-gpa-value">{{ eduGrades.total_credits }}</span>
          <span class="edu-gpa-label">已修学分</span>
        </div>
      </div>

      <!-- 课程表 -->
      <div class="edu-courses-card" v-if="eduCourses.length > 0">
        <h4 class="edu-subtitle">本学期课程</h4>
        <div class="edu-course-list">
          <div class="edu-course-item" v-for="(c, i) in eduCourses" :key="i">
            <div class="edu-course-left">
              <span class="edu-course-weekday">{{ c.weekday }}</span>
              <span class="edu-course-time">{{ c.start_time }}-{{ c.end_time }}</span>
            </div>
            <div class="edu-course-right">
              <span class="edu-course-name">{{ c.course_name }}</span>
              <span class="edu-course-meta">{{ c.location }} · {{ c.teacher }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== 6. 编辑资料 ===== -->
    <section class="profile-edit-card">
      <div class="edit-card-header">
        <h2 class="edit-card-title">
          <span class="iconify" data-icon="solar:pen-2-outline" data-width="20"></span>
          编辑资料
        </h2>
        <p class="edit-card-subtitle">完善个人信息，让同学更容易找到你</p>
      </div>

      <div class="edit-form-grid">
        <div class="form-field">
          <label class="form-label">用户名</label>
          <input v-model="editName" class="form-input" placeholder="你的用户名" />
        </div>
        <div class="form-field">
          <label class="form-label">学院</label>
          <input v-model="editCollege" class="form-input" placeholder="所属学院" />
        </div>
        <div class="form-field">
          <label class="form-label">年级</label>
          <select v-model="editGrade" class="form-input form-select">
            <option v-for="g in grades" :key="g" :value="g">{{ g }}</option>
          </select>
        </div>
        <div class="form-field">
          <label class="form-label">收货地址</label>
          <input v-model="editAddress" class="form-input" placeholder="请输入详细收货地址" />
        </div>
        <div class="form-field">
          <label class="form-label">新密码</label>
          <input v-model="editPw" type="password" class="form-input" placeholder="留空则不修改密码" />
        </div>
        <div class="form-field">
          <label class="form-label">确认密码</label>
          <input v-model="editPw2" type="password" class="form-input" placeholder="再次输入新密码" />
        </div>
      </div>

      <button class="save-btn" @click="saveProfile">
        <span class="iconify" data-icon="solar:check-circle-outline" data-width="18"></span>
        保存修改
      </button>
    </section>

    <!-- ===== 7. 快捷私聊 ===== -->
    <section class="quick-chat-card">
      <div class="quick-chat-header">
        <span class="iconify" data-icon="solar:chat-round-dots-outline" data-width="18"></span>
        <span>快速私聊</span>
      </div>
      <div class="quick-chat-body">
        <input v-model="chatTarget" placeholder="输入对方用户名" class="chat-input" @keydown.enter="startChat" />
        <button class="chat-submit-btn" @click="startChat" :disabled="!chatTarget.trim()">
          <span class="iconify" data-icon="solar:plain-2-outline" data-width="16"></span>
        </button>
      </div>
    </section>

    <!-- ===== 8. 设置 ===== -->
    <section class="settings-card">
      <h3 class="section-title">
        <span class="iconify" data-icon="solar:settings-outline" data-width="18"></span>
        设置
      </h3>
      <div class="settings-list">
        <div class="settings-item">
          <div class="settings-item-left">
            <span class="iconify" data-icon="solar:bell-bing-outline" data-width="18"></span>
            <span>通知设置</span>
          </div>
          <span class="settings-item-right">
            <span class="iconify" data-icon="solar:alt-arrow-right-outline" data-width="16"></span>
          </span>
        </div>
        <div class="settings-item">
          <div class="settings-item-left">
            <span class="iconify" data-icon="solar:shield-check-outline" data-width="18"></span>
            <span>隐私与安全</span>
          </div>
          <span class="settings-item-right">
            <span class="iconify" data-icon="solar:alt-arrow-right-outline" data-width="16"></span>
          </span>
        </div>
        <div class="settings-item">
          <div class="settings-item-left">
            <span class="iconify" data-icon="solar:info-circle-outline" data-width="18"></span>
            <span>关于去书</span>
          </div>
          <span class="settings-item-right">
            <span class="settings-item-text">v2.0</span>
            <span class="iconify" data-icon="solar:alt-arrow-right-outline" data-width="16"></span>
          </span>
        </div>
      </div>
    </section>

    <!-- ===== 9. 退出登录 ===== -->
    <button class="logout-btn" @click="doLogout">
      <span class="iconify" data-icon="solar:logout-2-outline" data-width="18"></span>
      退出登录
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useStore } from '../../stores/useStore'

const store = useStore()
const fileInput = ref(null)
const grades = ['大一', '大二', '大三', '大四', '研究生']

const user = computed(() => store.currentUser.value || {
  name: '张伟', college: '管理学院', grade: '大三', address: '', avatar: store.DEFAULT_AVATAR,
})

const editName = ref('')
const editPw = ref('')
const editPw2 = ref('')
const editCollege = ref('')
const editGrade = ref('')
const editAddress = ref('')
const currentAvatarSrc = ref(store.DEFAULT_AVATAR)
const chatTarget = ref('')

const stats = reactive({
  booksPublished: 0,
  booksSold: 0,
  earnings: '0.00',
  postsCount: 0,
})

const LEVELS = [
  { key: 'bronze', label: '青铜书友', icon: 'solar:bookmark-circle-outline', min: 0 },
  { key: 'silver', label: '白银书友', icon: 'solar:medal-ribbons-star-outline', min: 5 },
  { key: 'gold', label: '黄金书友', icon: 'solar:crown-star-outline', min: 15 },
  { key: 'diamond', label: '钻石书友', icon: 'solar:diamond-outline', min: 30 },
  { key: 'legend', label: '传奇书友', icon: 'solar:star-shine-outline', min: 60 },
]

const totalActivity = computed(() => stats.booksPublished + stats.booksSold + stats.postsCount)
const userLevel = computed(() => {
  let lv = LEVELS[0]
  for (const l of LEVELS) {
    if (totalActivity.value >= l.min) lv = l
  }
  return lv
})
const nextLevel = computed(() => {
  const idx = LEVELS.findIndex(l => l.key === userLevel.value.key)
  return idx < LEVELS.length - 1 ? LEVELS[idx + 1] : null
})
const levelProgressPercent = computed(() => {
  if (!nextLevel.value) return 100
  const range = nextLevel.value.min - userLevel.value.min
  if (range <= 0) return 100
  const prog = totalActivity.value - userLevel.value.min
  return Math.min(100, Math.max(0, (prog / range) * 100))
})
const levelProgressHint = computed(() => {
  if (!nextLevel.value) return '恭喜！你已达到最高等级 🎉'
  const remaining = nextLevel.value.min - totalActivity.value
  return `再获得 ${remaining} 点活跃即可升级为 ${nextLevel.value.label}`
})

const orderCount = computed(() => (store.orders.value || []).length)
const cartCount = computed(() => (store.cart || []).length)
const unreadNotifCount = computed(() => {
  const all = store.userNotifications.value || {}
  return Object.values(all).filter(n => n.unread).length
})

const recentActivities = computed(() => {
  if (!store.isLoggedIn.value) return []
  const name = store.currentUser.value?.name
  if (!name) return []

  const items = []

  const allOrders = store.orders.value || []
  const myOrders = allOrders.filter(o => o.buyer === name || o.seller === name)
  for (const o of myOrders.slice(0, 3)) {
    const isBuyer = o.buyer === name
    items.push({
      type: 'order',
      icon: isBuyer ? 'solar:cart-check-outline' : 'solar:check-read-outline',
      text: isBuyer ? `购买了《${o.title || '未知书籍'}》` : `售出了《${o.title || '未知书籍'}》`,
      time: o.date || '',
      action: () => store.navigateTo('orders'),
    })
  }

  const allPosts = store.getMergedPosts()
  const myPosts = allPosts.filter(p => p.author === name)
  for (const p of myPosts.slice(0, 3)) {
    items.push({
      type: 'post',
      icon: 'solar:document-add-outline',
      text: p.title ? `发表了「${p.title}」` : '发表了一条思想',
      time: p.time || '',
      action: () => store.navigateTo('community'),
    })
  }

  items.sort((a, b) => (b.time || '').localeCompare(a.time || ''))
  return items.slice(0, 4)
})

function loadStats() {
  if (!store.isLoggedIn.value || !store.currentUser.value) return
  const name = store.currentUser.value.name

  const userBooks = store.fetchUserBooks(name)
  stats.booksPublished = userBooks.books?.length || 0

  const sellerStats = store.fetchSellerStats(name) || {}
  stats.booksSold = sellerStats.total_books_sold || 0
  stats.earnings = (sellerStats.total_earnings || 0).toFixed(2)

  const allPosts = store.getMergedPosts()
  stats.postsCount = allPosts.filter(p => p.author === name).length
}

const eduStudent = reactive({
  student_id: '',
  department: '',
  class_name: '',
  campus: '',
})
const eduGrades = reactive({ gpa_overall: 0, average_score: 0, total_credits: 0 })
const eduCourses = ref([])
const eduDataSrc = ref('')
const showEduSection = computed(() => {
  if (!store.isLoggedIn.value || !store.currentUser.value) return false
  const u = store.currentUser.value
  return !!(u.studentId || u.name?.startsWith?.('32'))
})

async function loadEduData() {
  const uid = store.currentUser.value?.studentId || store.currentUser.value?.name
  if (!uid) return

  try {
    const [infoRes, gradesRes, coursesRes] = await Promise.all([
      fetch(`/api/zju/student-info?student_id=${uid}`),
      fetch(`/api/zju/grades?student_id=${uid}`),
      fetch(`/api/zju/courses?student_id=${uid}`),
    ])

    if (infoRes.ok) {
      const infoData = await infoRes.json()
      if (infoData.success) {
        Object.assign(eduStudent, infoData.student)
        eduDataSrc.value = infoData.data_source || ''
      }
    }

    if (gradesRes.ok) {
      const gradesData = await gradesRes.json()
      if (gradesData.success && gradesData.grades) {
        eduGrades.gpa_overall = gradesData.grades.gpa_overall || 0
        eduGrades.average_score = gradesData.grades.average_score || 0
        eduGrades.total_credits = gradesData.grades.total_credits || 0
      }
    }

    if (coursesRes.ok) {
      const coursesData = await coursesRes.json()
      if (coursesData.success && coursesData.courses?.courses) {
        eduCourses.value = coursesData.courses.courses
      }
    }
  } catch (e) {
    console.warn('[Edu] 教务数据加载失败:', e.message)
  }
}

function syncFormFromUser() {
  currentAvatarSrc.value = user.value.avatar || store.DEFAULT_AVATAR
  editName.value = user.value.name || ''
  editCollege.value = user.value.college || ''
  editGrade.value = user.value.grade || ''
  editAddress.value = user.value.address || ''
  editPw.value = ''
  editPw2.value = ''
}

onMounted(() => {
  loadStats()
  syncFormFromUser()
  loadEduData()
})

function triggerFileInput() {
  fileInput.value?.click()
}

function onAvatarChange(e) {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => {
    currentAvatarSrc.value = ev.target.result
  }
  reader.readAsDataURL(file)
}

function saveProfile() {
  if (!store.isLoggedIn.value || !store.currentUser.value) return
  if (!editName.value.trim()) { alert('用户名不能为空'); return }
  if (editPw.value && editPw.value !== editPw2.value) { alert('两次密码不一致'); return }

  const oldName = store.currentUser.value.name
  if (editName.value !== oldName && store.userExists(editName.value)) {
    alert('用户名已被占用'); return
  }

  const updates = {
    name: editName.value.trim(),
    college: editCollege.value,
    grade: editGrade.value,
    address: editAddress.value,
    avatar: currentAvatarSrc.value,
  }
  if (editPw.value) updates.password = editPw.value

  store.updateUser(oldName, updates)
  store.currentUser.value = { ...store.currentUser.value, ...updates }
  alert('个人资料已更新')
  loadStats()
}

function doLogout() {
  store.logout()
}

function startChat() {
  const target = chatTarget.value.trim()
  if (!target) return
  if (!store.isLoggedIn.value) { alert('请先登录'); return }
  if (target === store.currentUser.value?.name) { alert('不能和自己私聊'); return }
  sessionStorage.setItem('chat_target_user', target)
  store.navigateTo('chat')
}
</script>

<style scoped>
/* ================================================================
   Profile Page — Apple 级个人中心 v3（功能丰富版）
   布局：Hero → 数据仪表盘 → 等级进度 → 服务入口 → 动态 → 编辑 → 私聊 → 设置 → 退出
   ================================================================ */
.profile-page {
  max-width: 42rem;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding-bottom: 3rem;
}

/* ===== 通用 section 标题 ===== */
.section-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.9rem;
  letter-spacing: -0.01em;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* ===== 1. Hero 英雄卡片 ===== */
.profile-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2.5rem 2rem 1.75rem;
  background: var(--glass-bg-card);
  backdrop-filter: blur(var(--blur-md)) saturate(1.4);
  -webkit-backdrop-filter: blur(var(--blur-md)) saturate(1.4);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md), var(--shadow-glow);
  position: relative;
}

.hero-avatar-ring {
  position: relative;
  width: 6.5rem;
  height: 6.5rem;
  border-radius: 50%;
  padding: 3px;
  background: linear-gradient(135deg, #af52de 0%, #5ac8fa 100%);
  cursor: pointer;
  transition: transform 0.3s var(--ease-spring);
}

.hero-avatar-ring:hover { transform: scale(1.05); }
.hero-avatar-ring:active { transform: scale(0.97); }

.hero-ring-glow {
  position: absolute;
  inset: -8px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(175,82,222,0.2), rgba(90,200,250,0.2));
  filter: blur(16px);
  z-index: -1;
  pointer-events: none;
}

.hero-avatar-inner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
  position: relative;
  background: #e8e4f0;
}

.hero-avatar-img { width: 100%; height: 100%; object-fit: cover; }

.hero-avatar-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.35);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.3rem;
  opacity: 0;
  transition: opacity 0.25s var(--ease-out);
  color: #fff;
}

.hero-avatar-ring:hover .hero-avatar-overlay { opacity: 1; }

.hero-avatar-hint {
  font-size: 0.65rem;
  font-weight: 500;
  letter-spacing: 0.03em;
}

.hero-name {
  font-size: 1.65rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 1.1rem 0 0.4rem;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.hero-level-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.8rem;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  margin-bottom: 0.6rem;
}

.level-bronze { background: rgba(180,140,100,0.15); color: #8b6914; border: 1px solid rgba(180,140,100,0.3); }
.level-silver { background: rgba(160,170,190,0.15); color: #5a6378; border: 1px solid rgba(160,170,190,0.35); }
.level-gold { background: rgba(212,175,55,0.16); color: #9b7b1c; border: 1px solid rgba(212,175,55,0.35); }
.level-diamond { background: rgba(100,180,255,0.16); color: #2d6db5; border: 1px solid rgba(100,180,255,0.35); }
.level-legend { background: linear-gradient(135deg, rgba(175,82,222,0.16), rgba(255,100,100,0.14)); color: #7b3fc0; border: 1px solid rgba(175,82,222,0.4); }

.hero-badges {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.28rem 0.7rem;
  background: rgba(255,255,255,0.55);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.hero-badge-divider {
  width: 4px; height: 4px;
  border-radius: 50%;
  background: var(--text-tertiary);
  opacity: 0.5;
}

/* ===== 2. 数据仪表盘 ===== */
.profile-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.stat-card {
  background: var(--glass-bg-card);
  backdrop-filter: blur(var(--blur-sm)) saturate(1.3);
  -webkit-backdrop-filter: blur(var(--blur-sm)) saturate(1.3);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: 1.1rem 0.6rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  box-shadow: var(--shadow-xs);
  cursor: default;
  transition: transform 0.2s var(--ease-out), box-shadow 0.2s var(--ease-out);
}

.stat-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-sm), var(--shadow-glow); }

.stat-card-icon {
  width: 3rem; height: 3rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background: rgba(255,255,255,0.65);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  transition: transform 0.3s var(--ease-spring);
}
.stat-card-icon::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 50%;
  pointer-events: none;
  border: 1px solid rgba(255,255,255,0.8);
}
.stat-card-icon::after {
  content: '';
  position: absolute;
  width: 55%; height: 55%;
  top: 6%; left: 10%;
  border-radius: 50%;
  pointer-events: none;
  background: radial-gradient(ellipse at 30% 30%, rgba(255,255,255,0.55) 0%, transparent 70%);
}

.stat-card:hover .stat-card-icon { transform: scale(1.08); }

.stat-icon-publish { color: #30b158; box-shadow: 0 2px 10px rgba(52,199,89,0.18); }
.stat-icon-sold   { color: #0a84ff; box-shadow: 0 2px 10px rgba(10,132,255,0.18); }
.stat-icon-earn   { color: #9b51e0; box-shadow: 0 2px 10px rgba(155,81,224,0.18); }
.stat-icon-post   { color: #ff9f0a; box-shadow: 0 2px 10px rgba(255,159,10,0.18); }

.stat-card-value {
  font-size: 1.15rem; font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em; line-height: 1;
}

.stat-card-label {
  font-size: 0.7rem;
  color: var(--text-caption);
  font-weight: 400;
}

/* ===== 3. 等级进度 ===== */
.level-progress-card {
  background: var(--glass-bg-card);
  backdrop-filter: blur(var(--blur-sm)) saturate(1.3);
  -webkit-backdrop-filter: blur(var(--blur-sm)) saturate(1.3);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: 1.15rem 1.35rem;
  box-shadow: var(--shadow-xs);
}

.level-progress-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  margin-bottom: 0.65rem;
  font-size: 0.82rem;
  font-weight: 600;
}

.level-progress-current { color: var(--text-secondary); }
.level-progress-arrow { color: var(--text-tertiary); font-size: 0.7rem; }
.level-progress-next { color: var(--text-primary); }

.level-progress-bar-track {
  position: relative;
  height: 6px;
  background: rgba(0,0,0,0.06);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.level-progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #6c3fc0, #af52de);
  border-radius: var(--radius-full);
  transition: width 0.6s var(--ease-out);
  position: relative;
}

.level-progress-bar-glow {
  position: absolute;
  right: -6px; top: -4px;
  width: 14px; height: 14px;
  border-radius: 50%;
  background: #af52de;
  filter: blur(6px);
  opacity: 0.6;
}

.level-progress-hint {
  margin: 0.55rem 0 0;
  font-size: 0.72rem;
  color: var(--text-caption);
  text-align: center;
}

/* ===== 4. 我的服务 ===== */
.services-section {
  background: var(--glass-bg-card);
  backdrop-filter: blur(var(--blur-sm)) saturate(1.3);
  -webkit-backdrop-filter: blur(var(--blur-sm)) saturate(1.3);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  padding: 1.25rem 1.35rem 1.1rem;
  box-shadow: var(--shadow-xs);
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.service-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 0.4rem;
  background: var(--glass-bg-input);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-family: inherit;
  position: relative;
  transition: all 0.2s var(--ease-out);
}

.service-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
  border-color: var(--glass-border-hover);
}

.service-icon-wrap {
  width: 2.75rem; height: 2.75rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background: rgba(255,255,255,0.65);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  transition: transform 0.3s var(--ease-spring);
}
.service-icon-wrap::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 50%;
  pointer-events: none;
  border: 1px solid rgba(255,255,255,0.8);
}
.service-icon-wrap::after {
  content: '';
  position: absolute;
  width: 50%; height: 50%;
  top: 8%; left: 12%;
  border-radius: 50%;
  pointer-events: none;
  background: radial-gradient(ellipse at 30% 30%, rgba(255,255,255,0.5) 0%, transparent 70%);
}

.service-card:hover .service-icon-wrap { transform: scale(1.1); }

.service-icon-orders    { color: #0a84ff; box-shadow: 0 2px 10px rgba(10,132,255,0.16); }
.service-icon-cart      { color: #30b158; box-shadow: 0 2px 10px rgba(52,199,89,0.16); }
.service-icon-notif     { color: #ff9f0a; box-shadow: 0 2px 10px rgba(255,159,10,0.16); }
.service-icon-community { color: #5ac8fa; box-shadow: 0 2px 10px rgba(90,200,250,0.16); }
.service-icon-publish2  { color: #9b51e0; box-shadow: 0 2px 10px rgba(155,81,224,0.16); }
.service-icon-chat      { color: #ff375f; box-shadow: 0 2px 10px rgba(255,55,95,0.14); }

.service-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-secondary);
  letter-spacing: 0.01em;
}

.service-badge {
  position: absolute;
  top: 6px; right: 6px;
  min-width: 1.25rem; height: 1.25rem;
  padding: 0 0.3rem;
  background: #ff375f;
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
}

.service-badge-dot { min-width: 8px; height: 8px; padding: 0; }

/* ===== 5. 最近动态 ===== */
.activity-section {
  background: var(--glass-bg-card);
  backdrop-filter: blur(var(--blur-sm)) saturate(1.3);
  -webkit-backdrop-filter: blur(var(--blur-sm)) saturate(1.3);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  padding: 1.25rem 1.35rem;
  box-shadow: var(--shadow-xs);
}

.activity-list {
  display: flex;
  flex-direction: column;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.75rem 0.5rem;
  transition: background 0.15s var(--ease-out);
  border-radius: var(--radius-sm);
}

.activity-item + .activity-item {
  border-top: 1px solid rgba(0,0,0,0.04);
}

.activity-clickable:hover {
  background: rgba(255,255,255,0.4);
}

.activity-icon {
  width: 2.5rem; height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  background: rgba(255,255,255,0.6);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}
.activity-icon::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 50%;
  pointer-events: none;
  border: 1px solid rgba(255,255,255,0.75);
}
.activity-icon::after {
  content: '';
  position: absolute;
  width: 45%; height: 45%;
  top: 10%; left: 14%;
  border-radius: 50%;
  pointer-events: none;
  background: radial-gradient(ellipse at 30% 30%, rgba(255,255,255,0.45) 0%, transparent 70%);
}

.activity-order { color: #0a84ff; box-shadow: 0 1px 6px rgba(10,132,255,0.14); }
.activity-post  { color: #9b51e0; box-shadow: 0 1px 6px rgba(155,81,224,0.14); }

.activity-body { flex: 1; min-width: 0; }

.activity-text {
  font-size: 0.85rem;
  color: var(--text-primary);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.activity-time {
  font-size: 0.7rem;
  color: var(--text-caption);
  margin-top: 0.15rem;
  display: block;
}

.activity-arrow { color: var(--text-tertiary); flex-shrink: 0; }

/* ===== 6. 编辑资料 ===== */
.profile-edit-card {
  background: var(--glass-bg-card);
  backdrop-filter: blur(var(--blur-md)) saturate(1.4);
  -webkit-backdrop-filter: blur(var(--blur-md)) saturate(1.4);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md), var(--shadow-glow);
  padding: 1.75rem 1.75rem 1.5rem;
}

.edit-card-header { margin-bottom: 1.25rem; }

.edit-card-title {
  font-size: 1.05rem; font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.2rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.edit-card-subtitle {
  font-size: 0.78rem;
  color: var(--text-caption);
  margin: 0;
}

.edit-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem 1.25rem;
  margin-bottom: 1.25rem;
}

.form-field { display: flex; flex-direction: column; gap: 0.3rem; }

.form-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.form-input {
  width: 100%;
  padding: 0.65rem 0.85rem;
  background: var(--glass-bg-input);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 0.88rem;
  font-family: inherit;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input::placeholder { color: var(--text-tertiary); }

.form-input:focus {
  border-color: rgba(175,82,222,0.45);
  box-shadow: 0 0 0 3px rgba(175,82,222,0.08);
}

.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%238e8e93' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.7rem center;
  padding-right: 2rem;
}

.save-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.85rem;
  background: linear-gradient(135deg, #6c3fc0 0%, #9b59b6 40%, #af52de 100%);
  color: #fff;
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.92rem;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(108,63,192,0.3);
  transition: all 0.25s cubic-bezier(0.16,1,0.3,1);
}

.save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 7px 24px rgba(108,63,192,0.42);
  filter: brightness(1.08);
}

.save-btn:active { transform: scale(0.97); }

/* ===== 7. 快捷私聊 ===== */
.quick-chat-card {
  background: var(--glass-bg-card);
  backdrop-filter: blur(var(--blur-sm)) saturate(1.3);
  -webkit-backdrop-filter: blur(var(--blur-sm)) saturate(1.3);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: 1rem 1.25rem;
  box-shadow: var(--shadow-xs);
}

.quick-chat-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.7rem;
}

.quick-chat-body { display: flex; gap: 0.5rem; }

.chat-input {
  flex: 1;
  padding: 0.6rem 0.85rem;
  background: var(--glass-bg-input);
  backdrop-filter: blur(8px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 0.85rem;
  font-family: inherit;
  outline: none;
}

.chat-input:focus { border-color: rgba(175,82,222,0.4); }

.chat-submit-btn {
  width: 2.5rem; height: 2.5rem;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, #6c3fc0 0%, #af52de 100%);
  color: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 3px 10px rgba(108,63,192,0.3);
  transition: all 0.2s var(--ease-out);
  flex-shrink: 0;
}

.chat-submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 5px 16px rgba(108,63,192,0.4);
}

.chat-submit-btn:disabled { opacity: 0.45; cursor: not-allowed; }

/* ===== 8. 设置列表 ===== */
.settings-card {
  background: var(--glass-bg-card);
  backdrop-filter: blur(var(--blur-sm)) saturate(1.3);
  -webkit-backdrop-filter: blur(var(--blur-sm)) saturate(1.3);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  padding: 1.25rem 1.35rem 0.85rem;
  box-shadow: var(--shadow-xs);
}

.settings-list {
  display: flex;
  flex-direction: column;
}

.settings-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 0.35rem;
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: background 0.15s;
}

.settings-item + .settings-item {
  border-top: 1px solid rgba(0,0,0,0.04);
}

.settings-item:hover {
  background: rgba(255,255,255,0.35);
}

.settings-item-left {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
}

.settings-item-right {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  color: var(--text-tertiary);
}

.settings-item-text {
  font-size: 0.78rem;
  color: var(--text-tertiary);
  font-weight: 400;
}

/* ===== 5.5 教务信息 ===== */
.edu-section {
  background: var(--glass-bg-card);
  backdrop-filter: blur(var(--blur-md)) saturate(1.3);
  -webkit-backdrop-filter: blur(var(--blur-md)) saturate(1.3);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  padding: 1.25rem 1.35rem;
  box-shadow: var(--shadow-xs);
}

.edu-source-badge {
  font-size: 0.65rem; font-weight: 600;
  padding: 0.15rem 0.45rem; border-radius: var(--radius-full);
  background: rgba(251,191,36,0.1); color: #b45309;
  border: 1px solid rgba(251,191,36,0.2);
  margin-left: 0.35rem;
  vertical-align: middle;
}

.edu-source-badge--cas {
  background: rgba(22,163,74,0.1); color: #0d6b4e;
  border: 1px solid rgba(22,163,74,0.2);
}

.edu-student-card {
  background: var(--glass-bg-input);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  padding: 0.85rem 1rem;
  margin-bottom: 0.85rem;
}

.edu-student-row {
  display: flex; align-items: center;
  padding: 0.35rem 0;
}

.edu-student-row + .edu-student-row {
  border-top: 1px solid rgba(0,0,0,0.03);
}

.edu-label {
  width: 3rem; flex-shrink: 0;
  font-size: 0.78rem; color: var(--text-caption);
  font-weight: 500;
}

.edu-value {
  font-size: 0.85rem; color: var(--text-primary);
  font-weight: 500;
}

.edu-grades-summary {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 0.6rem; margin-bottom: 0.85rem;
}

.edu-gpa-card {
  background: var(--glass-bg-input);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  padding: 0.75rem 0.5rem;
  display: flex; flex-direction: column;
  align-items: center; gap: 0.2rem;
}

.edu-gpa-value {
  font-size: 1.5rem; font-weight: 700;
  color: var(--lavender-accent);
  font-family: var(--font-mono);
}

.edu-gpa-label {
  font-size: 0.7rem; color: var(--text-caption);
}

.edu-subtitle {
  font-size: 0.85rem; font-weight: 600;
  color: var(--text-secondary);
  margin: 0 0 0.6rem;
}

.edu-courses-card {
  background: var(--glass-bg-input);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  padding: 0.85rem 1rem;
}

.edu-course-list {
  display: flex; flex-direction: column;
}

.edu-course-item {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.5rem 0;
}

.edu-course-item + .edu-course-item {
  border-top: 1px solid rgba(0,0,0,0.04);
}

.edu-course-left {
  display: flex; flex-direction: column;
  align-items: center; flex-shrink: 0;
  width: 3rem;
}

.edu-course-weekday {
  font-size: 0.78rem; font-weight: 700;
  color: var(--lavender-accent);
}

.edu-course-time {
  font-size: 0.62rem; color: var(--text-caption);
  white-space: nowrap;
}

.edu-course-right {
  flex: 1; min-width: 0;
}

.edu-course-name {
  font-size: 0.82rem; font-weight: 600;
  color: var(--text-primary);
  display: block;
}

.edu-course-meta {
  font-size: 0.68rem; color: var(--text-caption);
  margin-top: 0.1rem; display: block;
}

/* ===== 9. 退出 ===== */
.logout-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.85rem;
  background: transparent;
  color: #ef4444;
  border: 1px solid rgba(239,68,68,0.25);
  border-radius: var(--radius-lg);
  font-size: 0.95rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s var(--ease-out);
}

.logout-btn:hover {
  background: rgba(239,68,68,0.07);
  border-color: rgba(239,68,68,0.45);
}

.hidden-input { display: none; }
</style>