<style lang="scss" scoped>
.page { display: flex; flex-direction: column; min-height: 100vh; background: #fbf7f0; }
.header { display: flex; align-items: center; padding: 40rpx 30rpx; background: #8c5a3c; }
.avatar { width: 120rpx; height: 120rpx; border-radius: 60rpx; background: #e8dcc8; }
.user-info { margin-left: 24rpx; }
.user-name { font-size: 32rpx; color: #fff; font-weight: 600; }
.user-level { margin-top: 8rpx; font-size: 24rpx; color: #f0e2d0; }
.stat-row { display: flex; padding: 30rpx; background: #ffffff; }
.stat-item { flex: 1; display: flex; flex-direction: column; align-items: center; }
.stat-value { font-size: 36rpx; color: #8c5a3c; font-weight: 600; }
.stat-label { margin-top: 6rpx; font-size: 22rpx; color: #9a8b7a; }
.cell-group { margin-top: 20rpx; background: #ffffff; }
.cell { display: flex; align-items: center; justify-content: space-between; padding: 30rpx; border-bottom: 1rpx solid #f2ece2; }
.cell-text { font-size: 28rpx; color: #3a2c20; }
.cell-arrow { font-size: 24rpx; color: #c0b6a8; }
.clock-btn { margin: 40rpx 30rpx; height: 88rpx; line-height: 88rpx; text-align: center; background: #8c5a3c; color: #fff; border-radius: 44rpx; font-size: 30rpx; }
</style>
<template>
  <view class="page">
    <view class="header">
      <image class="avatar" :src="avatarUrl" mode="aspectFill" />
      <view class="user-info">
        <text class="user-name">{{ nickName }}</text>
        <text class="user-level">等级 {{ levelInfo.level || 1 }} · {{ levelInfo.contributionStr || '初入书海' }}</text>
      </view>
    </view>

    <view class="stat-row">
      <view class="stat-item">
        <text class="stat-value">{{ levelInfo.clockDays || 0 }}</text>
        <text class="stat-label">累计打卡</text>
      </view>
      <view class="stat-item">
        <text class="stat-value">{{ levelInfo.continueDays || 0 }}</text>
        <text class="stat-label">连续打卡</text>
      </view>
      <view class="stat-item">
        <text class="stat-value">{{ levelInfo.contributionCount || 0 }}</text>
        <text class="stat-label">贡献次数</text>
      </view>
      <view class="stat-item">
        <text class="stat-value">{{ favoriteCount }}</text>
        <text class="stat-label">我的收藏</text>
      </view>
    </view>

    <view class="clock-btn" @click="onClock">今日阅读打卡</view>

    <view class="cell-group">
      <view class="cell" @click="onGo('/pages/guji/notes/notes')">
        <text class="cell-text">我的笔记与书签</text>
        <text class="cell-arrow">›</text>
      </view>
      <view class="cell" @click="onGo('/pages/guji/quotation/quotation?mine=1')">
        <text class="cell-text">我的名句收藏</text>
        <text class="cell-arrow">›</text>
      </view>
      <view class="cell" @click="onGo('/pages/guji/topic/topic')">
        <text class="cell-text">我的书单</text>
        <text class="cell-arrow">›</text>
      </view>
      <view class="cell" @click="onGo('/pages/guji/notice/notice')">
        <text class="cell-text">消息通知</text>
        <text class="cell-arrow">›</text>
      </view>
      <view class="cell" @click="onGo('/pages/guji/settings/settings')">
        <text class="cell-text">阅读设置</text>
        <text class="cell-arrow">›</text>
      </view>
      <view class="cell" @click="onGo('/pages/guji/ai/ai')">
        <text class="cell-text">古籍智能助手</text>
        <text class="cell-arrow">›</text>
      </view>
    </view>
  </view>
</template>
<script>
import { getUserLevel, getClockInfo, readerClock, countFavorite, getContribution } from '@/api/guji.js'

/**
 * 识典古籍 - 我的
 * 对应原App Lynx logged/myReadPage 页面：等级、打卡、贡献、收藏与设置入口
 */
export default
{
  data()
  {
    return {
      nickName: '古籍爱好者',
      avatarUrl: '/static/logo.png',
      levelInfo: {},
      favoriteCount: 0
    }
  },

  onShow()
  {
    this.loadData()
  },

  methods:
  {
    /**
     * 加载用户概览数据
     */
    async loadData()
    {
      try
      {
        const [levelRes, clockRes, favRes, contribRes] = await Promise.all([
          getUserLevel(),
          getClockInfo(),
          countFavorite('quotation'),
          getContribution()
        ])
        this.levelInfo = { ...levelRes, ...clockRes, ...contribRes }
        this.favoriteCount = favRes.count || 0
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '加载失败', icon: 'none' })
      }
    },

    /**
     * 每日打卡
     */
    async onClock()
    {
      try
      {
        const res = await readerClock()
        uni.showToast({ title: `已连续打卡 ${res.continueDays || 1} 天`, icon: 'none' })
        this.loadData()
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '打卡失败', icon: 'none' })
      }
    },

    /**
     * 页面跳转
     * @param {String} url 页面路径
     */
    onGo(url)
    {
      uni.navigateTo({ url })
    }
  }
}
</script>
