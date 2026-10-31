<style lang="scss" scoped>
.page { display: flex; flex-direction: column; min-height: 100vh; background: #fbf7f0; }
.notice { margin: 20rpx 30rpx; padding: 24rpx; background: #ffffff; border-radius: 16rpx; }
.notice-title { font-size: 30rpx; font-weight: 600; color: #3a2c20; }
.notice-content { margin-top: 12rpx; font-size: 26rpx; color: #6b5844; line-height: 42rpx; }
.notice-time { margin-top: 12rpx; font-size: 22rpx; color: #9a8b7a; }
.notice-unread { display: inline-block; margin-left: 12rpx; padding: 2rpx 10rpx; font-size: 20rpx; color: #ffffff; background: #c0472b; border-radius: 8rpx; }
.empty { padding: 80rpx; text-align: center; font-size: 26rpx; color: #9a8b7a; }
</style>
<template>
  <view class="page">
    <view class="notice" v-for="item in list" :key="item.noticeId">
      <view>
        <text class="notice-title">{{ item.title }}</text>
        <text class="notice-unread" v-if="!item.readFlag">未读</text>
      </view>
      <text class="notice-content">{{ item.content }}</text>
      <text class="notice-time">{{ item.createTime }}</text>
    </view>
    <view class="empty" v-if="!list.length">暂无通知</view>
  </view>
</template>
<script>
import { getNoticeList } from '@/api/guji.js'

/**
 * 识典古籍 - 通知中心
 * 对应原App Lynx notice 页面
 */
export default
{
  data()
  {
    return {
      list: []
    }
  },

  onShow()
  {
    this.loadData()
  },

  methods:
  {
    /**
     * 加载通知列表
     */
    async loadData()
    {
      try
      {
        const res = await getNoticeList(1, 50)
        this.list = res.rows || []
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '加载失败', icon: 'none' })
      }
    }
  }
}
</script>
