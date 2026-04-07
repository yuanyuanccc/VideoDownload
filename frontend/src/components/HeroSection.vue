<template>
  <section style="padding: 3rem 0; text-align: center;">
    <h1 style="font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">
      <span style="background: linear-gradient(90deg, #00d4ff, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        万能视频下载器
      </span>
    </h1>
    <p style="color: #9ca3af; margin-bottom: 2rem;">
      支持1800+平台，一键解析，高速下载
    </p>
    
    <div style="max-width: 56rem; margin: 0 auto;">
      <div style="display: flex; gap: 0.5rem; padding: 0.5rem; background: #1a1a2e; border-radius: 1rem; border: 1px solid #2a2a4a;">
        <input
          v-model="url"
          type="text"
          placeholder="粘贴视频链接..."
          style="flex: 1; padding: 0.75rem 1rem; background: transparent; color: #e5e7eb; border: none; outline: none; font-size: 1rem;"
          @keyup.enter="parseVideo"
        />
        <button
          @click="parseVideo"
          :disabled="loading || !url"
          style="padding: 0.75rem 1.5rem; background: linear-gradient(90deg, #00d4ff, #7c3aed); color: white; font-weight: 600; border-radius: 0.75rem; border: none; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; font-size: 1rem;"
        >
          <svg v-if="loading" style="width: 1rem; height: 1rem; animation: spin 1s linear infinite;" fill="none" viewBox="0 0 24 24">
            <circle style="opacity: 0.25;" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path style="opacity: 0.75;" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
          </svg>
          {{ loading ? '解析中' : '开始解析' }}
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const emit = defineEmits(['parsed'])
const url = ref('')
const loading = ref(false)

const parseVideo = async () => {
  if (!url.value) return
  
  let videoUrl = url.value.trim()
  
  if (videoUrl.includes('douyin.com')) {
    const modalMatch = videoUrl.match(/modal_id[=/](\d+)/)
    if (modalMatch) {
      videoUrl = `https://www.douyin.com/video/${modalMatch[1]}`
    }
    const avMatch = videoUrl.match(/av(\d+)/)
    if (avMatch) {
      videoUrl = `https://www.douyin.com/video/${avMatch[1]}`
    }
  }
  
  loading.value = true
  try {
    const response = await axios.post('/api/parse', { url: url.value })
    if (response.data.code === 0) {
      emit('parsed', response.data.data)
    } else {
      alert('解析失败，请检查链接是否正确')
    }
  } catch (error) {
    console.error('Parse error:', error)
    let msg = '解析失败，请检查链接是否正确'
    if (error.response?.data?.detail) {
      msg = error.response.data.detail
    } else if (error.message?.includes('Network')) {
      msg = '网络连接失败，请检查网络'
    }
    if (msg.includes('cookies')) {
      msg = '该平台需要登录 cookies，暂不支持解析'
    }
    if (msg.includes('empty') || msg.includes('无内容')) {
      msg = '抖音解析失败，可能是网络或地区限制，请尝试其他平台（如B站、YouTube）'
    }
    alert(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>