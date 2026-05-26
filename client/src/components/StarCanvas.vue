<template>
  <div class="star-canvas" aria-hidden="true">
    <div
      v-for="star in stars"
      :key="star.id"
      class="star-particle"
      :class="star.type"
      :style="{
        top: star.top + '%',
        left: star.left + '%',
        animationDelay: star.delay + 's',
        animationDuration: star.duration + 's',
      }"
    />
  </div>
</template>

<script setup>
/**
 * 场景二：【淘书星芒】—— 纯 CSS 空灵背景动效（高亮版）
 *
 * 设计理念：
 *   在毛玻璃背景遮罩层下，创造若隐若现的、呼吸状的紫金星芒流转。
 *   像夏夜启真湖畔闪烁的萤火虫，又像在书海中忽明忽暗的思想火花。
 *
 * 亮度提升 v2.0：
 *   - 粒子数量增加至 100 颗
 *   - 基础 opacity 提升 50%
 *   - box-shadow 光晕半径扩大 2x
 *   - 峰值亮度 opacity 达到 1.0
 *   - 新增 type-e 超亮星芒作为视觉锚点
 *
 * 性能：
 *   - 仅使用 transform/opacity/box-shadow（硬件加速）
 *   - will-change 精准声明
 *   - 所有动画使用 cubic-bezier(0.25, 1, 0.5, 1) 阻尼曲线
 */

import { computed } from 'vue'

// 生成 100 颗星芒粒子，分布在视口各处
const stars = computed(() => {
  const result = []
  const counts = {
    'type-a': 20,  // 大星芒 — 紫金色，缓慢呼吸
    'type-b': 28,  // 中星芒 — 淡紫色，柔和闪烁
    'type-c': 32,  // 小星芒 — 紫金微光，快速灵动
    'type-d': 16,  // 微型星芒 — 增加景深感
    'type-e': 4,   // 超亮星芒 — 视觉锚点，如启明星
  }

  let id = 0
  for (const [type, count] of Object.entries(counts)) {
    for (let i = 0; i < count; i++) {
      result.push({
        id: id++,
        type,
        top: Math.random() * 100,
        left: Math.random() * 100,
        delay: Math.random() * 8,
        duration: 6 + Math.random() * 10,
      })
    }
  }
  return result
})
</script>

<style scoped>
.star-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  pointer-events: none;
  overflow: hidden;
}

.star-particle {
  position: absolute;
  border-radius: 50%;
  will-change: transform, opacity, box-shadow;
  pointer-events: none;
}

/* ===== 大星芒 — 紫金色，缓慢呼吸 ===== */
.star-particle.type-a {
  width: 8px;
  height: 8px;
  background: rgba(220, 208, 255, 0.85);
  box-shadow:
    0 0 18px 4px rgba(220, 208, 255, 0.5),
    0 0 40px 10px rgba(230, 215, 184, 0.3),
    0 0 80px 20px rgba(220, 208, 255, 0.1);
  animation: starFloatA 8s cubic-bezier(0.25, 1, 0.5, 1) infinite;
}

/* ===== 中星芒 — 淡紫色，柔和闪烁 ===== */
.star-particle.type-b {
  width: 5px;
  height: 5px;
  background: rgba(196, 181, 224, 0.75);
  box-shadow:
    0 0 12px 3px rgba(196, 181, 224, 0.4),
    0 0 28px 8px rgba(220, 208, 255, 0.2);
  animation: starFloatB 12s cubic-bezier(0.25, 1, 0.5, 1) infinite;
}

/* ===== 小星芒 — 紫金微光，快速灵动 ===== */
.star-particle.type-c {
  width: 3px;
  height: 3px;
  background: rgba(230, 215, 184, 0.65);
  box-shadow:
    0 0 10px 2px rgba(230, 215, 184, 0.35),
    0 0 20px 6px rgba(220, 208, 255, 0.15);
  animation: starFloatC 6s cubic-bezier(0.25, 1, 0.5, 1) infinite;
}

/* ===== 微型星芒 — 增加景深感 ===== */
.star-particle.type-d {
  width: 2px;
  height: 2px;
  background: rgba(220, 208, 255, 0.5);
  box-shadow: 0 0 6px 2px rgba(220, 208, 255, 0.2);
  animation: starFloatD 15s cubic-bezier(0.25, 1, 0.5, 1) infinite;
}

/* ===== 超亮星芒 — 视觉锚点，如启明星 ===== */
.star-particle.type-e {
  width: 12px;
  height: 12px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow:
    0 0 24px 6px rgba(220, 208, 255, 0.7),
    0 0 60px 15px rgba(230, 215, 184, 0.4),
    0 0 120px 30px rgba(220, 208, 255, 0.15);
  animation: starFloatE 10s cubic-bezier(0.25, 1, 0.5, 1) infinite;
}

/* ===== 关键帧 ===== */

@keyframes starFloatA {
  0%, 100% {
    transform: translateY(0) translateX(0) scale(1);
    opacity: 0.7;
    box-shadow:
      0 0 18px 4px rgba(220, 208, 255, 0.5),
      0 0 40px 10px rgba(230, 215, 184, 0.3);
  }
  25% {
    transform: translateY(-35px) translateX(18px) scale(1.3);
    opacity: 1;
    box-shadow:
      0 0 30px 8px rgba(220, 208, 255, 0.8),
      0 0 60px 18px rgba(230, 215, 184, 0.5),
      0 0 100px 25px rgba(220, 208, 255, 0.2);
  }
  50% {
    transform: translateY(-12px) translateX(-24px) scale(0.85);
    opacity: 0.5;
    box-shadow:
      0 0 12px 2px rgba(220, 208, 255, 0.3),
      0 0 24px 6px rgba(230, 215, 184, 0.15);
  }
  75% {
    transform: translateY(-50px) translateX(12px) scale(1.15);
    opacity: 0.9;
    box-shadow:
      0 0 24px 6px rgba(220, 208, 255, 0.6),
      0 0 50px 14px rgba(230, 215, 184, 0.35);
  }
}

@keyframes starFloatB {
  0%, 100% {
    transform: translateY(0) translateX(0) scale(1);
    opacity: 0.6;
    box-shadow:
      0 0 12px 3px rgba(196, 181, 224, 0.4),
      0 0 28px 8px rgba(220, 208, 255, 0.2);
  }
  33% {
    transform: translateY(-30px) translateX(-12px) scale(1.4);
    opacity: 1;
    box-shadow:
      0 0 20px 5px rgba(196, 181, 224, 0.6),
      0 0 40px 12px rgba(220, 208, 255, 0.3);
  }
  66% {
    transform: translateY(-45px) translateX(18px) scale(0.75);
    opacity: 0.4;
    box-shadow:
      0 0 8px 2px rgba(196, 181, 224, 0.2),
      0 0 16px 5px rgba(220, 208, 255, 0.1);
  }
}

@keyframes starFloatC {
  0%, 100% {
    transform: translateY(0) translateX(0) scale(1);
    opacity: 0.5;
    box-shadow:
      0 0 10px 2px rgba(230, 215, 184, 0.35),
      0 0 20px 6px rgba(220, 208, 255, 0.15);
  }
  50% {
    transform: translateY(-25px) translateX(10px) scale(1.6);
    opacity: 1;
    box-shadow:
      0 0 16px 4px rgba(230, 215, 184, 0.6),
      0 0 32px 10px rgba(220, 208, 255, 0.25);
  }
}

@keyframes starFloatD {
  0%, 100% {
    transform: translateY(0) translateX(0);
    opacity: 0.3;
    box-shadow: 0 0 6px 2px rgba(220, 208, 255, 0.2);
  }
  50% {
    transform: translateY(-70px) translateX(-25px);
    opacity: 0.7;
    box-shadow: 0 0 10px 4px rgba(220, 208, 255, 0.35);
  }
}

@keyframes starFloatE {
  0%, 100% {
    transform: translateY(0) translateX(0) scale(1);
    opacity: 0.6;
    box-shadow:
      0 0 24px 6px rgba(220, 208, 255, 0.7),
      0 0 60px 15px rgba(230, 215, 184, 0.4);
  }
  30% {
    transform: translateY(-40px) translateX(20px) scale(1.2);
    opacity: 1;
    box-shadow:
      0 0 40px 12px rgba(220, 208, 255, 1),
      0 0 80px 24px rgba(230, 215, 184, 0.6),
      0 0 150px 40px rgba(220, 208, 255, 0.25);
  }
  60% {
    transform: translateY(-15px) translateX(-30px) scale(0.9);
    opacity: 0.7;
    box-shadow:
      0 0 20px 5px rgba(220, 208, 255, 0.5),
      0 0 50px 12px rgba(230, 215, 184, 0.3);
  }
}
</style>
