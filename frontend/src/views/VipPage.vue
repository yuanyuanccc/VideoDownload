<template>
  <div style="min-height: 100vh; background: linear-gradient(180deg, #0f0f23 0%, #13132a 100%); color: #e5e7eb;">
    <Navbar />
    <main style="max-width: 72rem; margin: 0 auto; padding: 0 1rem;">
      <!-- Page Header -->
      <section style="padding: 3rem 0 2rem; text-align: center;">
        <h1 style="font-size: 2.5rem; font-weight: 800; margin-bottom: 0.75rem; letter-spacing: -0.025em;">
          <span style="background: linear-gradient(135deg, #fff 0%, #00d4ff 50%, #7c3aed 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            升级 VIP
          </span>
        </h1>
        <p style="color: #9ca3af; font-size: 1.125rem; max-width: 500px; margin: 0 auto;">
          解锁无限可能，体验极致下载
        </p>
      </section>

      <!-- Pricing Cards -->
      <section style="padding: 1rem 0 2rem;">
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; max-width: 60rem; margin: 0 auto;">
          <!-- Free Plan -->
          <div style="background: linear-gradient(135deg, rgba(30,30,63,0.9) 0%, rgba(15,15,35,0.95) 100%); border-radius: 1.5rem; border: 1px solid rgba(58,58,92,0.6); padding: 2rem; text-align: center; transition: all 0.3s;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">🆓</div>
            <h3 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem; color: #fff;">免费版</h3>
            <div style="font-size: 2rem; font-weight: 800; color: #9ca3af; margin-bottom: 0.5rem;">¥0</div>
            <div style="color: #6b7280; font-size: 0.9rem; margin-bottom: 1.5rem;">永久免费</div>
            <div style="text-align: left; margin-bottom: 1.5rem;">
              <div v-for="feature in freeFeatures" :key="feature" style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; color: #9ca3af;">
                <span style="color: #6b7280;">✕</span>
                {{ feature }}
              </div>
            </div>
            <button style="width: 100%; padding: 0.875rem; background: #374151; color: #9ca3af; border: none; border-radius: 0.75rem; font-weight: 600; cursor: not-allowed;">
              当前版本
            </button>
          </div>

          <!-- Monthly VIP -->
          <div style="background: linear-gradient(135deg, rgba(0,212,255,0.15) 0%, rgba(124,58,237,0.15) 100%); border-radius: 1.5rem; border: 2px solid #00d4ff; padding: 2rem; text-align: center; position: relative; transform: scale(1.02);">
            <div style="position: absolute; top: -0.75rem; left: 50%; transform: translateX(-50%); padding: 0.375rem 1rem; background: linear-gradient(135deg, #00d4ff, #7c3aed); color: #fff; font-size: 0.75rem; font-weight: 700; border-radius: 9999px; letter-spacing: 0.05em;">
              最受欢迎
            </div>
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">⭐</div>
            <h3 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem; color: #fff;">月付 VIP</h3>
            <div style="font-size: 2.5rem; font-weight: 800; color: #00d4ff; margin-bottom: 0.5rem;">¥29<span style="font-size: 1rem; color: #9ca3af;">/月</span></div>
            <div style="color: #9ca3af; font-size: 0.9rem; margin-bottom: 1.5rem;">每天仅需 ¥0.97</div>
            <div style="text-align: left; margin-bottom: 1.5rem;">
              <div v-for="feature in monthlyFeatures" :key="feature" style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; color: #10b981;">
                <span>✓</span>
                {{ feature }}
              </div>
            </div>
            <button style="width: 100%; padding: 0.875rem; background: linear-gradient(135deg, #00d4ff, #7c3aed); color: white; border: none; border-radius: 0.75rem; font-weight: 700; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 10px 25px -5px rgba(0,212,255,0.4)'" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='none'">
              立即升级
            </button>
          </div>

          <!-- Annual VIP -->
          <div style="background: linear-gradient(135deg, rgba(124,58,237,0.15) 0%, rgba(0,212,255,0.1) 100%); border-radius: 1.5rem; border: 2px solid #7c3aed; padding: 2rem; text-align: center; position: relative;">
            <div style="position: absolute; top: -0.75rem; left: 50%; transform: translateX(-50%); padding: 0.375rem 1rem; background: linear-gradient(135deg, #7c3aed, #9333ea); color: #fff; font-size: 0.75rem; font-weight: 700; border-radius: 9999px; letter-spacing: 0.05em;">
              超值优惠
            </div>
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">👑</div>
            <h3 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem; color: #fff;">年付 VIP</h3>
            <div style="font-size: 2.5rem; font-weight: 800; color: #7c3aed; margin-bottom: 0.5rem;">¥199<span style="font-size: 1rem; color: #9ca3af;">/年</span></div>
            <div style="color: #10b981; font-size: 0.9rem; margin-bottom: 1.5rem;">节省 ¥149 (43%)</div>
            <div style="text-align: left; margin-bottom: 1.5rem;">
              <div v-for="feature in annualFeatures" :key="feature" style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; color: #10b981;">
                <span>✓</span>
                {{ feature }}
              </div>
            </div>
            <button style="width: 100%; padding: 0.875rem; background: linear-gradient(135deg, #7c3aed, #9333ea); color: white; border: none; border-radius: 0.75rem; font-weight: 700; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 10px 25px -5px rgba(124,58,237,0.4)'" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='none'">
              立即开通
            </button>
          </div>
        </div>
      </section>

      <!-- Feature Comparison -->
      <section style="padding: 2rem 0 3rem;">
        <div style="background: linear-gradient(135deg, rgba(30,30,63,0.6) 0%, rgba(15,15,35,0.8) 100%); border-radius: 1rem; border: 1px solid rgba(58,58,92,0.6); padding: 2rem;">
          <h2 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1.5rem; color: #fff; text-align: center;">功能对比</h2>
          <table style="width: 100%; border-collapse: collapse;">
            <thead>
              <tr style="border-bottom: 1px solid rgba(58,58,92,0.6);">
                <th style="text-align: left; padding: 1rem; color: #9ca3af; font-weight: 500;">功能</th>
                <th style="text-align: center; padding: 1rem; color: #9ca3af; font-weight: 500;">免费版</th>
                <th style="text-align: center; padding: 1rem; color: #00d4ff; font-weight: 500;">月付 VIP</th>
                <th style="text-align: center; padding: 1rem; color: #7c3aed; font-weight: 500;">年付 VIP</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="feature in comparisonFeatures" :key="feature.name" style="border-bottom: 1px solid rgba(58,58,92,0.4);">
                <td style="padding: 1rem; color: #e5e7eb;">{{ feature.name }}</td>
                <td style="text-align: center; padding: 1rem; color: feature.free === '✓' ? '#10b981' : '#6b7280;">{{ feature.free }}</td>
                <td style="text-align: center; padding: 1rem; color: feature.monthly === '✓' ? '#10b981' : '#6b7280;">{{ feature.monthly }}</td>
                <td style="text-align: center; padding: 1rem; color: feature.annual === '✓' ? '#10b981' : '#6b7280;">{{ feature.annual }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- AI Features -->
      <section style="padding: 0 0 3rem;">
        <div style="background: linear-gradient(135deg, rgba(124,58,237,0.1) 0%, rgba(0,212,255,0.1) 100%); border-radius: 1rem; border: 1px solid rgba(0,212,255,0.2); padding: 2rem;">
          <h2 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem; color: #fff; text-align: center;">AI 智能功能（年付VIP专享）</h2>
          <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; margin-top: 1.5rem;">
            <div v-for="ai in aiFeatures" :key="ai.name" style="text-align: center; padding: 1.5rem; background: rgba(15,15,35,0.6); border-radius: 1rem;">
              <div style="font-size: 2rem; margin-bottom: 0.75rem;">{{ ai.icon }}</div>
              <div style="font-weight: 700; color: #fff; margin-bottom: 0.5rem;">{{ ai.name }}</div>
              <div style="color: #9ca3af; font-size: 0.85rem;">{{ ai.desc }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- FAQ -->
      <section style="padding: 0 0 4rem;">
        <div style="background: linear-gradient(135deg, rgba(30,30,63,0.6) 0%, rgba(15,15,35,0.8) 100%); border-radius: 1rem; border: 1px solid rgba(58,58,92,0.6); padding: 2rem;">
          <h2 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1.5rem; color: #fff;">常见问题</h2>
          <div style="display: flex; flex-direction: column; gap: 1rem;">
            <div v-for="faq in faqs" :key="faq.q" style="border-bottom: 1px solid rgba(58,58,92,0.4); padding-bottom: 1rem;">
              <div style="color: #00d4ff; font-weight: 600; margin-bottom: 0.5rem;">{{ faq.q }}</div>
              <div style="color: #9ca3af; font-size: 0.9rem;">{{ faq.a }}</div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import Navbar from '../components/Navbar.vue'

const freeFeatures = [
  '每日 3 次下载',
  '高清画质 (720P)',
  '单线程下载',
  '基础解析功能'
]

const monthlyFeatures = [
  '无限制下载次数',
  '4K 超清画质',
  '批量下载',
  '高速下载通道',
  'AI 视频总结'
]

const annualFeatures = [
  '无限制下载次数',
  '4K/8K 超清画质',
  '批量下载',
  '高速下载通道',
  '完整 AI 功能',
  '新功能优先体验',
  '专属客服支持'
]

const comparisonFeatures = [
  { name: '每日下载次数', free: '3次', monthly: '∞', annual: '∞' },
  { name: '视频清晰度', free: '720P', monthly: '4K', annual: '8K' },
  { name: '批量下载', free: '✕', monthly: '✓', annual: '✓' },
  { name: '去水印', free: '✓', monthly: '✓', annual: '✓' },
  { name: '下载速度', free: '普通', monthly: '高速', annual: '极速' },
  { name: 'AI 视频总结', free: '✕', monthly: '✓', annual: '✓' },
  { name: '字幕提取', free: '✕', monthly: '✓', annual: '✓' },
  { name: '思维导图生成', free: '✕', monthly: '✕', annual: '✓' },
  { name: 'AI 问答互动', free: '✕', monthly: '✕', annual: '✓' },
  { name: '客服支持', free: '✕', monthly: '标准', annual: '专属' }
]

const aiFeatures = [
  { icon: '🤖', name: 'AI 总结', desc: '智能分析视频内容，生成结构化总结' },
  { icon: '📝', name: '字幕提取', desc: '���取���频字幕，支持多种语言' },
  { icon: '🗺️', name: '思维导图', desc: '基于总结自动生成思维导图' },
  { icon: '💬', name: 'AI 问答', desc: '基于视频内容进行智能问答' }
]

const faqs = [
  { q: '免费版每天几次下载？', a: '免费版每天可以下载 3 次视频，次日凌晨自动重置。' },
  { q: 'VIP 可以退款吗？', a: '支持 7 天无理由退款，质量问题全额退款。' },
  { q: '年付 VIP 比月付便宜多少？', a: '年付 VIP 只需 ¥199，比月付（¥29×12=¥348）节省 ¥149，相当于 43% 折扣。' },
  { q: 'AI 功能有什么作用？', a: 'AI 功能可以自动分析视频内容，生成文字总结、提取字幕、生成思维导图，方便学习和整理内容。' },
  { q: '批量下载怎么使用？', a: '登录 VIP 账户后，在下载页面可以一次性添加多个链接，系统会按顺序依次下载。' }
]
</script>