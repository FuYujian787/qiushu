<script setup>
import SearchBar from './SearchBar.vue'
</script>

<template>
  <section class="hero">
    <div class="hero-content">
      <h1 class="hero-title">
        求书 · 書緣
      </h1>
      <p class="hero-subtitle">
        浙江大学校内二手书交易平台 — 在流转中，不只有书，还有浙大人的知识与记忆。
      </p>
      <div class="hero-search">
        <SearchBar />
      </div>
      <div class="hero-tags">
        <span class="tag-label">热门分类：</span>
        <router-link v-for="cat in ['数学', '计算机', '外语', '经管', '理工', '人文']"
          :key="cat"
          :to="{ name: 'Browse', query: { category: cat } }"
          class="tag"
        >
          {{ cat }}
        </router-link>
      </div>
    </div>
    <div class="hero-decoration">
      <div class="deco-circle"></div>
      <div class="deco-dots"></div>
    </div>
  </section>
</template>

<style scoped>
.hero {
  position: relative;
  padding: 80px 24px 60px;
  text-align: center;
  overflow: hidden;
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 700px;
  margin: 0 auto;
}

.hero-title {
  font-family: var(--font-display);
  font-size: 56px;
  font-weight: 900;
  color: var(--text-primary);
  margin-bottom: 12px;
  letter-spacing: 2px;
}

.hero-subtitle {
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 32px;
}

.hero-search {
  display: flex;
  justify-content: center;
  margin-bottom: 28px;
}

.hero-tags {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-label {
  font-size: 13px;
  color: var(--text-muted);
}

.tag {
  display: inline-block;
  padding: 6px 16px;
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  font-size: 13px;
  text-decoration: none;
  transition: all 0.2s;
}

.tag:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
  background: var(--accent-primary-light);
}

.hero-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.deco-circle {
  position: absolute;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle, var(--accent-primary-light) 0%, transparent 70%);
  top: -200px;
  right: -100px;
  opacity: 0.5;
}

[data-theme="cyber"] .deco-circle {
  background: radial-gradient(circle, rgba(0, 212, 255, 0.08) 0%, transparent 70%);
}

.deco-dots {
  position: absolute;
  width: 200px;
  height: 200px;
  background-image: radial-gradient(var(--accent-primary-light) 1px, transparent 1px);
  background-size: 20px 20px;
  bottom: -40px;
  left: -40px;
  opacity: 0.3;
}

@media (max-width: 768px) {
  .hero { padding: 48px 16px 40px; }
  .hero-title { font-size: 36px; }
  .hero-subtitle { font-size: 14px; }
}
</style>
