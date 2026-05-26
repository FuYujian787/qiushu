<template>
  <!-- ============================================================
       IntroAnimation.vue — 紫金求思 · 电影级开场进入动图
       ============================================================
       四阶段分镜 (0ms - 3000ms)：
         阶段一 (0-600ms)   微米级凝聚：粒子从四周向中心汇聚成 Logo
         阶段二 (600-1800ms) 求是之光：全息高光爆发 + 书页翻动 + 碎金漂散
         阶段三 (1800-2400ms)玻璃拟态破茧：放大镜 Z 轴拉伸 + 圆形遮罩推开
         阶段四 (2400-3000ms)全局解构：clip-path 涟漪扩散 + 事件派发
       ============================================================ -->

  <!-- 主容器：全屏固定定位，z-index 极高以覆盖所有内容 -->
  <div
    ref="containerRef"
    class="intro-animation"
    :class="{ 'intro-animation--reduced': prefersReducedMotion }"
    :style="{ opacity: componentOpacity }"
  >
    <!-- ====== Canvas 层：粒子系统 + 雷达扫描线 + 密码字符 ====== -->
    <canvas
      ref="canvasRef"
      class="intro-canvas"
      :width="canvasWidth"
      :height="canvasHeight"
    ></canvas>

    <!-- ====== SVG 叠加层：Logo 路径 + 翻页动效 + 放大镜 ====== -->
    <div class="intro-svg-layer" ref="svgLayerRef">
      <svg
        ref="logoSvgRef"
        class="intro-logo-svg"
        viewBox="0 0 400 400"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <!-- 全息高光渐变：用于星星爆发 -->
          <radialGradient id="starGlowGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#FFFFFF" stop-opacity="1" />
            <stop offset="30%" stop-color="#DCD0FF" stop-opacity="0.8" />
            <stop offset="60%" stop-color="#C4B5E0" stop-opacity="0.3" />
            <stop offset="100%" stop-color="#C4B5E0" stop-opacity="0" />
          </radialGradient>

          <!-- 书本渐变 -->
          <linearGradient id="bookGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#DCD0FF" stop-opacity="0.9" />
            <stop offset="50%" stop-color="#C4B5E0" stop-opacity="0.7" />
            <stop offset="100%" stop-color="#B8A9DA" stop-opacity="0.5" />
          </linearGradient>

          <!-- 放大镜镜片玻璃渐变 -->
          <radialGradient id="lensGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="rgba(255,255,255,0.15)" />
            <stop offset="70%" stop-color="rgba(220,208,255,0.08)" />
            <stop offset="100%" stop-color="rgba(196,181,224,0.02)" />
          </radialGradient>

          <!-- 发光滤镜 -->
          <filter id="glowFilter">
            <feGaussianBlur in="SourceGraphic" stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          <!-- 强发光滤镜 -->
          <filter id="strongGlow">
            <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <!-- ====== 翻开的书（Book）路径 ====== -->
        <g ref="bookGroupRef" class="book-group" opacity="0">
          <!-- 左页 -->
          <path
            class="book-page book-page-left"
            d="M 200 280
               C 160 280, 120 260, 100 220
               L 100 120
               C 120 160, 160 180, 200 180
               Z"
            fill="url(#bookGrad)"
            stroke="#DCD0FF"
            stroke-width="0.5"
            stroke-opacity="0.6"
          />
          <!-- 右页 -->
          <path
            class="book-page book-page-right"
            d="M 200 280
               C 240 280, 280 260, 300 220
               L 300 120
               C 280 160, 240 180, 200 180
               Z"
            fill="url(#bookGrad)"
            stroke="#DCD0FF"
            stroke-width="0.5"
            stroke-opacity="0.6"
          />
          <!-- 书脊线 -->
          <line
            class="book-spine"
            x1="200" y1="180"
            x2="200" y2="280"
            stroke="#DCD0FF"
            stroke-width="0.8"
            stroke-opacity="0.4"
          />
          <!-- 左页内文字线 -->
          <line class="book-text-line" x1="120" y1="200" x2="185" y2="200" stroke="#C4B5E0" stroke-width="0.3" stroke-opacity="0.3" />
          <line class="book-text-line" x1="120" y1="215" x2="185" y2="215" stroke="#C4B5E0" stroke-width="0.3" stroke-opacity="0.3" />
          <line class="book-text-line" x1="120" y1="230" x2="175" y2="230" stroke="#C4B5E0" stroke-width="0.3" stroke-opacity="0.3" />
          <!-- 右页内文字线 -->
          <line class="book-text-line" x1="215" y1="200" x2="280" y2="200" stroke="#C4B5E0" stroke-width="0.3" stroke-opacity="0.3" />
          <line class="book-text-line" x1="215" y1="215" x2="280" y2="215" stroke="#C4B5E0" stroke-width="0.3" stroke-opacity="0.3" />
          <line class="book-text-line" x1="215" y1="230" x2="270" y2="230" stroke="#C4B5E0" stroke-width="0.3" stroke-opacity="0.3" />
        </g>

        <!-- ====== 放大镜（Magnifier）路径 ====== -->
        <g ref="magnifierGroupRef" class="magnifier-group" opacity="0">
          <!-- 镜框 -->
          <circle
            class="magnifier-ring"
            cx="200" cy="160"
            r="45"
            fill="none"
            stroke="#DCD0FF"
            stroke-width="1.5"
            stroke-opacity="0.7"
          />
          <!-- 镜片（玻璃拟态） -->
          <circle
            class="magnifier-lens"
            cx="200" cy="160"
            r="42"
            fill="url(#lensGrad)"
            stroke="rgba(220,208,255,0.15)"
            stroke-width="0.5"
          />
          <!-- 镜片高光反射 -->
          <ellipse
            class="magnifier-glare"
            cx="188" cy="148"
            rx="12" ry="6"
            fill="rgba(255,255,255,0.12)"
            transform="rotate(-30 188 148)"
          />
          <!-- 手柄 -->
          <line
            class="magnifier-handle"
            x1="228" y1="188"
            x2="270" y2="230"
            stroke="#DCD0FF"
            stroke-width="2"
            stroke-opacity="0.5"
            stroke-linecap="round"
          />
        </g>

        <!-- ====== 星星（Star）路径 ====== -->
        <g ref="starGroupRef" class="star-group" opacity="0">
          <!-- 星星光晕 -->
          <circle
            class="star-halo"
            cx="200" cy="100"
            r="8"
            fill="url(#starGlowGrad)"
            filter="url(#strongGlow)"
          />
          <!-- 星星主体（四角星） -->
          <path
            class="star-body"
            d="M 200 88
               L 203 97 L 212 100 L 203 103 L 200 112
               L 197 103 L 188 100 L 197 97 Z"
            fill="#FFFFFF"
            filter="url(#glowFilter)"
          />
          <!-- 十字光芒线 -->
          <line class="star-ray" x1="200" y1="82" x2="200" y2="118" stroke="#DCD0FF" stroke-width="0.5" stroke-opacity="0.4" />
          <line class="star-ray" x1="182" y1="100" x2="218" y2="100" stroke="#DCD0FF" stroke-width="0.5" stroke-opacity="0.4" />
          <line class="star-ray" x1="187" y1="87" x2="213" y2="113" stroke="#DCD0FF" stroke-width="0.3" stroke-opacity="0.3" />
          <line class="star-ray" x1="187" y1="113" x2="213" y2="87" stroke="#DCD0FF" stroke-width="0.3" stroke-opacity="0.3" />
        </g>
      </svg>
    </div>

    <!-- ====== 密码字符层（"USERS", "BOOKS", "ZJU - SEEK TRUTH"） ====== -->
    <div ref="codeTextLayerRef" class="intro-code-layer" aria-hidden="true">
      <span class="code-char" v-for="(char, i) in codeChars" :key="'code-' + i"
        :style="{
          left: char.x + '%',
          top: char.y + '%',
          animationDelay: char.delay + 's',
          '--char-opacity': char.opacity
        }"
      >{{ char.text }}</span>
    </div>

    <!-- ====== 数学坐标轴 / 雷达扫描线（CSS 辅助层） ====== -->
    <div ref="radarLayerRef" class="intro-radar-layer" aria-hidden="true">
      <div class="radar-line radar-line-h"></div>
      <div class="radar-line radar-line-v"></div>
      <div class="radar-scan"></div>
    </div>

    <!-- ====== 底部品牌文字 ====== -->
    <div ref="brandTextRef" class="intro-brand-text">
      <span class="brand-cn">紫金求思</span>
      <span class="brand-en">ZIJIN · QIUSI</span>
    </div>
  </div>
</template>

<script setup>
/**
 * ============================================================
 *  IntroAnimation.vue — 紫金求思 · 电影级开场进入动图
 * ============================================================
 *  技术栈：HTML5 Canvas + SVG + CSS Animations + RequestAnimationFrame
 *  物理引擎：自定义粒子系统（阻尼弹性 + 流体动力学模拟）
 *  运动曲线：Cinematic 贝塞尔曲线 cubic-bezier(0.16, 1, 0.3, 1)
 *  性能目标：4K 120Hz 全 GPU 加速，锁定 60/120 FPS
 * ============================================================
 */

import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'

// ==================== 组件事件 ====================
const emit = defineEmits(['animation-done'])

// ==================== 响应式状态 ====================
const containerRef = ref(null)
const canvasRef = ref(null)
const svgLayerRef = ref(null)
const logoSvgRef = ref(null)
const bookGroupRef = ref(null)
const magnifierGroupRef = ref(null)
const starGroupRef = ref(null)
const codeTextLayerRef = ref(null)
const radarLayerRef = ref(null)
const brandTextRef = ref(null)

const canvasWidth = ref(window.innerWidth)
const canvasHeight = ref(window.innerHeight)
const componentOpacity = ref(1)
const prefersReducedMotion = ref(false)

// ==================== 密码字符配置 ====================
/**
 * 密码字符层：模拟数据流中跳动的数据库模型字符和校训文本
 * 每个字符有独立的 x/y 位置、延迟和透明度，创造密码线般的静默跳动感
 */
const codeChars = [
  // 左上区域：数据库模型
  { text: 'U', x: 8, y: 12, delay: 0.02, opacity: 0.15 },
  { text: 'S', x: 14, y: 18, delay: 0.05, opacity: 0.12 },
  { text: 'E', x: 20, y: 8, delay: 0.08, opacity: 0.10 },
  { text: 'R', x: 26, y: 15, delay: 0.03, opacity: 0.13 },
  { text: 'S', x: 32, y: 10, delay: 0.06, opacity: 0.11 },
  // 右上区域
  { text: 'B', x: 68, y: 8, delay: 0.04, opacity: 0.14 },
  { text: 'O', x: 74, y: 14, delay: 0.07, opacity: 0.12 },
  { text: 'O', x: 80, y: 10, delay: 0.02, opacity: 0.10 },
  { text: 'K', x: 86, y: 16, delay: 0.05, opacity: 0.13 },
  { text: 'S', x: 92, y: 8, delay: 0.09, opacity: 0.11 },
  // 左下区域：校训
  { text: 'Z', x: 10, y: 82, delay: 0.06, opacity: 0.10 },
  { text: 'J', x: 16, y: 88, delay: 0.03, opacity: 0.08 },
  { text: 'U', x: 22, y: 84, delay: 0.08, opacity: 0.09 },
  { text: '-', x: 28, y: 90, delay: 0.04, opacity: 0.07 },
  { text: 'S', x: 34, y: 86, delay: 0.07, opacity: 0.10 },
  { text: 'E', x: 40, y: 92, delay: 0.02, opacity: 0.08 },
  { text: 'E', x: 46, y: 88, delay: 0.05, opacity: 0.09 },
  { text: 'K', x: 52, y: 84, delay: 0.09, opacity: 0.07 },
  // 右下区域
  { text: 'T', x: 70, y: 82, delay: 0.04, opacity: 0.10 },
  { text: 'R', x: 76, y: 88, delay: 0.07, opacity: 0.08 },
  { text: 'U', x: 82, y: 84, delay: 0.02, opacity: 0.09 },
  { text: 'T', x: 88, y: 90, delay: 0.06, opacity: 0.07 },
  { text: 'H', x: 94, y: 86, delay: 0.08, opacity: 0.10 },
  // 边缘散落数学符号
  { text: '∑', x: 5, y: 45, delay: 0.10, opacity: 0.06 },
  { text: 'π', x: 95, y: 40, delay: 0.12, opacity: 0.06 },
  { text: '∫', x: 50, y: 5, delay: 0.11, opacity: 0.05 },
  { text: '∂', x: 50, y: 95, delay: 0.13, opacity: 0.05 },
]

// ==================== 粒子系统 ====================
/**
 * Particle 类 — 微米级粒子物理引擎
 *
 * 物理属性说明：
 *   x, y      : 当前位置（像素坐标）
 *   vx, vy    : 速度向量（像素/帧）
 *   ax, ay    : 加速度（用于流体动力学模拟）
 *   alpha     : 当前透明度 (0-1)
 *   targetAlpha: 目标透明度（用于平滑过渡）
 *   size      : 粒子半径（像素）
 *   life      : 生命周期（0-1, 1 为刚出生）
 *   ease      : 弹性系数（0-1, 越大越有弹性）
 *   damping   : 阻尼系数（0-1, 模拟空气阻力）
 *   targetX, targetY: 目标位置（汇聚终点）
 *   originX, originY: 初始位置（生成时的位置）
 *   phase     : 相位偏移（用于错峰延迟 Stagger）
 *   hue       : 色相（淡紫色系 260-290）
 *   saturation: 饱和度
 *   lightness : 明度
 */
class Particle {
  constructor(x, y, targetX, targetY, phase) {
    this.x = x
    this.y = y
    this.originX = x
    this.originY = y
    this.targetX = targetX
    this.targetY = targetY
    this.vx = 0
    this.vy = 0
    this.ax = 0
    this.ay = 0
    this.alpha = 0
    this.targetAlpha = 0.6 + Math.random() * 0.3
    this.size = 0.8 + Math.random() * 2.0  // 0.8px - 2.8px 极细粒子
    this.life = 0
    this.phase = phase  // 错峰延迟相位 (0-1)
    this.damping = 0.90 + Math.random() * 0.08  // 阻尼系数 0.90-0.98
    this.ease = 0.025 + Math.random() * 0.025   // 弹性系数 0.025-0.05
    this.hue = 260 + Math.random() * 30         // 淡紫色系 260-290
    this.saturation = 40 + Math.random() * 30   // 饱和度 40-70
    this.lightness = 65 + Math.random() * 20    // 明度 65-85
    this.overshoot = 0  // 反向舒展量（用于弹性 overshoot 效果）
    this.converged = false  // 是否已到达目标位置
  }

  /**
   * update() — 每帧更新粒子物理状态
   *
   * 物理模型：带阻尼的弹性趋近（Damped Harmonic Oscillator）
   * 公式：F = -k * (x - target) - b * v
   * 其中 k 为弹性系数（ease），b 为阻尼系数（damping）
   *
   * 当粒子接近目标时，会产生轻微的 overshoot（反向舒展）
   * 模拟真实物理世界中弹簧停止前的微小震荡
   */
  update(deltaTime, progress) {
    // 错峰延迟：根据 phase 控制粒子开始移动的时间
    // phase 范围 0-1，乘以总汇聚时间（前 20% 的动画时长）
    const convergeDuration = ANIMATION_DURATION * 0.2
    const activationDelay = this.phase * convergeDuration
    const localProgress = Math.max(0, (progress * ANIMATION_DURATION - activationDelay) / (ANIMATION_DURATION - activationDelay))

    if (localProgress <= 0) {
      this.life = 0
      return
    }

    // 弹性趋近力（Hooke's Law）：F = -k * displacement
    const dx = this.targetX - this.x
    const dy = this.targetY - this.y

    // 应用弹性系数，产生平滑的趋近运动
    this.ax = dx * this.ease
    this.ay = dy * this.ease

    // 应用阻尼（空气阻力）：b * v
    this.vx = (this.vx + this.ax) * this.damping
    this.vy = (this.vy + this.ay) * this.damping

    // 更新位置
    this.x += this.vx
    this.y += this.vy

    // 判断是否已汇聚到目标位置
    const distToTarget = Math.sqrt(dx * dx + dy * dy)
    if (distToTarget < 2) {
      this.converged = true
      // 轻微 overshoot 效果
      this.overshoot = Math.min(1, (5 - distToTarget) / 5)
    } else {
      this.overshoot *= 0.9
    }

    // 生命周期管理：
    // 汇聚阶段 (0-0.3): 透明度从 0 逐渐增加到 targetAlpha
    // 保持阶段 (0.3-0.85): 保持完全可见
    // 消散阶段 (0.85-1.0): 透明度逐渐归零
    if (localProgress < 0.3) {
      this.life = localProgress / 0.3
    } else if (localProgress > 0.85) {
      this.life = Math.max(0, (1 - localProgress) / 0.15)
    } else {
      this.life = 1
    }

    this.alpha = this.targetAlpha * this.life
  }

  /**
   * draw() — 在 Canvas 上绘制粒子
   *
   * 使用圆形渐变绘制，模拟发光微粒子效果
   * 粒子极小（0.8-2.8px），通过径向渐变产生光晕
   */
  draw(ctx) {
    if (this.alpha < 0.01) return

    ctx.save()
    ctx.globalAlpha = this.alpha

    // 使用径向渐变绘制发光粒子
    const gradient = ctx.createRadialGradient(
      this.x, this.y, 0,
      this.x, this.y, this.size * 2.5
    )
    gradient.addColorStop(0, `hsla(${this.hue}, ${this.saturation}%, ${this.lightness}%, 1)`)
    gradient.addColorStop(0.4, `hsla(${this.hue}, ${this.saturation}%, ${this.lightness}%, 0.6)`)
    gradient.addColorStop(1, `hsla(${this.hue}, ${this.saturation}%, ${this.lightness}%, 0)`)

    ctx.fillStyle = gradient
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size * 2.5, 0, Math.PI * 2)
    ctx.fill()

    ctx.restore()
  }
}

// ==================== Canvas 粒子系统管理 ====================
let particles = []
let animationFrameId = null
let startTime = 0
let canvasCtx = null
let isAnimating = false
const ANIMATION_DURATION = 4000  // 总时长 4000ms（延长至 4 秒，让首页有更多时间浮现）

/**
 * 生成粒子系统
 *
 * 粒子数量：约 2000 个（在性能和视觉效果之间取得平衡）
 * 分布策略：从屏幕四周向中心 Logo 位置汇聚
 * 错峰延迟：每个粒子有独立的 phase 值（0-1），控制到达时间
 */
function createParticles(width, height) {
  const particleCount = 2000
  const centerX = width / 2
  const centerY = height / 2
  const newParticles = []

  for (let i = 0; i < particleCount; i++) {
    // 粒子初始位置：分布在屏幕四周边缘
    let x, y
    const edge = Math.random()

    if (edge < 0.25) {
      x = Math.random() * width
      y = -10 - Math.random() * 80
    } else if (edge < 0.5) {
      x = Math.random() * width
      y = height + 10 + Math.random() * 80
    } else if (edge < 0.75) {
      x = -10 - Math.random() * 80
      y = Math.random() * height
    } else {
      x = width + 10 + Math.random() * 80
      y = Math.random() * height
    }

    // 目标位置：围绕 Logo 中心（书本区域）随机分布
    // 形成半翻开的书的轮廓
    const angle = Math.random() * Math.PI * 2
    const radius = 20 + Math.random() * 90
    const targetX = centerX + Math.cos(angle) * radius * (0.5 + Math.random() * 0.5)
    const targetY = centerY + Math.sin(angle) * radius * 0.6 - 20

    // 错峰延迟相位：0-1 均匀分布，创造多米诺骨牌效应
    const phase = Math.random()

    newParticles.push(new Particle(x, y, targetX, targetY, phase))
  }

  return newParticles
}

/**
 * 绘制雷达扫描线和坐标轴
 *
 * 数学坐标轴：极细 0.5px 半透明线条
 * 雷达扫描线：旋转的扇形扫描效果
 */
function drawRadarLines(ctx, width, height, progress) {
  const centerX = width / 2
  const centerY = height / 2
  const alpha = Math.max(0, 0.15 * (1 - progress * 2))

  if (alpha < 0.01) return

  ctx.save()
  ctx.globalAlpha = alpha

  // 水平坐标轴
  ctx.strokeStyle = '#DCD0FF'
  ctx.lineWidth = 0.5
  ctx.beginPath()
  ctx.moveTo(0, centerY)
  ctx.lineTo(width, centerY)
  ctx.stroke()

  // 垂直坐标轴
  ctx.beginPath()
  ctx.moveTo(centerX, 0)
  ctx.lineTo(centerX, height)
  ctx.stroke()

  // 刻度标记
  ctx.strokeStyle = '#C4B5E0'
  ctx.lineWidth = 0.3
  for (let i = 0; i < 20; i++) {
    const x = (width / 20) * i
    const y = (height / 20) * i

    ctx.beginPath()
    ctx.moveTo(x, centerY - 5)
    ctx.lineTo(x, centerY + 5)
    ctx.stroke()

    ctx.beginPath()
    ctx.moveTo(centerX - 5, y)
    ctx.lineTo(centerX + 5, y)
    ctx.stroke()
  }

  // 雷达扫描线（旋转扇形）
  const scanAngle = (Date.now() / 2000) * Math.PI * 2
  ctx.strokeStyle = '#DCD0FF'
  ctx.lineWidth = 0.3
  ctx.beginPath()
  ctx.moveTo(centerX, centerY)
  ctx.lineTo(
    centerX + Math.cos(scanAngle) * Math.max(width, height) * 0.7,
    centerY + Math.sin(scanAngle) * Math.max(width, height) * 0.7
  )
  ctx.stroke()

  // 雷达扫描扇形（半透明填充）
  ctx.fillStyle = 'rgba(220, 208, 255, 0.02)'
  ctx.beginPath()
  ctx.moveTo(centerX, centerY)
  ctx.arc(centerX, centerY, Math.max(width, height) * 0.5, scanAngle - 0.1, scanAngle)
  ctx.closePath()
  ctx.fill()

  ctx.restore()
}

/**
 * 碎金粒子系统（从书页中漂散）
 *
 * 模拟条形码符号和汉字偏旁从书页中向后漂散消融
 */
let debrisParticles = []

function createDebrisParticles(centerX, centerY) {
  const count = 80
  const newDebris = []

  for (let i = 0; i < count; i++) {
    const angle = -Math.PI / 2 + (Math.random() - 0.5) * Math.PI * 0.8
    const speed = 0.5 + Math.random() * 2.0
    newDebris.push({
      x: centerX + (Math.random() - 0.5) * 80,
      y: centerY + (Math.random() - 0.5) * 50,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed - 0.8,
      alpha: 0.5 + Math.random() * 0.5,
      size: 1 + Math.random() * 2.5,
      life: 1,
      decay: 0.003 + Math.random() * 0.008,
      rotation: Math.random() * Math.PI * 2,
      rotSpeed: (Math.random() - 0.5) * 0.08,
      shape: Math.floor(Math.random() * 3),
    })
  }

  return newDebris
}

function updateDebrisParticles(debris, deltaTime) {
  for (const d of debris) {
    d.x += d.vx
    d.y += d.vy
    d.vy += 0.02
    d.alpha -= d.decay
    d.life -= d.decay
    d.rotation += d.rotSpeed
  }
  return debris.filter(d => d.life > 0 && d.alpha > 0)
}

function drawDebrisParticles(ctx, debris) {
  ctx.save()

  for (const d of debris) {
    ctx.globalAlpha = Math.max(0, d.alpha)
    ctx.translate(d.x, d.y)
    ctx.rotate(d.rotation)

    ctx.strokeStyle = '#DCD0FF'
    ctx.fillStyle = '#DCD0FF'
    ctx.lineWidth = 0.5

    if (d.shape === 0) {
      ctx.beginPath()
      ctx.arc(0, 0, d.size, 0, Math.PI * 2)
      ctx.fill()
    } else if (d.shape === 1) {
      ctx.fillRect(-d.size * 0.3, -d.size * 2, d.size * 0.6, d.size * 4)
    } else {
      ctx.strokeRect(-d.size, -d.size, d.size * 2, d.size * 2)
    }

    ctx.setTransform(1, 0, 0, 1, 0, 0)
  }

  ctx.restore()
}

/**
 * 主渲染循环 — RequestAnimationFrame 驱动
 *
 * 性能优化策略：
 * 1. 使用 requestAnimationFrame 与浏览器 VSync 同步
 * 2. 每帧只绘制可见粒子（alpha > 0.01 的粒子）
 * 3. 粒子数量控制在 2000 个以内
 * 4. 使用 Canvas 2D 上下文，避免 DOM 操作开销
 * 5. 在 4K 屏幕上自动适配 canvas 尺寸
 */
function renderLoop(timestamp) {
  if (!isAnimating) return

  const ctx = canvasCtx
  if (!ctx) return

  const width = canvasWidth.value
  const height = canvasHeight.value

  // 计算动画进度（0-1）
  if (!startTime) startTime = timestamp
  const elapsed = timestamp - startTime
  const progress = Math.min(1, elapsed / ANIMATION_DURATION)

  // 清空画布
  ctx.clearRect(0, 0, width, height)

  // ====== 阶段一 (0-20%)：绘制雷达扫描线和坐标轴 ======
  if (progress < 0.2) {
    drawRadarLines(ctx, width, height, progress / 0.2)
  }

  // ====== 更新并绘制粒子（所有阶段持续绘制） ======
  for (const p of particles) {
    p.update(1, progress)
    p.draw(ctx)
  }

  // ====== 阶段二 (20%-60%)：碎金粒子漂散 ======
  if (progress >= 0.2 && progress < 0.6) {
    if (debrisParticles.length === 0 && progress >= 0.2 && progress < 0.25) {
      debrisParticles = createDebrisParticles(width / 2, height / 2)
    }
    if (debrisParticles.length > 0) {
      debrisParticles = updateDebrisParticles(debrisParticles, 1)
      drawDebrisParticles(ctx, debrisParticles)
    }
  }

  // ====== 阶段三 (60%-75%)：超新星爆发（Supernova Burst） ======
  // 粒子从汇聚位置向外剧烈爆炸式飞散，像超新星爆发
  // 每个粒子沿随机方向高速飞散，伴随拖尾光效
  // 使用 burstProgress² 弹性曲线产生先慢后快的爆发感
  if (progress >= 0.6 && progress < 0.75) {
    const burstProgress = (progress - 0.6) / 0.15
    ctx.save()
    for (const p of particles) {
      if (p.converged) {
        // 为每个粒子生成一个独特的爆炸方向（基于 phase 种子）
        const burstAngle = p.phase * Math.PI * 2 + burstProgress * 0.3
        // 爆炸距离：使用平方曲线，从 0 到最大 500px，产生先慢后快的爆发感
        const burstDist = burstProgress * burstProgress * 500
        const burstX = Math.cos(burstAngle) * burstDist
        const burstY = Math.sin(burstAngle) * burstDist

        // 保存原始位置
        const savedX = p.x
        const savedY = p.y
        p.x += burstX
        p.y += burstY

        // 透明度：前半段保持高亮，后半段逐渐降低
        const burstAlpha = burstProgress < 0.4
          ? 1
          : Math.max(0, 1 - (burstProgress - 0.4) / 0.6)
        const savedAlpha = p.alpha
        p.alpha = p.targetAlpha * burstAlpha

        // 粒子大小随爆炸距离增大而缩小（模拟星尘消散）
        const savedSize = p.size
        p.size = savedSize * Math.max(0.2, 1 - burstProgress * 0.8)

        // 绘制粒子
        p.draw(ctx)

        // 绘制拖尾光效：在粒子后方绘制一条渐隐的细线
        if (burstProgress > 0.1) {
          ctx.save()
          ctx.globalAlpha = p.alpha * 0.3
          ctx.strokeStyle = `hsla(${p.hue}, ${p.saturation}%, ${p.lightness}%, 0.3)`
          ctx.lineWidth = p.size * 0.5
          ctx.beginPath()
          const trailLength = burstDist * 0.15
          ctx.moveTo(p.x, p.y)
          ctx.lineTo(
            p.x - Math.cos(burstAngle) * trailLength,
            p.y - Math.sin(burstAngle) * trailLength
          )
          ctx.stroke()
          ctx.restore()
        }

        // 恢复原始属性
        p.x = savedX
        p.y = savedY
        p.alpha = savedAlpha
        p.size = savedSize
      }
    }
    ctx.restore()
  }

  // ====== 阶段四 (70%-100%)：涟漪式粒子蒸发（Ripple Evaporation） ======
  // 粒子从中心向外呈涟漪状扩散，像石头扔进水中激起的涟漪
  // 黑色背景通过 mask-image radial-gradient 从中心向外涟漪式变透明
  // 涟漪边缘有发光粒子跟随，创造"水面波纹"般的视觉效果
  // 首页在涟漪扩散的过程中逐渐露出，没有任何"突然切换"
  // 阶段四占 30% 总时长（1200ms）
  if (progress >= 0.7) {
    const rippleProgress = (progress - 0.7) / 0.3
    // 使用 ease-out 曲线：涟漪开始时快速扩散，然后逐渐减速
    // 模拟真实水面涟漪的物理特性
    const easedProgress = 1 - Math.pow(1 - rippleProgress, 2)

    // 涟漪半径：从 0% 到 100%（覆盖整个屏幕）
    const rippleRadius = easedProgress * 100

    // 使用 mask-image radial-gradient 从中心向外涟漪式变透明
    // 透明区域从中心逐渐扩大，黑色背景从中心向外"蒸发"
    const container = containerRef.value
    if (container) {
      // 涟漪边缘宽度：5% 的模糊过渡带，创造柔和的消散边缘
      const blurEdge = 5
      const solidStart = Math.min(rippleRadius + blurEdge, 100)
      container.style.maskImage = `radial-gradient(circle at 50% 50%, transparent 0%, transparent ${rippleRadius}%, #0D0A12 ${solidStart}%, #0D0A12 100%)`
      container.style.webkitMaskImage = `radial-gradient(circle at 50% 50%, transparent 0%, transparent ${rippleRadius}%, #0D0A12 ${solidStart}%, #0D0A12 100%)`
    }

    // 粒子随涟漪向外扩散
    ctx.save()
    for (const p of particles) {
      if (p.converged) {
        // 粒子沿径向向外扩散（从中心指向四周）
        const angle = Math.atan2(p.y - canvasHeight.value / 2, p.x - canvasWidth.value / 2)
        // 扩散距离：随涟漪进度增加，最大 600px
        const burstDist = easedProgress * easedProgress * 600
        const burstX = Math.cos(angle) * burstDist
        const burstY = Math.sin(angle) * burstDist

        const savedX = p.x
        const savedY = p.y
        p.x += burstX
        p.y += burstY

        // 透明度：涟漪边缘的粒子保持可见，其他粒子逐渐消失
        const distFromCenter = Math.sqrt(
          Math.pow(p.x - canvasWidth.value / 2, 2) +
          Math.pow(p.y - canvasHeight.value / 2, 2)
        )
        const maxDist = Math.max(canvasWidth.value, canvasHeight.value) * 0.7
        const normalizedDist = Math.min(1, distFromCenter / maxDist)
        // 粒子在涟漪边缘附近最亮，远离边缘则消失
        const edgeProximity = 1 - Math.abs(normalizedDist - rippleProgress * 0.7) * 3
        const particleAlpha = Math.max(0, Math.min(1, edgeProximity))
        const savedAlpha = p.alpha
        p.alpha = p.targetAlpha * particleAlpha

        const savedSize = p.size
        p.size = savedSize * Math.max(0.15, 1 - easedProgress * 0.85)

        p.draw(ctx)

        p.x = savedX
        p.y = savedY
        p.alpha = savedAlpha
        p.size = savedSize
      }
    }
    ctx.restore()
  }

  // ====== 动画结束检测 ======
  if (progress >= 1) {
    isAnimating = false
    // 动画主循环结束，但不要立即 emit
    // 此时 mask-image 已让容器完全透明（rippleRadius = 100%）
    // 但容器元素本身还在（position: fixed, z-index: 999999）
    // 触发 CSS transition：opacity → 0, transform → scale(0.95)
    // 等 transitionend 事件触发后再 emit('animation-done')
    triggerContainerFadeOut()
    return
  }

  // 继续下一帧
  animationFrameId = requestAnimationFrame(renderLoop)
}

// ==================== SVG 动画控制 ====================
/**
 * 控制 SVG 各元素的入场和动画时序
 * 使用 CSS Animations + JavaScript 时间线控制
 */
function animateSVGElements(progress) {
  const bookGroup = bookGroupRef.value
  const magnifierGroup = magnifierGroupRef.value
  const starGroup = starGroupRef.value

  if (!bookGroup || !magnifierGroup || !starGroup) return

  // ====== 阶段一 (0-20%)：粒子汇聚，SVG 元素准备 ======
  if (progress >= 0.15 && progress < 0.25) {
    // 书本组逐渐显现
    const bookAlpha = (progress - 0.15) / 0.10
    bookGroup.setAttribute('opacity', String(bookAlpha))
    // 星星组开始显现
    const starAlpha = Math.max(0, (progress - 0.18) / 0.07)
    starGroup.setAttribute('opacity', String(starAlpha))
  }

  // ====== 阶段二 (25%-65%)：全息高光爆发 + 书页翻动 ======
  if (progress >= 0.25 && progress < 0.65) {
    // 书本完全显现
    bookGroup.setAttribute('opacity', '1')
    starGroup.setAttribute('opacity', '1')

    // 星星高光脉冲：在阶段二前半段达到峰值
    const starPulse = Math.sin((progress - 0.25) / 0.40 * Math.PI)
    const starHalo = starGroup.querySelector('.star-halo')
    if (starHalo) {
      const scale = 1 + starPulse * 2  // 放大 1-3 倍
      starHalo.setAttribute('transform', `scale(${scale})`)
      starHalo.setAttribute('transform-origin', '200 100')
    }

    // 书页翻动动效：左右页交替错峰
    const pageProgress = (progress - 0.25) / 0.40  // 0-1
    const leftPage = bookGroup.querySelector('.book-page-left')
    const rightPage = bookGroup.querySelector('.book-page-right')
    if (leftPage && rightPage) {
      // 左页翻动：绕书脊旋转
      const leftRotate = -15 * Math.sin(pageProgress * Math.PI)
      leftPage.setAttribute('transform', `skewY(${leftRotate})`)
      // 右页翻动：绕书脊旋转（错峰延迟 0.1）
      const rightRotate = 15 * Math.sin(Math.max(0, pageProgress - 0.1) / 0.9 * Math.PI)
      rightPage.setAttribute('transform', `skewY(${rightRotate})`)
    }

    // 放大镜组在阶段二后半段开始显现
    if (progress >= 0.45) {
      const magAlpha = (progress - 0.45) / 0.10
      magnifierGroup.setAttribute('opacity', String(Math.min(1, magAlpha)))
    }
  }

  // ====== 阶段三 (65%-90%)：玻璃拟态破茧 ======
  if (progress >= 0.65 && progress < 0.90) {
    // 放大镜 Z 轴拉伸（通过 scale 模拟）
    const magProgress = (progress - 0.65) / 0.25
    const magScale = 1 + magProgress * 0.15  // 放大 1-1.15 倍
    magnifierGroup.setAttribute('transform', `scale(${magScale})`)
    magnifierGroup.setAttribute('transform-origin', '200 160')
    magnifierGroup.setAttribute('opacity', '1')

    // 书本和星星逐渐淡出
    const fadeOut = Math.max(0, 1 - (progress - 0.70) / 0.20)
    bookGroup.setAttribute('opacity', String(fadeOut))
    starGroup.setAttribute('opacity', String(fadeOut))
  }

  // ====== 阶段四 (90%-100%)：全局解构 ======
  if (progress >= 0.90) {
    // 所有 SVG 元素淡出
    bookGroup.setAttribute('opacity', '0')
    magnifierGroup.setAttribute('opacity', '0')
    starGroup.setAttribute('opacity', '0')
  }
}

// ==================== 容器淡出控制 ====================

/**
 * triggerContainerFadeOut() — 动画主循环结束后触发容器 CSS 淡出
 *
 * 此时 mask-image 已让容器内容完全透明（rippleRadius = 100%）
 * 但容器的 background-color: #0D0A12 不受 mask 影响，仍然可见
 * 如果直接清除 mask-image，黑色背景会瞬间"返场"
 *
 * 正确做法：
 * 1. 保持 mask-image 不变（内容已透明）
 * 2. 将 background 设为 transparent（消除黑色背景）
 * 3. 设置 pointer-events: none（不阻挡首页交互）
 * 4. 触发 CSS transition 让 opacity 平滑过渡到 0
 * 5. transitionend 事件触发后 emit('animation-done')
 * 6. 父组件通过 v-if 移除组件（此时容器已完全不可见）
 */
function triggerContainerFadeOut() {
  const container = containerRef.value
  if (container) {
    // 关键：不要清除 mask-image！保持内容透明状态
    // 将 background 设为 transparent，消除黑色背景
    container.style.background = 'transparent'
    // 不阻挡首页交互
    container.style.pointerEvents = 'none'
  }
  // 触发 CSS transition：opacity → 0
  // 300ms ease-out 曲线，足够平滑
  componentOpacity.value = 0
}

/**
 * handleTransitionEnd() — CSS transition 完成后的回调
 * 此时容器已经完全透明，可以安全地通知父组件移除
 *
 * 防重复发射保护：使用 alreadyEmitted 标记确保只 emit 一次
 * 因为 transitionend 可能因多个 CSS 属性触发多次
 */
let alreadyEmitted = false
function handleTransitionEnd(event) {
  // 只处理 opacity 过渡完成，且确保只 emit 一次
  if (event.propertyName === 'opacity' && !alreadyEmitted) {
    alreadyEmitted = true
    emit('animation-done')
  }
}

// ==================== 组件生命周期 ====================

/**
 * 检测用户是否开启了"减少动态效果"偏好
 * 如果是，则优雅降级为简单淡入淡出
 */
function checkReducedMotion() {
  const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  prefersReducedMotion.value = mediaQuery.matches

  // 监听偏好变化
  mediaQuery.addEventListener('change', (e) => {
    prefersReducedMotion.value = e.matches
  })
}

/**
 * 启动动画
 * 如果用户开启了减少动态效果，则执行简单淡入淡出
 */
function startAnimation() {
  if (prefersReducedMotion.value) {
    // 优雅降级：0.5s 简单淡入淡出
    componentOpacity.value = 0
    setTimeout(() => {
      componentOpacity.value = 1
    }, 50)
    setTimeout(() => {
      componentOpacity.value = 0
    }, 400)
    setTimeout(() => {
      emit('animation-done')
    }, 500)
    return
  }

  // 正常启动 Canvas 粒子动画
  const canvas = canvasRef.value
  if (!canvas) return

  canvasCtx = canvas.getContext('2d', {
    alpha: true,
    desynchronized: true,  // 启用 desynchronized 提示浏览器使用独立合成线程
  })

  // 生成粒子
  particles = createParticles(canvasWidth.value, canvasHeight.value)

  // 启动渲染循环
  isAnimating = true
  startTime = 0
  animationFrameId = requestAnimationFrame(renderLoop)

  // 启动 SVG 动画时间线
  const svgStartTime = performance.now()
  const svgTimeline = () => {
    if (!isAnimating) return
    const elapsed = performance.now() - svgStartTime
    const progress = Math.min(1, elapsed / ANIMATION_DURATION)
    animateSVGElements(progress)
    if (progress < 1) {
      requestAnimationFrame(svgTimeline)
    }
  }
  requestAnimationFrame(svgTimeline)
}

/**
 * 窗口大小变化时重新适配 Canvas 尺寸
 * 确保在 4K 屏幕上正确显示
 */
function handleResize() {
  canvasWidth.value = window.innerWidth
  canvasHeight.value = window.innerHeight

  // 如果动画尚未开始，重新生成粒子
  if (!isAnimating && particles.length > 0) {
    particles = createParticles(canvasWidth.value, canvasHeight.value)
  }
}

onMounted(() => {
  // 检测减少动态效果偏好
  checkReducedMotion()

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)

  // 监听容器 CSS transition 完成事件
  // 当 triggerContainerFadeOut() 将 componentOpacity 设为 0 后，
  // CSS transition 会平滑过渡，完成后触发 handleTransitionEnd
  const container = containerRef.value
  if (container) {
    container.addEventListener('transitionend', handleTransitionEnd)
  }

  // 使用 nextTick 确保 DOM 已渲染完成
  nextTick(() => {
    startAnimation()
  })
})

onBeforeUnmount(() => {
  // 清理动画资源
  isAnimating = false
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }

  // 清理粒子
  particles = []
  debrisParticles = []

  // 移除事件监听
  window.removeEventListener('resize', handleResize)

  // 移除 transitionend 监听，防止内存泄漏
  const container = containerRef.value
  if (container) {
    container.removeEventListener('transitionend', handleTransitionEnd)
  }

  // 清理 Canvas 上下文
  canvasCtx = null
})
</script>

<style scoped>
/* ============================================================
   IntroAnimation.vue — 紫金求思 · 电影级开场进入动图
   ============================================================
   设计语言：极简主义 + 精密科技感
   配色体系：
     --bg-deep: #0D0A12       (深邃极暗紫黑)
     --lavender: #DCD0FF      (薰衣草淡紫 - 高光/发光)
     --lilac: #C4B5E0         (丁香紫 - 中调)
     --text-muted: #4A3B5A    (柔和的深灰紫)
   运动曲线：cubic-bezier(0.16, 1, 0.3, 1) — Cinematic Slow-down
   ============================================================ */

/* ---- 主容器：全屏固定定位，深邃紫黑背景 ---- */
.intro-animation {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 999999;
  background: #0D0A12;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: all;
  /* 平滑透明度过渡：当组件被 v-if 移除时，避免突然消失 */
  transition: opacity 0.3s ease-out;
}

/* ---- Canvas 层：全屏覆盖 ---- */
.intro-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  /* GPU 加速提示 */
  transform: translateZ(0);
  will-change: transform;
}

/* ---- SVG 叠加层：居中定位 ---- */
.intro-svg-layer {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
  z-index: 2;
}

/* ---- Logo SVG ---- */
.intro-logo-svg {
  width: 280px;
  height: 280px;
  filter: drop-shadow(0 0 40px rgba(220, 208, 255, 0.08));
}

/* ---- 密码字符层 ---- */
.intro-code-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.code-char {
  position: absolute;
  font-family: 'Courier New', monospace;
  font-size: 10px;
  color: #DCD0FF;
  opacity: var(--char-opacity, 0.1);
  animation: codePulse 2s ease-in-out infinite;
  letter-spacing: 1px;
  font-weight: 300;
  text-shadow: 0 0 8px rgba(220, 208, 255, 0.15);
}

@keyframes codePulse {
  0%, 100% { opacity: var(--char-opacity, 0.1); }
  50% { opacity: calc(var(--char-opacity, 0.1) * 2.5); }
}

/* ---- 雷达扫描线层 ---- */
.intro-radar-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
  opacity: 0.08;
  animation: radarFade 0.6s ease-out forwards;
}

@keyframes radarFade {
  0% { opacity: 0.15; }
  100% { opacity: 0; }
}

.radar-line {
  position: absolute;
  background: #DCD0FF;
}

.radar-line-h {
  top: 50%;
  left: 0;
  width: 100%;
  height: 0.5px;
  transform: translateY(-50%);
}

.radar-line-v {
  left: 50%;
  top: 0;
  height: 100%;
  width: 0.5px;
  transform: translateX(-50%);
}

.radar-scan {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 200%;
  height: 200%;
  transform: translate(-50%, -50%);
  background: conic-gradient(
    from 0deg,
    transparent 0deg,
    rgba(220, 208, 255, 0.03) 1deg,
    transparent 2deg
  );
  animation: radarSpin 2s linear infinite;
  border-radius: 50%;
}

@keyframes radarSpin {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

/* ---- 底部品牌文字 ---- */
.intro-brand-text {
  position: absolute;
  bottom: 60px;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  z-index: 3;
  opacity: 0;
  animation: brandFadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.6s forwards;
}

@keyframes brandFadeIn {
  0% {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
  100% {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.brand-cn {
  display: block;
  font-size: 28px;
  font-weight: 300;
  letter-spacing: 0.3em;
  color: #DCD0FF;
  text-shadow: 0 0 30px rgba(220, 208, 255, 0.1);
  margin-bottom: 6px;
}

.brand-en {
  display: block;
  font-size: 11px;
  font-weight: 200;
  letter-spacing: 0.5em;
  color: #C4B5E0;
  text-shadow: 0 0 20px rgba(196, 181, 224, 0.08);
}

/* ---- 减少动态效果降级 ---- */
.intro-animation--reduced {
  animation: simpleFade 0.5s ease-out;
}

@keyframes simpleFade {
  0% { opacity: 0; }
  100% { opacity: 1; }
}

/* ---- 响应式适配 ---- */
@media (max-width: 768px) {
  .intro-logo-svg {
    width: 200px;
    height: 200px;
  }

  .brand-cn {
    font-size: 22px;
  }

  .brand-en {
    font-size: 9px;
  }

  .code-char {
    font-size: 8px;
  }
}

@media (max-width: 480px) {
  .intro-logo-svg {
    width: 160px;
    height: 160px;
  }

  .brand-cn {
    font-size: 18px;
  }

  .brand-en {
    font-size: 8px;
  }
}
</style>
