<style lang="scss" scoped>
.page { display: flex; flex-direction: column; min-height: 100vh; background: #fbf7f0; }
.block { margin: 20rpx 30rpx; padding: 24rpx; background: #ffffff; border-radius: 16rpx; }
.block-title { font-size: 30rpx; font-weight: 600; color: #3a2c20; margin-bottom: 20rpx; }
.slider-row { display: flex; align-items: center; }
.slider { flex: 1; margin: 0 20rpx; }
.slider-value { width: 80rpx; text-align: right; font-size: 26rpx; color: #8c5a3c; }
.label { font-size: 26rpx; color: #6b5844; }
.swatches { display: flex; justify-content: space-between; margin-top: 16rpx; }
.swatch { width: 110rpx; height: 70rpx; border-radius: 12rpx; border: 2rpx solid #e0d3b8; }
.swatch-active { border-color: #8c5a3c; }
.switch-row { display: flex; align-items: center; justify-content: space-between; padding: 16rpx 0; }
.preview { margin: 20rpx 30rpx; padding: 30rpx; border-radius: 16rpx; }
.preview-text { font-size: 32rpx; color: #2f2418; line-height: 56rpx; }
.save-btn { margin: 40rpx 30rpx; padding: 24rpx; text-align: center; font-size: 30rpx; color: #ffffff; background: #8c5a3c; border-radius: 12rpx; }
</style>
<template>
  <view class="page">
    <!-- 字号 -->
    <view class="block">
      <text class="block-title">正文字号</text>
      <view class="slider-row">
        <text class="label">小</text>
        <slider class="slider" :min="24" :max="48" :value="setting.fontSize" show-value="false" @changing="onFontSize" @change="onFontSize" />
        <text class="label">大</text>
        <text class="slider-value">{{ setting.fontSize }}</text>
      </view>
    </view>

    <!-- 行距 -->
    <view class="block">
      <text class="block-title">行距</text>
      <view class="slider-row">
        <text class="label">紧</text>
        <slider class="slider" :min="1.4" :max="2.4" :step="0.1" :value="setting.lineHeight" @changing="onLineHeight" @change="onLineHeight" />
        <text class="label">松</text>
        <text class="slider-value">{{ setting.lineHeight }}</text>
      </view>
    </view>

    <!-- 背景 -->
    <view class="block">
      <text class="block-title">阅读背景</text>
      <view class="swatches">
        <view
          class="swatch"
          :class="{ 'swatch-active': setting.bgColor === item.color }"
          :style="{ background: item.color }"
          v-for="item in backgrounds"
          :key="item.color"
          @click="onPickBg(item)"
        />
      </view>
    </view>

    <!-- 开关项 -->
    <view class="block">
      <view class="switch-row">
        <text class="label">显示译文</text>
        <switch :checked="setting.showTranslate" color="#8c5a3c" @change="onSwitch('showTranslate', $event)" />
      </view>
      <view class="switch-row">
        <text class="label">显示注疏</text>
        <switch :checked="setting.showAnnotation" color="#8c5a3c" @change="onSwitch('showAnnotation', $event)" />
      </view>
      <view class="switch-row">
        <text class="label">繁体正文</text>
        <switch :checked="setting.traditional" color="#8c5a3c" @change="onSwitch('traditional', $event)" />
      </view>
      <view class="switch-row">
        <text class="label">竖排排版</text>
        <switch :checked="setting.vertical" color="#8c5a3c" @change="onSwitch('vertical', $event)" />
      </view>
      <view class="switch-row">
        <text class="label">夜间模式</text>
        <switch :checked="setting.night" color="#8c5a3c" @change="onSwitch('night', $event)" />
      </view>
    </view>

    <!-- 预览 -->
    <view class="preview" :style="{ background: setting.bgColor }">
      <text
        class="preview-text"
        :style="{ fontSize: setting.fontSize + 'rpx', lineHeight: (setting.fontSize * setting.lineHeight) + 'rpx' }"
      >子曰：学而时习之，不亦说乎？</text>
    </view>

    <view class="save-btn" @click="onSave">保存设置</view>
  </view>
</template>
<script>
import { loadReaderSetting, saveReaderSetting } from '@/utils/gujiSetting.js'

/**
 * 识典古籍 - 阅读设置
 * 对应原App H5 readerSetting 页面：字号/行距/背景/简繁/竖排/夜间
 */
export default
{
  data()
  {
    return {
      setting: loadReaderSetting(),
      backgrounds:
      [
        { color: '#f7f1e4' },
        { color: '#ffffff' },
        { color: '#e8f0e3' },
        { color: '#e6eef5' },
        { color: '#2b2620' }
      ]
    }
  },

  onLoad()
  {
    this.setting = loadReaderSetting()
  },

  methods:
  {
    /**
     * 字号滑动
     * @param {Object} e 事件
     */
    onFontSize(e)
    {
      this.setting.fontSize = Math.round(e.detail.value)
    },

    /**
     * 行距滑动
     * @param {Object} e 事件
     */
    onLineHeight(e)
    {
      this.setting.lineHeight = Number(e.detail.value)
    },

    /**
     * 选择背景色
     * @param {Object} item 背景项
     */
    onPickBg(item)
    {
      this.setting.bgColor = item.color
      this.setting.night = item.color === '#2b2620'
    },

    /**
     * 开关变更
     * @param {String} key 字段
     * @param {Object} e 事件
     */
    onSwitch(key, e)
    {
      this.setting[key] = e.detail.value
    },

    /**
     * 保存设置到本地
     */
    onSave()
    {
      saveReaderSetting(this.setting)
      uni.showToast({ title: '已保存', icon: 'none' })
      setTimeout(() => uni.navigateBack(), 500)
    }
  }
}
</script>
