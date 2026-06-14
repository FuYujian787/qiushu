<script setup>
const year = new Date().getFullYear()
</script>

<template>
  <footer class="app-footer">
    <div class="footer-inner">
      <div class="footer-brand">
        <div class="footer-logo">
          <span class="footer-seal">求书</span>
          <span class="footer-name">·書緣</span>
        </div>
        <p class="footer-desc">浙江大学校内二手书交易平台 — 在流转中，不只有书，还有浙大人的知识与记忆。</p>
      </div>
      <div class="footer-links">
        <div class="footer-section">
          <h4>平台</h4>
          <router-link to="/browse">浏览书籍</router-link>
          <router-link to="/publish">发布书籍</router-link>
          <router-link to="/forum">课程论坛</router-link>
        </div>
        <div class="footer-section">
          <h4>功能</h4>
          <router-link to="/wishes">求书许愿墙</router-link>
          <router-link to="/exchange">以书换书</router-link>
          <router-link to="/profile">个人中心</router-link>
        </div>
        <div class="footer-section">
          <h4>关于</h4>
          <a href="https://www.zju.edu.cn" target="_blank">浙江大学</a>
          <a href="https://zjuam.zju.edu.cn" target="_blank">浙大通行证</a>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; {{ year }} 求书 · 書緣 — 大数据信息系统分析与设计课程项目</p>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  position: relative;
  z-index: 1;
  background: var(--surface-tertiary);
  border-top: 1px solid var(--border-default);
  padding: 48px 24px 24px;
  transition: background-color 0.5s;
}

[data-theme="cyber"] .app-footer {
  background: rgba(9, 5, 26, 0.85);
  backdrop-filter: blur(4px);
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 64px;
  flex-wrap: wrap;
}

.footer-brand {
  flex: 1;
  min-width: 240px;
}

.footer-logo { margin-bottom: 8px; }

.footer-seal {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--accent-primary);
  color: #fff;
  font-family: var(--font-brush);
  font-size: 14px;
  border-radius: 4px;
}

.footer-name {
  font-family: var(--font-brush);
  font-size: 18px;
  color: var(--text-primary);
  margin-left: 4px;
}

.footer-desc {
  color: var(--text-muted);
  font-size: 13px;
  line-height: 1.6;
}

.footer-links {
  display: flex;
  gap: 48px;
  flex-wrap: wrap;
}

.footer-section h4 {
  font-family: var(--font-display);
  font-size: 14px;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.footer-section a {
  display: block;
  color: var(--text-muted);
  font-size: 13px;
  padding: 4px 0;
  text-decoration: none;
  transition: color 0.2s;
}

.footer-section a:hover {
  color: var(--accent-primary);
}

.footer-bottom {
  max-width: 1200px;
  margin: 32px auto 0;
  padding-top: 16px;
  border-top: 1px solid var(--border-default);
  text-align: center;
}

.footer-bottom p {
  color: var(--text-muted);
  font-size: 12px;
}

@media (max-width: 768px) {
  .footer-inner { flex-direction: column; gap: 32px; }
  .footer-links { gap: 32px; }
}
</style>
