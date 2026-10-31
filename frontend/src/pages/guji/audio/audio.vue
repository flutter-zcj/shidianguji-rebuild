<style lang="scss" scoped>
.page { display: flex; flex-direction: column; min-height: 100vh; background: #fbf7f0; }
.tabs { display: flex; padding: 20rpx 30rpx; background: #8c5a3c; }
.tab { flex: 1; text-align: center; padding: 12rpx 0; font-size: 28rpx; color: #f0e2d0; }
.tab-active { color: #ffffff; font-weight: 600; }
.audio { display: flex; align-items: center; padding: 24rpx 30rpx; background: #ffffff; border-bottom: 1rpx solid #f2ece2; }
.audio-cover { width: 110rpx; height: 110rpx; border-radius: 12rpx; background: #e8dcc8; }
.audio-info { flex: 1; margin-left: 20rpx; }
.audio-title { font-size: 28rpx; color: #3a2c20; }
.audio-sub { margin-top: 8rpx; font-size: 22rpx; color: #9a8b7a; }
.audio-play { font-size: 26rpx; color: #8c5a3c; }
.player { position: fixed; left: 0; right: 0; bottom: 0; padding: 24rpx 30rpx; background: #efe6d2; }
.player-title { font-size: 28rpx; color: #3a2c20; font-weight: 600; }
.player-ctrl { margin-top: 12rpx; display: flex; justify-content: space-between; }
.ctrl-btn { font-size: 26rpx; color: #8c5a3c; }
.lyric { margin-top: 12rpx; font-size: 24rpx; color: #6b5844; }
.empty { padding: 80rpx; text-align: center; font-size: 26rpx; color: #9a8b7a; }
</style>
<template>
  <view class="page">
    <view class="tabs">
      <view class="tab" :class="{ 'tab-active': tab === 'listen' }" @click="onSwitch('listen')">听书</view>
      <view class="tab" :class="{ 'tab-active': tab === 'podcast' }" @click="onSwitch('podcast')">播客</view>
    </view>

    <view class="audio" v-for="item in list" :key="item.audioId || item.bookId">
      <image class="audio-cover" :src="item.coverUrl || defaultCover" mode="aspectFill" />
      <view class="audio-info" @click="onOpenBook(item)">
        <text class="audio-title">{{ item.audioTitle || item.bookName || item.title }}</text>
        <text class="audio-sub">{{ item.speaker || item.generalAuthor || item.author || '识典古籍' }}</text>
      </view>
      <text class="audio-play" @click="onPlay(item)">播放</text>
    </view>

    <view class="empty" v-if="!list.length">暂无音频内容</view>

    <!-- 播放器 -->
    <view class="player" v-if="current.audioId">
      <text class="player-title">{{ current.audioTitle || current.title || current.bookName }}</text>
      <view class="player-ctrl">
        <text class="ctrl-btn" @click="onToggle">{{ playing ? '暂停' : '播放' }}</text>
        <text class="ctrl-btn" @click="onStop">停止</text>
        <text class="ctrl-btn" @click="onLoadLyric">歌词</text>
      </view>
      <text class="lyric" v-if="lyric">{{ lyric }}</text>
    </view>
  </view>
</template>
<script>
import { listListeningBook, listPodcast, getBookAudio, getAudioLyric } from '@/api/guji.js'

/**
 * 识典古籍 - 听书
 * 对应原App Lynx audio 页面：听书列表 / 播客列表 / 音频播放与歌词
 */
export default
{
  data()
  {
    return {
      tab: 'listen',
      list: [],
      current: {},
      lyric: '',
      playing: false,
      audioCtx: null,
      defaultCover: '/static/logo.png'
    }
  },

  onShow()
  {
    this.loadData()
  },

  onUnload()
  {
    this.onStop()
  },

  methods:
  {
    /**
     * 切换 Tab
     * @param {String} tab 标签
     */
    onSwitch(tab)
    {
      this.tab = tab
      this.loadData()
    },

    /**
     * 加载听书/播客列表
     */
    async loadData()
    {
      try
      {
        const res = this.tab === 'listen' ? await listListeningBook(1, 30) : await listPodcast(1, 30)
        this.list = res.rows || []
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '加载失败', icon: 'none' })
      }
    },

    /**
     * 打开书籍详情
     * @param {Object} item 音频项
     */
    onOpenBook(item)
    {
      if (!item.bookId)
        return
      uni.navigateTo({ url: `/pages/guji/book/book?bookId=${item.bookId}` })
    },

    /**
     * 播放音频：无音频地址时按书籍拉取
     * @param {Object} item 音频项
     */
    async onPlay(item)
    {
      try
      {
        let audio = item
        if (!item.uri && !item.audioUrl && item.bookId)
        {
          const res = await getBookAudio(item.bookId)
          const rows = res.rows || res.audioList || []
          audio = rows.length ? rows[0] : item
        }
        this.current = { ...audio, audioId: audio.audioId || audio.bookId }
        this.play(audio.audioUrl || audio.uri)
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '获取音频失败', icon: 'none' })
      }
    },

    /**
     * 播放指定地址
     * @param {String} url 音频地址
     */
    play(url)
    {
      if (!url)
      {
        uni.showToast({ title: '音频地址为空', icon: 'none' })
        return
      }
      if (!this.audioCtx)
        this.audioCtx = uni.createInnerAudioContext()
      this.audioCtx.src = url
      this.audioCtx.play()
      this.playing = true
    },

    /**
     * 播放/暂停切换
     */
    onToggle()
    {
      if (!this.audioCtx)
        return
      if (this.playing)
        this.audioCtx.pause()
      else
        this.audioCtx.play()
      this.playing = !this.playing
    },

    /**
     * 停止播放
     */
    onStop()
    {
      if (this.audioCtx)
      {
        this.audioCtx.stop()
        this.audioCtx.destroy()
        this.audioCtx = null
      }
      this.playing = false
    },

    /**
     * 加载当前音频歌词
     */
    async onLoadLyric()
    {
      try
      {
        const res = await getAudioLyric(this.current.audioId)
        this.lyric = res.lyric || res.content || '暂无歌词'
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '歌词加载失败', icon: 'none' })
      }
    }
  }
}
</script>
