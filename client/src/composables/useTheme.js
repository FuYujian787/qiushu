import { ref, watchEffect } from 'vue'

const theme = ref(
  (localStorage.getItem('qiu-shu-theme') || 'paper')
)

watchEffect(() => {
  document.documentElement.setAttribute('data-theme', theme.value)
  localStorage.setItem('qiu-shu-theme', theme.value)
})

export function useTheme() {
  function toggle() {
    theme.value = theme.value === 'paper' ? 'cyber' : 'paper'
  }

  function setTheme(t) {
    if (t === 'paper' || t === 'cyber') {
      theme.value = t
    }
  }

  // 首次访问时跟随系统
  function initTheme() {
    if (!localStorage.getItem('qiu-shu-theme')) {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      theme.value = prefersDark ? 'cyber' : 'paper'
    }
  }

  return { theme, toggle, setTheme, initTheme }
}
