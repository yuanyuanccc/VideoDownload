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
          <pre>{{ summaryContent }}</pre>
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
        <div v-else class="subtitle-list">
          <div v-for="(sub, i) in subtitles" :key="i" class="subtitle-item">
            <span class="time">{{ sub.start }}</span>
            <span class="text">{{ sub.text }}</span>
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
          <div class="mindmap-tree">
            <div class="mindmap-root">{{ mindmapData.root }}</div>
            <div class="mindmap-branches">
              <div v-for="(branch, i) in mindmapData.children" :key="i" class="branch">
                <div class="branch-line"></div>
                <div class="branch-content">
                  <div class="branch-node">
                    <span class="node-dot"></span>
                    <span class="node-text">{{ branch.text }}</span>
                  </div>
                  <div v-if="branch.children && branch.children.length" class="sub-branches">
                    <div v-for="(sub, j) in branch.children" :key="j" class="sub-branch">
                      <div class="sub-line"></div>
                      <div class="sub-node">
                        <span class="sub-dot"></span>
                        <span class="sub-text">{{ sub.text }}</span>
                      </div>
                    </div>
                  </div>
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
import { ref } from 'vue'

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
  max-height: 400px;
  overflow-y: auto;
}

.mindmap-tree {
  display: flex;
  flex-direction: column;
}

.mindmap-root {
  font-size: 1.1rem;
  font-weight: bold;
  color: #00d4ff;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(0, 212, 255, 0.05));
  border-radius: 8px;
  border-left: 3px solid #00d4ff;
  margin-bottom: 1rem;
}

.mindmap-branches {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.branch {
  display: flex;
  align-items: flex-start;
}

.branch-line {
  width: 24px;
  height: 20px;
  border-left: 2px solid #4b5563;
  border-bottom: 2px solid #4b5563;
  border-bottom-left-radius: 8px;
  margin-right: 0.5rem;
  flex-shrink: 0;
}

.branch-content {
  flex: 1;
}

.branch-node {
  display: flex;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: rgba(75, 85, 99, 0.3);
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.node-dot {
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  margin-right: 0.5rem;
  flex-shrink: 0;
}

.node-text {
  color: #e5e7eb;
  font-weight: 500;
}

.sub-branches {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-left: 1rem;
}

.sub-branch {
  display: flex;
  align-items: center;
}

.sub-line {
  width: 16px;
  height: 16px;
  border-left: 1px solid #6b7280;
  margin-right: 0.5rem;
  flex-shrink: 0;
}

.sub-node {
  display: flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
}

.sub-dot {
  width: 5px;
  height: 5px;
  background: #9ca3af;
  border-radius: 50%;
  margin-right: 0.5rem;
  flex-shrink: 0;
}

.sub-text {
  color: #9ca3af;
  font-size: 0.9rem;
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