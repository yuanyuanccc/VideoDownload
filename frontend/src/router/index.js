import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import PlatformsPage from '../views/PlatformsPage.vue'
import VipPage from '../views/VipPage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
    meta: { title: '万能视频下载器 | 支持YouTube/B站/抖音下载' }
  },
  {
    path: '/platforms',
    name: 'Platforms',
    component: PlatformsPage,
    meta: { title: '支持平台 | VideoGrab - 1800+平台视频下载' }
  },
  {
    path: '/vip',
    name: 'Vip',
    component: VipPage,
    meta: { title: 'VIP会员 | VideoGrab - 升级解锁更多特权' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})

export default router