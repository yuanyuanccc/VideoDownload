<template>
  <div class="video-summary">
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
          <p class="hint">AI智能分析视频内容，生成结构化总结</p>
          <button @click="generateSummary" :disabled="aiUsed" class="generate-btn">
            {{ aiUsed ? '免费版已使用1次' : '生成AI总结 (免费版剩余1次)' }}
          </button>
        </div>
        <div v-else-if="loadingSummary" class="loading">
          <span class="loading-text">AI分析中...</span>
        </div>
        <div v-else class="summary-result">
          <div class="markdown-content" v-html="renderedSummary"></div>
        </div>
      </div>

      <!-- 字幕 -->
      <div v-show="activeTab === 'subtitle'" class="subtitle-panel">
        <div v-if="!subtitles.length && !loadingSubtitle && !subtitleError" class="empty-state">
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
            <button @click="downloadSubtitle" class="download-btn">下载SRT</button>
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
          <p class="hint">基于AI总结生成思维导图</p>
          <button @click="generateMindmap" class="generate-btn">生成思维导图</button>
        </div>
        <div v-else-if="loadingMindmap" class="loading">
          <span class="loading-text">生成思维导图中...</span>
        </div>
        <div v-else-if="mindmapData" class="mindmap-container">
          <div class="mindmap-toolbar">
            <button @click="downloadMindmapImage" class="download-btn">下载图片</button>
            <button @click="downloadMindmapJson" class="download-btn">下载JSON</button>
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
          <div ref="exportArea" class="mindmap-export" style="position:absolute; left:-9999px; top:-9999px; background:#1a1a2e; padding:30px; width:900px;">
            <div style="display:flex; align-items:center; justify-content:center; flex-wrap:wrap; gap:20px;">
              <div style="background:linear-gradient(135deg,#00d4ff,#7c3aed); color:#1a1a2e; padding:12px 24px; border-radius:25px; font-weight:bold; font-size:16px;">{{ mindmapData.root }}</div>
              <div style="width:30px; height:2px; background:#4b5563;"></div>
              <div v-for="(branch, i) in mindmapData.children" :key="i" style="display:flex; flex-direction:column; align-items:center; background:#fff; padding:10px 16px; border-radius:10px; border:2px solid #1a1a2e;">
                <div style="color:#1a1a2e; font-weight:600; font-size:14px;">{{ branch.text }}</div>
                <div v-if="branch.children && branch.children.length" style="display:flex; gap:6px; margin-top:8px; flex-wrap:wrap; justify-content:center;">
                  <div v-for="(sub, j) in branch.children" :key="j" style="background:#fef3c7; color:#1a1a2e; padding:4px 10px; border-radius:6px; border:1px solid #1a1a2e; font-size:12px;">{{ sub.text }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p class="hint">请先生成AI总结</p>
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
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  videoUrl: { type: String, required: true }
})

const tabs = [
  { key: 'summary', label: 'AI总结' },
  { key: 'subtitle', label: '字幕' },
  { key: 'mindmap', label: '思维导图' },
  { key: 'chat', label: '问答' }
]

const activeTab = ref('summary')
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

import html2canvas from 'html2canvas'

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

watch(() => props.videoUrl, () => {
  summaryContent.value = ''
  subtitles.value = []
  subtitleError.value = ''
  mindmapData.value = null
  chatMessages.value = []
  chatInput.value = ''
  aiUsed.value = false
  activeTab.value = 'summary'
})

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

const generateSummary = async () => {
  loadingSummary.value = true
  summaryContent.value = ''

  try {
    const response = await fetch('/api/ai/summary/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: props.videoUrl })
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
              summaryContent.value += parsed.choices[0].delta.content
            }
            if (parsed.error) {
              alert(parsed.error)
              break
            }
          } catch {}
        }
      }
    }

    if (summaryContent.value) {
      aiUsed.value = true
    }
  } catch (err) {
    alert('生成总结失败: ' + err.message)
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
      body: JSON.stringify({ url: props.videoUrl })
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
    console.log('Mindmap response status:', res.status)
    const data = await res.json()
    console.log('Mindmap response data:', data)
    if (data.code === 0) {
      mindmapData.value = data.data
    } else {
      alert(data.message || '生成思维导图失败')
    }
  } catch (err) {
    console.error('Mindmap error:', err)
    alert('生成思维导图失败: ' + err.message)
  } finally {
    loadingMindmap.value = false
  }
}

const formatTimestamp = (timeStr) => {
  const parts = timeStr.split(':')
  if (parts.length === 3) {
    return timeStr
  } else if (parts.length === 2) {
    return `00:${parts[0]}:${parts[1]}`
  }
  return timeStr
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
        url: props.videoUrl,
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
</script>

<style scoped>
.video-summary {
  background: #1a1a2e;
  border-radius: 1rem;
  border: 1px solid #2a2a4a;
  padding: 1.5rem;
  margin-top: 1.5rem;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: none;
  background: #0f0f23;
  color: #9ca3af;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.tab-btn.active {
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  color: white;
}

.tab-content {
  min-height: 200px;
}

.empty-state {
  text-align: center;
  padding: 2rem;
}

.error-state {
  text-align: center;
  padding: 2rem;
  color: #f87171;
}

.hint {
  color: #9ca3af;
  margin-bottom: 1rem;
}

.generate-btn {
  padding: 0.75rem 2rem;
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  color: white;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  font-weight: 600;
}

.generate-btn:disabled {
  background: #374151;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #9ca3af;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.loading::before {
  content: '';
  width: 24px;
  height: 24px;
  border: 2px solid #4b5563;
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.summary-result pre {
  white-space: pre-wrap;
  line-height: 1.8;
  color: #e5e7eb;
  font-family: inherit;
}

.markdown-content {
  line-height: 1.8;
  color: #e5e7eb;
}

.markdown-content h1 {
  font-size: 1.5rem;
  font-weight: bold;
  color: #00d4ff;
  margin: 1rem 0 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #2a2a4a;
}

.markdown-content h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #00d4ff;
  margin: 1rem 0 0.5rem;
}

.markdown-content h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #7c3aed;
  margin: 0.75rem 0 0.5rem;
}

.markdown-content strong {
  color: #7c3aed;
  font-weight: 600;
}

.markdown-content code {
  background: #2a2a4a;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  color: #00d4ff;
}

.markdown-content ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.markdown-content li {
  margin: 0.25rem 0;
  list-style-type: disc;
}

.markdown-content p {
  margin: 0.5rem 0;
}

.subtitle-wrapper {
  display: flex;
  flex-direction: column;
}

.subtitle-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid #2a2a4a;
}

.subtitle-count {
  color: #9ca3af;
  font-size: 0.875rem;
}

.download-btn {
  padding: 0.5rem 1rem;
  background: #10b981;
  color: white;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
}

.download-btn:hover {
  background: #059669;
}

.subtitle-list {
  max-height: 400px;
  overflow-y: auto;
}

.subtitle-item {
  padding: 0.5rem;
  border-bottom: 1px solid #1a1a2e;
  display: flex;
  gap: 1rem;
}

.subtitle-item .time {
  color: #6b7280;
  font-size: 0.75rem;
  min-width: 70px;
}

.subtitle-item .text {
  color: #e5e7eb;
}

.mindmap-panel {
  padding: 1rem;
}

.mindmap-container {
  min-height: 300px;
  overflow: auto;
  padding: 0.5rem;
}

.mindmap-toolbar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.mindmap-display {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
  padding: 1rem;
  min-height: 150px;
}

.mindmap-root {
  font-size: 1.25rem;
  font-weight: bold;
  background: linear-gradient(135deg, #00d4ff, #7c3aed);
  color: #1a1a2e;
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  white-space: nowrap;
}

.mindmap-branches {
  display: flex;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
}

.branch {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #fff;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  border: 2px solid #1a1a2e;
}

.branch-node {
  color: #1a1a2e;
  font-weight: 600;
  text-align: center;
}

.sub-nodes {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
  justify-content: center;
}

.sub-node {
  background: #fef3c7;
  color: #1a1a2e;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  border: 1px solid #1a1a2e;
  font-size: 0.8rem;
}

.chat-panel {
  display: flex;
  flex-direction: column;
  height: 300px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.chat-msg {
  margin-bottom: 1rem;
}

.chat-msg.user {
  text-align: right;
}

.chat-msg .msg-content {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  max-width: 80%;
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
  gap: 0.5rem;
  padding: 0.5rem;
  border-top: 1px solid #2a2a4a;
}

.chat-input input {
  flex: 1;
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid #2a2a4a;
  background: #1a1a2e;
  color: #e5e7eb;
}

.chat-input button {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  color: white;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  font-weight: 600;
}

.chat-input button:disabled {
  background: #374151;
  cursor: not-allowed;
}
</style>