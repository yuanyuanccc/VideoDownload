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

          <button
            @click="showSummary = true"
            :style="{
              marginTop: '1rem', 
              marginLeft: '0.75rem',
              padding: '0.75rem 1.5rem', 
              background: 'transparent', 
              color: '#00d4ff', 
              fontWeight: '600', 
              borderRadius: '0.5rem', 
              border: '1px solid #00d4ff', 
              cursor: 'pointer',
              display: 'inline-block'
            }"
          >
            AI智能分析
          </button>
        </div>
      </div>

      <VideoSummary v-if="showSummary" :video-url="videoInfo.url" @close="showSummary = false" />
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import VideoSummary from './VideoSummary.vue'

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
const showSummary = ref(false)

const aiUsed = ref(false)
const loadingSummary = ref(false)
const summaryData = ref('')
const loadingSubtitle = ref(false)
const subtitles = ref([])
const loadingMindmap = ref(false)
const mindmapData = ref(null)
const loadingChat = ref(false)
const chatMessages = ref([])
const chatInput = ref('')

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

const generateSummary = async () => {
  loadingSummary.value = true
  summaryData.value = ''
  
  try {
    const response = await fetch('/api/summarize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: props.videoInfo.url })
    })

    if (!response.ok) {
      alert('请求失败: ' + response.status)
      loadingSummary.value = false
      return
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let fullContent = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      const text = decoder.decode(value)
      const lines = text.split('\n')
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') continue
          
          try {
            const parsed = JSON.parse(data)
            if (parsed.choices && parsed.choices[0].delta && parsed.choices[0].delta.content) {
              fullContent += parsed.choices[0].delta.content
              summaryData.value = fullContent
            }
            if (parsed.error) {
              alert(parsed.error)
              loadingSummary.value = false
              return
            }
          } catch {}
        }
      }
    }
    
    if (summaryData.value) {
      aiUsed.value = true
    } else {
      alert('未能获取到总结内容，请检查视频是否有字幕')
    }
  } catch (err) {
    alert('生成总结失败: ' + err.message)
  } finally {
    loadingSummary.value = false
  }
}

const loadSubtitles = async () => {
  loadingSubtitle.value = true
  try {
    const res = await fetch('/api/subtitle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: props.videoInfo.url })
    })
    const data = await res.json()
    if (data.code === 0) {
      subtitles.value = data.data.subtitles || []
    } else {
      alert(data.message || '加载字幕失败')
    }
  } catch (err) {
    alert('加载字幕失败')
  } finally {
    loadingSubtitle.value = false
  }
}

const generateMindmap = async () => {
  loadingMindmap.value = true
  try {
    const res = await fetch('/api/mindmap', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ summary: summaryData.value })
    })
    const data = await res.json()
    if (data.code === 0) {
      mindmapData.value = data.data
    } else {
      alert(data.message || '生成思维导图失败')
    }
  } catch (err) {
    alert('生成思维导图失败')
  } finally {
    loadingMindmap.value = false
  }
}
</script>