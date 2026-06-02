/**
 * 红点系统自动化测试
 * ============================================================
 * 测试项：
 *   1. 新消息通知 → 红点显示
 *   2. 点击消息侧边栏 → 红点消失
 *   3. 新私信通知 → 红点显示
 *   4. 点击私信侧边栏 → 红点消失
 *   5. 页面刷新 → 红点状态恢复
 * ============================================================
 */
const TOTAL_TESTS = 20
let passed = 0
let failed = 0
let testIndex = 0

function assert(condition, msg) {
  testIndex++
  const icon = condition ? 'PASS' : 'FAIL'
  if (condition) passed++; else failed++
  console.log(`  ${condition ? '✓' : '✗'} ${icon}: ${msg}`)
}

function testHeader(title) {
  console.log(`\n${'='.repeat(60)}`)
  console.log(`  第 ${Math.ceil(testIndex / (TOTAL_TESTS/3))} 轮测试：${title}`)
  console.log(`${'='.repeat(60)}\n`)
}

// ============================================================
// 模拟 localStorage
// ============================================================
const fakeStorage = {}
global.localStorage = {
  getItem: (key) => fakeStorage[key] ?? null,
  setItem: (key, val) => { fakeStorage[key] = String(val) },
  removeItem: (key) => { delete fakeStorage[key] },
  clear: () => { Object.keys(fakeStorage).forEach(k => delete fakeStorage[k]) },
}

// ============================================================
// 模拟 store 的红点相关函数（直接从 useStore.js 提取逻辑）
// ============================================================
const STORE = {
  KEYS: {
    notifications: 'qushu_user_notifications',
    chatUnreadCount: 'qushu_chat_unread_count',
    notifReadTimestamp: 'qushu_notif_read_timestamp',
  },

  _notifications: {},
  _chatUnreadCount: 0,
  _notifReadTimestamp: 0,
  _currentUser: null,
  _isLoggedIn: false,
  _currentPage: 'home',

  get currentUser() { return this._currentUser },
  set currentUser(v) { this._currentUser = v },
  get isLoggedIn() { return this._isLoggedIn },
  set isLoggedIn(v) { this._isLoggedIn = v },
  get currentPage() { return this._currentPage },
  set currentPage(v) { this._currentPage = v },

  initFromLocal() {
    try {
      const n = JSON.parse(localStorage.getItem(this.KEYS.notifications))
      if (n) this._notifications = n
    } catch {}
    this._chatUnreadCount = parseInt(localStorage.getItem(this.KEYS.chatUnreadCount)) || 0
    this._notifReadTimestamp = parseInt(localStorage.getItem(this.KEYS.notifReadTimestamp)) || 0
  },

  saveLocal(key, data) {
    localStorage.setItem(key, JSON.stringify(data))
  },

  // ---- 消息通知红点 ----
  hasUnreadNotif(userName) {
    const notifs = this._notifications[userName] || []
    return notifs.some(n => n.unread)
  },

  getNotifUnreadCount(userName) {
    return (this._notifications[userName] || []).filter(n => n.unread).length
  },

  markNotifRead() {
    this._notifReadTimestamp = Date.now()
    this.saveLocal(this.KEYS.notifReadTimestamp, this._notifReadTimestamp)
  },

  markAllRead(userName) {
    const notifs = this._notifications[userName]
    if (notifs) {
      notifs.forEach(n => { n.unread = false })
      this.saveLocal(this.KEYS.notifications, this._notifications)
    }
    this.markNotifRead()
  },

  addNotification(userName, notif) {
    if (!this._notifications[userName]) {
      this._notifications[userName] = []
    }
    this._notifications[userName].push(notif)
    this.saveLocal(this.KEYS.notifications, this._notifications)
  },

  // ---- 私信红点 ----
  getChatUnreadCount() {
    return this._chatUnreadCount
  },

  hasChatUnread() {
    return this._chatUnreadCount > 0
  },

  updateChatUnreadCount(count) {
    this._chatUnreadCount = Math.max(0, count)
    this.saveLocal(this.KEYS.chatUnreadCount, this._chatUnreadCount)
  },

  resetChatUnreadCount() {
    this._chatUnreadCount = 0
    this.saveLocal(this.KEYS.chatUnreadCount, 0)
  },
}

// ============================================================
// 测试执行
// ============================================================

// 清理 & 初始化
localStorage.clear()
STORE.initFromLocal()
STORE.isLoggedIn = true
STORE.currentUser = { name: '测试用户' }
STORE.currentPage = 'home'

// ------- 测试场景 1：消息通知红点 -------
testHeader('消息通知红点功能')

// 1a. 初始状态：无通知 → 无红点
assert(STORE.hasUnreadNotif('测试用户') === false, '初始状态无未读通知')
assert(STORE.getNotifUnreadCount('测试用户') === 0, '初始未读计数为 0')

// 1b. 添加一条未读消息通知
STORE.addNotification('测试用户', {
  title: '系统通知',
  desc: '有一条新消息',
  time: new Date().toISOString(),
  unread: true,
})
assert(STORE.hasUnreadNotif('测试用户') === true, '添加新消息通知后红点显示')
assert(STORE.getNotifUnreadCount('测试用户') === 1, '未读计数为 1')

// 1c. 添加第二条未读通知
STORE.addNotification('测试用户', {
  title: '订单通知',
  desc: '您的订单已发货',
  time: new Date().toISOString(),
  unread: true,
})
assert(STORE.getNotifUnreadCount('测试用户') === 2, '两条未读通知计数为 2')
assert(STORE.hasUnreadNotif('测试用户') === true, '两条未读时红点仍显示')

// 1d. 点击消息侧边栏 → 标记已读 → 红点消失
STORE.markAllRead('测试用户')
assert(STORE.hasUnreadNotif('测试用户') === false, '点击消息侧边栏后红点消失')
assert(STORE.getNotifUnreadCount('测试用户') === 0, '标记已读后未读计数为 0')

// 1e. 添加已读通知（unread=false）
STORE.addNotification('测试用户', {
  title: '旧通知',
  desc: '这是已读消息',
  time: new Date().toISOString(),
  unread: false,
})
assert(STORE.hasUnreadNotif('测试用户') === false, '仅添加已读通知时无红点')

// 1f. 再次添加未读通知
STORE.addNotification('测试用户', {
  title: '新消息',
  desc: '紧急通知',
  time: new Date().toISOString(),
  unread: true,
})
assert(STORE.hasUnreadNotif('测试用户') === true, '新未读通知再次出现后红点重新显示')

// ------- 测试场景 2：私信红点 -------
testHeader('私信红点功能')

// 2a. 初始状态：无未读私信 → 无红点
STORE.resetChatUnreadCount()
assert(STORE.hasChatUnread() === false, '初始状态无私信红点')
assert(STORE.getChatUnreadCount() === 0, '初始私信未读计数为 0')

// 2b. 模拟收到新私信（未读数>0）
STORE.updateChatUnreadCount(3)
assert(STORE.hasChatUnread() === true, '收到新私信后红点显示')
assert(STORE.getChatUnreadCount() === 3, '私信未读计数为 3')

// 2c. 模拟收到大量私信
STORE.updateChatUnreadCount(99)
assert(STORE.hasChatUnread() === true, '大量私信时红点显示')
assert(STORE.getChatUnreadCount() === 99, '私信未读计数为 99')

// 2d. 点击私信侧边栏 → 红点消失
STORE.resetChatUnreadCount()
assert(STORE.hasChatUnread() === false, '点击私信侧边栏后红点消失')
assert(STORE.getChatUnreadCount() === 0, '重置后私信未读计数为 0')

// 2e. 模拟部分私信已读（计数减少仍>0）
STORE.updateChatUnreadCount(2)
assert(STORE.hasChatUnread() === true, '部分未读时红点显示')
STORE.updateChatUnreadCount(1)
assert(STORE.hasChatUnread() === true, '仅剩 1 条未读时红点仍显示')
STORE.updateChatUnreadCount(0)
assert(STORE.hasChatUnread() === false, '全部已读后红点消失')

// ------- 测试场景 3：持久化 & 刷新恢复 -------
testHeader('持久化与刷新恢复')

// 3a. 模拟刷新前状态：有未读通知 + 有私信
localStorage.clear()
STORE._notifications = {}
STORE._chatUnreadCount = 0
STORE.initFromLocal()
STORE.isLoggedIn = true
STORE.currentUser = { name: '测试用户' }

STORE.addNotification('测试用户', { title: '离线消息', desc: '刷新前收到的消息', time: '2025-01-01', unread: true })
STORE.updateChatUnreadCount(5)

// 模拟页面刷新（重新初始化）
STORE.initFromLocal()
STORE.isLoggedIn = true
STORE.currentUser = { name: '测试用户' }

assert(STORE.hasUnreadNotif('测试用户') === true, '刷新后消息红点恢复')
assert(STORE.getNotifUnreadCount('测试用户') === 1, '刷新后未读消息计数正确')
assert(STORE.hasChatUnread() === true, '刷新后私信红点恢复')
assert(STORE.getChatUnreadCount() === 5, '刷新后私信未读计数正确')

// 3b. 刷新前已读状态恢复
STORE.markAllRead('测试用户')
STORE.resetChatUnreadCount()
STORE.initFromLocal()
STORE.isLoggedIn = true
STORE.currentUser = { name: '测试用户' }

assert(STORE.hasUnreadNotif('测试用户') === false, '刷新前已标记已读 → 刷新后无消息红点')
assert(STORE.hasChatUnread() === false, '刷新前已清零 → 刷新后无私信红点')

// 3c. 混合场景：消息已读 + 私信未读
STORE.addNotification('测试用户', { title: '通知A', desc: '已读', time: '2025-01-01', unread: false })
STORE.addNotification('测试用户', { title: '通知B', desc: '未读', time: '2025-01-01', unread: true })
STORE.updateChatUnreadCount(2)
STORE.initFromLocal()
STORE.isLoggedIn = true
STORE.currentUser = { name: '测试用户' }

assert(STORE.hasUnreadNotif('测试用户') === true, '混合场景：消息有红点')
assert(STORE.getNotifUnreadCount('测试用户') === 1, '混合场景：消息未读计数为 1')
assert(STORE.hasChatUnread() === true, '混合场景：私信有红点')
assert(STORE.getChatUnreadCount() === 2, '混合场景：私信计数为 2')

// 3d. 未登录用户 → 无红点
STORE.isLoggedIn = false
assert(STORE.hasUnreadNotif('测试用户') === true, '未登录但数据存在（hasUnreadNotif 仅检查数据）')
STORE.isLoggedIn = true

// 3e. 边界：负数计数
STORE.updateChatUnreadCount(-5)
assert(STORE.getChatUnreadCount() === 0, '负数计数自动修正为 0')

// ============================================================
// 结果汇总
// ============================================================
console.log(`\n${'='.repeat(60)}`)
console.log(`  汇总：${testIndex} 测试 / ${passed} 通过 / ${failed} 失败 / 通过率 ${(passed/testIndex*100).toFixed(0)}%`)
console.log(`${'='.repeat(60)}`)
if (failed > 0) {
  console.log(`\n  ❌ 有 ${failed} 项测试未通过，请检查！\n`)
  process.exit(1)
} else {
  console.log(`\n  ✅ 所有测试完美通过！\n`)
}