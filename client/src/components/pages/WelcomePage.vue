<template>
  <div class="welcome-wrap">
    <div class="welcome-content">
      <!-- 装饰性书脊线条 -->
      <div class="book-spine-decor">
        <span class="spine-line" v-for="i in 5" :key="i" :style="{ animationDelay: `${i * 0.15}s` }"></span>
      </div>

      <div class="welcome-text">
        <p class="welcome-greeting stagger-1">欢迎回来</p>
        <h1 class="welcome-title stagger-2">
          <span class="char" v-for="(c, i) in '紫金求思'" :key="i" :style="{ animationDelay: `${0.4 + i * 0.08}s` }">{{ c }}</span>
        </h1>
        <p class="welcome-subtitle stagger-3">让知识在校园流动</p>
        <p class="welcome-desc stagger-4">
          智慧购书清单 · 求是书摊 · 学习社区<br>
          一站式校园二手书交易平台
        </p>
      </div>

      <button class="enter-btn stagger-5" @click="enterApp">
        <span class="btn-text">进入求是书摊</span>
        <span class="btn-icon">
          <span class="iconify" data-icon="solar:alt-arrow-right-linear" data-width="20"></span>
        </span>
      </button>

      <p class="welcome-footer stagger-6">
        <span class="iconify" data-icon="solar:shield-check-outline" data-width="14"></span>
        浙江大学 · 校园二手书交易平台
      </p>
    </div>
  </div>
</template>

<script setup>
import { useStore } from '../../stores/useStore'

const store = useStore()

function enterApp() {
  store.hasSeenWelcome.value = true
  localStorage.setItem(store.KEYS.hasSeenWelcome, '1')
  store.navigateTo('procurement')
}
</script>

<style scoped>
.welcome-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100%;
  padding: 2rem;
}

.welcome-content {
  text-align: center;
  max-width: 480px;
  width: 100%;
  position: relative;
}

/* 书脊装饰线 */
.book-spine-decor {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-bottom: 3rem;
  height: 4px;
}

.spine-line {
  width: 32px;
  height: 4px;
  border-radius: 2px;
  background: linear-gradient(90deg, var(--lavender-accent-soft), var(--lavender-accent));
  opacity: 0;
  animation: spineReveal 0.6s cubic-bezier(0.25, 0.8, 0.25, 1) forwards;
}

@keyframes spineReveal {
  from { opacity: 0; transform: scaleX(0); }
  to { opacity: 1; transform: scaleX(1); }
}

/* 文字区域 */
.welcome-text {
  margin-bottom: 3rem;
}

.welcome-greeting {
  font-family: var(--font-serif);
  font-size: 1rem;
  color: var(--text-caption);
  margin: 0 0 1rem;
  letter-spacing: 0.15em;
  opacity: 0;
  animation: fadeUp 0.6s 0.2s cubic-bezier(0.25, 0.8, 0.25, 1) forwards;
}

.welcome-title {
  font-family: var(--font-serif-display);
  font-size: 3.5rem;
  font-weight: 700;
  margin: 0 0 0.75rem;
  letter-spacing: 0.08em;
  color: var(--text-primary);
  display: flex;
  justify-content: center;
  gap: 0.08em;
}

.char {
  display: inline-block;
  opacity: 0;
  animation: charFadeIn 0.5s cubic-bezier(0.25, 0.8, 0.25, 1) forwards;
}

@keyframes charFadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

.welcome-subtitle {
  font-family: var(--font-serif);
  font-size: 1.05rem;
  color: var(--lavender-accent);
  margin: 0 0 1.5rem;
  font-weight: 500;
  letter-spacing: 0.06em;
  opacity: 0;
  animation: fadeUp 0.6s 0.7s cubic-bezier(0.25, 0.8, 0.25, 1) forwards;
}

.welcome-desc {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.8;
  margin: 0;
  opacity: 0;
  animation: fadeUp 0.6s 0.85s cubic-bezier(0.25, 0.8, 0.25, 1) forwards;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 进入按钮 */
.enter-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 2.5rem;
  background: var(--glass-bg-card);
  backdrop-filter: blur(20px) saturate(1.4);
  -webkit-backdrop-filter: blur(20px) saturate(1.4);
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  color: var(--text-primary);
  font-family: var(--font-serif);
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  box-shadow: var(--shadow-md), var(--shadow-glow), inset 0 1px 0 rgba(255,255,255,0.55);
  opacity: 0;
  animation: fadeUp 0.6s 1s cubic-bezier(0.25, 0.8, 0.25, 1) forwards;
  position: relative;
  overflow: hidden;
}

.enter-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.3), transparent 60%);
  opacity: 0;
  transition: opacity 0.3s;
}

.enter-btn:hover {
  transform: translateY(-1px);
  border-color: var(--lavender-accent-soft);
  box-shadow: var(--shadow-lg), 0 0 24px rgba(180, 160, 220, 0.25), inset 0 1px 0 rgba(255,255,255,0.55);
}

.enter-btn:hover::before { opacity: 1; }

.enter-btn:active {
  transform: translateY(0);
}

.btn-icon {
  display: flex;
  align-items: center;
  transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.enter-btn:hover .btn-icon {
  transform: translateX(3px);
}

/* 底部 */
.welcome-footer {
  margin-top: 3rem;
  font-size: 0.75rem;
  color: var(--text-caption);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  opacity: 0;
  animation: fadeUp 0.6s 1.2s cubic-bezier(0.25, 0.8, 0.25, 1) forwards;
}

/* 响应式 */
@media (max-width: 480px) {
  .welcome-title { font-size: 2.5rem; }
  .welcome-desc { font-size: 0.8rem; }
  .enter-btn { padding: 0.75rem 2rem; font-size: 0.9rem; }
}

/* 减少动效 */
@media (prefers-reduced-motion: reduce) {
  .spine-line, .welcome-greeting, .char, .welcome-subtitle,
  .welcome-desc, .enter-btn, .welcome-footer {
    animation: none;
    opacity: 1;
  }
}
</style>