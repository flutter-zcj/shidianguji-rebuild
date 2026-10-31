<style lang="scss" scoped>
.detail-page { display: flex; flex-direction: column; min-height: 100vh; background: #F8F6F1; }
.detail-header { display: flex; padding: 32rpx; background: #F5EFE6; }
.detail-cover { display: flex; align-items: center; justify-content: center; width: 180rpx; height: 240rpx; margin-right: 32rpx; background: #EFE6D8; font-size: 56rpx; color: #8B5E3C; font-weight: 600; border-radius: 12rpx; }
.detail-info { display: flex; flex: 1; flex-direction: column; justify-content: center; }
.detail-name { font-size: 40rpx; color: #333333; font-weight: 600; }
.detail-meta { font-size: 26rpx; color: #999999; margin-top: 12rpx; }
.detail-tags { display: flex; margin-top: 16rpx; gap: 12rpx; }
.detail-tag { padding: 4rpx 16rpx; font-size: 22rpx; color: #8B5E3C; background: #FFFFFF; border-radius: 8rpx; }
.detail-intro { padding: 32rpx; font-size: 28rpx; color: #666666; line-height: 1.8; }
.action-bar { display: flex; padding: 0 32rpx 32rpx; gap: 20rpx; }
.action-btn { display: flex; align-items: center; justify-content: center; height: 88rpx; font-size: 30rpx; border-radius: 16rpx; }
.action-btn--primary { flex: 1; background: #8B5E3C; color: #FFFFFF; }
.action-btn--normal { flex: 1; background: #FFFFFF; color: #8B5E3C; border: 1rpx solid #8B5E3C; }
.section-title { padding: 16rpx 32rpx; font-size: 30rpx; color: #333333; font-weight: 600; }
.chapter-list { display: flex; flex-direction: column; padding: 0 32rpx 40rpx; gap: 16rpx; }
.chapter-item { display: flex; align-items: center; justify-content: space-between; padding: 28rpx 24rpx; background: #FFFFFF; font-size: 28rpx; color: #333333; border-radius: 12rpx; }
.chapter-arrow { font-size: 26rpx; color: #BBBBBB; }
.audio-list { display: flex; flex-direction: column; padding: 0 32rpx 40rpx; gap: 16rpx; }
.audio-item { display: flex; align-items: center; justify-content: space-between; padding: 24rpx; background: #FFFFFF; font-size: 26rpx; color: #333333; border-radius: 12rpx; }
.audio-dur { font-size: 22rpx; color: #999999; }
.empty-tip { display: flex; align-items: center; justify-content: center; height: 200rpx; font-size: 26rpx; color: #999999; }
</style>
<template>
  <!-- 🚀 页面主体 -->
  <view class="detail-page">
    <!-- 🚀 书目信息区 -->
    <view class="detail-header">
      <view class="detail-cover">{{ getCoverText() }}</view>
      <view class="detail-info">
        <view class="detail-name">{{ book.bookName }}</view>
        <view class="detail-meta">{{ book.author }} · {{ book.dynasty }} · 共{{ book.chapterCount }}篇</view>
        <view class="detail-tags">
          <view v-for="tag in getBookTags()" :key="tag" class="detail-tag">{{ tag }}</view>
        </view>
      </view>
    </view>
    <!-- 🚀 简介 -->
    <view class="detail-intro">{{ book.intro || '暂无简介' }}</view>
    <!-- 🚀 操作区 -->
    <view class="action-bar">
      <view class="action-btn action-btn--primary" @click="handleStartRead">开始阅读</view>
      <view class="action-btn action-btn--normal" @click="handleAddShelf">加入书架</view>
    </view>
    <!-- 🚀 章节目录 -->
    <view class="section-title">章节目录（{{ chapterList.length }}）</view>
    <view class="chapter-list">
      <view v-for="item in chapterList" :key="item.chapterId" class="chapter-item" @click="handleOpenChapter(item)">
        <text>{{ item.chapterNo }}. {{ item.chapterName }}</text>
        <text class="chapter-arrow">›</text>
      </view>
      <view v-if="chapterList.length === 0" class="empty-tip">暂无章节</view>
    </view>
    <!-- 🚀 听书音频 -->
    <view class="section-title">听书音频（{{ audioList.length }}）</view>
    <view class="audio-list">
      <view v-for="item in audioList" :key="item.audioId" class="audio-item" @click="handlePlayAudio(item)">
        <text>{{ item.audioName }}</text>
        <text class="audio-dur">{{ formatDuration(item.durationSec) }}</text>
      </view>
      <view v-if="audioList.length === 0" class="empty-tip">暂无音频</view>
    </view>
  </view>
</template>
<script>
/**
 * 组件名称：book-detail
 * 功能说明：书目详情页，展示书目信息、章节目录与听书音频，支持开始阅读与加入书架
 * 研发时间：2026/10/31
 * 研发人员：Doubao
 *
 * 变量说明：
 * @data {Object}  book         - 书目详情
 * @data {Array}   chapterList  - 章节目录列表
 * @data {Array}   audioList    - 听书音频列表
 *
 * 事件说明：
 * @event onLoad          - 页面加载后拉取详情、章节与音频
 * @event getCoverText    - 获取封面占位文字
 * @event getBookTags     - 生成书目标签
 * @event handleStartRead - 开始阅读第一章
 * @event handleAddShelf  - 加入书架
 * @event handleOpenChapter - 打开指定章节阅读
 * @event handlePlayAudio - 播放音频（示例提示）
 * @event formatDuration  - 格式化音频时长
 * @event loadDetail      - 拉取书目详情
 *
 * 插槽说明：
 */
/**
 * 修改时间       人员        说明
 */

import { getBookDetail, getChapters, getAudio, addBookshelf } from '../../utils/gujiApi'

export default
{
  data()
  {
    return {
      bookId: 0,
      book: {},
      chapterList: [],
      audioList: [],
    }
  },

  onLoad(query)
  {
    /**
     * 页面加载后拉取详情、章节与音频
     * @param {Object} query - 页面参数（bookId）
     */
    this.bookId = Number(query.bookId)
    this.loadDetail()
  },

  methods:
  {
    /**
     * 获取封面占位文字
     * @returns {String} 封面占位文字
     */
    getCoverText()
    {
      return this.book.bookName ? this.book.bookName.charAt(0) : '古'
    },

    /**
     * 生成书目标签
     * @returns {Array} 标签数组
     */
    getBookTags()
    {
      const tags = []
      if (this.book.category)
      {
        tags.push(this.book.category)
      }
      if (this.book.dynasty)
      {
        tags.push(this.book.dynasty)
      }
      return tags
    },

    /**
     * 开始阅读第一章
     */
    handleStartRead()
    {
      if (this.chapterList.length === 0)
      {
        uni.showToast({ title: '本书暂无章节', icon: 'none' })
        return
      }
      this.handleOpenChapter(this.chapterList[0])
    },

    /**
     * 加入书架
     */
    handleAddShelf()
    {
      addBookshelf(this.bookId)
        .then((res) =>
        {
          if (res.code === 200)
          {
            uni.showToast({ title: res.data.message || '加入成功', icon: 'success' })
          }
          else
          {
            uni.showToast({ title: res.msg || '请先登录', icon: 'none' })
          }
        })
        .catch(() => uni.showToast({ title: '操作失败', icon: 'none' }))
    },

    /**
     * 打开指定章节阅读
     * @param {Object} item - 章节对象
     */
    handleOpenChapter(item)
    {
      uni.navigateTo({ url: `/pages/reader/index?bookId=${this.bookId}&chapterId=${item.chapterId}` })
    },

    /**
     * 播放音频（示例提示）
     * @param {Object} item - 音频对象
     */
    handlePlayAudio(item)
    {
      uni.showToast({ title: `试听：${item.audioName}`, icon: 'none' })
    },

    /**
     * 格式化音频时长
     * @param {Number} seconds - 秒数
     * @returns {String} 格式化时长
     */
    formatDuration(seconds)
    {
      if (!seconds)
      {
        return ''
      }
      const minutes = Math.floor(seconds / 60)
      const rest = seconds % 60
      return `${minutes}分${rest}秒`
    },

    /**
     * 拉取书目详情、章节与音频
     */
    loadDetail()
    {
      getBookDetail(this.bookId)
        .then((res) =>
        {
          if (res.code === 200)
          {
            this.book = res.data
          }
        })
        .catch(() => uni.showToast({ title: '书目不存在', icon: 'none' }))
      getChapters(this.bookId)
        .then((res) =>
        {
          if (res.code === 200)
          {
            this.chapterList = res.data
          }
        })
        .catch(() =>
        {
        })
      getAudio(this.bookId)
        .then((res) =>
        {
          if (res.code === 200)
          {
            this.audioList = res.data
          }
        })
        .catch(() =>
        {
        })
    },
  },
}
</script>
