<style lang="scss" scoped>
.mine-page { display: flex; flex-direction: column; min-height: 100vh; background: #F8F6F1; }
.user-header { display: flex; align-items: center; padding: 48rpx 32rpx; background: #F5EFE6; }
.user-avatar { display: flex; align-items: center; justify-content: center; width: 120rpx; height: 120rpx; margin-right: 24rpx; background: #8B5E3C; font-size: 48rpx; color: #FFFFFF; font-weight: 600; border-radius: 50%; }
.user-info { display: flex; flex-direction: column; }
.user-name { font-size: 34rpx; color: #333333; font-weight: 600; }
.user-sub { font-size: 26rpx; color: #999999; margin-top: 8rpx; }
.entry-list { display: flex; flex-direction: column; padding: 24rpx; gap: 20rpx; }
.entry-card { display: flex; align-items: center; justify-content: space-between; padding: 32rpx 24rpx; background: #FFFFFF; font-size: 30rpx; color: #333333; border-radius: 16rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06); }
.entry-card--danger { color: #C0392B; }
.arrow { font-size: 28rpx; color: #BBBBBB; }
.login-btn { display: flex; align-items: center; justify-content: center; margin: 40rpx 32rpx; height: 88rpx; background: #8B5E3C; font-size: 32rpx; color: #FFFFFF; border-radius: 16rpx; }
</style>
<template>
  <!-- 🚀 页面主体 -->
  <view class="mine-page">
    <!-- 🚀 用户信息区 -->
    <view class="user-header">
      <view class="user-avatar">{{ getAvatarText() }}</view>
      <view class="user-info">
        <view class="user-name">{{ isLoggedIn ? userInfo.userName : '未登录' }}</view>
        <view class="user-sub">{{ isLoggedIn ? `用户ID：${userInfo.userId}` : '登录后同步书架与阅读进度' }}</view>
      </view>
    </view>
    <!-- 🚀 功能入口 -->
    <view class="entry-list">
      <view v-if="isLoggedIn" class="entry-card" @click="handleOpenBookshelf">
        <text>我的书架</text>
        <text class="arrow">›</text>
      </view>
      <view v-if="isLoggedIn" class="entry-card" @click="handleOpenHistory">
        <text>阅读历史</text>
        <text class="arrow">›</text>
      </view>
      <view v-if="isLoggedIn" class="entry-card entry-card--danger" @click="handleLogout">
        <text>退出登录</text>
      </view>
    </view>
    <!-- 🚀 登录按钮 -->
    <view v-if="!isLoggedIn" class="login-btn" @click="handleLogin">立即登录</view>
  </view>
</template>
<script>
/**
 * 组件名称：mine
 * 功能说明：我的页面，展示登录用户信息，提供书架、阅读历史入口与退出登录
 * 研发时间：2026/10/31
 * 研发人员：Doubao
 *
 * 变量说明：
 * @data {Object}  userInfo   - 当前登录用户信息
 * @data {Boolean} isLoggedIn - 是否已登录
 *
 * 事件说明：
 * @event onShow          - 页面显示时刷新用户信息
 * @event getAvatarText   - 获取头像占位文字
 * @event handleOpenBookshelf - 打开我的书架
 * @event handleOpenHistory   - 打开阅读历史
 * @event handleLogout    - 退出登录
 * @event handleLogin     - 跳转登录页
 * @event loadUserInfo    - 拉取当前用户信息
 *
 * 插槽说明：
 */
/**
 * 修改时间       人员        说明
 */

import { getInfo } from '../../utils/gujiApi'

export default
{
  data()
  {
    return {
      userInfo: {},
      isLoggedIn: false,
    }
  },

  onShow()
  {
    /**
     * 页面显示时刷新用户信息
     */
    this.loadUserInfo()
  },

  methods:
  {
    /**
     * 获取头像占位文字
     * @returns {String} 头像占位文字
     */
    getAvatarText()
    {
      if (this.isLoggedIn && this.userInfo.userName)
      {
        return this.userInfo.userName.charAt(0)
      }
      return '客'
    },

    /**
     * 打开我的书架
     */
    handleOpenBookshelf()
    {
      uni.switchTab({ url: '/pages/bookshelf/index' })
    },

    /**
     * 打开阅读历史
     */
    handleOpenHistory()
    {
      uni.navigateTo({ url: '/pages/history/index' })
    },

    /**
     * 退出登录
     */
    handleLogout()
    {
      uni.showModal({
        title: '提示',
        content: '确定退出登录吗？',
        success: (res) =>
        {
          if (res.confirm)
          {
            uni.removeStorageSync('guji_token')
            this.isLoggedIn = false
            this.userInfo = {}
            uni.showToast({ title: '已退出', icon: 'success' })
          }
        },
      })
    },

    /**
     * 跳转登录页
     */
    handleLogin()
    {
      uni.navigateTo({ url: '/pages/login/index' })
    },

    /**
     * 拉取当前用户信息
     */
    loadUserInfo()
    {
      const token = uni.getStorageSync('guji_token')
      if (!token)
      {
        this.isLoggedIn = false
        return
      }
      getInfo()
        .then((res) =>
        {
          if (res.code === 200)
          {
            this.isLoggedIn = true
            this.userInfo = res.user || {}
          }
          else
          {
            this.isLoggedIn = false
          }
        })
        .catch(() =>
        {
          this.isLoggedIn = false
        })
    },
  },
}
</script>
