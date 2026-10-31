<style lang="scss" scoped>
.page { display: flex; flex-direction: column; min-height: 100vh; background: #fbf7f0; }
.topic { margin: 20rpx 30rpx; padding: 24rpx; background: #ffffff; border-radius: 16rpx; }
.topic-name { font-size: 30rpx; font-weight: 600; color: #3a2c20; }
.topic-desc { margin-top: 10rpx; font-size: 26rpx; color: #6b5844; line-height: 42rpx; }
.topic-meta { margin-top: 12rpx; font-size: 22rpx; color: #9a8b7a; }
.topic-actions { margin-top: 16rpx; display: flex; }
.action { margin-right: 30rpx; font-size: 26rpx; color: #8c5a3c; }
.book-row { display: flex; align-items: center; padding: 20rpx 30rpx; background: #ffffff; border-bottom: 1rpx solid #f2ece2; }
.book-cover { width: 90rpx; height: 126rpx; border-radius: 8rpx; background: #e8dcc8; }
.book-info { flex: 1; margin-left: 20rpx; }
.book-name { font-size: 28rpx; color: #3a2c20; }
.book-author { margin-top: 6rpx; font-size: 22rpx; color: #9a8b7a; }
.book-del { font-size: 24rpx; color: #c0472b; }
.create-bar { display: flex; padding: 20rpx 30rpx; background: #8c5a3c; }
.create-input { flex: 1; height: 68rpx; padding: 0 20rpx; font-size: 26rpx; background: #ffffff; border-radius: 34rpx; }
.create-btn { margin-left: 20rpx; padding: 0 30rpx; line-height: 68rpx; font-size: 26rpx; color: #ffffff; }
.empty { padding: 80rpx; text-align: center; font-size: 26rpx; color: #9a8b7a; }
</style>
<template>
  <view class="page">
    <!-- 新建书单 -->
    <view class="create-bar">
      <input class="create-input" v-model="topicName" placeholder="输入书单名称" />
      <view class="create-btn" @click="onCreate">创建</view>
    </view>

    <!-- 书单列表 -->
    <view class="topic" v-for="topic in topics" :key="topic.topicId" @click="onOpen(topic)">
      <text class="topic-name">{{ topic.topicName }}</text>
      <text class="topic-desc">{{ topic.description || '暂无介绍' }}</text>
      <text class="topic-meta">{{ topic.bookCount || 0 }} 本书 · {{ topic.followCount || 0 }} 人关注</text>
      <view class="topic-actions">
        <text class="action" @click.stop="onFollow(topic)">{{ topic.followed ? '取消关注' : '关注' }}</text>
        <text class="action" @click.stop="onDelete(topic)">删除</text>
      </view>
    </view>

    <!-- 书单内书籍 -->
    <template v-if="currentTopic.topicId">
      <view class="book-row" v-for="book in books" :key="book.bookId">
        <image class="book-cover" :src="book.coverUrl || defaultCover" mode="aspectFill" />
        <view class="book-info" @click="onOpenBook(book)">
          <text class="book-name">{{ book.bookName }}</text>
          <text class="book-author">{{ book.authors }}</text>
        </view>
        <text class="book-del" @click="onRemoveBook(book)">移除</text>
      </view>
      <view class="empty" v-if="!books.length">书单内还没有书籍</view>
    </template>

    <view class="empty" v-if="!topics.length && !currentTopic.topicId">还没有书单，创建一个吧</view>
  </view>
</template>
<script>
import {
  listPersonalTopic,
  createTopic,
  followTopic,
  unfollowTopic,
  listTopicBook,
  addTopicBook,
  deleteTopicBook
} from '@/api/guji.js'

/**
 * 识典古籍 - 书单（话题）
 * 对应原App H5 topic 页面：我的书单、关注、书单内书籍管理
 */
export default
{
  data()
  {
    return {
      topics: [],
      books: [],
      currentTopic: {},
      topicName: '',
      defaultCover: '/static/logo.png'
    }
  },

  onLoad(options)
  {
    if (options.topicId)
      this.onOpen({ topicId: Number(options.topicId) })
  },

  onShow()
  {
    this.loadTopic()
  },

  methods:
  {
    /**
     * 加载我的书单
     */
    async loadTopic()
    {
      try
      {
        const res = await listPersonalTopic(1, 50)
        this.topics = res.rows || []
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '加载失败', icon: 'none' })
      }
    },

    /**
     * 展开书单内的书籍
     * @param {Object} topic 书单
     */
    async onOpen(topic)
    {
      this.currentTopic = topic
      try
      {
        const res = await listTopicBook(topic.topicId)
        this.books = res.rows || []
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '加载失败', icon: 'none' })
      }
    },

    /**
     * 创建新书单
     */
    async onCreate()
    {
      const name = (this.topicName || '').trim()
      if (!name)
      {
        uni.showToast({ title: '请输入书单名称', icon: 'none' })
        return
      }
      try
      {
        await createTopic({ topicName: name })
        this.topicName = ''
        uni.showToast({ title: '创建成功', icon: 'none' })
        this.loadTopic()
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '创建失败', icon: 'none' })
      }
    },

    /**
     * 关注 / 取消关注
     * @param {Object} topic 书单
     */
    async onFollow(topic)
    {
      try
      {
        if (topic.followed)
          await unfollowTopic(topic.topicId)
        else
          await followTopic(topic.topicId)
        topic.followed = !topic.followed
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '操作失败', icon: 'none' })
      }
    },

    /**
     * 删除书单
     * @param {Object} topic 书单
     */
    async onDelete(topic)
    {
      try
      {
        await deleteTopicBook(topic.topicId, undefined)
        uni.showToast({ title: '已删除', icon: 'none' })
        this.currentTopic = {}
        this.books = []
        this.loadTopic()
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '删除失败', icon: 'none' })
      }
    },

    /**
     * 打开书籍详情
     * @param {Object} book 书籍
     */
    onOpenBook(book)
    {
      uni.navigateTo({ url: `/pages/guji/book/book?bookId=${book.bookId}` })
    },

    /**
     * 从书单移除书籍
     * @param {Object} book 书籍
     */
    async onRemoveBook(book)
    {
      try
      {
        await deleteTopicBook(this.currentTopic.topicId, book.bookId)
        this.onOpen(this.currentTopic)
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '移除失败', icon: 'none' })
      }
    },

    /**
     * 占位：书内加书单入口
     */
    async onAddBook(bookId)
    {
      if (!this.currentTopic.topicId)
        return
      await addTopicBook(this.currentTopic.topicId, bookId)
      this.onOpen(this.currentTopic)
    }
  }
}
</script>
