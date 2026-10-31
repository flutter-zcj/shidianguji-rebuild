<style lang="scss" scoped>
.page { display: flex; flex-direction: column; min-height: 100vh; background: #fbf7f0; }
.detail-head { display: flex; padding: 30rpx; background: #ffffff; }
.cover { width: 200rpx; height: 280rpx; border-radius: 12rpx; background: #e8dcc8; }
.head-info { flex: 1; display: flex; flex-direction: column; margin-left: 24rpx; }
.book-name { font-size: 36rpx; color: #3a2c20; font-weight: 600; }
.book-author { margin-top: 12rpx; font-size: 26rpx; color: #6b5844; }
.book-meta { margin-top: 12rpx; font-size: 22rpx; color: #9a8b7a; }
.book-tags { display: flex; margin-top: 16rpx; }
.tag { padding: 4rpx 14rpx; margin-right: 12rpx; font-size: 22rpx; color: #8c5a3c; background: #f5ece0; border-radius: 8rpx; }
.action-row { display: flex; padding: 24rpx 30rpx; background: #ffffff; }
.btn-read { flex: 2; height: 80rpx; line-height: 80rpx; text-align: center; background: #8c5a3c; color: #fff; border-radius: 40rpx; font-size: 30rpx; }
.btn-shelf { flex: 1; height: 80rpx; line-height: 80rpx; text-align: center; margin-left: 20rpx; background: #f2e8d8; color: #8c5a3c; border-radius: 40rpx; font-size: 30rpx; }
.section { padding: 30rpx; }
.section-title { font-size: 30rpx; font-weight: 600; color: #3a2c20; margin-bottom: 16rpx; }
.intro { font-size: 26rpx; color: #6b5844; line-height: 44rpx; }
.chapter-item { display: flex; align-items: center; justify-content: space-between; padding: 22rpx 0; border-bottom: 1rpx solid #efe6d8; }
.chapter-name { font-size: 28rpx; color: #3a2c20; }
.chapter-arrow { font-size: 24rpx; color: #c0b6a8; }
.contrib { font-size: 24rpx; color: #9a8b7a; margin-right: 16rpx; }
.empty { padding: 40rpx; text-align: center; font-size: 24rpx; color: #9a8b7a; }
</style>
<template>
  <view class="page">
    <view class="detail-head">
      <image class="cover" :src="book.coverUrl || defaultCover" mode="aspectFill" />
      <view class="head-info">
        <text class="book-name">{{ book.bookName }}</text>
        <text class="book-author">{{ book.authors }}</text>
        <text class="book-meta">{{ book.dynastyName }} · {{ book.traditionalCategory }}部 · {{ book.edition }}</text>
        <view class="book-tags">
          <text class="tag" v-if="book.isListeningSupported">可听书</text>
          <text class="tag" v-if="book.isPodcastSupported">有讲书</text>
        </view>
      </view>
    </view>

    <view class="action-row">
      <view class="btn-read" @click="onRead">{{ progress ? '继续阅读' : '开始阅读' }}</view>
      <view class="btn-shelf" @click="onToggleShelf">{{ inShelf ? '已入书架' : '加入书架' }}</view>
    </view>

    <view class="section">
      <text class="section-title">内容简介</text>
      <text class="intro">{{ book.introduction || book.abstract || '暂无简介' }}</text>
    </view>

    <view class="section">
      <text class="section-title">目录（共 {{ chapters.length }} 章）</text>
      <view class="chapter-item" v-for="chapter in chapters" :key="chapter.chapterId" @click="onReadChapter(chapter)">
        <text class="chapter-name">{{ chapter.chapterName }}</text>
        <text class="chapter-arrow">›</text>
      </view>
      <view class="empty" v-if="!chapters.length">暂无目录</view>
    </view>

    <view class="section">
      <text class="section-title">整理校对</text>
      <text class="contrib" v-for="item in contributors" :key="item.contributorId">{{ item.nickName }}</text>
      <view class="empty" v-if="!contributors.length">—</view>
    </view>
  </view>
</template>
<script>
import {
  getBookDetail,
  checkShelf,
  addShelf,
  deleteShelf,
  getHistory,
  getBookContributor
} from '@/api/guji.js'

/**
 * 识典古籍 - 书籍详情
 * 对应原App H5/Lynx 书籍详情：简介、目录、整理者、加入书架、开始阅读
 */
export default
{
  data()
  {
    return {
      bookId: '',
      book: {},
      chapters: [],
      contributors: [],
      inShelf: false,
      progress: '',
      defaultCover: '/static/logo.png'
    }
  },

  onLoad(options)
  {
    this.bookId = options.bookId || options.id || ''
    this.loadData()
  },

  methods:
  {
    /**
     * 加载书籍详情
     */
    async loadData()
    {
      if (!this.bookId)
        return
      try
      {
        const [detailRes, shelfRes, historyRes, contribRes] = await Promise.all([
          getBookDetail(this.bookId, 1),
          checkShelf([this.bookId]),
          getHistory(this.bookId),
          getBookContributor(this.bookId)
        ])
        this.book = detailRes || {}
        this.chapters = detailRes.chapters || []
        const status = shelfRes.shelfStatus || {}
        this.inShelf = status[this.bookId] === 1
        this.progress = (historyRes.historyInfo && historyRes.historyInfo.progress) || ''
        this.contributors = contribRes.contributorList || []
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '加载失败', icon: 'none' })
      }
    },

    /**
     * 开始/继续阅读
     */
    onRead()
    {
      const chapter = this.chapters.length ? this.chapters[0] : null
      this.onReadChapter(chapter)
    },

    /**
     * 阅读指定章节
     * @param {Object} chapter 章节对象
     */
    onReadChapter(chapter)
    {
      const chapterId = chapter ? chapter.chapterId : ''
      uni.navigateTo({ url: `/pages/guji/reader/reader?bookId=${this.bookId}&chapterId=${chapterId}` })
    },

    /**
     * 加入/移出书架
     */
    async onToggleShelf()
    {
      try
      {
        if (this.inShelf)
          await deleteShelf([this.bookId])
        else
          await addShelf(this.bookId)
        this.inShelf = !this.inShelf
        uni.showToast({ title: this.inShelf ? '已加入书架' : '已移出书架', icon: 'none' })
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '操作失败', icon: 'none' })
      }
    }
  }
}
</script>
