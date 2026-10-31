<style lang="scss" scoped>
.reader-page { display: flex; flex-direction: column; min-height: 100vh; background: #FBF8F2; }
.reader-header { display: flex; align-items: center; justify-content: space-between; padding: 20rpx 32rpx; background: #F5EFE6; font-size: 28rpx; color: #666666; }
.reader-nav-btn { display: flex; align-items: center; justify-content: center; height: 64rpx; padding: 0 24rpx; background: #FFFFFF; font-size: 26rpx; color: #8B5E3C; border-radius: 12rpx; }
.reader-nav-btn--disabled { color: #BBBBBB; }
.reader-body { display: flex; flex-direction: column; padding: 32rpx; gap: 24rpx; }
.paragraph-block { display: flex; flex-direction: column; }
.paragraph-text { font-size: 34rpx; color: #3D3A34; line-height: 1.9; letter-spacing: 2rpx; }
.paragraph-seq { font-size: 24rpx; color: #BBBBBB; margin-bottom: 8rpx; }
.load-tip { display: flex; align-items: center; justify-content: center; height: 100rpx; font-size: 26rpx; color: #999999; }
</style>
<template>
  <!-- 🚀 页面主体 -->
  <view class="reader-page">
    <!-- 🚀 阅读器导航条 -->
    <view class="reader-header">
      <view class="reader-nav-btn"
            :class="{ 'reader-nav-btn--disabled': !hasPrev }"
            @click="handlePrevChapter">
        上一章
      </view>
      <text>{{ chapterName }}</text>
      <view class="reader-nav-btn"
            :class="{ 'reader-nav-btn--disabled': !hasNext }"
            @click="handleNextChapter">
        下一章
      </view>
    </view>
    <!-- 🚀 段落内容 -->
    <view class="reader-body">
      <view v-for="item in paragraphs" :key="item.paragraphId" class="paragraph-block" @click="handleReportProgress(item)">
        <view class="paragraph-seq">第 {{ item.paraSeq }} 段</view>
        <view class="paragraph-text">{{ item.paraText }}</view>
      </view>
      <view class="load-tip" v-if="hasMore" @click="handleLoadMore">
        <text v-if="loading">加载中...</text>
        <text v-else>加载更多</text>
      </view>
      <view class="load-tip" v-if="!hasMore && paragraphs.length > 0">— 本章完 —</view>
      <view class="load-tip" v-if="paragraphs.length === 0 && !loading">暂无内容</view>
    </view>
  </view>
</template>
<script>
/**
 * 组件名称：reader
 * 功能说明：古籍阅读器页面，按章节分页展示段落文本，支持上下章切换、加载更多与阅读进度上报
 * 研发时间：2026/10/31
 * 研发人员：Doubao
 *
 * 变量说明：
 * @data {Number}  bookId       - 书目ID
 * @data {Number}  chapterId    - 当前章节ID
 * @data {Number}  paragraphId  - 目标段落ID（用于定位）
 * @data {Array}   chapterList  - 全书章节列表
 * @data {Number}  chapterIndex - 当前章节在列表中的索引
 * @data {String}  chapterName  - 当前章节名
 * @data {Array}   paragraphs   - 段落列表
 * @data {Number}  pageNum      - 当前段落页码
 * @data {Number}  pageSize     - 每页段落条数
 * @data {Boolean} hasMore      - 是否还有更多段落
 * @data {Boolean} loading      - 是否加载中
 * @data {Number}  lastReportId - 最近上报的段落ID
 *
 * 事件说明：
 * @event onLoad          - 页面加载后初始化阅读器
 * @event onReachBottom   - 触底加载更多段落
 * @event onUnload        - 页面卸载时上报最后阅读进度
 * @event handlePrevChapter - 切换上一章
 * @event handleNextChapter - 切换下一章
 * @event handleLoadMore  - 加载更多段落
 * @event handleReportProgress - 上报阅读进度
 * @event loadChapterList - 拉取全书章节列表
 * @event loadParagraphs  - 拉取当前章节段落
 *
 * 插槽说明：
 */
/**
 * 修改时间       人员        说明
 */

import { getChapters, getParagraphs, addHistory } from '../../utils/gujiApi'

export default
{
  data()
  {
    return {
      bookId: 0,
      chapterId: 0,
      paragraphId: 0,
      chapterList: [],
      chapterIndex: -1,
      chapterName: '',
      paragraphs: [],
      pageNum: 1,
      pageSize: 20,
      hasMore: true,
      loading: false,
      lastReportId: 0,
    }
  },

  computed:
  {
    hasPrev()
    {
      return this.chapterIndex > 0
    },
    hasNext()
    {
      return this.chapterIndex >= 0 && this.chapterIndex < this.chapterList.length - 1
    },
  },

  onLoad(query)
  {
    /**
     * 页面加载后初始化阅读器
     * @param {Object} query - 页面参数（bookId/chapterId/paragraphId）
     */
    this.bookId = Number(query.bookId)
    this.chapterId = Number(query.chapterId || 0)
    this.paragraphId = Number(query.paragraphId || 0)
    this.loadChapterList()
  },

  onReachBottom()
  {
    /**
     * 触底加载更多段落
     */
    if (this.hasMore && !this.loading)
    {
      this.loadParagraphs(false)
    }
  },

  onUnload()
  {
    /**
     * 页面卸载时上报最后阅读进度
     */
    if (this.lastReportId)
    {
      addHistory({
        bookId: this.bookId,
        chapterId: this.chapterId,
        paragraphId: this.lastReportId,
      }).catch(() =>
      {
      })
    }
  },

  methods:
  {
    /**
     * 切换上一章
     */
    handlePrevChapter()
    {
      if (!this.hasPrev)
      {
        return
      }
      this.switchChapter(this.chapterIndex - 1)
    },

    /**
     * 切换下一章
     */
    handleNextChapter()
    {
      if (!this.hasNext)
      {
        return
      }
      this.switchChapter(this.chapterIndex + 1)
    },

    /**
     * 加载更多段落
     */
    handleLoadMore()
    {
      this.loadParagraphs(false)
    },

    /**
     * 上报阅读进度
     * @param {Object} item - 段落对象
     */
    handleReportProgress(item)
    {
      this.lastReportId = item.paragraphId
      addHistory({
        bookId: this.bookId,
        chapterId: this.chapterId,
        paragraphId: item.paragraphId,
      }).catch(() =>
      {
      })
    },

    /**
     * 拉取全书章节列表
     */
    loadChapterList()
    {
      getChapters(this.bookId)
        .then((res) =>
        {
          if (res.code === 200)
          {
            this.chapterList = res.data
            if (this.chapterList.length > 0)
            {
              if (!this.chapterId)
              {
                this.chapterId = this.chapterList[0].chapterId
              }
              const index = this.chapterList.findIndex((item) => item.chapterId === this.chapterId)
              this.chapterIndex = index >= 0 ? index : 0
              if (index < 0)
              {
                this.chapterId = this.chapterList[0].chapterId
              }
              this.chapterName = this.chapterList[this.chapterIndex].chapterName
              uni.setNavigationBarTitle({ title: this.chapterName })
            }
          }
        })
        .catch(() => uni.showToast({ title: '章节加载失败', icon: 'none' }))
        .finally(() =>
        {
          if (this.chapterId)
          {
            this.loadParagraphs(true)
          }
        })
    },

    /**
     * 拉取当前章节段落
     * @param {Boolean} reset - 是否重置分页
     */
    loadParagraphs(reset)
    {
      if (reset)
      {
        this.pageNum = 1
        this.paragraphs = []
        this.hasMore = true
      }
      this.loading = true
      getParagraphs(this.chapterId, this.pageNum, this.pageSize)
        .then((res) =>
        {
          if (res.code === 200)
          {
            const rows = res.data.rows
            this.paragraphs = reset ? rows : this.paragraphs.concat(rows)
            this.hasMore = res.data.hasNext
            this.pageNum += 1
            this.locateParagraph()
          }
        })
        .catch(() => uni.showToast({ title: '段落加载失败', icon: 'none' }))
        .finally(() =>
        {
          this.loading = false
        })
    },

    /**
     * 定位目标段落：若目标段落不在当前已加载数据中且还有下一页，继续加载
     */
    locateParagraph()
    {
      if (!this.paragraphId || this.paragraphs.some((item) => item.paragraphId === this.paragraphId))
      {
        this.paragraphId = 0
        return
      }
      if (this.hasMore && this.pageNum <= 10)
      {
        this.loadParagraphs(false)
      }
      else
      {
        this.paragraphId = 0
      }
    },

    /**
     * 切换章节
     * @param {Number} index - 目标章节索引
     */
    switchChapter(index)
    {
      if (index < 0 || index >= this.chapterList.length)
      {
        return
      }
      this.chapterIndex = index
      this.chapterId = this.chapterList[index].chapterId
      this.chapterName = this.chapterList[index].chapterName
      this.paragraphId = 0
      this.lastReportId = 0
      uni.setNavigationBarTitle({ title: this.chapterName })
      this.loadParagraphs(true)
    },
  },
}
</script>
