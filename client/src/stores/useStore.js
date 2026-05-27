import { ref, reactive, computed, shallowRef } from 'vue'

const DEFAULT_AVATAR = '5492ec47e5014900a8690086552604d9.jpg'
const IMG_POOL = ['R-C.jpg']
const TOTAL_PRODUCTS = 100000

// localStorage keys
const KEYS = {
  users: 'qushu_users',
  publishedBooks: 'qushu_published_books',
  orders: 'qushu_orders',
  notifications: 'qushu_user_notifications',
  userPosts: 'qushu_user_posts',
  postReplies: 'qushu_post_replies',
  loggedInUser: 'qushu_logged_in_user',
}

// Reactive state
const currentUser = ref(null)
const isLoggedIn = ref(false)
const cart = reactive([])
const orders = ref([])
const publishedBooks = ref([])
const userNotifications = ref({})
const userPosts = ref([])
const postReplies = ref({})
const currentPage = ref('login')
const procurementFilter = ref('全部')
const procurementPage = ref(1)
const searchQuery = ref('')
const productCache = shallowRef([])
const communityPosts = ref([])
const bookDetailId = ref(null)
const categoriesData = ref(null)

// Load functions
function loadLocal(key, fallback) {
  try {
    const val = localStorage.getItem(key)
    return val ? JSON.parse(val) : fallback
  } catch {
    return fallback
  }
}

function saveLocal(key, data) {
  localStorage.setItem(key, JSON.stringify(data))
}

// Initialize from localStorage
function initFromLocal() {
  orders.value = loadLocal(KEYS.orders, [])
  publishedBooks.value = loadLocal(KEYS.publishedBooks, [])
  userNotifications.value = loadLocal(KEYS.notifications, {})
  userPosts.value = loadLocal(KEYS.userPosts, [])
  postReplies.value = loadLocal(KEYS.postReplies, {})
}

function generateProducts(categories) {
  if (productCache.value.length > 0) return
  const subjects = categories?.subjects || ['微积分', '线性代数', '大学英语', '有机化学']
  const conditions = categories?.conditions || ['九成新', '八成新', '全新未拆', '有笔记', '七成新']
  const categoryMap = categories?.categoryMap || {}
  const products = []
  for (let i = 0; i < TOTAL_PRODUCTS; i++) {
    const subj = subjects[i % subjects.length]
    const authors = ['同济大学', '清华大学', '浙江大学', '外研社']
    products.push({
      id: i + 1,
      title: `${subj} 辅导书 第${Math.floor(i / 10) + 1}版`,
      author: authors[i % 4],
      price: (10 + Math.random() * 50).toFixed(1),
      oldPrice: (30 + Math.random() * 80).toFixed(1),
      condition: conditions[i % conditions.length],
      seller: `同学${100 + (i % 900)}`,
      img: IMG_POOL[0],
      category: categoryMap[subj] || '教材',
      isUserPublished: false,
    })
  }
  productCache.value = [...publishedBooks.value, ...products]
}

function getRandomProducts(count = 4) {
  if (productCache.value.length === 0) return []
  const arr = []
  for (let i = 0; i < count; i++) {
    arr.push(productCache.value[Math.floor(Math.random() * TOTAL_PRODUCTS)])
  }
  return arr
}

function addToCart(book) {
  const exist = cart.find(i => i.id === book.id)
  if (exist) {
    exist.qty++
  } else {
    cart.push({ ...book, qty: 1 })
  }
}

function removeFromCart(id) {
  const idx = cart.findIndex(i => i.id === id)
  if (idx !== -1) cart.splice(idx, 1)
}

// User management
const users = ref([])

function findUser(name, password) {
  return users.value.find(u => u.name === name && u.password === password)
}

function userExists(name) {
  return users.value.some(u => u.name === name)
}

function addUser(user) {
  users.value.push(user)
  saveLocal(KEYS.users, users.value)
}

function updateUser(oldName, newData) {
  const idx = users.value.findIndex(u => u.name === oldName)
  if (idx !== -1) {
    users.value[idx] = { ...users.value[idx], ...newData }
    saveLocal(KEYS.users, users.value)
  }
}

function login(userObj) {
  currentUser.value = { ...userObj }
  isLoggedIn.value = true
  localStorage.setItem(KEYS.loggedInUser, userObj.name)
}

function logout() {
  currentUser.value = null
  isLoggedIn.value = false
  localStorage.removeItem(KEYS.loggedInUser)
  currentPage.value = 'login'
}

// Notifications
function addNotification(userName, notif) {
  if (!userNotifications.value[userName]) {
    userNotifications.value[userName] = []
  }
  userNotifications.value[userName].push(notif)
  saveLocal(KEYS.notifications, userNotifications.value)
}

function markAllRead(userName) {
  const notifs = userNotifications.value[userName]
  if (notifs) {
    notifs.forEach(n => { n.unread = false })
    saveLocal(KEYS.notifications, userNotifications.value)
  }
}

function hasUnread(userName) {
  const notifs = userNotifications.value[userName] || []
  return notifs.some(n => n.unread)
}

// Posts
function addPost(post) {
  userPosts.value.push(post)
  saveLocal(KEYS.userPosts, userPosts.value)
}

function addReply(postId, reply) {
  // 确保 postId 为字符串，保证键值一致性
  const key = String(postId)
  // 创建新数组以保证响应式触发
  const current = postReplies.value[key] ? [...postReplies.value[key]] : []
  current.push(reply)
  // 使用展开运算符创建新对象，强制触发 Vue 响应式更新
  postReplies.value = { ...postReplies.value, [key]: current }
  saveLocal(KEYS.postReplies, postReplies.value)
}


function getMergedPosts() {
  const fixedPresets = communityPosts.value.map((p, idx) => {
    if (!p.id) p.id = 'preset_' + idx
    return p
  })
  return [...fixedPresets, ...userPosts.value]
}

// Orders
function placeOrder(buyerName, address) {
  for (const item of cart) {
    const order = {
      id: 'ORD-' + Date.now() + Math.random().toString(36).substr(2, 4),
      title: item.title,
      price: item.price,
      status: '已售',
      date: new Date().toISOString().slice(0, 10),
      buyer: buyerName,
      seller: item.seller || '未知卖家',
      bookId: item.id,
    }
    orders.value.unshift(order)
    if (item.isUserPublished) {
      publishedBooks.value = publishedBooks.value.filter(b => b.id !== item.id)
      productCache.value = productCache.value.filter(p => p.id !== item.id)
      saveLocal(KEYS.publishedBooks, publishedBooks.value)
      addNotification(item.seller, {
        title: '书籍售出通知',
        desc: `买家 ${buyerName} 已购买您的书籍《${item.title}》，收货地址：${address}`,
        time: new Date().toLocaleString('zh-CN'),
        unread: true,
      })
    }
  }
  saveLocal(KEYS.orders, orders.value)
  cart.splice(0, cart.length)
}

// Publishing
function publishBook(book) {
  publishedBooks.value.unshift(book)
  saveLocal(KEYS.publishedBooks, publishedBooks.value)
  if (productCache.value.length > 0) {
    productCache.value.unshift(book)
  }
}

// Fetch user's published books
function fetchUserBooks(userName) {
  const allBooks = productCache.value || []
  const userBooks = allBooks.filter(b => b.seller === userName || b.isUserPublished)
  return { books: userBooks }
}

// Seller stats (localStorage-based)
function fetchSellerStats(sellerName) {
  // Count orders where the buyer purchased books from this seller
  const allOrders = orders.value || []
  // Check both: orders with seller field matching, OR orders where the book in productCache belongs to this seller
  const soldBooks = allOrders.filter(o => {
    // Direct match via seller field stored in order
    if (o.seller === sellerName) return true
    // Fallback: find the book in productCache to check seller
    const book = productCache.value.find(p => p.id === o.bookId || p.title === o.title)
    return book && book.seller === sellerName
  })
  const total_books_sold = soldBooks.length
  const total_earnings = soldBooks.reduce((sum, o) => sum + parseFloat(o.price || 0), 0)
  return {
    success: true,
    total_books_sold,
    total_earnings: parseFloat(total_earnings.toFixed(2)),
  }
}

// Navigation
function navigateTo(page, params) {
  currentPage.value = page
  if (page === 'bookDetail') {
    bookDetailId.value = params
  }
}

export function useStore() {
  return {
    // State
    currentUser,
    isLoggedIn,
    cart,
    orders,
    publishedBooks,
    userNotifications,
    userPosts,
    postReplies,
    currentPage,
    procurementFilter,
    procurementPage,
    searchQuery,
    productCache,
    communityPosts,
    bookDetailId,
    categoriesData,
    users,

    // Functions
    initFromLocal,
    generateProducts,
    getRandomProducts,
    addToCart,
    removeFromCart,
    findUser,
    userExists,
    addUser,
    updateUser,
    login,
    logout,
    addNotification,
    markAllRead,
    hasUnread,
    addPost,
    addReply,
    getMergedPosts,
    placeOrder,
    publishBook,
    fetchUserBooks,
    fetchSellerStats,
    navigateTo,
    saveLocal,

    // Constants
    DEFAULT_AVATAR,
    IMG_POOL,
    TOTAL_PRODUCTS,
    KEYS,
  }
}