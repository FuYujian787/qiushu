<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const auth = useAuthStore()

const treeData = ref(null)
const loading = ref(false)
const error = ref('')
const selectedNode = ref(null)

// 按 depth 分组节点
const depthGroups = computed(() => {
  if (!treeData.value?.nodes) return []
  const groups = {}
  treeData.value.nodes.forEach(node => {
    const d = node.depth ?? 0
    if (!groups[d]) groups[d] = []
    groups[d].push(node)
  })
  return Object.keys(groups)
    .sort((a, b) => Number(a) - Number(b))
    .map(depth => ({
      depth: Number(depth),
      nodes: groups[depth],
    }))
})

// 按起点分组边
const edgesByFrom = computed(() => {
  if (!treeData.value?.edges) return {}
  const map = {}
  treeData.value.edges.forEach(edge => {
    if (!map[edge.from]) map[edge.from] = []
    map[edge.from].push(edge)
  })
  return map
})

onMounted(async () => {
  if (!auth.isLoggedIn) return
  loading.value = true
  error.value = ''
  try {
    const res = await api.get('/tree')
    treeData.value = res.data
  } catch (err) {
    error.value = err.message || '加载传承树失败'
  } finally {
    loading.value = false
  }
})

function selectNode(node) {
  selectedNode.value = selectedNode.value?.id === node.id ? null : node
}

function nodeConnections(nodeId) {
  if (!treeData.value?.edges) return { incoming: [], outgoing: [] }
  const incoming = treeData.value.edges.filter(e => e.to === nodeId)
  const outgoing = treeData.value.edges.filter(e => e.from === nodeId)
  return { incoming, outgoing }
}
</script>

<template>
  <div class="tree-page page-enter">
    <div class="page-container">
      <!-- Header -->
      <div class="tree-header">
        <h1 class="page-title">🌳 知识传承树</h1>
        <p class="page-subtitle">每一本书的流转，都是知识的传承。连接越密，传承越深。</p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="tree-loader">
          <span class="loader-ring"></span>
          <p>正在绘制知识图谱...</p>
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="empty-state">
        <div class="empty-icon">⚠️</div>
        <p>{{ error }}</p>
      </div>

      <!-- Not Logged In -->
      <div v-else-if="!auth.isLoggedIn" class="empty-state">
        <div class="empty-icon">🔐</div>
        <p class="empty-title">登录后查看你的知识传承树</p>
        <p class="empty-hint">发布并交易书籍后，这里将展示你与他人之间的知识传递关系</p>
      </div>

      <!-- Empty Tree -->
      <div v-else-if="!treeData || !treeData.nodes?.length" class="empty-state">
        <div class="empty-icon">🌱</div>
        <p class="empty-title">传承树还是空的</p>
        <p class="empty-hint">买或卖一本书，就会种下一颗传承的种子</p>
      </div>

      <!-- Tree Visualization -->
      <div v-else class="tree-container">
        <!-- Stats -->
        <div class="tree-stats">
          <div class="stat-item">
            <span class="stat-value">{{ treeData.stats?.total_nodes || 0 }}</span>
            <span class="stat-label">节点</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ treeData.stats?.total_edges || 0 }}</span>
            <span class="stat-label">连接</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ treeData.stats?.max_depth || 0 }}</span>
            <span class="stat-label">深度</span>
          </div>
        </div>

        <!-- SVG Graph -->
        <div class="tree-graph" v-if="depthGroups.length > 0">
          <!-- Depth levels -->
          <div
            v-for="group in depthGroups"
            :key="group.depth"
            class="depth-level"
          >
            <div class="depth-label">
              {{ group.depth === 0 ? '我' : `第 ${group.depth} 层` }}
            </div>
            <div class="depth-nodes">
              <div
                v-for="node in group.nodes"
                :key="node.id"
                :class="[
                  'graph-node',
                  `level-${Math.min(group.depth, 3)}`,
                  { selected: selectedNode?.id === node.id },
                  { 'is-root': group.depth === 0 },
                ]"
                @click="selectNode(node)"
              >
                <!-- Node Avatar -->
                <div class="node-avatar">
                  {{ (node.name || '书友')[0] }}
                </div>
                <div class="node-info">
                  <span class="node-name">{{ node.name }}</span>
                  <span v-if="node.college" class="node-college">{{ node.college }}</span>
                </div>

                <!-- Edge count badge -->
                <span
                  v-if="(edgesByFrom[node.id]?.length || 0) > 0"
                  class="node-edge-badge"
                  :title="`${edgesByFrom[node.id].length} 条传出连接`"
                >
                  {{ edgesByFrom[node.id].length }}→
                </span>
              </div>
            </div>
          </div>

          <!-- Edge Lines (SVG overlay) -->
          <svg class="edges-svg" v-if="treeData.edges?.length">
            <line
              v-for="(edge, i) in treeData.edges"
              :key="i"
              class="edge-line"
              x1="0" y1="0" x2="0" y2="0"
              :data-from="edge.from"
              :data-to="edge.to"
            />
          </svg>

          <!-- Connection Legend -->
          <div class="edge-legend" v-if="treeData.edges?.length">
            <div
              v-for="(edge, i) in treeData.edges.slice(0, 10)"
              :key="i"
              class="edge-item"
            >
              <span class="edge-from">{{ treeData.nodes.find(n => n.id === edge.from)?.name || '书友' }}</span>
              <span class="edge-arrow">—📖→</span>
              <span class="edge-to">{{ treeData.nodes.find(n => n.id === edge.to)?.name || '书友' }}</span>
              <span class="edge-book" :title="edge.book_title">{{ edge.book_title }}</span>
            </div>
            <p v-if="treeData.edges.length > 10" class="edge-more">
              还有 {{ treeData.edges.length - 10 }} 条连接...
            </p>
          </div>
        </div>

        <!-- Selected Node Detail -->
        <div v-if="selectedNode" class="node-detail-panel">
          <h3>
            <span class="detail-avatar">{{ (selectedNode.name || '书友')[0] }}</span>
            {{ selectedNode.name }}
          </h3>
          <p v-if="selectedNode.college">{{ selectedNode.college }}</p>
          <div class="node-stats">
            <span>传出了 {{ nodeConnections(selectedNode.id).outgoing.length }} 本书</span>
            <span>收到了 {{ nodeConnections(selectedNode.id).incoming.length }} 本书</span>
          </div>
          <div v-if="nodeConnections(selectedNode.id).outgoing.length" class="node-books">
            <p class="books-label">传出的书：</p>
            <span
              v-for="conn in nodeConnections(selectedNode.id).outgoing"
              :key="conn.book_id"
              class="book-tag"
            >
              {{ conn.book_title }}
            </span>
          </div>
          <div v-if="nodeConnections(selectedNode.id).incoming.length" class="node-books">
            <p class="books-label">收到的书：</p>
            <span
              v-for="conn in nodeConnections(selectedNode.id).incoming"
              :key="conn.book_id"
              class="book-tag"
            >
              {{ conn.book_title }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ========== Header ========== */
.tree-header {
  margin-bottom: 32px;
  text-align: center;
}
.page-title {
  font-family: var(--font-display);
  font-size: 28px;
  color: var(--text-primary);
  font-weight: 700;
  margin-bottom: 8px;
}
.page-subtitle {
  color: var(--text-muted);
  font-size: 14px;
}

/* ========== States ========== */
.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 24px;
  text-align: center;
}
.tree-loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--text-muted);
}
.loader-ring {
  width: 48px;
  height: 48px;
  border: 3px solid var(--border-default);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.empty-icon { font-size: 48px; margin-bottom: 16px; }
.empty-title { font-size: 16px; color: var(--text-primary); font-weight: 600; margin-bottom: 6px; }
.empty-hint { font-size: 13px; color: var(--text-muted); max-width: 320px; }

/* ========== Tree Container ========== */
.tree-container {
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: 32px;
}

/* ========== Stats ========== */
.tree-stats {
  display: flex;
  justify-content: center;
  gap: 48px;
  margin-bottom: 36px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-default);
}
.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.stat-value {
  font-family: var(--font-mono);
  font-size: 32px;
  font-weight: 700;
  color: var(--accent-primary);
}
.stat-label {
  font-size: 12px;
  color: var(--text-muted);
}

/* ========== Depth Levels ========== */
.depth-level {
  margin-bottom: 28px;
  position: relative;
}
.depth-label {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 10px;
  padding-left: 4px;
}
.depth-nodes {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

/* ========== Graph Node ========== */
.graph-node {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  border-radius: var(--radius-md);
  border: 2px solid var(--border-default);
  background: var(--surface-primary);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  min-width: 140px;
}
.graph-node:hover {
  border-color: var(--accent-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
.graph-node.selected {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--accent-primary-light);
}
.graph-node.is-root {
  border-width: 3px;
  border-color: var(--accent-primary);
  background: var(--accent-primary-light);
}
.graph-node.level-0 { border-color: var(--accent-primary); }
.graph-node.level-1 { border-color: rgba(196,30,58,0.4); }
.graph-node.level-2 { border-color: rgba(196,30,58,0.25); }
.graph-node.level-3 { border-color: var(--border-strong); }

[data-theme="cyber"] .graph-node.level-0 { border-color: #00D4FF; box-shadow: 0 0 16px rgba(0,212,255,0.2); }
[data-theme="cyber"] .graph-node.level-1 { border-color: rgba(0,212,255,0.4); }
[data-theme="cyber"] .graph-node.level-2 { border-color: rgba(168,85,247,0.3); }
[data-theme="cyber"] .graph-node.level-3 { border-color: var(--border-strong); }
[data-theme="cyber"] .graph-node.is-root {
  border-color: #00D4FF;
  background: rgba(0,212,255,0.08);
  box-shadow: 0 0 24px rgba(0,212,255,0.15);
}

.node-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--accent-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 15px;
  flex-shrink: 0;
}
.is-root .node-avatar {
  width: 44px;
  height: 44px;
  font-size: 18px;
}
.node-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.node-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.node-college {
  font-size: 11px;
  color: var(--text-muted);
}
.node-edge-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: var(--accent-secondary);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 10px;
  font-family: var(--font-mono);
}

/* ========== Edges Legend ========== */
.edge-legend {
  margin-top: 24px;
  padding: 20px;
  background: var(--surface-primary);
  border-radius: var(--radius-sm);
  border: 1px dashed var(--border-strong);
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.edge-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--surface-secondary);
  border-radius: 20px;
  font-size: 13px;
  border: 1px solid var(--border-default);
}
.edge-arrow {
  color: var(--accent-primary);
  font-size: 14px;
}
.edge-from, .edge-to {
  font-weight: 500;
  color: var(--text-primary);
}
.edge-book {
  color: var(--text-muted);
  font-size: 11px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.edge-more {
  width: 100%;
  text-align: center;
  color: var(--text-muted);
  font-size: 12px;
  margin: 0;
  padding-top: 4px;
}

/* ========== Node Detail Panel ========== */
.node-detail-panel {
  margin-top: 24px;
  padding: 20px;
  background: var(--surface-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
}
.node-detail-panel h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  color: var(--text-primary);
  margin-bottom: 8px;
}
.detail-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent-primary);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
}
.node-stats {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}
.node-books {
  margin-top: 8px;
}
.books-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 6px;
}
.book-tag {
  display: inline-block;
  padding: 3px 10px;
  margin: 2px 4px 2px 0;
  background: var(--surface-tertiary);
  border-radius: 12px;
  font-size: 12px;
  color: var(--text-secondary);
}

/* ========== SVG overlay (placeholder) ========== */
.edges-svg {
  display: none;
}

/* ========== Dark theme ========== */
[data-theme="cyber"] .graph-node:hover {
  box-shadow: 0 0 20px rgba(0,212,255,0.15);
}
[data-theme="cyber"] .graph-node.selected {
  box-shadow: 0 0 0 2px rgba(0,212,255,0.3), 0 0 16px rgba(0,212,255,0.1);
}
[data-theme="cyber"] .tree-stats { border-bottom-color: rgba(255,255,255,0.06); }
[data-theme="cyber"] .edge-item {
  background: var(--surface-tertiary);
  border-color: rgba(255,255,255,0.06);
}

/* ========== Responsive ========== */
@media (max-width: 768px) {
  .tree-container {
    padding: 16px;
  }
  .tree-stats {
    gap: 28px;
  }
  .stat-value {
    font-size: 24px;
  }
  .graph-node {
    min-width: 120px;
    padding: 8px 12px;
  }
}
</style>
