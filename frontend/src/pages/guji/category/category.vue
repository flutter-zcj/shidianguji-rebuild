<style lang="scss" scoped>
.page { display: flex; flex-direction: row; min-height: 100vh; background: #fbf7f0; }
.side { width: 200rpx; background: #f2e8d8; }
.side-item { padding: 32rpx 20rpx; font-size: 28rpx; color: #6b5844; text-align: center; }
.side-item-active { background: #ffffff; color: #8c5a3c; font-weight: 600; }
.main { flex: 1; padding: 20rpx; }
.book-row { display: flex; padding: 20rpx; margin-bottom: 16rpx; background: #ffffff; border-radius: 14rpx; }
.book-cover { width: 100rpx; height: 140rpx; border-radius: 8rpx; background: #e8dcc8; }
.book-info { flex: 1; display: flex; flex-direction: column; margin-left: 20rpx; }
.book-name { font-size: 30rpx; color: #3a2c20; font-weight: 500; }
.book-author { margin-top: 8rpx; font-size: 24rpx; color: #9a8b7a; }
.book-desc { margin-top: 8rpx; font-size: 22rpx; color: #b0a79c; lines: 2; }
.empty { padding: 80rpx; text-align: center; font-size: 26rpx; color: #9a8b7a; }
</style>
<template>
  <view class="page">
    <scroll-view class="side" scroll-y>
      <view
        class="side-item"
        :class="{ 'side-item-active': currentCateId === item.cateId }"
        v-for="item in categories"
        :key="item.cateId"
        @click="onSelect(item)"
      >
        {{ item.cateName }}
      </view>
    </scroll-view>

    <scroll-view class="main" scroll-y>
      <view class="book-row" v-for="book in books" :key="book.bookId" @click="onOpenBook(book)">
        <image class="book-cover" :src="book.coverUrl || defaultCover" mode="aspectFill" />
        <view class="book-info">
          <text class="book-name">{{ book.bookName }}</text>
          <text class="book-author">{{ book.authors }} · {{ book.dynastyName }}</text>
          <text class="book-desc">{{ book.abstract }}</text>
        </view>
      </view>
      <view class="empty" v-if="!books.length">该分类下暂无书籍</view>
    </scroll-view>
  </view>
</template>
<script>
import { getCategoryTree, getBookByCategory } from '@/api/guji.js'

/**
 * 识典古籍 - 分类
 * 对应原App Lynx category 页面：四部（经史子集）分类树 + 书籍列表
 */
export default
{
  data()
  {
    return {
      categories: [],
      books: [],
      currentCateId: '',
      defaultCover: '/static/logo.png'
    }
  },

  onShow()
  {
    this.loadCategory()
  },

  methods:
  {
    /**
     * 加载分类树
     */
    async loadCategory()
    {
      try
      {
        const res = await getCategoryTree()
        this.categories = res.categoryTree || res.rows || []
        if (this.categories.length)
          this.onSelect(this.categories[0])
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '加载失败', icon: 'none' })
      }
    },

    /**
     * 选择分类
     * @param {Object} item 分类对象
     */
    async onSelect(item)
    {
      this.currentCateId = item.cateId
      try
      {
        const res = await getBookByCategory(item.cateId, 1, 30)
        this.books = res.rows || []
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
    }
  }
}
</script>
