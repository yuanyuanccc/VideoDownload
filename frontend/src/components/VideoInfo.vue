<template>
  <section style="padding: 2rem 0;">
    <div style="background: #1a1a2e; border-radius: 1rem; border: 1px solid #2a2a4a; padding: 1.5rem; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
      <div style="display: flex; gap: 1.5rem;">
        <div style="width: 240px; flex-shrink: 0;">
          <img
            :src="videoInfo.thumbnail"
            :alt="videoInfo.title"
            style="width: 100%; border-radius: 0.5rem; object-fit: cover;"
            v-if="videoInfo.thumbnail"
          />
          <div v-else style="width: 100%; height: 135px; background: #0f0f23; border-radius: 0.5rem; display: flex; align-items: center; justify-content: center;">
            <svg style="width: 2.5rem; height: 2.5rem; color: #9ca3af;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
            </svg>
          </div>
        </div>
        
        <div style="flex: 1;">
          <h2 style="font-size: 1.25rem; font-weight: bold; margin-bottom: 0.5rem; color: #e5e7eb; line-height: 1.4;">{{ videoInfo.title }}</h2>
          <div style="display: flex; gap: 1rem; margin-bottom: 1rem; font-size: 0.875rem; color: #9ca3af;">
            <span v-if="videoInfo.uploader">👤 {{ videoInfo.uploader }}</span>
            <span v-if="videoInfo.duration">⏱️ {{ formatDuration(videoInfo.duration) }}</span>
          </div>
          
          <div style="margin-top: 1rem;">
            <h3 style="font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem; color: #9ca3af;">选择清晰度：</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
              <div
                v-for="format in filteredFormats"
                :key="format.format_id"
                @click="selectedFormat = format"
                :style="{
                  padding: '0.5rem 0.75rem',
                  borderRadius: '0.5rem',
                  border: selectedFormat?.format_id === format.format_id ? '1px solid #00d4ff' : '1px solid #2a2a4a',
                  background: selectedFormat?.format_id === format.format_id ? 'rgba(0, 212, 255, 0.15)' : '#0f0f23',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  fontSize: '0.875rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }"
              >
                <span style="color: #e5e7eb; font-weight: 500;">{{ format.quality }}</span>
                <span style="color: #6b7280; font-size: 0.75rem;">{{ format.ext.toUpperCase() }}</span>
              </div>
            </div>
          </div>
          
          <button
            @click="handleDownload"
            :disabled="!selectedFormat || downloading"
            :style="{
              marginTop: '1rem', 
              padding: '0.75rem 2rem', 
              background: !selectedFormat ? '#374151' : (downloading ? '#6b7280' : 'linear-gradient(90deg, #00d4ff, #7c3aed)'), 
              color: 'white', 
              fontWeight: '600', 
              borderRadius: '0.5rem', 
              border: 'none', 
              cursor: (!selectedFormat || downloading) ? 'not-allowed' : 'pointer',
              display: 'inline-block'
            }"
          >
            {{ downloading ? '下载中...' : '立即下载' }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  videoInfo: {
    type: Object,
    required: true
  },
  downloading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['download'])
const selectedFormat = ref(null)

const filteredFormats = computed(() => {
  const formats = props.videoInfo.formats?.filter(f => f.quality && f.quality !== 'unknown' && f.quality !== 'audio only') || []
  return formats.sort((a, b) => {
    const getRes = (q) => {
      if (q.includes('1080')) return 1080
      if (q.includes('720')) return 720
      if (q.includes('480')) return 480
      if (q.includes('360')) return 360
      if (q.includes('240')) return 240
      const match = q.match(/(\d+)/)
      return match ? parseInt(match[1]) : 0
    }
    return getRes(b.quality) - getRes(a.quality)
  })
})

const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.round(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const handleDownload = () => {
  if (!selectedFormat.value) return
  emit('download', {
    url: props.videoInfo.url,
    format: selectedFormat.value
  })
}
</script>