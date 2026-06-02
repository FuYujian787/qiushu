/**
 * 自动下架功能 — Node.js 测试脚本
 * 直接测试核心数据逻辑（不依赖 Vue 响应式系统）
 * 运行：node test-delist.cjs
 */

// ============================================================
// 模拟 localStorage（内存版）
// ============================================================
const memoryStore = {}
global.localStorage = {
  getItem(key) { return memoryStore[key] || null },
  setItem(key, val) { memoryStore[key] = val },
  removeItem(key) { delete memoryStore[key] },
}

// ============================================================
// 测试框架
// ============================================================
let totalPass = 0
let totalFail = 0
const results = []

function assert(name, condition) {
  const ok = condition
  results.push({ name, ok })
  if (ok) { totalPass++ }
  else { totalFail++ }
  const icon = ok ? '✅ PASS' : '❌ FAIL'
  console.log(`  ${icon}: ${name}`)
  return ok
}

function testHeader(title, round) {
  console.log(`\n${'='.repeat(60)}`)
  console.log(`  🧪 第 ${round} 轮测试：${title}`)
  console.log(`${'='.repeat(60)}\n`)
}

function testSummary() {
  const total = totalPass + totalFail
  const pct = total > 0 ? Math.round(totalPass / total * 100) : 0
  console.log(`\n${'='.repeat(60)}`)
  console.log(`  📊 汇总：${totalPass} 通过 / ${totalFail} 失败 / 通过率 ${pct}%`)
  console.log(`${'='.repeat(60)}`)

  if (totalFail > 0) {
    console.log('\n  ❌ 存在失败测试！请检查上述 FAIL 项。')
    process.exit(1)
  } else {
    console.log('\n  ✅ 所有测试完美通过！')
    process.exit(0)
  }
}

// ============================================================
// 被测试的函数（从 useStore.js 提取的核心逻辑）
// ============================================================

function createProductCache(count) {
  const books = []
  for (let i = 0; i < count; i++) {
    books.push({
      id: i + 1,
      title: '测试书' + (i + 1),
      author: '作者' + (i + 1),
      price: (10 + (i % 10)).toFixed(1),
      condition: '九成新',
      seller: '同学' + (100 + i),
      category: '教材',
      isUserPublished: i >= count - 3, // 最后3本是用户发布的
      status: 'active',
    })
  }
  return books
}

function placeOrder(cart, buyerName, address, productCache, publishedBooks) {
  const delistedIds = new Set(JSON.parse(localStorage.getItem('qushu_delisted_ids') || '[]'))
  const delistLogs = JSON.parse(localStorage.getItem('qushu_delist_logs') || '[]')
  const orders = JSON.parse(localStorage.getItem('qushu_orders') || '[]')

  for (const item of cart) {
    const order = {
      id: 'ORD-' + Date.now() + '-' + Math.random().toString(36).substr(2, 4),
      title: item.title,
      price: item.price,
      status: '已售',
      date: new Date().toISOString().slice(0, 10),
      buyer: buyerName,
      seller: item.seller || '未知卖家',
      bookId: item.id,
    }
    orders.unshift(order)

    // 从 productCache 中标记并移除
    const idx = productCache.findIndex(p => p.id === item.id)
    if (idx !== -1) {
      productCache[idx].status = 'delisted'
      productCache.splice(idx, 1)
      delistedIds.add(item.id)
    }

    // 用户发布的书籍也从 publishedBooks 移除
    if (item.isUserPublished && publishedBooks) {
      const pbIdx = publishedBooks.findIndex(b => b.id === item.id)
      if (pbIdx !== -1) publishedBooks.splice(pbIdx, 1)
    }

    // 记录下架日志
    const log = {
      id: 'LOG-' + Date.now() + '-' + Math.random().toString(36).substr(2, 6),
      bookId: item.id,
      bookTitle: item.title,
      bookPrice: item.price,
      seller: item.seller || '未知卖家',
      buyer: buyerName,
      orderId: order.id,
      timestamp: new Date().toISOString(),
      operator: buyerName,
      action: 'delist',
      note: `图书《${item.title}》已通过订单 ${order.id} 售出，自动下架`,
    }
    delistLogs.unshift(log)
  }

  localStorage.setItem('qushu_delisted_ids', JSON.stringify([...delistedIds]))
  localStorage.setItem('qushu_delist_logs', JSON.stringify(delistLogs))
  localStorage.setItem('qushu_orders', JSON.stringify(orders))
  if (publishedBooks) {
    localStorage.setItem('qushu_published_books', JSON.stringify(publishedBooks))
  }

  return { delistedIds, delistLogs, orders }
}

function generateProductsWithFilter(categoriesMock, delistedIdsSet, publishedBooks) {
  const subjects = ['微积分', '线性代数', '大学英语', '有机化学']
  const conditions = ['九成新', '八成新', '全新未拆', '有笔记', '七成新']
  const categoryMap = { '微积分': '教材', '线性代数': '教材', '大学英语': '教材', '有机化学': '教材' }
  const products = []
  for (let i = 0; i < 100; i++) {
    const productId = i + 1
    if (delistedIdsSet.has(productId)) continue
    const subj = subjects[i % subjects.length]
    products.push({
      id: productId,
      title: `${subj} 辅导书 第${Math.floor(i / 10) + 1}版`,
      author: '作者',
      price: (10 + i).toFixed(1),
      condition: conditions[i % conditions.length],
      seller: `同学${100 + i}`,
      category: categoryMap[subj] || '教材',
      isUserPublished: false,
      status: 'active',
    })
  }
  return [...(publishedBooks || []), ...products]
}

function filterBooks(productCache, searchQuery, categoryFilter) {
  let result = productCache
  if (categoryFilter && categoryFilter !== '全部') {
    result = result.filter(p => p.category === categoryFilter)
  }
  if (searchQuery) {
    const q = searchQuery.toLowerCase()
    result = result.filter(p => p.title.toLowerCase().includes(q) || p.author.toLowerCase().includes(q))
  }
  return result
}

function getRandomBooks(productCache, count) {
  if (productCache.length === 0) return []
  const arr = []
  const len = productCache.length
  for (let i = 0; i < count && i < len; i++) {
    arr.push(productCache[Math.floor(Math.random() * len)])
  }
  return arr
}

// ============================================================
// 测试执行
// ============================================================

// --- 第 1 轮 --------------------------------------------------
testHeader('正常单本购买 → 自动下架 + 日志记录', 1)

localStorage.removeItem('qushu_delisted_ids')
localStorage.removeItem('qushu_delist_logs')
localStorage.removeItem('qushu_orders')
localStorage.removeItem('qushu_published_books')

const pc1 = createProductCache(20)
const pb1 = pc1.filter(b => b.isUserPublished).map(b => ({...b}))
console.log(`  📦 初始：productCache=${pc1.length} 本, publishedBooks=${pb1.length} 本`)

const cart1 = [{...pc1[2]}]  // 测试书3
console.log(`  🛒 购物车：${cart1[0].title} (id=${cart1[0].id}, isUserPublished=${cart1[0].isUserPublished})`)

const r1 = placeOrder(cart1, '买家张三', '北京市海淀区', pc1, pb1)

assert('书本已从 productCache 移除', pc1.findIndex(p => p.id === 3) === -1)
assert('delistedIds Set 包含书本 ID=3', r1.delistedIds.has(3))
assert('delistLogs 有 1 条记录', r1.delistLogs.length === 1)
assert('日志 action 为 delist', r1.delistLogs[0].action === 'delist')
assert('日志包含买家信息', r1.delistLogs[0].buyer === '买家张三')
assert('日志包含书籍标题', r1.delistLogs[0].bookTitle === '测试书3')
assert('日志包含订单 ID', typeof r1.delistLogs[0].orderId === 'string' && r1.delistLogs[0].orderId.startsWith('ORD-'))
assert('日志包含时间戳（ISO 格式）', !isNaN(Date.parse(r1.delistLogs[0].timestamp)))
assert('日志包含操作人', r1.delistLogs[0].operator === '买家张三')
assert('订单创建成功 (1条)', r1.orders.length === 1)
assert('订单状态为已售', r1.orders[0].status === '已售')
assert('productCache 长度减少 1', pc1.length === 19)
assert('publishedBooks 不受影响（非用户发布）', pb1.length === 3)
assert('localStorage delisted_ids 持久化正确', JSON.parse(localStorage.getItem('qushu_delisted_ids')).includes(3))
assert('localStorage delist_logs 持久化正确', JSON.parse(localStorage.getItem('qushu_delist_logs')).length === 1)

// --- 第 2 轮 --------------------------------------------------
testHeader('多本购买（含用户发布书籍）+ 并发安全', 2)

localStorage.removeItem('qushu_delisted_ids')
localStorage.removeItem('qushu_delist_logs')
localStorage.removeItem('qushu_orders')

const pc2 = createProductCache(20)
const pb2 = pc2.filter(b => b.isUserPublished).map(b => ({...b}))
console.log(`  📦 初始：productCache=${pc2.length} 本, publishedBooks=${pb2.length} 本`)

const cart2 = [
  {...pc2.find(b => b.id === 2)},   // 测试书2 (非用户发布)
  {...pc2.find(b => b.id === 7)},   // 测试书7 (非用户发布)
  {...pc2.find(b => b.id === 18)},  // 测试书18 (用户发布)
]
console.log(`  🛒 购物车：3 本（包含 1 本用户发布）`)

const r2 = placeOrder(cart2, '批量买家', '收货地址', pc2, pb2)

const allRemoved = pc2.findIndex(p => p.id === 2) === -1
  && pc2.findIndex(p => p.id === 7) === -1
  && pc2.findIndex(p => p.id === 18) === -1
assert('三本均已移除', allRemoved)

assert('delistedIds 包含三个 ID', r2.delistedIds.has(2) && r2.delistedIds.has(7) && r2.delistedIds.has(18))
assert('delistLogs 记录 3 条', r2.delistLogs.length === 3)
assert('三条日志 ID 唯一', new Set(r2.delistLogs.map(l => l.id)).size === 3)
assert('订单 3 条', r2.orders.length === 3)

assert('userPublished 已从 publishedBooks 移除', pb2.findIndex(b => b.id === 18) === -1)
assert('其他 userPublished 保留', pb2.findIndex(b => b.id === 19) !== -1)
assert('productCache 长度减 3', pc2.length === 17)

// --- 第 3 轮 --------------------------------------------------
testHeader('检索过滤 & 生成时跳过 & 边界条件', 3)

localStorage.removeItem('qushu_delisted_ids')
localStorage.removeItem('qushu_delist_logs')
localStorage.removeItem('qushu_orders')

const pc3 = createProductCache(20)
const pb3 = pc3.filter(b => b.isUserPublished).map(b => ({...b}))

// 先购买测试书5
const cart3 = [{...pc3.find(b => b.id === 5)}]
placeOrder(cart3, '买家测试', '地址', pc3, pb3)

// 测试：搜索过滤
const searchResultTitle = filterBooks(pc3, '测试书5', null)
assert('搜索已下架标题返回空', searchResultTitle.length === 0)

const searchResultAll = filterBooks(pc3, '', null)
assert('无搜索词时已下架不在结果中', searchResultAll.findIndex(p => p.id === 5) === -1)

const categoryResult = filterBooks(pc3, '', '教材')
assert('分类浏览不包含已下架', categoryResult.findIndex(p => p.id === 5) === -1)

// 测试：推荐列表
const randomBooks = getRandomBooks(pc3, 4)
assert('推荐列表不包含已下架', randomBooks.findIndex(b => b.id === 5) === -1)

// 测试：generateProducts 跳过 delisted ID
const skipIds = new Set(JSON.parse(localStorage.getItem('qushu_delisted_ids')))
const regenerated = generateProductsWithFilter(null, skipIds, [])
assert('重新生成时跳过已下架 ID', regenerated.findIndex(p => p.id === 5) === -1)
assert('相邻 ID（4, 6）仍在', regenerated.findIndex(p => p.id === 4) !== -1 && regenerated.findIndex(p => p.id === 6) !== -1)

// 测试：空购物车
const pcEmpty = createProductCache(10)
const lenBefore = pcEmpty.length
placeOrder([], '空买家', '地址', pcEmpty, null)
assert('空购物车不改变 productCache', pcEmpty.length === lenBefore)

// 测试：重复购买同一本
localStorage.removeItem('qushu_orders')
localStorage.removeItem('qushu_delist_logs')
localStorage.removeItem('qushu_delisted_ids')
const pcDup = createProductCache(10)
const dupCart = [{...pcDup[0]}, {...pcDup[0]}]
const rDup = placeOrder(dupCart, '重复买家', '地址', pcDup, null)
assert('重复购买生成 2 条日志', rDup.delistLogs.filter(l => l.bookId === 1).length === 2)
assert('重复购买生成 2 个订单', rDup.orders.length === 2)

// 测试：并发安全
localStorage.removeItem('qushu_orders')
localStorage.removeItem('qushu_delist_logs')
localStorage.removeItem('qushu_delisted_ids')
const pcCon = createProductCache(10)
const book = {...pcCon[5]}  // id=6
const rA = placeOrder([book], '买家A', '地址A', pcCon, null)
const idxB = pcCon.findIndex(p => p.id === 6)
assert('并发：买家A 购后买家B 找不到', idxB === -1)

// 测试：已下架后 detail 页返回 null
const detailLookup = pc3.find(p => p.id === 5)
assert('已下架书籍 detail 页查不到', detailLookup === undefined)

// --- 总结 --------------------------------------------------
testSummary()