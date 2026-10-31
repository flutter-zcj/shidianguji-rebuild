<style lang="scss" scoped>
.page { display: flex; flex-direction: column; min-height: 100vh; background: #fbf7f0; }
.search-bar { position: relative; display: flex; align-items: center; padding: 20rpx 30rpx; background: #8c5a3c; }
.search-input { flex: 1; display: flex; align-items: center; height: 68rpx; padding: 0 24rpx; background: #ffffff; border-radius: 34rpx; }
.search-placeholder { font-size: 26rpx; color: #b0a79c; }
.section { position: relative; display: flex; flex-direction: column; padding: 30rpx; }
.section-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20rpx; }
.section-title { font-size: 32rpx; font-weight: 600; color: #3a2c20; }
.section-more { font-size: 24rpx; color: #9a8b7a; }
.banner { width: 100%; height: 220rpx; border-radius: 16rpx; background: linear-gradient(135deg, #a9714b, #8c5a3c); }
.banner-title { position: absolute; left: 40rpx; top: 60rpx; font-size: 36rpx; color: #fff; font-weight: 600; }
.banner-sub { position: absolute; left: 40rpx; top: 120rpx; font-size: 24rpx; color: #f0e2d0; }
.book-grid { display: flex; flex-wrap: wrap; justify-content: space-between; }
.book-card { width: 210rpx; margin-bottom: 30rpx; }
.book-cover { width: 210rpx; height: 290rpx; border-radius: 12rpx; background: #e8dcc8; }
.book-name { margin-top: 12rpx; font-size: 26rpx; color: #3a2c20; lines: 1; }
.book-author { margin-top: 6rpx; font-size: 22rpx; color: #9a8b7a; }
.entry-row { display: flex; justify-content: space-around; padding: 20rpx 0; background: #ffffff; border-radius: 16rpx; }
.entry-item { display: flex; flex-direction: column; align-items: center; }
.entry-icon { width: 80rpx; height: 80rpx; border-radius: 40rpx; background: #f2e8d8; }
.entry-text { margin-top: 10rpx; font-size: 24rpx; color: #6b5844; }
.quote-card { padding: 28rpx; background: #ffffff; border-radius: 16rpx; }
.quote-text { font-size: 30rpx; color: #3a2c20; line-height: 48rpx; }
.quote-from { margin-top: 12rpx; font-size: 24rpx; color: #9a8b7a; }
.empty { padding: 60rpx; text-align: center; font-size: 26rpx; color: #9a8b7a; }
</style>
<template>
  <view class="page">
    <!-- 搜索入口 -->
    <view class="search-bar">
      <view class="search-input" @click="onGoSearch">
        <text class="search-placeholder">搜索书名、作者或原文</text>
      </view>
    </view>

    <!-- 功能入口 -->
    <view class="section">
      <view class="entry-row">
        <view class="entry-item" @click="onGo('category')">
          <view class="entry-icon" />
          <text class="entry-text">四部分类</text>
        </view>
        <view class="entry-item" @click="onGo('quotation')">
          <view class="entry-icon" />
          <text class="entry-text">名句</text>
        </view>
        <view class="entry-item" @click="onGo('audio')">
          <view class="entry-icon" />
          <text class="entry-text">听书</text>
        </view>
        <view class="entry-item" @click="onGo('video')">
          <view class="entry-icon" />
          <text class="entry-text">讲书</text>
        </view>
      </view>
    </view>

    <!-- Banner -->
    <view class="section" v-if="banners.length">
      <view class="banner">
        <text class="banner-title">{{ banners[0].title }}</text>
        <text class="banner-sub">识典古籍 · 免费阅读</text>
      </view>
    </view>

    <!-- 今日推荐 -->
    <view class="section">
      <view class="section-head">
        <text class="section-title">今日推荐</text>
        <text class="section-more" @click="onMore">查看全部</text>
      </view>
      <view class="book-grid">
        <view
          class="book-card"
          v-for="book in books"
          :key="book.bookId"
          @click="onOpenBook(book)"
        >
          <image class="book-cover" :src="book.coverUrl || defaultCover" mode="aspectFill" />
          <text class="book-name">{{ book.bookName }}</text>
          <text class="book-author">{{ book.authors }}</text>
        </view>
      </view>
    </view>

    <!-- 每日名句 -->
    <view class="section" v-if="quotation.famousQuote">
      <view class="section-head">
        <text class="section-title">每日名句</text>
        <text class="section-more" @click="onGo('quotation')">更多</text>
      </view>
      <view class="quote-card" @click="onOpenQuotation">
        <text class="quote-text">{{ quotation.famousQuote }}</text>
        <text class="quote-from">—— {{ quotation.author }}《{{ quotation.bookName }}》</text>
      </view>
    </view>

    <view class="empty" v-if="!books.length">暂无推荐内容</view>
  </view>
</template>
<script>
import { getHomepage, getHomepageBanner, getBookList, recommendQuotation } from '@/api/guji.js'

/**
 * 识典古籍 - 首页
 * 对应原App Lynx home 页面：Banner + 推荐书籍 + 每日名句 + 功能入口
 */
export default
{
  data()
  {
    return {
      banners: [],
      books: [],
      quotation: {},
      defaultCover: '/static/logo.png'
    }
  },

  onShow()
  {
    this.loadData()
  },

  onPullDownRefresh()
  {
    this.loadData()
      .then(() => uni.stopPullDownRefresh())
  },

  methods:
  {
    /**
     * 加载首页数据
     */
    async loadData()
    {
      try
      {
        const [home, bannerRes, bookRes, quoteRes] = await Promise.all([
          getHomepage(),
          getHomepageBanner(),
          getBookList({ pageNum: 1, pageSize: 6 }),
          recommendQuotation(1)
        ])
        this.banners = bannerRes.bannerList || []
        this.books = bookRes.rows || []
        const rows = (quoteRes && quoteRes.rows) || []
        this.quotation = rows.length ? rows[0] : {}
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '加载失败', icon: 'none' })
      }
    },

    /**
     * 打开书籍详情
     * @param {Object} book 书籍对象
     */
    onOpenBook(book)
    {
      uni.navigateTo({ url: `/pages/guji/book/book?bookId=${book.bookId}` })
    },

    /**
     * 打开名句详情
     */
    onOpenQuotation()
    {
      uni.navigateTo({ url: `/pages/guji/quotation/quotation?quotationId=${this.quotation.quotationId}` })
    },

    /**
     * 跳转功能页
     * @param {String} page 页面标识
     */
    onGo(page)
    {
      const map =
      {
        category: '/pages/guji/category/category',
        quotation: '/pages/guji/quotation/quotation',
        audio: '/pages/guji/audio/audio',
        video: '/pages/guji/video/video'
      }
      if (page === 'category')
        uni.switchTab({ url: map[page] })
      else
        uni.navigateTo({ url: map[page] })
    },

    /**
     * 查看更多书籍
     */
    onMore()
    {
      uni.navigateTo({ url: '/pages/guji/search/search' })
    },

    /**
     * 跳转搜索页
     */
    onGoSearch()
    {
      uni.navigateTo({ url: '/pages/guji/search/search' })
    }
  }
}
</script>
