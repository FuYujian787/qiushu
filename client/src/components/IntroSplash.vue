<template>
  <div
    v-if="visible"
    class="intro-splash"
    :class="{ 'splash-exit': exiting }"
  >
    <!-- 背景：深灰紫毛玻璃迷雾 -->
    <div class="splash-bg"></div>

    <!-- 光晕层 -->
    <div class="splash-glow"></div>

    <!-- 核心 Logo 区域 -->
    <div class="splash-logo-wrapper">
      <!-- 紫金光晕光环 -->
      <div class="logo-halo"></div>

      <!-- SVG Logo：紫金求思 抽象文字 Logo -->
      <svg
        class="splash-logo-svg"
        viewBox="0 0 400 160"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <!-- 阶段一：星芒汇聚使用的渐变 -->
          <linearGradient id="logoGradStart" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#E6D7B8" stop-opacity="0.3" />
            <stop offset="50%" stop-color="#E6D7B8" stop-opacity="0.8" />
            <stop offset="100%" stop-color="#E6D7B8" stop-opacity="0.3" />
          </linearGradient>

          <!-- 阶段二：流光思辨使用的渐变色位移 -->
          <linearGradient id="logoGradFlow" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#DCD0FF">
              <animate
                attributeName="stop-color"
                values="#DCD0FF;#C4B5E0;#DCD0FF"
                dur="0.6s"
                repeatCount="1"
                fill="freeze"
              />
            </stop>
            <stop offset="50%" stop-color="#C4B5E0">
              <animate
                attributeName="stop-color"
                values="#C4B5E0;#B8A9DA;#C4B5E0"
                dur="0.6s"
                repeatCount="1"
                fill="freeze"
              />
            </stop>
            <stop offset="100%" stop-color="#B8A9DA">
              <animate
                attributeName="stop-color"
                values="#B8A9DA;#DCD0FF;#B8A9DA"
                dur="0.6s"
                repeatCount="1"
                fill="freeze"
              />
            </stop>
          </linearGradient>

          <!-- 粒子散去渐变 -->
          <radialGradient id="particleGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#E6D7B8" stop-opacity="0.9" />
            <stop offset="100%" stop-color="#C4B5E0" stop-opacity="0" />
          </radialGradient>

          <!-- 剪切路径：用于 Logo 的 clip-path 爆破效果 -->
          <clipPath id="logoClip">
            <rect x="0" y="0" width="400" height="160" />
          </clipPath>
        </defs>

        <!-- 背景光晕圆 -->
        <circle
          class="logo-glow-circle"
          cx="200" cy="80" r="60"
          fill="url(#logoGradStart)"
          opacity="0"
        />

        <!-- 主文字：紫金求思（使用路径模拟书法感） -->
        <g class="logo-text-group">
          <!-- 紫 -->
          <text
            x="60" y="95"
            class="logo-char"
            font-family="'PingFang SC', 'STKaiti', serif"
            font-size="52"
            font-weight="700"
            fill="url(#logoGradFlow)"
            text-anchor="middle"
          >紫</text>
          <!-- 金 -->
          <text
            x="145" y="95"
            class="logo-char"
            font-family="'PingFang SC', 'STKaiti', serif"
            font-size="52"
            font-weight="700"
            fill="url(#logoGradFlow)"
            text-anchor="middle"
          >金</text>
          <!-- 求 -->
          <text
            x="230" y="95"
            class="logo-char"
            font-family="'PingFang SC', 'STKaiti', serif"
            font-size="52"
            font-weight="700"
            fill="url(#logoGradFlow)"
            text-anchor="middle"
          >求</text>
          <!-- 思 -->
          <text
            x="315" y="95"
            class="logo-char"
            font-family="'PingFang SC', 'STKaiti', serif"
            font-size="52"
            font-weight="700"
            fill="url(#logoGradFlow)"
            text-anchor="middle"
          >思</text>
        </g>

        <!-- 底部英文副标题 -->
        <text
          x="200" y="135"
          class="logo-subtitle"
          font-family="'Inter', 'SF Pro Display', sans-serif"
          font-size="14"
          font-weight="300"
          fill="#B8A9DA"
          text-anchor="middle"
          letter-spacing="6"
          opacity="0"
        >ZIJIN · QIUSI</text>
      </svg>

      <!-- 粒子容器：用于阶段三的爆破粒子 -->
      <div class="particle-container">
        <div
          v-for="i in 24"
          :key="i"
          class="particle"
          :style="getParticleStyle(i)"
        ></div>
      </div>
    </div>

    <!-- 底部加载提示（极淡） -->
    <div class="splash-footer">
      <span class="splash-dot"></span>
      <span class="splash-dot"></span>
      <span class="splash-dot"></span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const visible = ref(true)
const exiting = ref(false)

const emit = defineEmits(['finished'])

// 粒子配置：24 个粒子向不同方向扩散
const particleAngles = Array.from({ length: 24 }, (_, i) => (i * 360) / 24)

function getParticleStyle(index) {
  const angle = particleAngles[index]
  const distance = 80 + Math.random() * 120
  const size = 3 + Math.random() * 5
  const delay = 1.2 + Math.random() * 0.15
  const hue = 260 + Math.random() * 30 // 淡紫到薰衣草色域
  const sat = 40 + Math.random() * 30
  const light = 60 + Math.random() * 25

  return {
    '--angle': `${angle}deg`,
    '--distance': `${distance}px`,
    '--size': `${size}px`,
    '--delay': `${delay}s`,
    '--hue': hue,
    '--sat': `${sat}%`,
    '--light': `${light}%`,
    '--x': `${Math.cos((angle * Math.PI) / 180) * distance}px`,
    '--y': `${Math.sin((angle * Math.PI) / 180) * distance}px`,
  }
}

onMounted(() => {
  // 阶段三：1.2s 后触发粒子爆破
  const burstTimer = setTimeout(() => {
    exiting.value = true
  }, 1200)

  // 2.0s 后完全销毁组件
  const destroyTimer = setTimeout(() => {
    visible.value = false
    emit('finished')
  }, 2000)

  onBeforeUnmount(() => {
    clearTimeout(burstTimer)
    clearTimeout(destroyTimer)
  })
})
</script>

<style scoped>
/* ============================================================
   IntroSplash.vue — 紫金求思 · 电影级开场转场动画
   ============================================================
   三阶段设计：
     阶段一 (0.0-0.6s)：星芒汇聚 — Logo 从无到有呼吸放大
     阶段二 (0.6-1.2s)：流光思辨 — 渐变色位移流动
     阶段三 (1.2-2.0s)：破茧散去 — 粒子爆破 + 遮罩消融
   ============================================================ */

/* ---- 遮罩层容器 ---- */
.intro-splash {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 99999;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  pointer-events: all;
}

/* ---- 背景：深灰紫半透明毛玻璃迷雾 ---- */
.splash-bg {
  position: absolute;
  inset: 0;
  background: rgba(74, 59, 90, 0.85);
  backdrop-filter: blur(24px) saturate(1.4);
  -webkit-backdrop-filter: blur(24px) saturate(1.4);
  animation: bgFadeIn 0.6s cubic-bezier(0.19, 1, 0.22, 1) forwards;
}

/* ---- 光晕层 ---- */
.splash-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 600px;
  height: 600px;
  transform: translate(-50%, -50%);
  background: radial-gradient(
    circle at center,
    rgba(230, 215, 184, 0.08) 0%,
    rgba(196, 181, 224, 0.04) 30%,
    transparent 70%
  );
  animation: glowPulse 1.2s cubic-bezier(0.25, 1, 0.5, 1) forwards;
}

/* ---- Logo 容器 ---- */
.splash-logo-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: logoContainerIn 0.6s cubic-bezier(0.25, 1, 0.5, 1) forwards;
}

/* ---- 紫金光晕光环 ---- */
.logo-halo {
  position: absolute;
  width: 320px;
  height: 320px;
  border-radius: 50%;
  background: radial-gradient(
    circle at center,
    rgba(230, 215, 184, 0.15) 0%,
    rgba(196, 181, 224, 0.08) 30%,
    rgba(74, 59, 90, 0.02) 60%,
    transparent 75%
  );
  animation: haloExpand 0.8s cubic-bezier(0.25, 1, 0.5, 1) forwards;
  opacity: 0;
}

/* ---- SVG Logo ---- */
.splash-logo-svg {
  width: 400px;
  height: 160px;
  position: relative;
  z-index: 2;
  filter: drop-shadow(0 0 30px rgba(230, 215, 184, 0.15));
}

/* ---- 单个文字字符 ---- */
.logo-char {
  opacity: 0;
  animation: charAppear 0.5s cubic-bezier(0.25, 1, 0.5, 1) forwards;
}
.logo-char:nth-child(1) { animation-delay: 0.05s; }
.logo-char:nth-child(2) { animation-delay: 0.12s; }
.logo-char:nth-child(3) { animation-delay: 0.19s; }
.logo-char:nth-child(4) { animation-delay: 0.26s; }

/* ---- 光晕圆 ---- */
.logo-glow-circle {
  animation: glowCircleIn 0.6s cubic-bezier(0.25, 1, 0.5, 1) forwards;
}

/* ---- 副标题 ---- */
.logo-subtitle {
  animation: subtitleIn 0.8s cubic-bezier(0.25, 1, 0.5, 1) 0.4s forwards;
}

/* ---- 粒子容器 ---- */
.particle-container {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  z-index: 3;
  pointer-events: none;
}

/* ---- 单个粒子 ---- */
.particle {
  position: absolute;
  width: var(--size);
  height: var(--size);
  border-radius: 50%;
  background: hsla(var(--hue), var(--sat), var(--light), 0.9);
  box-shadow: 0 0 6px hsla(var(--hue), var(--sat), var(--light), 0.5);
  opacity: 0;
  animation: particleBurst 0.8s cubic-bezier(0.25, 0.1, 0.25, 1) var(--delay) forwards;
}

/* ---- 底部加载点 ---- */
.splash-footer {
  position: absolute;
  bottom: 48px;
  display: flex;
  gap: 8px;
  align-items: center;
}

.splash-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(220, 208, 255, 0.3);
  animation: dotPulse 1.4s ease-in-out infinite;
}
.splash-dot:nth-child(2) { animation-delay: 0.2s; }
.splash-dot:nth-child(3) { animation-delay: 0.4s; }

/* ============================================================
   退出状态：阶段三 — 破茧散去
   ============================================================ */
.splash-exit .splash-bg {
  animation: bgDissolve 0.8s cubic-bezier(0.65, 0, 0.35, 1) forwards;
}

.splash-exit .splash-logo-wrapper {
  animation: logoBurst 0.8s cubic-bezier(0.65, 0, 0.35, 1) forwards;
}

.splash-exit .splash-glow {
  animation: glowDissolve 0.8s cubic-bezier(0.65, 0, 0.35, 1) forwards;
}

.splash-exit .logo-halo {
  animation: haloShrink 0.6s cubic-bezier(0.65, 0, 0.35, 1) forwards;
}

.splash-exit .logo-char {
  animation: charDissolve 0.7s cubic-bezier(0.65, 0, 0.35, 1) forwards;
}

.splash-exit .logo-subtitle {
  animation: subtitleDissolve 0.5s cubic-bezier(0.65, 0, 0.35, 1) forwards;
}

/* ============================================================
   @keyframes 关键帧定义
   ============================================================ */

/* ---- 背景淡入 ---- */
@keyframes bgFadeIn {
  0%   { opacity: 0; backdrop-filter: blur(0px); }
  100% { opacity: 1; backdrop-filter: blur(24px) saturate(1.4); }
}

/* ---- 背景消融（放射状淡出） ---- */
@keyframes bgDissolve {
  0% {
    opacity: 1;
    backdrop-filter: blur(24px) saturate(1.4);
    clip-path: circle(150% at 50% 50%);
  }
  100% {
    opacity: 0;
    backdrop-filter: blur(0px) saturate(1);
    clip-path: circle(0% at 50% 50%);
  }
}

/* ---- 光晕脉冲 ---- */
@keyframes glowPulse {
  0%   { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
  50%  { opacity: 1; transform: translate(-50%, -50%) scale(1.1); }
  100% { opacity: 0.6; transform: translate(-50%, -50%) scale(1); }
}

/* ---- 光晕消散 ---- */
@keyframes glowDissolve {
  0%   { opacity: 0.6; transform: translate(-50%, -50%) scale(1); }
  100% { opacity: 0; transform: translate(-50%, -50%) scale(1.8); }
}

/* ---- Logo 容器入场 ---- */
@keyframes logoContainerIn {
  0%   { transform: scale(0.6); opacity: 0; filter: blur(8px); }
  60%  { transform: scale(1.05); opacity: 1; filter: blur(0); }
  100% { transform: scale(1); opacity: 1; filter: blur(0); }
}

/* ---- Logo 爆破散去 ---- */
@keyframes logoBurst {
  0%   { transform: scale(1); opacity: 1; filter: blur(0); }
  40%  { transform: scale(1.15); opacity: 0.8; filter: blur(2px); }
  100% { transform: scale(1.5); opacity: 0; filter: blur(8px); }
}

/* ---- 光环展开 ---- */
@keyframes haloExpand {
  0%   { opacity: 0; transform: scale(0.5); }
  50%  { opacity: 0.6; transform: scale(1.2); }
  100% { opacity: 0.4; transform: scale(1); }
}

/* ---- 光环收缩 ---- */
@keyframes haloShrink {
  0%   { opacity: 0.4; transform: scale(1); }
  100% { opacity: 0; transform: scale(0.3); }
}

/* ---- 光晕圆入场 ---- */
@keyframes glowCircleIn {
  0%   { opacity: 0; r: 0; }
  100% { opacity: 0.6; r: 60; }
}

/* ---- 文字字符入场（带呼吸感） ---- */
@keyframes charAppear {
  0% {
    opacity: 0;
    transform: translateY(12px) scale(0.8);
    filter: blur(4px);
  }
  60% {
    opacity: 1;
    transform: translateY(-2px) scale(1.02);
    filter: blur(0);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
    filter: blur(0);
  }
}

/* ---- 文字字符消散 ---- */
@keyframes charDissolve {
  0% {
    opacity: 1;
    transform: translateY(0) scale(1);
    filter: blur(0);
  }
  100% {
    opacity: 0;
    transform: translateY(-20px) scale(1.3);
    filter: blur(6px);
  }
}

/* ---- 副标题入场 ---- */
@keyframes subtitleIn {
  0%   { opacity: 0; transform: translateY(8px); letter-spacing: 12px; }
  100% { opacity: 0.7; transform: translateY(0); letter-spacing: 6px; }
}

/* ---- 副标题消散 ---- */
@keyframes subtitleDissolve {
  0%   { opacity: 0.7; transform: translateY(0); }
  100% { opacity: 0; transform: translateY(-10px); }
}

/* ---- 粒子爆破 ---- */
@keyframes particleBurst {
  0% {
    opacity: 0;
    transform: translate(0, 0) scale(0);
  }
  20% {
    opacity: 1;
    transform: translate(0, 0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translate(var(--x), var(--y)) scale(0.2);
  }
}

/* ---- 底部点脉冲 ---- */
@keyframes dotPulse {
  0%, 100% { opacity: 0.2; transform: scale(1); }
  50%      { opacity: 0.6; transform: scale(1.3); }
}
</style>
