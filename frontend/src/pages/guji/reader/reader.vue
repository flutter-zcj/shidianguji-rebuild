<style lang="scss" scoped>
.page { display: flex; flex-direction: column; min-height: 100vh; background: #f7f1e4; }
.top-bar { display: flex; align-items: center; justify-content: space-between; padding: 20rpx 30rpx; background: #efe6d2; }
.chapter-name { font-size: 30rpx; color: #3a2c20; font-weight: 600; }
.top-actions { display: flex; }
.top-btn { margin-left: 24rpx; font-size: 26rpx; color: #8c5a3c; }
.content { flex: 1; padding: 30rpx 40rpx; }
.para { margin-bottom: 36rpx; }
.para-origin { font-size: 32rpx; color: #2f2418; line-height: 56rpx; }
.para-trans { margin-top: 16rpx; font-size: 28rpx; color: #6b5844; line-height: 50rpx; }
.para-note { margin-top: 12rpx; padding-left: 16rpx; font-size: 24rpx; color: #9a8b7a; border-left: 4rpx solid #e0d3b8; }
.bottom-bar { display: flex; justify-content: space-around; padding: 20rpx 0; background: #efe6d2; }
.bottom-btn { font-size: 26rpx; color: #6b5844; }
.mask { position: fixed; left: 0; right: 0; top: 0; bottom: 0; background: rgba(0, 0, 0, 0.4); }
.drawer { position: fixed; left: 0; right: 0; bottom: 0; max-height: 60vh; padding: 30rpx; background: #fff; border-radius: 24rpx 24rpx 0 0; }
.drawer-title { font-size: 30rpx; font-weight: 600; color: #3a2c20; margin-bottom: 20rpx; }
.drawer-item { padding: 22rpx 0; font-size: 28rpx; color: #3a2c20; border-bottom: 1rpx solid #f2ece2; }
.drawer-item-active { color: #8c5a3c; font-weight: 600; }
.note-input { width: 100%; height: 160rpx; padding: 16rpx; background: #f7f1e4; border-radius: 12rpx; font-size: 28rpx; }
.empty { padding: 80rpx; text-align: center; font-size: 26rpx; color: #9a8b7a; }
</style>
<template>
  <view class="page" :style="{ background: bgColor }">
    <view class="top-bar">
      <text class="chapter-name">{{ currentChapter.chapterName || '正文' }}</text>
      <view class="top-actions">
        <text class="top-btn" @click="onToggleTranslate">{{ showTranslate ? '隐藏译文' : '显示译文' }}</text>
        <text class="top-btn" @click="onOpenCatalog">目录</text>
        <text class="top-btn" @click="onGoSetting">设置</text>
      </view>
    </view>

    <scroll-view class="content" scroll-y>
      <view class="para" v-for="para in paragraphs" :key="para.paragraphId" @longpress="onLongPress(para)">
        <text
          class="para-origin"
          :style="{ fontSize: fontSize + 'rpx', lineHeight: (fontSize * lineHeight) + 'rpx' }"
        >{{ para.content }}</text>
        <text class="para-trans" v-if="showTranslate && para.translation">{{ para.translation }}</text>
        <text class="para-note" v-if="showAnnotation && para.annotation">{{ para.annotation }}</text>
      </view>
      <view class="empty" v-if="!paragraphs.length">本章暂无正文</view>
    </scroll-view>

    <view class="bottom-bar">
      <text class="bottom-btn" @click="onAddBookmark">书签</text>
      <text class="bottom-btn" @click="showNote = true">笔记</text>
      <text class="bottom-btn" @click="onGoAi">问AI</text>
      <text class="bottom-btn" @click="onMarkFinish">标记读完</text>
    </view>

    <!-- 目录抽屉 -->
    <view class="mask" v-if="showCatalog" @click="showCatalog = false" />
    <view class="drawer" v-if="showCatalog">
      <text class="drawer-title">目录</text>
      <scroll-view scroll-y style="max-height: 46vh;">
        <view
          class="drawer-item"
          :class="{ 'drawer-item-active': chapter.chapterId === chapterId }"
          v-for="chapter in chapters"
          :key="chapter.chapterId"
          @click="onSelectChapter(chapter)"
        >
          {{ chapter.chapterName }}
        </view>
      </scroll-view>
    </view>

    <!-- 笔记输入 -->
    <view class="mask" v-if="showNote" @click="showNote = false" />
    <view class="drawer" v-if="showNote">
      <text class="drawer-title">写笔记</text>
      <textarea class="note-input" v-model="noteContent" placeholder="记下你的理解…" />
      <view class="drawer-item" style="color:#8c5a3c;" @click="onSubmitNote">保存笔记</view>
    </view>
  </view>
</template>
<script>
import {
  getBookDetail,
  getBookParagraphs,
  reportHistory,
  addBookmark,
  addReview
} from '@/api/guji.js'
import { loadReaderSetting } from '@/utils/gujiSetting.js'

/**
 * 识典古籍 - 阅读器
 * 对应原App H5 read 页面：原文/译文/注疏同段下发，位标记控制显示
 */
export default
{
  data()
  {
    return {
      bookId: '',
      chapterId: '',
      chapters: [],
      paragraphs: [],
      currentChapter: {},
      showTranslate: true,
      showAnnotation: true,
      showCatalog: false,
      showNote: false,
      noteContent: '',
      fontSize: 32,
      lineHeight: 1.8,
      bgColor: '#f7f1e4',
      pageIndex: 1
    }
  },

  onLoad(options)
  {
    this.bookId = options.bookId || ''
    this.chapterId = options.chapterId || ''
    this.loadCatalog()
  },

  onShow()
  {
    // 每次进入阅读器同步本地阅读设置
    const setting = loadReaderSetting()
    this.fontSize = setting.fontSize
    this.lineHeight = setting.lineHeight
    this.bgColor = setting.bgColor
    this.showTranslate = setting.showTranslate
    this.showAnnotation = setting.showAnnotation
  },

  onUnload()
  {
    this.reportProgress()
  },

  methods:
  {
    /**
     * 加载目录与正文
     */
    async loadCatalog()
    {
      try
      {
        const detail = await getBookDetail(this.bookId, 1)
        this.chapters = detail.chapters || []
        if (!this.chapterId && this.chapters.length)
          this.chapterId = String(this.chapters[0].chapterId)
        this.currentChapter = this.chapters.find((item) => String(item.chapterId) === String(this.chapterId)) || {}
        await this.loadParagraphs()
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '加载失败', icon: 'none' })
      }
    },

    /**
     * 加载章节正文
     */
    async loadParagraphs()
    {
      try
      {
        const res = await getBookParagraphs({
          bookId: Number(this.bookId),
          chapterId: Number(this.chapterId),
          pageIndex: this.pageIndex,
          pageSize: 50
        })
        this.paragraphs = res.paragraphs || []
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '正文加载失败', icon: 'none' })
      }
    },

    /**
     * 切换章节
     * @param {Object} chapter 章节对象
     */
    onSelectChapter(chapter)
    {
      this.chapterId = String(chapter.chapterId)
      this.currentChapter = chapter
      this.showCatalog = false
      this.loadParagraphs()
      this.reportProgress()
    },

    /**
     * 打开目录
     */
    onOpenCatalog()
    {
      this.showCatalog = true
    },

    /**
     * 切换译文显示
     */
    onToggleTranslate()
    {
      this.showTranslate = !this.showTranslate
    },

    /**
     * 长按段落：加入书签
     * @param {Object} para 段落对象
     */
    async onLongPress(para)
    {
      try
      {
        await addBookmark({
          bookId: Number(this.bookId),
          chapterId: Number(this.chapterId),
          chapterName: this.currentChapter.chapterName,
          markedText: para.content,
          bookmarkStyle: 'underline',
          colorStyle: 'yellow'
        })
        uni.showToast({ title: '已添加书签', icon: 'none' })
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '操作失败', icon: 'none' })
      }
    },

    /**
     * 加入书签（首段）
     */
    onAddBookmark()
    {
      if (!this.paragraphs.length)
        return
      this.onLongPress(this.paragraphs[0])
    },

    /**
     * 提交笔记
     */
    async onSubmitNote()
    {
      if (!this.noteContent.trim())
      {
        uni.showToast({ title: '请输入笔记内容', icon: 'none' })
        return
      }
      try
      {
        await addReview({
          bookId: Number(this.bookId),
          chapterId: Number(this.chapterId),
          chapterName: this.currentChapter.chapterName,
          content: this.noteContent,
          markedText: this.paragraphs.length ? this.paragraphs[0].content : ''
        })
        this.noteContent = ''
        this.showNote = false
        uni.showToast({ title: '笔记已保存' })
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '保存失败', icon: 'none' })
      }
    },

    /**
     * 上报阅读进度
     */
    async reportProgress()
    {
      if (!this.bookId)
        return
      const percent = this.chapters.length
        ? Math.round(((this.chapters.findIndex((c) => String(c.chapterId) === String(this.chapterId)) + 1) / this.chapters.length) * 100)
        : 0
      try
      {
        await reportHistory({
          bookId: String(this.bookId),
          chapterId: String(this.chapterId),
          chapterName: this.currentChapter.chapterName,
          progress: `${percent}%`,
          lastContent: this.paragraphs.length ? this.paragraphs[0].content : ''
        })
      }
      catch (err)
      {
        // 进度上报失败不打断阅读
      }
    },

    /**
     * 标记读完
     */
    async onMarkFinish()
    {
      await this.reportProgress()
      uni.showToast({ title: '本篇已读完', icon: 'none' })
    },

    /**
     * 打开阅读设置
     */
    onGoSetting()
    {
      uni.navigateTo({ url: '/pages/guji/settings/settings' })
    },

    /**
     * 打开AI助手
     */
    onGoAi()
    {
      uni.navigateTo({ url: `/pages/guji/ai/ai?bookId=${this.bookId}` })
    }
  }
}
</script>
