<style lang="scss" scoped>
.page { display: flex; flex-direction: column; min-height: 100vh; background: #fbf7f0; }
.tabs { display: flex; padding: 20rpx 30rpx; background: #8c5a3c; }
.tab { flex: 1; text-align: center; padding: 12rpx 0; font-size: 28rpx; color: #f0e2d0; }
.tab-active { color: #ffffff; font-weight: 600; }
.group { margin: 20rpx 30rpx; padding: 24rpx; background: #ffffff; border-radius: 16rpx; }
.group-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16rpx; }
.group-title { font-size: 30rpx; font-weight: 600; color: #3a2c20; }
.group-count { font-size: 22rpx; color: #9a8b7a; }
.item { padding: 18rpx 0; border-top: 1rpx solid #f2ece2; }
.item-text { font-size: 28rpx; color: #3a2c20; line-height: 44rpx; }
.item-meta { margin-top: 8rpx; font-size: 22rpx; color: #9a8b7a; }
.item-del { margin-left: 16rpx; font-size: 22rpx; color: #c0472b; }
.empty { padding: 80rpx; text-align: center; font-size: 26rpx; color: #9a8b7a; }
</style>
<template>
  <view class="page">
    <view class="tabs">
      <view class="tab" :class="{ 'tab-active': tab === 'bookmark' }" @click="onSwitch('bookmark')">书签</view>
      <view class="tab" :class="{ 'tab-active': tab === 'review' }" @click="onSwitch('review')">笔记</view>
    </view>

    <view class="group" v-for="group in groups" :key="group.bookId">
      <view class="group-head">
        <text class="group-title">{{ group.bookName }}</text>
        <text class="group-count">{{ group.items.length }} 条</text>
      </view>
      <view class="item" v-for="item in group.items" :key="item.id" @click="onOpen(group, item)">
        <text class="item-text">{{ item.text }}</text>
        <view>
          <text class="item-meta">{{ item.chapterName }} · {{ item.createTime }}</text>
          <text class="item-del" @click.stop="onDelete(item)">删除</text>
        </view>
      </view>
    </view>

    <view class="empty" v-if="!groups.length">还没有{{ tab === 'bookmark' ? '书签' : '笔记' }}，去阅读页添加吧</view>
  </view>
</template>
<script>
import {
  listMarkedBook,
  listBookmark,
  deleteBookmark,
  listReview,
  deleteReview
} from '@/api/guji.js'

/**
 * 识典古籍 - 我的笔记/书签
 * 对应原App H5 myNote 页面：先取有标记的书籍，再按书聚合书签与笔记
 */
export default
{
  data()
  {
    return {
      tab: 'bookmark',
      groups: []
    }
  },

  onShow()
  {
    this.loadData()
  },

  methods:
  {
    /**
     * 切换书签/笔记 Tab
     * @param {String} tab 标签
     */
    onSwitch(tab)
    {
      this.tab = tab
      this.loadData()
    },

    /**
     * 加载标记数据：先取有标记的书籍，再按书籍拉取明细
     */
    async loadData()
    {
      uni.showLoading({ title: '加载中' })
      try
      {
        const bookRes = await listMarkedBook()
        const books = bookRes.rows || []
        const groups = []
        for (const book of books)
        {
          const res = this.tab === 'bookmark'
            ? await listBookmark(book.bookId)
            : await listReview(book.bookId)
          const rows = res.rows || res.list || []
          if (!rows.length)
            continue
          groups.push(
          {
            bookId: book.bookId,
            bookName: book.bookName || `书籍 ${book.bookId}`,
            items: rows.map((row) => (
            {
              id: row.bookmarkId || row.reviewId,
              text: row.content || row.reviewContent || row.paragraphContent || '',
              chapterName: row.chapterName || '',
              chapterId: row.chapterId,
              createTime: row.createTime || ''
            }))
          })
        }
        this.groups = groups
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '加载失败', icon: 'none' })
      }
      finally
      {
        uni.hideLoading()
      }
    },

    /**
     * 跳转到对应章节继续阅读
     * @param {Object} group 分组
     * @param {Object} item 明细
     */
    onOpen(group, item)
    {
      uni.navigateTo(
      {
        url: `/pages/guji/reader/reader?bookId=${group.bookId}&chapterId=${item.chapterId || ''}`
      })
    },

    /**
     * 删除书签或笔记
     * @param {Object} item 明细
     */
    async onDelete(item)
    {
      try
      {
        if (this.tab === 'bookmark')
          await deleteBookmark(item.id)
        else
          await deleteReview(item.id)
        uni.showToast({ title: '已删除', icon: 'none' })
        this.loadData()
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '删除失败', icon: 'none' })
      }
    }
  }
}
</script>
