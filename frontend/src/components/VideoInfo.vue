<template>
  <section style="padding: 0.5rem 0 1.5rem;">
    <div style="background: linear-gradient(135deg, rgba(30,30,63,0.8) 0%, rgba(15,15,35,0.9) 100%); border-radius: 1rem; border: 1px solid rgba(58,58,92,0.6); padding: 1.25rem; box-shadow: 0 20px 40px -10px rgba(0,0,0,0.4);">
      <div class="video-layout">
        <!-- 左栏：视频信息 -->
        <div class="video-left">
          <div style="position: relative; border-radius: 0.75rem; overflow: hidden; aspect-ratio: 16/9; background: #0f0f23;">
            <img
              :src="videoInfo.thumbnail"
              :alt="videoInfo.title"
              style="width: 100%; height: 100%; object-fit: cover;"
              v-if="videoInfo.thumbnail"
            />
            <div v-else style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;">
              <svg style="width: 3rem; height: 3rem; color: #4b5563;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
              </svg>
            </div>
            <div v-if="videoInfo.duration" style="position: absolute; bottom: 0.5rem; right: 0.5rem; padding: 0.2rem 0.5rem; background: rgba(0,0,0,0.75); color: #fff; font-size: 0.75rem; border-radius: 0.25rem; font-weight: 500;">
              {{ formatDuration(videoInfo.duration) }}
            </div>
          </div>
          
          <h2 style="font-size: 1rem; font-weight: 600; margin-top: 1rem; color: #fff; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
            {{ videoInfo.title }}
          </h2>
          <div style="display: flex; gap: 1rem; margin: 0.5rem 0; font-size: 0.8rem; color: #9ca3af; flex-wrap: wrap;">
            <span v-if="videoInfo.uploader" style="display: flex; align-items: center; gap: 0.25rem;">
              <svg style="width: 0.875rem; height: 0.875rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
              {{ videoInfo.uploader }}
            </span>
          </div>
          
          <div style="margin-top: 1rem;">
            <h3 style="font-size: 0.75rem; font-weight: 600; margin-bottom: 0.5rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em;">选择清晰度</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 0.4rem;">
              <div
                v-for="format in filteredFormats"
                :key="format.format_id"
                @click="selectedFormat = format"
                class="format-option"
                :class="{ selected: selectedFormat?.format_id === format.format_id }"
              >
                <span style="color: #fff; font-weight: 600;">{{ format.quality }}</span>
                <span style="color: #6b7280; font-size: 0.7rem;">{{ format.ext.toUpperCase() }}</span>
              </div>
            </div>
          </div>
          
          <button
            @click="handleDownload"
            :disabled="!selectedFormat || downloading"
            :style="{
              marginTop: '1rem', 
              padding: '0.875rem 1.5rem', 
              width: '100%',
              background: !selectedFormat ? '#374151' : (downloading ? '#6b7280' : 'linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%)'), 
              color: 'white', 
              fontWeight: '700', 
              borderRadius: '0.625rem', 
              border: 'none', 
              cursor: (!selectedFormat || downloading) ? 'not-allowed' : 'pointer',
              fontSize: '0.95rem',
              transition: 'all 0.2s',
              boxShadow: selectedFormat && !downloading ? '0 4px 15px -3px rgba(0,212,255,0.3)' : 'none'
            }"
          >
            <span v-if="downloading" style="display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
              <svg style="width: 1rem; height: 1rem; animation: spin 1s linear infinite;" fill="none" viewBox="0 0 24 24">
                <circle style="opacity: 0.25;" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path style="opacity: 0.75;" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
              下载中...
            </span>
            <span v-else>立即下载</span>
          </button>
        </div>

        <!-- 右栏：AI功能Tab区 -->
        <div style="display: flex; flex-direction: column; height: 100%;">
          <div class="tabs">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              @click="activeTab = tab.key"
              :class="['tab-btn', { active: activeTab === tab.key }]"
            >
              {{ tab.label }}
            </button>
          </div>

          <div class="tab-content">
            <!-- AI总结 -->
            <div v-show="activeTab === 'summary'" class="summary-panel">
              <div v-if="!summaryContent && !loadingSummary" class="empty-state">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">🤖</div>
                <p class="hint">AI 智能分析视频内容，生成结构化总结</p>
                <button @click="generateSummary" :disabled="aiUsed" class="generate-btn">
                  {{ aiUsed ? '已生成' : '生成 AI 总结' }}
                </button>
              </div>
              <div v-else-if="loadingSummary" class="loading">
                <span class="loading-text">AI 分析中...</span>
              </div>
              <div v-else class="summary-result">
                <div class="markdown-content" v-html="renderedSummary"></div>
              </div>
            </div>

            <!-- 字幕 -->
            <div v-show="activeTab === 'subtitle'" class="subtitle-panel">
              <div v-if="!subtitles.length && !loadingSubtitle && !subtitleError" class="empty-state">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">📝</div>
                <p class="hint">提取视频字幕内容</p>
                <button @click="loadSubtitles" class="generate-btn">加载字幕</button>
              </div>
              <div v-else-if="loadingSubtitle" class="loading">
                <span class="loading-text">加载中...</span>
              </div>
              <div v-else-if="subtitleError" class="error-state">
                <p>{{ subtitleError }}</p>
                <button @click="loadSubtitles" class="generate-btn">重试</button>
              </div>
              <div v-else class="subtitle-wrapper">
                <div class="subtitle-toolbar">
                  <span class="subtitle-count">{{ subtitles.length }} 条字幕</span>
                  <button @click="downloadSubtitle" class="download-btn">下载 SRT</button>
                </div>
                <div class="subtitle-list">
                  <div v-for="(sub, i) in subtitles" :key="i" class="subtitle-item">
                    <span class="time">{{ sub.start }}</span>
                    <span class="text">{{ sub.text }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 思维导图 -->
            <div v-show="activeTab === 'mindmap'" class="mindmap-panel">
              <div v-if="!mindmapData && !loadingMindmap && summaryContent" class="empty-state">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">🗺️</div>
                <p class="hint">基于 AI 总结生成思维导图</p>
                <button @click="generateMindmap" class="generate-btn">生成思维导图</button>
              </div>
              <div v-else-if="loadingMindmap" class="loading">
                <span class="loading-text">生成思维导图中...</span>
              </div>
              <div v-else-if="mindmapData" class="mindmap-container">
                <div class="mindmap-toolbar">
                  <button @click="downloadMindmapImage" class="download-btn">下载图片</button>
                  <button @click="downloadMindmapJson" class="download-btn">下载 JSON</button>
                </div>
                <div class="mindmap-display">
                  <div class="mindmap-root">{{ mindmapData.root }}</div>
                  <div class="mindmap-branches">
                    <div v-for="(branch, i) in mindmapData.children" :key="i" class="branch">
                      <div class="branch-node">{{ branch.text }}</div>
                      <div v-if="branch.children && branch.children.length" class="sub-nodes">
                        <div v-for="(sub, j) in branch.children" :key="j" class="sub-node">{{ sub.text }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-state">
                <div style="font-size: 2rem; margin-bottom: 0.75rem;">🗺️</div>
                <p class="hint">请先生成 AI 总结</p>
              </div>
            </div>

            <!-- 问答 -->
            <div v-show="activeTab === 'chat'" class="chat-panel">
              <div class="chat-messages">
                <div v-for="(msg, i) in chatMessages" :key="i" :class="['chat-msg', msg.role]">
                  <span class="msg-content">{{ msg.content }}</span>
                </div>
              </div>
              <div class="chat-input">
                <input
                  v-model="chatInput"
                  @keyup.enter="sendChat"
                  placeholder="关于视频内容有什么问题？"
                  :disabled="loadingChat"
                />
                <button @click="sendChat" :disabled="!chatInput.trim() || loadingChat">
                  {{ loadingChat ? '...' : '发送' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import axios from 'axios'
import html2canvas from 'html2canvas'

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

const tabs = [
  { key: 'summary', label: '总结' },
  { key: 'subtitle', label: '字幕' },
  { key: 'mindmap', label: '导图' },
  { key: 'chat', label: '问答' }
]

const activeTab = ref('summary')
const selectedFormat = ref(null)

const aiUsed = ref(false)
const loadingSummary = ref(false)
const summaryContent = ref('')
const loadingSubtitle = ref(false)
const subtitles = ref([])
const subtitleError = ref('')
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

watch(() => props.videoInfo, () => {
  summaryContent.value = ''
  subtitles.value = []
  subtitleError.value = ''
  mindmapData.value = null
  chatMessages.value = []
  chatInput.value = ''
  aiUsed.value = false
  activeTab.value = 'summary'
  selectedFormat.value = null
  // 自动触发AI总结
  if (props.videoInfo && props.videoInfo.url) {
    setTimeout(() => generateSummary(), 800)
  }
}, { immediate: true })

const generateSummary = async () => {
  if (aiUsed.value && summaryContent.value) return
  loadingSummary.value = true

  try {
    const response = await fetch('/api/ai/summary/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: props.videoInfo.url })
    })
    
    if (!response.ok) {
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
              summaryContent.value = fullContent
            }
            if (parsed.error) {
              loadingSummary.value = false
              return
            }
          } catch {}
        }
      }
    }

    if (summaryContent.value) {
      aiUsed.value = true
    }
  } catch (err) {
    console.error('Summary error:', err)
  } finally {
    loadingSummary.value = false
  }
}

const loadSubtitles = async () => {
  loadingSubtitle.value = true
  subtitleError.value = ''
  try {
    const res = await fetch('/api/ai/subtitle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: props.videoInfo.url })
    })
    const data = await res.json()
    if (data.code === 0) {
      subtitles.value = data.data.subtitles || []
      if (!subtitles.value.length) {
        subtitleError.value = '该视频暂无字幕'
      }
    } else {
      subtitleError.value = data.message || '加载字幕失败'
    }
  } catch (err) {
    subtitleError.value = '加载字幕失败'
  } finally {
    loadingSubtitle.value = false
  }
}

const generateMindmap = async () => {
  loadingMindmap.value = true
  try {
    const res = await fetch('/api/ai/mindmap', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ summary: summaryContent.value })
    })
    const data = await res.json()
    if (data.code === 0) {
      mindmapData.value = data.data
    } else {
      alert(data.message || '生成思维导图失败')
    }
  } catch (err) {
    alert('生成思维导图失败: ' + err.message)
  } finally {
    loadingMindmap.value = false
  }
}

const downloadMindmapImage = async () => {
  if (!mindmapData.value) return
  const container = document.querySelector('.mindmap-display')
  if (!container) {
    alert('找不到导出区域')
    return
  }
  
  try {
    const canvas = await html2canvas(container, {
      backgroundColor: '#1a1a2e',
      scale: 2,
      useCORS: true,
      logging: false
    })
    
    const link = document.createElement('a')
    link.download = 'mindmap.png'
    link.href = canvas.toDataURL('image/png')
    link.click()
  } catch (err) {
    console.error('html2canvas error:', err)
    alert('生成图片失败: ' + err.message)
  }
}

const downloadMindmapJson = () => {
  if (!mindmapData.value) return
  const blob = new Blob([JSON.stringify(mindmapData.value, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'mindmap.json'
  a.click()
  URL.revokeObjectURL(url)
}

const toSrtTime = (timeStr) => {
  let t = timeStr.replace('.', ',')
  const parts = t.split(':')
  if (parts.length === 2) {
    return `00:${parts[0]}:${parts[1]}`
  } else if (parts.length === 1) {
    return `00:00:${parts[0]},000`
  }
  return t
}

const downloadSubtitle = () => {
  if (!subtitles.value.length) return
  
  let srtContent = ''
  subtitles.value.forEach((sub, index) => {
    srtContent += `${index + 1}\n`
    srtContent += `${toSrtTime(sub.start)} --> ${toSrtTime(sub.end)}\n`
    srtContent += `${sub.text}\n\n`
  })
  
  const blob = new Blob([srtContent], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'subtitle.srt'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const sendChat = async () => {
  if (!chatInput.value.trim()) return
  const userMsg = chatInput.value.trim()
  chatMessages.value.push({ role: 'user', content: userMsg })
  chatInput.value = ''
  loadingChat.value = true

  let assistantMsg = { role: 'assistant', content: '' }
  chatMessages.value.push(assistantMsg)

  try {
    const response = await fetch('/api/ai/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: props.videoInfo.url,
        messages: chatMessages.value.slice(0, -1)
      })
    })

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

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
              assistantMsg.content += parsed.choices[0].delta.content
              chatMessages.value[chatMessages.value.length - 1] = { ...assistantMsg }
            }
            if (parsed.error) {
              alert(parsed.error)
              break
            }
          } catch {}
        }
      }
    }
  } catch (err) {
    alert('问答失败')
  } finally {
    loadingChat.value = false
  }
}

const renderMarkdown = (text) => {
  if (!text) return ''
  let html = text
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/^(\d+)\. (.+)$/gm, '<li class="ordered">$2</li>')
  html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
  html = html.replace(/\n\n/g, '</p><p>')
  html = html.replace(/\n/g, '<br>')
  return `<p>${html}</p>`
}

const renderedSummary = computed(() => renderMarkdown(summaryContent.value))
</script>

<style scoped>
.tabs {
  display: flex;
  gap: 0.4rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 0.5rem 0.8rem;
  border-radius: 0.4rem;
  border: none;
  background: #0f0f23;
  color: #9ca3af;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.tab-btn.active {
  background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%);
  color: white;
}

.tab-content {
  overflow-y: auto;
}

.empty-state {
  text-align: center;
  padding: 1.5rem;
}

.error-state {
  text-align: center;
  padding: 1.5rem;
  color: #f87171;
}

.hint {
  color: #9ca3af;
  margin-bottom: 1rem;
  font-size: 0.85rem;
}

.generate-btn {
  padding: 0.6rem 1.5rem;
  background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%);
  color: white;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.generate-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px -3px rgba(0,212,255,0.4);
}

.generate-btn:disabled {
  background: #374151;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 1.5rem;
  color: #9ca3af;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.loading::before {
  content: '';
  width: 20px;
  height: 20px;
  border: 2px solid #4b5563;
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.markdown-content {
  line-height: 1.7;
  color: #e5e7eb;
  font-size: 0.9rem;
  max-height: 350px;
  overflow-y: auto;
}

.markdown-content h1 {
  font-size: 1.2rem;
  font-weight: bold;
  color: #00d4ff;
  margin: 0.8rem 0 0.4rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid #2a2a4a;
}

.markdown-content h2 {
  font-size: 1.05rem;
  font-weight: 600;
  color: #00d4ff;
  margin: 0.8rem 0 0.4rem;
}

.markdown-content h3 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #7c3aed;
  margin: 0.6rem 0 0.3rem;
}

.markdown-content strong {
  color: #7c3aed;
  font-weight: 600;
}

.markdown-content code {
  background: #2a2a4a;
  padding: 0.1rem 0.3rem;
  border-radius: 0.2rem;
  font-size: 0.85rem;
  color: #00d4ff;
}

.markdown-content ul {
  margin: 0.4rem 0;
  padding-left: 1.2rem;
}

.markdown-content li {
  margin: 0.2rem 0;
  list-style-type: disc;
}

.markdown-content p {
  margin: 0.4rem 0;
}

.subtitle-wrapper {
  display: flex;
  flex-direction: column;
}

.subtitle-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.4rem 0;
  margin-bottom: 0.4rem;
  border-bottom: 1px solid #2a2a4a;
}

.subtitle-count {
  color: #9ca3af;
  font-size: 0.8rem;
}

.download-btn {
  padding: 0.4rem 0.8rem;
  background: #10b981;
  color: white;
  border-radius: 0.4rem;
  border: none;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 500;
}

.download-btn:hover {
  background: #059669;
}

.subtitle-list {
  max-height: 300px;
  overflow-y: auto;
}

.subtitle-item {
  padding: 0.4rem;
  border-bottom: 1px solid #1a1a2e;
  display: flex;
  gap: 0.8rem;
}

.subtitle-item .time {
  color: #6b7280;
  font-size: 0.7rem;
  min-width: 60px;
}

.subtitle-item .text {
  color: #e5e7eb;
  font-size: 0.85rem;
}

.mindmap-panel {
  padding: 0.5rem;
}

.mindmap-container {
  min-height: 250px;
  overflow: auto;
  padding: 0.4rem;
}

.mindmap-toolbar {
  display: flex;
  gap: 0.4rem;
  margin-bottom: 0.8rem;
}

.mindmap-display {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.8rem;
  padding: 0.8rem;
  min-height: 120px;
}

.mindmap-root {
  font-size: 1rem;
  font-weight: bold;
  background: linear-gradient(135deg, #00d4ff, #7c3aed);
  color: #1a1a2e;
  padding: 0.6rem 1.2rem;
  border-radius: 50px;
  white-space: nowrap;
}

.mindmap-branches {
  display: flex;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0.8rem;
  justify-content: center;
}

.branch {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #fff;
  padding: 0.6rem 0.8rem;
  border-radius: 10px;
  border: 2px solid #1a1a2e;
}

.branch-node {
  color: #1a1a2e;
  font-weight: 600;
  text-align: center;
  font-size: 0.85rem;
}

.sub-nodes {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.4rem;
  justify-content: center;
}

.sub-node {
  background: #fef3c7;
  color: #1a1a2e;
  padding: 0.25rem 0.5rem;
  border-radius: 5px;
  border: 1px solid #1a1a2e;
  font-size: 0.7rem;
}

.chat-panel {
  display: flex;
  flex-direction: column;
  height: 280px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 0.4rem;
}

.chat-msg {
  margin-bottom: 0.8rem;
}

.chat-msg.user {
  text-align: right;
}

.chat-msg .msg-content {
  display: inline-block;
  padding: 0.4rem 0.8rem;
  border-radius: 0.4rem;
  max-width: 80%;
  font-size: 0.85rem;
}

.chat-msg.user .msg-content {
  background: #2a2a4a;
  color: #e5e7eb;
}

.chat-msg.assistant .msg-content {
  background: linear-gradient(90deg, rgba(0,212,255,0.1), rgba(124,58,237,0.1));
  color: #e5e7eb;
  white-space: pre-wrap;
}

.chat-input {
  display: flex;
  gap: 0.4rem;
  padding: 0.4rem;
  border-top: 1px solid #2a2a4a;
}

.chat-input input {
  flex: 1;
  padding: 0.6rem;
  border-radius: 0.4rem;
  border: 1px solid #2a2a4a;
  background: #1a1a2e;
  color: #e5e7eb;
  font-size: 0.85rem;
}

.chat-input button {
  padding: 0.6rem 1.2rem;
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  color: white;
  border-radius: 0.4rem;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
}

.chat-input button:disabled {
  background: #374151;
  cursor: not-allowed;
}

.format-option {
  padding: 0.35rem 0.6rem;
  background: #1a1a2e;
  border: 1px solid #2a2a4a;
  border-radius: 0.4rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 55px;
}

.format-option:hover {
  border-color: #00d4ff;
}

.format-option.selected {
  background: linear-gradient(135deg, rgba(0,212,255,0.2) 0%, rgba(124,58,237,0.2) 100%);
  border-color: #00d4ff;
}

.video-layout {
  display: grid;
  grid-template-columns: 42% 1fr;
  gap: 1.25rem;
}

@media (max-width: 800px) {
  .video-layout {
    grid-template-columns: 1fr;
  }
}
</style>
