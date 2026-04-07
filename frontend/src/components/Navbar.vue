<template>
  <nav style="border-bottom: 1px solid #2a2a4a; background: rgba(26, 26, 46, 0.8); backdrop-filter: blur(10px); position: sticky; top: 0; z-index: 50;">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" style="max-width: 80rem; margin: 0 auto; padding: 0 1rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; height: 4rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <div style="width: 2.5rem; height: 2.5rem; border-radius: 0.5rem; background: linear-gradient(135deg, #00d4ff, #7c3aed); display: flex; align-items: center; justify-content: center;">
            <svg style="width: 1.5rem; height: 1.5rem; color: white;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
            </svg>
          </div>
          <span style="font-size: 1.25rem; font-weight: bold; background: linear-gradient(90deg, #00d4ff, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            VideoGrab
          </span>
        </div>
        <div style="display: flex; align-items: center; gap: 1.5rem;">
          <a href="#" style="color: #9ca3af; text-decoration: none;">首页</a>
          <a href="#" style="color: #9ca3af; text-decoration: none;">支持平台</a>
          <a href="#" style="color: #9ca3af; text-decoration: none;">VIP特权</a>
          <button style="padding: 0.5rem 1rem; background: linear-gradient(90deg, #00d4ff, #7c3aed); color: white; border: none; border-radius: 0.5rem; cursor: pointer;">
            登录 / 注册
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>