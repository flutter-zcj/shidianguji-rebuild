<style lang="scss" scoped>
.page { display: flex; flex-direction: column; min-height: 100vh; background: #fbf7f0; }
.search-bar { display: flex; align-items: center; padding: 20rpx 30rpx; background: #8c5a3c; }
.search-input { flex: 1; height: 68rpx; padding: 0 24rpx; background: #ffffff; border-radius: 34rpx; font-size: 28rpx; }
.search-btn { margin-left: 20rpx; font-size: 28rpx; color: #fff; }
.tab-row { display: flex; padding: 20rpx 30rpx; background: #ffffff; }
.tab-item { flex: 1; text-align: center; font-size: 28rpx; color: #6b5844; padding-bottom: 12rpx; }
.tab-active { color: #8c5a3c; font-weight: 600; border-bottom: 4rpx solid #8c5a3c; }
.result { flex: 1; padding: 20rpx 30rpx; }
.result-item { padding: 24rpx; margin-bottom: 16rpx; background: #ffffff; border-radius: 14rpx; }
.result-title { font-size: 30rpx; color: #3a2c20; font-weight: 500; }
.result-sub { margin-top: 10rpx; font-size: 24rpx; color: #9a8b7a; }
.result-content { margin-top: 12rpx; font-size: 26rpx; color: #4a3a28; line-height: 44rpx; }
.highlight { color: #c07070; }
.empty { padding: 100rpx; text-align: center; font-size: 26rpx; color: #9a8b7a; }
</style>
<template>
  <view class="page">
    <view class="search-bar">
      <input
        class="search-input"
        v-model="keyword"
        placeholder="搜索书名、作者或原文"
        confirm-type="search"
        @confirm="onSearch"
      />
      <text class="search-btn" @click="onSearch">搜索</text>
    </view>

    <view class="tab-row">
      <view class="tab-item" :class="{ 'tab-active': tab === 'book' }" @click="tab = 'book'; onSearch()">古籍</view>
      <view class="tab-item" :class="{ 'tab-active': tab === 'paragraph' }" @click="tab = 'paragraph'; onSearch()">原文</view>
    </view>

    <scroll-view class="result" scroll-y>
      <view class="result-item" v-for="item in results" :key="item.bookId || item.paragraphId" @click="onOpen(item)">
        <text class="result-title">{{ tab === 'book' ? item.bookName : item.chapterName }}</text>
        <text class="result-sub" v-if="tab === 'book'">{{ item.authors }} · {{ item.dynastyName }}</text>
        <text class="result-content" v-if="tab === 'paragraph'">{{ item.content }}</text>
      </view>
      <view class="empty" v-if="searched && !results.length">换个关键词试试</view>
    </scroll-view>
  </view>
</template>
<script>
import { searchBook, searchParagraph } from '@/api/guji.js'

/**
 * 识典古籍 - 搜索
 * 对应原App Lynx search 页面：古籍检索 + 全文段落检索
 */
export default
{
  data()
  {
    return {
      keyword: '',
      tab: 'book',
      results: [],
      searched: false
    }
  },

  methods:
  {
    /**
     * 执行检索
     */
    async onSearch()
    {
      if (!this.keyword.trim())
        return
      try
      {
        const res = this.tab === 'book'
          ? await searchBook(this.keyword, 1, 30)
          : await searchParagraph({ queryText: this.keyword, pageNum: 1, pageSize: 30 })
        this.results = res.rows || []
        this.searched = true
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '检索失败', icon: 'none' })
      }
    },

    /**
     * 打开检索结果
     * @param {Object} item 结果对象
     */
    onOpen(item)
    {
      const bookId = item.bookId
      if (!bookId)
        return
      uni.navigateTo({ url: `/pages/guji/book/book?bookId=${bookId}` })
    }
  }
}
</script>
