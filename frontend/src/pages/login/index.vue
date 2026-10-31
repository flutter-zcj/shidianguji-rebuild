<style lang="scss" scoped>
.login-page { display: flex; flex-direction: column; justify-content: center; min-height: 100vh; padding: 0 56rpx; background: #F8F6F1; }
.login-title { font-size: 48rpx; color: #333333; font-weight: 600; text-align: center; margin-bottom: 24rpx; }
.login-sub { font-size: 26rpx; color: #999999; text-align: center; margin-bottom: 64rpx; }
.form-item { display: flex; align-items: center; height: 96rpx; padding: 0 28rpx; margin-bottom: 28rpx; background: #FFFFFF; border: 1rpx solid #DDD5C6; border-radius: 16rpx; }
.form-input { display: flex; flex: 1; height: 96rpx; font-size: 30rpx; color: #333333; }
.login-btn { display: flex; align-items: center; justify-content: center; height: 96rpx; margin-top: 40rpx; background: #8B5E3C; font-size: 32rpx; color: #FFFFFF; border-radius: 16rpx; }
.login-tip { font-size: 24rpx; color: #BBBBBB; text-align: center; margin-top: 32rpx; }
</style>
<template>
  <!-- 🚀 页面主体 -->
  <view class="login-page">
    <!-- 🚀 标题区 -->
    <view class="login-title">识典古籍</view>
    <view class="login-sub">登录后同步书架与阅读进度</view>
    <!-- 🚀 表单区 -->
    <view class="form-item">
      <input class="form-input" v-model="username" placeholder="请输入用户名" />
    </view>
    <view class="form-item">
      <input class="form-input" v-model="password" password placeholder="请输入密码" @confirm="handleLogin" />
    </view>
    <!-- 🚀 登录按钮 -->
    <view class="login-btn" @click="handleLogin">登 录</view>
    <view class="login-tip">测试账号：admin / admin123</view>
  </view>
</template>
<script>
/**
 * 组件名称：login
 * 功能说明：登录页面，调用后端登录接口换取 JWT 并缓存 token
 * 研发时间：2026/10/31
 * 研发人员：Doubao
 *
 * 变量说明：
 * @data {String} username - 用户名
 * @data {String} password - 密码
 * @data {Boolean} loading - 是否提交中
 *
 * 事件说明：
 * @event handleLogin - 提交登录
 *
 * 插槽说明：
 */
/**
 * 修改时间       人员        说明
 */

import { login } from '../../utils/gujiApi'

export default
{
  data()
  {
    return {
      username: '',
      password: '',
      loading: false,
    }
  },

  methods:
  {
    /**
     * 提交登录
     */
    handleLogin()
    {
      if (!this.username || !this.password)
      {
        uni.showToast({ title: '请输入用户名和密码', icon: 'none' })
        return
      }
      if (this.loading)
      {
        return
      }
      this.loading = true
      login(this.username, this.password)
        .then((res) =>
        {
          if (res.code === 200 && res.token)
          {
            uni.setStorageSync('guji_token', res.token)
            uni.showToast({ title: '登录成功', icon: 'success' })
            setTimeout(() => uni.navigateBack(), 600)
          }
          else
          {
            uni.showToast({ title: res.msg || '登录失败', icon: 'none' })
          }
        })
        .catch(() => uni.showToast({ title: '网络异常，请稍后重试', icon: 'none' }))
        .finally(() =>
        {
          this.loading = false
        })
    },
  },
}
</script>
