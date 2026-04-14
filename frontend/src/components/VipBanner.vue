<template>
  <section style="padding: 3rem 0 4rem;">
    <div style="background: linear-gradient(135deg, rgba(124, 58, 237, 0.15) 0%, rgba(0, 212, 255, 0.1) 50%, rgba(124, 58, 237, 0.15) 100%); border-radius: 1.5rem; border: 1px solid rgba(0, 212, 255, 0.2); padding: 2.5rem; text-align: center; position: relative; overflow: hidden;">
      <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(circle at 30% 50%, rgba(0,212,255,0.1) 0%, transparent 50%); pointer-events: none;"></div>
      <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(circle at 70% 50%, rgba(124,58,237,0.1) 0%, transparent 50%); pointer-events: none;"></div>
      
      <div style="position: relative; z-index: 1;">
        <h2 style="font-size: 1.75rem; font-weight: 800; margin-bottom: 0.75rem; color: #fff; letter-spacing: -0.025em;">
          升级 VIP，解锁无限可能
        </h2>
        <p style="color: #9ca3af; font-size: 0.95rem; margin-bottom: 2rem; max-width: 36rem; margin-left: auto; margin-right: auto;">
          无限制下载 · 4K/8K超清 · 批量下载 · AI智能分析
        </p>
        
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; max-width: 48rem; margin: 0 auto 1.5rem;">
          <div style="background: rgba(15,15,35,0.6); border-radius: 1rem; padding: 1.25rem; border: 1px solid rgba(58,58,92,0.5); transition: all 0.3s;">
            <div style="font-size: 1.75rem; margin-bottom: 0.5rem;">🆓</div>
            <h3 style="font-size: 1rem; font-weight: 700; margin-bottom: 0.25rem; color: #fff;">免费版</h3>
            <p style="color: #9ca3af; font-size: 0.8rem;">每日 3 次下载</p>
            <p style="color: #6b7280; font-size: 0.75rem;">高清画质</p>
          </div>
          
          <div style="background: linear-gradient(135deg, rgba(0,212,255,0.15) 0%, rgba(124,58,237,0.15) 100%); border-radius: 1rem; padding: 1.25rem; border: 2px solid #00d4ff; position: relative; transition: all 0.3s; transform: scale(1.02);">
            <div style="position: absolute; top: -0.6rem; left: 50%; transform: translateX(-50%); padding: 0.2rem 0.6rem; background: linear-gradient(135deg, #00d4ff, #7c3aed); color: #fff; font-size: 0.7rem; font-weight: 700; border-radius: 9999px; letter-spacing: 0.05em;">
              最受欢迎
            </div>
            <div style="font-size: 1.75rem; margin-bottom: 0.5rem;">⭐</div>
            <h3 style="font-size: 1rem; font-weight: 700; margin-bottom: 0.25rem; color: #fff;">月付 VIP</h3>
            <p style="font-size: 1.5rem; font-weight: 800; color: #00d4ff; margin-bottom: 0.25rem;">¥29<span style="font-size: 0.75rem; color: #9ca3af;">/月</span></p>
            <p style="color: #d1d5db; font-size: 0.75rem;">无限下载</p>
            <p style="color: #6b7280; font-size: 0.7rem;">4K 超清</p>
          </div>
          
          <div style="background: rgba(15,15,35,0.6); border-radius: 1rem; padding: 1.25rem; border: 1px solid rgba(124,58,237,0.5); transition: all 0.3s;">
            <div style="font-size: 1.75rem; margin-bottom: 0.5rem;">👑</div>
            <h3 style="font-size: 1rem; font-weight: 700; margin-bottom: 0.25rem; color: #fff;">年付 VIP</h3>
            <p style="font-size: 1.5rem; font-weight: 800; color: #7c3aed; margin-bottom: 0.25rem;">¥199<span style="font-size: 0.75rem; color: #9ca3af;">/年</span></p>
            <p style="color: #d1d5db; font-size: 0.75rem;">所有月付功能</p>
            <p style="color: #6b7280; font-size: 0.7rem;">AI 视频总结</p>
          </div>
        </div>
        
        <button style="padding: 0.875rem 2rem; background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%); color: white; font-size: 1rem; font-weight: 700; border-radius: 0.75rem; border: none; cursor: pointer; box-shadow: 0 10px 25px -5px rgba(0, 212, 255, 0.4); transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 15px 30px -5px rgba(0,212,255,0.5)'" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 10px 25px -5px rgba(0,212,255,0.4)'">
          立即升级 →
        </button>
      </div>
    </div>
  </section>
</template>