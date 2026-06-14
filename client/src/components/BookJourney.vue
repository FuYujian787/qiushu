<script setup>
const props = defineProps({
  journeys: {
    type: Array,
    default: () => [],
  },
})

const eventConfig = {
  '初次上架': { label: '首次发布', icon: '📚', color: '#5B8C5A' },
  '售出': { label: '转手', icon: '🤝', color: '#C41E3A' },
  '再次上架': { label: '再次上架', icon: '🔄', color: '#B8860B' },
}

function getEventStyle(type) {
  const config = eventConfig[type]
  if (!config) return {}
  return { '--node-color': config.color }
}

function getEventLabel(type) {
  return eventConfig[type]?.label || type
}

function getEventIcon(type) {
  return eventConfig[type]?.icon || '📖'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${day} ${h}:${min}`
}

function getDescription(journey) {
  const { event_type: type, from_user_name: fromName, to_user_name: toName, note } = journey
  switch (type) {
    case '初次上架':
      return fromName ? `${fromName} 首次发布此书` : '书籍首次发布'
    case '售出':
      if (fromName && toName) {
        return `${fromName} 转让给 ${toName}`
      }
      return note || '书籍已售出'
    case '再次上架':
      return fromName ? `${fromName} 再次上架此书` : '书籍再次上架'
    default:
      return note || type
  }
}
</script>

<template>
  <div class="book-journey">
    <h3 class="journey-title">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
        <circle cx="12" cy="12" r="10"/>
        <polyline points="12 6 12 12 16 14"/>
      </svg>
      书籍旅程
    </h3>

    <!-- Empty State -->
    <div v-if="!journeys || journeys.length === 0" class="journey-empty">
      <div class="empty-icon">📖</div>
      <p class="empty-text">这本书正在等待它的第一位主人</p>
      <p class="empty-hint">每一本书都有一段独特的旅程，而这段旅程还未开始</p>
    </div>

    <!-- Timeline -->
    <div v-else class="timeline">
      <div
        v-for="(item, index) in journeys"
        :key="item.id || index"
        class="timeline-node"
        :class="{ 'is-last': index === journeys.length - 1 }"
        :style="getEventStyle(item.event_type)"
      >
        <div class="node-marker">
          <span class="node-icon">{{ getEventIcon(item.event_type) }}</span>
        </div>
        <div class="node-content">
          <div class="node-header">
            <span class="node-type" :style="{ color: eventConfig[item.event_type]?.color }">
              {{ getEventLabel(item.event_type) }}
            </span>
            <span class="node-time">{{ formatDate(item.created_at) }}</span>
          </div>
          <p class="node-description">{{ getDescription(item) }}</p>
          <p v-if="item.note && item.event_type !== '售出'" class="node-note">{{ item.note }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.book-journey {
  grid-column: 1 / -1;
  margin-top: 48px;
  padding: 32px;
  background: var(--surface-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
}

.journey-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-display);
  font-size: 20px;
  color: var(--text-primary);
  margin-bottom: 28px;
}

/* ========== Empty State ========== */
.journey-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 24px;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.8;
}

.empty-text {
  font-family: var(--font-display);
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.empty-hint {
  font-size: 13px;
  color: var(--text-muted);
}

/* ========== Timeline ========== */
.timeline {
  position: relative;
  padding-left: 36px;
}

/* Vertical line */
.timeline::before {
  content: '';
  position: absolute;
  left: 15px;
  top: 8px;
  bottom: 0;
  width: 2px;
  background: var(--border-strong);
  border-radius: 1px;
}

/* ========== Timeline Node ========== */
.timeline-node {
  position: relative;
  padding-bottom: 28px;
  --node-color: var(--accent-primary);
}

.timeline-node.is-last {
  padding-bottom: 0;
}

/* Circle marker on the line */
.node-marker {
  position: absolute;
  left: -27px;
  top: 2px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--surface-secondary);
  border: 2px solid var(--node-color, var(--accent-primary));
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

.node-icon {
  font-size: 11px;
  line-height: 1;
}

.node-content {
  background: var(--surface-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  padding: 14px 18px;
  transition: box-shadow 0.2s;
}

.node-content:hover {
  box-shadow: var(--shadow-sm);
}

.node-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.node-type {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
}

.node-time {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-muted);
}

.node-description {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0;
}

.node-note {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
  font-style: italic;
}

/* ========== Cyber theme ========== */
[data-theme="cyber"] .journey-empty .empty-icon {
  filter: drop-shadow(0 0 8px rgba(0,212,255,0.4));
}

[data-theme="cyber"] .node-marker {
  box-shadow: 0 0 8px var(--node-color, rgba(0,212,255,0.5));
}

[data-theme="cyber"] .node-content {
  background: var(--surface-secondary);
  backdrop-filter: blur(8px);
}
</style>
