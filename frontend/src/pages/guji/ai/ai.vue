<style lang="scss" scoped>
.page { display: flex; flex-direction: column; min-height: 100vh; background: #fbf7f0; }
.nav { padding: 24rpx 30rpx; background: #8c5a3c; }
.nav-title { font-size: 34rpx; color: #fff; font-weight: 600; }
.chat-area { flex: 1; padding: 24rpx 30rpx; }
.msg { margin-bottom: 28rpx; }
.msg-user { display: flex; justify-content: flex-end; }
.msg-ai { display: flex; justify-content: flex-start; }
.bubble-user { max-width: 76%; padding: 20rpx 24rpx; background: #8c5a3c; color: #fff; border-radius: 16rpx; font-size: 28rpx; }
.bubble-ai { max-width: 84%; padding: 20rpx 24rpx; background: #ffffff; color: #3a2c20; border-radius: 16rpx; font-size: 28rpx; line-height: 46rpx; }
.input-bar { display: flex; align-items: center; padding: 20rpx 30rpx; background: #ffffff; }
.input { flex: 1; height: 72rpx; padding: 0 20rpx; background: #f7f1e4; border-radius: 36rpx; font-size: 28rpx; }
.send { margin-left: 20rpx; font-size: 28rpx; color: #8c5a3c; }
.tip { padding: 16rpx 30rpx; font-size: 22rpx; color: #9a8b7a; }
</style>
<template>
  <view class="page">
    <view class="nav">
      <text class="nav-title">古籍智能助手</text>
    </view>

    <scroll-view class="chat-area" scroll-y :scroll-top="scrollTop">
      <view class="msg msg-ai" v-if="!messages.length">
        <view class="bubble-ai">可以问我：这句话出自哪部典籍？某句话是什么意思？某位作者的生平？</view>
      </view>
      <view v-for="(msg, index) in messages" :key="index">
        <view class="msg msg-user" v-if="msg.role === 'user'">
          <view class="bubble-user">{{ msg.content }}</view>
        </view>
        <view class="msg msg-ai" v-else>
          <view class="bubble-ai">{{ msg.content }}</view>
        </view>
      </view>
    </scroll-view>

    <view class="tip">回答由AI基于古籍库内容生成，仅供参考</view>
    <view class="input-bar">
      <input class="input" v-model="question" placeholder="输入你的问题…" confirm-type="send" @confirm="onSend" />
      <text class="send" @click="onSend">发送</text>
    </view>
  </view>
</template>
<script>
import { assistantChat } from '@/api/guji.js'

/**
 * 识典古籍 - 古籍智能助手
 * 对应原App H5 ai 页面
 */
export default
{
  data()
  {
    return {
      bookId: '',
      question: '',
      messages: [],
      scrollTop: 0
    }
  },

  onLoad(options)
  {
    this.bookId = options.bookId || ''
  },

  methods:
  {
    /**
     * 发送提问
     */
    async onSend()
    {
      const text = this.question.trim()
      if (!text)
        return
      this.messages.push({ role: 'user', content: text })
      this.question = ''
      this.scrollToBottom()
      try
      {
        const res = await assistantChat(text, this.bookId ? Number(this.bookId) : undefined)
        this.messages.push({ role: 'assistant', content: res.answer || '暂未找到相关内容' })
      }
      catch (err)
      {
        this.messages.push({ role: 'assistant', content: err.message || '请求失败，请稍后再试' })
      }
      this.scrollToBottom()
    },

    /**
     * 滚动到底部
     */
    scrollToBottom()
    {
      this.scrollTop = this.messages.length * 1000
    }
  }
}
</script>
