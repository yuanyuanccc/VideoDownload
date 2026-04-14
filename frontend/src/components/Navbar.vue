<template>
  <nav style="border-bottom: 1px solid rgba(58,58,92,0.6); background: rgba(15,15,35,0.9); backdrop-filter: blur(20px); position: sticky; top: 0; z-index: 50;">
    <div style="max-width: 80rem; margin: 0 auto; padding: 0 1.5rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; height: 4.5rem;">
        <router-link to="/" style="display: flex; align-items: center; gap: 0.75rem; cursor: pointer; text-decoration: none;">
          <div style="width: 2.5rem; height: 2.5rem; border-radius: 0.625rem; background: linear-gradient(135deg, #00d4ff, #7c3aed); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px -3px rgba(0,212,255,0.3);">
            <svg style="width: 1.25rem; height: 1.25rem; color: white;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
            </svg>
          </div>
          <span style="font-size: 1.25rem; font-weight: 700; color: #fff; letter-spacing: -0.025em;">
            VideoGrab
          </span>
        </router-link>
        <div style="display: flex; align-items: center; gap: 2rem;">
          <router-link to="/" style="color: #9ca3af; text-decoration: none; font-size: 0.9rem; transition: color 0.2s;" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='#9ca3af'" :class="{ 'router-link-active': $route.path === '/' }">首页</router-link>
          <router-link to="/platforms" style="color: #9ca3af; text-decoration: none; font-size: 0.9rem; transition: color 0.2s;" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='#9ca3af'" :class="{ 'router-link-active': $route.path === '/platforms' }">支持平台</router-link>
          <router-link to="/vip" style="color: #9ca3af; text-decoration: none; font-size: 0.9rem; transition: color 0.2s;" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='#9ca3af'" :class="{ 'router-link-active': $route.path === '/vip' }">VIP特权</router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
</script>

<style scoped>
.router-link-active {
  color: #00d4ff !important;
}
</style>