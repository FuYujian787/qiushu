<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useTheme } from '@/composables/useTheme'

const { theme } = useTheme()

// ── Particle System ──────────────────────────────────────
const canvasRef = ref(null)
let animationId = null

class Particle {
  constructor(w, h) {
    this.x = Math.random() * w
    this.y = Math.random() * h
    this.vx = (Math.random() - 0.5) * 0.6
    this.vy = (Math.random() - 0.5) * 0.6
    this.radius = Math.random() * 2 + 0.5
    this.opacity = Math.random() * 0.4 + 0.08
    // Mix of cyan and purple particles
    this.hue = Math.random() < 0.6 ? 192 : 272  // 192=cyan, 272=purple
  }

  update(w, h) {
    this.x += this.vx
    this.y += this.vy
    if (this.x < -50 || this.x > w + 50) this.vx *= -1
    if (this.y < -50 || this.y > h + 50) this.vy *= -1
  }

  draw(ctx) {
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2)
    ctx.fillStyle = `hsla(${this.hue}, 100%, 70%, ${this.opacity})`
    ctx.fill()
  }
}

let particles = []

function initParticles() {
  const canvas = canvasRef.value
  if (!canvas) return
  const w = (canvas.width = window.innerWidth)
  const h = (canvas.height = window.innerHeight)
  particles = Array.from({ length: 50 }, () => new Particle(w, h))
}

function drawParticles() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const w = canvas.width
  const h = canvas.height

  ctx.clearRect(0, 0, w, h)

  // Draw particles
  for (const p of particles) {
    p.update(w, h)
    p.draw(ctx)
  }

  // Draw connection lines between nearby particles
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x
      const dy = particles[i].y - particles[j].y
      const dist = Math.sqrt(dx * dx + dy * dy)
      if (dist < 130) {
        ctx.beginPath()
        ctx.moveTo(particles[i].x, particles[i].y)
        ctx.lineTo(particles[j].x, particles[j].y)
        const alpha = 0.06 * (1 - dist / 130)
        ctx.strokeStyle = `rgba(0, 212, 255, ${alpha})`
        ctx.lineWidth = 0.5
        ctx.stroke()
      }
    }
  }

  animationId = requestAnimationFrame(drawParticles)
}

function handleResize() {
  const canvas = canvasRef.value
  if (!canvas) return
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
}

onMounted(() => {
  initParticles()
  drawParticles()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <!-- Only visible in cyber (dark) theme -->
  <div v-show="theme === 'cyber'" class="cyber-background" aria-hidden="true">
    <!-- Layer 1: Atmospheric background image -->
    <div class="bg-image-layer">
      <img
        src="/mock/images/1ebdf91c-24ee-4556-9c68-ceb7ed6282f3.png"
        alt=""
        class="bg-image"
        loading="eager"
      />
    </div>

    <!-- Layer 2: Gradient overlays -->
    <div class="bg-gradient-overlay"></div>
    <div class="bg-vignette"></div>

    <!-- Layer 3: Particle canvas -->
    <canvas ref="canvasRef" class="particle-canvas" />

    <!-- Layer 4: Subtle scanline effect -->
    <div class="bg-scanlines"></div>
  </div>
</template>

<style scoped>
.cyber-background {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

/* ── Layer 1: Background Image ─────────────────────────── */
.bg-image-layer {
  position: absolute;
  inset: 0;
  /* Center the image, cover the viewport */
  display: flex;
  align-items: center;
  justify-content: center;
}

.bg-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  /* Blend with deep purple-black surface */
  opacity: 0.38;
  filter:
    blur(0.5px)
    brightness(0.85)
    saturate(1.3);
  /* Screen blend mode creates luminous effect against dark bg */
  mix-blend-mode: screen;
  transform: scale(1.01);
}

/* ── Layer 2: Gradient Overlays ────────────────────────── */
.bg-gradient-overlay {
  position: absolute;
  inset: 0;
  background:
    /* Gentle fade at very edges only — text areas stay clear */
    linear-gradient(180deg,
      rgba(9, 5, 26, 0.45) 0%,
      rgba(9, 5, 26, 0.08) 12%,
      rgba(9, 5, 26, 0.0)  25%,
      rgba(9, 5, 26, 0.0)  75%,
      rgba(9, 5, 26, 0.08) 88%,
      rgba(9, 5, 26, 0.45) 100%
    ),
    /* Cyan accent glow — top-right */
    radial-gradient(ellipse 600px 400px at 85% 15%, rgba(0, 212, 255, 0.10) 0%, transparent 70%),
    /* Purple accent glow — bottom-left */
    radial-gradient(ellipse 500px 350px at 15% 85%, rgba(168, 85, 247, 0.08) 0%, transparent 70%),
    /* Warm accent — center-right */
    radial-gradient(ellipse 400px 300px at 70% 50%, rgba(0, 212, 255, 0.06) 0%, transparent 60%);
}

.bg-vignette {
  position: absolute;
  inset: 0;
  background: radial-gradient(
    ellipse at center,
    transparent 50%,
    rgba(9, 5, 26, 0.25) 80%,
    rgba(9, 5, 26, 0.45) 100%
  );
}

/* ── Layer 3: Particle Canvas ──────────────────────────── */
.particle-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

/* ── Layer 4: Scanlines ────────────────────────────────── */
.bg-scanlines {
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 0, 0, 0.03) 2px,
    rgba(0, 0, 0, 0.03) 4px
  );
  opacity: 0.3;
  pointer-events: none;
}

/* ── Reduced motion ────────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
  .bg-image {
    filter: blur(1px) brightness(0.6) saturate(1.4);
  }
}
</style>
