<style lang="scss" scoped>
.page { display: flex; flex-direction: column; min-height: 100vh; background: #fbf7f0; }
.tabs { display: flex; padding: 20rpx 30rpx; background: #8c5a3c; }
.tab { flex: 1; text-align: center; padding: 12rpx 0; font-size: 28rpx; color: #f0e2d0; }
.tab-active { color: #ffffff; font-weight: 600; }
.video { margin: 20rpx 30rpx; padding: 20rpx; background: #ffffff; border-radius: 16rpx; }
.video-cover { width: 100%; height: 300rpx; border-radius: 12rpx; background: #e8dcc8; }
.video-title { margin-top: 14rpx; font-size: 28rpx; color: #3a2c20; }
.video-sub { margin-top: 8rpx; font-size: 22rpx; color: #9a8b7a; }
.series { display: flex; align-items: center; padding: 24rpx 30rpx; background: #ffffff; border-bottom: 1rpx solid #f2ece2; }
.series-cover { width: 120rpx; height: 90rpx; border-radius: 10rpx; background: #e8dcc8; }
.series-info { flex: 1; margin-left: 20rpx; }
.series-title { font-size: 28rpx; color: #3a2c20; }
.series-sub { margin-top: 8rpx; font-size: 22rpx; color: #9a8b7a; }
.series-enter { font-size: 26rpx; color: #8c5a3c; }
.explain { padding: 20rpx 30rpx; font-size: 28rpx; color: #3a2c20; background: #ffffff; border-bottom: 1rpx solid #f2ece2; }
.detail-head { padding: 24rpx 30rpx; background: #efe6d2; }
.detail-title { font-size: 32rpx; font-weight: 600; color: #3a2c20; }
.detail-desc { margin-top: 10rpx; font-size: 24rpx; color: #6b5844; }
.back { font-size: 26rpx; color: #8c5a3c; }
.empty { padding: 80rpx; text-align: center; font-size: 26rpx; color: #9a8b7a; }
</style>
<template>
  <view class="page">
    <view class="tabs">
      <view class="tab" :class="{ 'tab-active': tab === 'video' }" @click="onSwitch('video')">视频</view>
      <view class="tab" :class="{ 'tab-active': tab === 'course' }" @click="onSwitch('course')">讲书</view>
    </view>

    <!-- 视频列表 -->
    <template v-if="tab === 'video'">
      <view class="video" v-for="item in videos" :key="item.videoId">
        <image class="video-cover" :src="item.coverUrl || defaultCover" mode="aspectFill" @click="onOpenBook(item)" />
        <text class="video-title">{{ item.videoName || item.title }}</text>
        <text class="video-sub">{{ item.generalAuthor || item.author || '识典讲书' }} · {{ item.duration || 0 }} 秒</text>
      </view>
      <view class="empty" v-if="!videos.length">暂无视频</view>
    </template>

    <!-- 讲书系列 -->
    <template v-else>
      <!-- 系列详情 -->
      <template v-if="detail.seriesId">
        <view class="detail-head">
          <text class="detail-title">{{ detail.seriesName }}</text>
          <text class="detail-desc">{{ detail.description }}</text>
          <text class="back" @click="onBackList">返回列表</text>
        </view>
        <view class="explain" v-for="item in explains" :key="item.explainId" @click="onOpenBook(item)">
          {{ item.title }}
        </view>
        <view class="empty" v-if="!explains.length">该系列暂无讲解</view>
      </template>

      <!-- 系列列表 -->
      <template v-else>
        <view class="series" v-for="item in series" :key="item.seriesId">
          <image class="series-cover" :src="item.coverUrl || defaultCover" mode="aspectFill" />
          <view class="series-info" @click="onOpenSeries(item)">
            <text class="series-title">{{ item.seriesName }}</text>
            <text class="series-sub">{{ item.explainCount || 0 }} 讲 · {{ item.author || '识典古籍' }}</text>
          </view>
          <text class="series-enter" @click="onOpenSeries(item)">进入</text>
        </view>
        <view class="empty" v-if="!series.length">暂无讲书系列</view>
      </template>
    </template>
  </view>
</template>
<script>
import {
  listVideo,
  listCourseSeries,
  getCourseDetail,
  listCourseExplain,
  searchExplain
} from '@/api/guji.js'

/**
 * 识典古籍 - 视频 / 讲书
 * 对应原App Lynx video 与 courseSeries 页面
 */
export default
{
  data()
  {
    return {
      tab: 'video',
      videos: [],
      series: [],
      explains: [],
      detail: {},
      keyword: '',
      defaultCover: '/static/logo.png'
    }
  },

  onShow()
  {
    this.loadData()
  },

  methods:
  {
    /**
     * 切换 Tab
     * @param {String} tab 标签
     */
    onSwitch(tab)
    {
      this.tab = tab
      this.loadData()
    },

    /**
     * 加载视频或讲书系列
     */
    async loadData()
    {
      try
      {
        if (this.tab === 'video')
        {
          const res = await listVideo(1, 30)
          this.videos = res.rows || []
        }
        else
        {
          const res = await listCourseSeries(1, 30)
          this.series = res.rows || []
        }
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '加载失败', icon: 'none' })
      }
    },

    /**
     * 打开讲书系列详情
     * @param {Object} item 系列
     */
    async onOpenSeries(item)
    {
      try
      {
        const [detailRes, explainRes] = await Promise.all([
          getCourseDetail(item.seriesId),
          listCourseExplain(item.seriesId)
        ])
        this.detail = { ...item, ...(detailRes || {}) }
        this.explains = explainRes.rows || explainRes.list || []
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '加载失败', icon: 'none' })
      }
    },

    /**
     * 返回系列列表
     */
    onBackList()
    {
      this.detail = {}
      this.explains = []
    },

    /**
     * 打开关联书籍
     * @param {Object} item 条目
     */
    onOpenBook(item)
    {
      if (!item.bookId)
        return
      uni.navigateTo({ url: `/pages/guji/book/book?bookId=${item.bookId}` })
    },

    /**
     * 搜索讲解内容
     * @param {String} keyword 关键词
     */
    async onSearch(keyword)
    {
      this.keyword = keyword
      try
      {
        const res = await searchExplain(keyword)
        this.explains = res.rows || []
        this.detail = { seriesId: -1, seriesName: `“${keyword}” 搜索结果`, description: '' }
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '搜索失败', icon: 'none' })
      }
    }
  }
}
</script>
