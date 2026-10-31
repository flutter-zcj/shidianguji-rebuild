<style lang="scss" scoped>
.page { display: flex; flex-direction: column; min-height: 100vh; background: #fbf7f0; }
.nav { padding: 24rpx 30rpx; background: #8c5a3c; }
.nav-title { font-size: 34rpx; color: #fff; font-weight: 600; }
.quote-list { flex: 1; padding: 20rpx 30rpx; }
.quote-card { padding: 30rpx; margin-bottom: 20rpx; background: #ffffff; border-radius: 16rpx; }
.quote-text { font-size: 32rpx; color: #3a2c20; line-height: 52rpx; }
.quote-foot { display: flex; align-items: center; justify-content: space-between; margin-top: 20rpx; }
.quote-from { font-size: 24rpx; color: #9a8b7a; }
.quote-action { font-size: 24rpx; color: #8c5a3c; }
.empty { padding: 100rpx; text-align: center; font-size: 26rpx; color: #9a8b7a; }
</style>
<template>
  <view class="page">
    <view class="nav">
      <text class="nav-title">{{ mine ? '我的名句收藏' : '名句' }}</text>
    </view>

    <scroll-view class="quote-list" scroll-y @scrolltolower="onLoadMore">
      <view class="quote-card" v-for="item in list" :key="item.quotationId || item.favoriteId">
        <text class="quote-text">{{ item.famousQuote || item.title }}</text>
        <view class="quote-foot">
          <text class="quote-from">—— {{ item.author }}《{{ item.bookName }}》</text>
          <text class="quote-action" @click="onToggleFavorite(item)">
            {{ item.isFavorite ? '取消收藏' : '收藏' }}
          </text>
        </view>
      </view>
      <view class="empty" v-if="!list.length">暂无名句</view>
    </scroll-view>
  </view>
</template>
<script>
import { listQuotation, recommendQuotation, addFavorite, delFavorite, listFavorite } from '@/api/guji.js'

/**
 * 识典古籍 - 名句
 * 对应原App Lynx quotationCollect/quotationBook 页面
 */
export default
{
  data()
  {
    return {
      list: [],
      mine: false,
      nextPageToken: 0,
      pageSize: 20
    }
  },

  onLoad(options)
  {
    this.mine = options.mine === '1'
  },

  onShow()
  {
    this.nextPageToken = 0
    this.list = []
    this.loadData()
  },

  methods:
  {
    /**
     * 加载名句数据
     */
    async loadData()
    {
      try
      {
        const res = this.mine
          ? await listFavorite('quotation', this.pageSize, this.nextPageToken)
          : await recommendQuotation(this.pageSize, this.nextPageToken)
        const rows = res.rows || []
        this.list = this.nextPageToken ? this.list.concat(rows) : rows
        if (res.nextPageToken)
          this.nextPageToken = Number(res.nextPageToken)
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '加载失败', icon: 'none' })
      }
    },

    /**
     * 加载更多
     */
    onLoadMore()
    {
      this.loadData()
    },

    /**
     * 收藏/取消收藏
     * @param {Object} item 名句对象
     */
    async onToggleFavorite(item)
    {
      const bizId = String(item.quotationId || item.bizId || '')
      try
      {
        if (item.isFavorite)
          await delFavorite(bizId)
        else
          await addFavorite(bizId)
        this.$set(item, 'isFavorite', item.isFavorite ? 0 : 1)
        uni.showToast({ title: item.isFavorite ? '已收藏' : '已取消收藏', icon: 'none' })
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '操作失败', icon: 'none' })
      }
    }
  }
}
</script>
