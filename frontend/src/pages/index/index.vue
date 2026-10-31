<style lang="scss" scoped>
.home-page { display: flex; flex-direction: column; min-height: 100vh; background: #F8F6F1; }
.search-bar { display: flex; padding: 20rpx 24rpx; background: #F5EFE6; }
.search-input { display: flex; flex: 1; height: 72rpx; padding: 0 24rpx; border: 1rpx solid #DDD5C6; margin-right: 16rpx; background: #FFFFFF; font-size: 28rpx; color: #333333; border-radius: 12rpx; }
.search-btn { display: flex; align-items: center; justify-content: center; width: 140rpx; height: 72rpx; background: #8B5E3C; font-size: 28rpx; color: #FFFFFF; border-radius: 12rpx; }
.category-chips { display: flex; flex-wrap: wrap; padding: 8rpx 24rpx; gap: 16rpx; }
.category-chip { display: flex; align-items: center; justify-content: center; height: 56rpx; padding: 0 28rpx; background: #FFFFFF; font-size: 26rpx; color: #666666; border-radius: 28rpx; }
.category-chip--active { background: #8B5E3C; color: #FFFFFF; }
.book-list { display: flex; flex-direction: column; padding: 8rpx 24rpx 40rpx; gap: 20rpx; }
.book-card { display: flex; padding: 24rpx; background: #FFFFFF; border-radius: 16rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06); }
.book-cover { display: flex; align-items: center; justify-content: center; width: 140rpx; height: 180rpx; margin-right: 24rpx; background: #EFE6D8; font-size: 40rpx; color: #8B5E3C; font-weight: 600; border-radius: 12rpx; }
.book-info { display: flex; flex: 1; flex-direction: column; justify-content: center; }
.book-name { font-size: 32rpx; color: #333333; font-weight: 600; }
.book-meta { font-size: 26rpx; color: #999999; margin-top: 12rpx; }
.book-tags { display: flex; margin-top: 16rpx; gap: 12rpx; }
.book-tag { padding: 4rpx 16rpx; font-size: 22rpx; color: #8B5E3C; background: #F5EFE6; border-radius: 8rpx; }
.empty-tip { display: flex; align-items: center; justify-content: center; height: 240rpx; font-size: 28rpx; color: #999999; }
.load-more { display: flex; align-items: center; justify-content: center; height: 80rpx; font-size: 26rpx; color: #999999; }
</style>
<template>
  <!-- 🚀 页面主体 -->
  <view class="home-page">
    <!-- 🚀 搜索栏 -->
    <view class="search-bar">
      <input class="search-input" v-model="keyword" placeholder="搜索古籍书名" confirm-type="search"
             @confirm="handleSearch"/>
      <view class="search-btn" @click="handleSearch">搜索</view>
    </view>
    <!-- 🚀 分类快捷筛选 -->
    <view class="category-chips">
      <view v-for="item in categoryOptions" :key="item"
            class="category-chip"
            :class="{ 'category-chip--active': category === item }"
            @click="handleCategoryChange(item)">
        {{ item }}
      </view>
    </view>
    <!-- 🚀 书目列表 -->
    <view class="book-list">
      <view v-for="book in bookList" :key="book.bookId" class="book-card" @click="handleOpenBook(book)">
        <view class="book-cover">{{ getCoverText(book) }}</view>
        <view class="book-info">
          <view class="book-name">{{ book.bookName }}</view>
          <view class="book-meta">{{ book.author }} · {{ book.dynasty }} · 共{{ book.chapterCount }}篇</view>
          <view class="book-tags">
            <view v-for="tag in getBookTags(book)" :key="tag" class="book-tag">{{ tag }}</view>
          </view>
        </view>
      </view>
      <view v-if="bookList.length === 0 && !loading" class="empty-tip">暂无古籍数据</view>
    </view>
    <!-- 🚀 加载更多 -->
    <view class="load-more" v-if="hasNext">
      <text v-if="loading">加载中...</text>
      <text v-else @click="handleLoadMore">加载更多</text>
    </view>
  </view>
</template>
<script>
/**
 * 组件名称：home
 * 功能说明：识典古籍首页，提供搜索与分类筛选，展示古籍书目列表（分页加载）
 * 研发时间：2026/10/31
 * 研发人员：Doubao
 *
 * 变量说明：
 * @data {String}  keyword       - 搜索关键词
 * @data {String}  category      - 当前选中分类（全部/经/史/子/集/蒙学）
 * @data {Array}   categoryOptions - 分类筛选项
 * @data {Array}   bookList      - 书目列表数据
 * @data {Number}  pageNum       - 当前页码
 * @data {Number}  pageSize      - 每页条数
 * @data {Boolean} hasNext       - 是否还有下一页
 * @data {Boolean} loading       - 是否加载中
 *
 * 事件说明：
 * @event onLoad             - 页面加载后拉取首页书目
 * @event onPullDownRefresh  - 下拉刷新书目列表
 * @event onReachBottom      - 触底加载更多书目
 * @event handleSearch       - 执行搜索
 * @event handleCategoryChange - 切换分类筛选
 * @event handleLoadMore     - 加载下一页书目
 * @event handleOpenBook     - 打开书目详情
 * @event getCoverText       - 获取封面占位文字
 * @event getBookTags        - 生成书目标签
 * @event loadBooks          - 拉取书目列表（公共方法）
 *
 * 插槽说明：
 */
/**
 * 修改时间       人员        说明
 */

import { getBookPage } from '../../utils/gujiApi'

export default
{
  data()
  {
    return {
      keyword: '',
      category: '全部',
      categoryOptions: ['全部', '经', '史', '子', '集', '蒙学'],
      bookList: [],
      pageNum: 1,
      pageSize: 10,
      hasNext: false,
      loading: false,
    }
  },

  onLoad()
  {
    /**
     * 页面加载后拉取首页书目
     */
    this.loadBooks(true)
  },

  onPullDownRefresh()
  {
    /**
     * 下拉刷新书目列表
     */
    this.loadBooks(true).finally(() => uni.stopPullDownRefresh())
  },

  onReachBottom()
  {
    /**
     * 触底加载更多书目
     */
    if (this.hasNext && !this.loading)
    {
      this.loadBooks(false)
    }
  },

  methods:
  {
    /**
     * 执行搜索，重置分页并拉取书目
     */
    handleSearch()
    {
      this.loadBooks(true)
    },

    /**
     * 切换分类筛选
     * @param {String} item - 选中的分类
     */
    handleCategoryChange(item)
    {
      this.category = item
      this.loadBooks(true)
    },

    /**
     * 加载下一页书目
     */
    handleLoadMore()
    {
      this.loadBooks(false)
    },

    /**
     * 打开书目详情
     * @param {Object} book - 书目对象
     */
    handleOpenBook(book)
    {
      uni.navigateTo({ url: `/pages/book/detail?bookId=${book.bookId}` })
    },

    /**
     * 获取封面占位文字
     * @param {Object} book - 书目对象
     * @returns {String} 封面占位文字
     */
    getCoverText(book)
    {
      return book.bookName ? book.bookName.charAt(0) : '古'
    },

    /**
     * 生成书目标签
     * @param {Object} book - 书目对象
     * @returns {Array} 标签数组
     */
    getBookTags(book)
    {
      const tags = []
      if (book.category)
      {
        tags.push(book.category)
      }
      if (book.dynasty)
      {
        tags.push(book.dynasty)
      }
      return tags
    },

    /**
     * 拉取书目列表
     * @param {Boolean} reset - 是否重置分页并刷新列表
     */
    loadBooks(reset)
    {
      if (reset)
      {
        this.pageNum = 1
        this.bookList = []
      }
      this.loading = true
      const category = this.category === '全部' ? '' : this.category
      getBookPage({
        pageNum: this.pageNum,
        pageSize: this.pageSize,
        bookName: this.keyword || undefined,
        category: category || undefined,
      })
        .then((res) =>
        {
          if (res.code === 200)
          {
            this.bookList = reset ? res.data.rows : this.bookList.concat(res.data.rows)
            this.hasNext = res.data.hasNext
            this.pageNum += 1
          }
        })
        .catch(() => uni.showToast({ title: '加载失败', icon: 'none' }))
        .finally(() =>
        {
          this.loading = false
        })
    },
  },
}
</script>
