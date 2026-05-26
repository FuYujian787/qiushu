<template>
  <div class="logo-img" :style="{ width: size + 'px', height: size + 'px' }">
    <img src="/logo1.png" :width="size" :height="size" alt="紫金求思" />
  </div>
</template>

<script setup>
defineProps({
  size: { type: Number, default: 64 }
})
</script>

<style scoped>
.logo-img {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  border-radius: 8px;
  overflow: hidden;
}
.logo-img:hover {
  transform: scale(1.05) rotate(-2deg);
}
.logo-img img {
  display: block;
  object-fit: contain;
}
</style>
