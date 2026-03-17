<template>
  <section class="login-page">
    <div class="login-shell">
      <section class="hero-panel">
        <div class="brand-chip">
          <span class="brand-dot"></span>
          <span>灵感画廊</span>
        </div>

        <div class="hero-copy">
          <p class="eyebrow">Moderation Console</p>
          <h1 class="hero-title">管理员审核大厅作品、评论和用户列表。</h1>
          <p class="hero-desc">
            当前管理端只使用文档里已有的管理员接口，不额外扩展越界操作。
          </p>
        </div>

        <div class="credential-card">
          <span class="credential-label">默认管理员账号</span>
          <code>admin1433223</code>
          <span class="credential-sep">/</span>
          <code>admin1433223</code>
        </div>
      </section>

      <section class="form-panel">
        <div class="login-card">
          <div class="card-head">
            <p class="card-kicker">管理员登录</p>
            <h2 class="card-title">进入管理端</h2>
            <p class="card-desc">仅管理员账号可进入，普通用户会被拦截。</p>
          </div>

          <form class="auth-form" @submit.prevent="onLogin">
            <label class="field-label" for="account-code">账号编号</label>
            <input
              id="account-code"
              v-model.trim="form.accountCode"
              class="text-input"
              type="text"
              placeholder="请输入管理员账号编号"
              required
            />

            <label class="field-label" for="password">密码</label>
            <input
              id="password"
              v-model="form.password"
              class="text-input"
              type="password"
              placeholder="请输入密码"
              required
            />

            <button type="submit" class="primary-btn" :disabled="submitting">
              {{ submitting ? '登录中...' : '进入后台' }}
            </button>
          </form>

          <p v-if="message" class="message-text" :class="{ error: hasError, ok: !hasError }">
            {{ message }}
          </p>
        </div>
      </section>
    </div>
  </section>
</template>

<script>
import { login } from '../api/auth'
import { setAdminSession } from '../utils/auth'

const ADMIN_ACCOUNT_CODE = 'admin1433223'

export default {
  name: 'AdminLoginView',
  data() {
    return {
      form: {
        accountCode: '',
        password: ''
      },
      message: '',
      hasError: false,
      submitting: false,
      autoSubmitted: false
    }
  },
  mounted() {
    const query = this.$route.query || {}
    const accountCode = typeof query.account_code === 'string' ? query.account_code : ''
    const password = typeof query.password === 'string' ? query.password : ''
    const auto = query.auto === '1'

    if (accountCode) this.form.accountCode = accountCode
    if (password) this.form.password = password

    if (auto && accountCode && password && !this.autoSubmitted) {
      this.autoSubmitted = true
      this.onLogin()
    }
  },
  methods: {
    validateForm() {
      const accountCode = (this.form.accountCode || '').trim().toLowerCase()
      const password = this.form.password || ''

      if (!accountCode || !password) return '账号编号和密码不能为空'
      if (accountCode !== ADMIN_ACCOUNT_CODE) return '当前只允许默认管理员账号进入管理端'

      this.form.accountCode = accountCode
      return ''
    },
    async onLogin() {
      if (this.submitting) return

      const validationError = this.validateForm()
      if (validationError) {
        this.message = validationError
        this.hasError = true
        return
      }

      this.submitting = true
      this.message = ''
      this.hasError = false

      try {
        const res = await login({
          account_code: this.form.accountCode,
          password: this.form.password
        })
        const data = (res && res.data && res.data.data) || {}
        const user = data.user || null
        if (!user || user.role !== 'admin') {
          throw new Error('当前账号没有管理员权限')
        }

        setAdminSession(data.token, user)
        this.message = '登录成功，正在进入管理端...'
        this.$router.replace('/artworks')
      } catch (error) {
        this.hasError = true
        this.message =
          (error && error.response && error.response.data && error.response.data.message) ||
          error.message ||
          '登录失败'
      } finally {
        this.submitting = false
      }
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100%;
  display: grid;
  place-items: center;
  padding: 28px;
  overflow-y: auto;
  background:
    radial-gradient(circle at 16% 18%, rgba(224, 235, 224, 0.92), transparent 38%),
    radial-gradient(circle at 88% 12%, rgba(255, 216, 223, 0.42), transparent 22%),
    linear-gradient(180deg, #f5f6f1 0%, #eef2eb 100%);
}

.login-shell {
  width: min(1100px, 100%);
  min-height: min(720px, calc(100vh - 56px));
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  border: 1px solid #dde4da;
  border-radius: 28px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.84);
  box-shadow: 0 28px 80px rgba(35, 44, 37, 0.08);
}

.hero-panel {
  padding: 38px 36px 32px;
  background:
    radial-gradient(circle at top left, rgba(255, 255, 255, 0.9), transparent 34%),
    linear-gradient(160deg, #e8efe4 0%, #f6f8f3 52%, #eef2e9 100%);
  display: flex;
  flex-direction: column;
}

.brand-chip {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 22px;
  font-weight: 700;
  color: #1f2921;
}

.brand-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ff335f;
  box-shadow: 0 0 0 8px rgba(255, 51, 95, 0.12);
}

.hero-copy {
  margin-top: 56px;
  max-width: 470px;
}

.eyebrow {
  margin: 0 0 10px;
  color: #687567;
  font-size: 13px;
  letter-spacing: 0.14em;
}

.hero-title {
  margin: 0;
  color: #1d2a20;
  font-size: clamp(34px, 4vw, 50px);
  line-height: 1.08;
}

.hero-desc {
  margin: 18px 0 0;
  color: #5f6b60;
  font-size: 16px;
  line-height: 1.65;
}

.credential-card {
  margin-top: auto;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  width: fit-content;
  border: 1px solid #dbe2d7;
  border-radius: 20px;
  padding: 14px 18px;
  background: rgba(255, 255, 255, 0.72);
}

.credential-label {
  color: #6c776d;
  font-size: 13px;
}

.credential-card code {
  color: #243027;
  font-size: 16px;
  font-weight: 700;
}

.credential-sep {
  color: #8a9389;
}

.form-panel {
  padding: 28px;
  background: linear-gradient(180deg, #ffffff 0%, #f8faf6 100%);
  display: grid;
  place-items: center;
}

.login-card {
  width: min(430px, 100%);
  border: 1px solid #e1e7dd;
  border-radius: 24px;
  background: #fff;
  padding: 28px;
  box-shadow: 0 18px 40px rgba(31, 39, 33, 0.06);
}

.card-head {
  margin-bottom: 24px;
}

.card-kicker {
  margin: 0 0 8px;
  color: #7b887b;
  font-size: 12px;
  letter-spacing: 0.12em;
}

.card-title {
  margin: 0;
  color: #1f2a21;
  font-size: 30px;
}

.card-desc {
  margin: 10px 0 0;
  color: #6d776d;
  font-size: 14px;
  line-height: 1.55;
}

.auth-form {
  display: flex;
  flex-direction: column;
}

.field-label {
  display: block;
  margin: 16px 0 8px;
  color: #4e5c50;
  font-size: 13px;
}

.text-input {
  width: 100%;
  height: 48px;
  border: 1px solid #d6ddd3;
  border-radius: 16px;
  background: #fbfcfa;
  padding: 0 14px;
  font-size: 14px;
  outline: none;
}

.text-input:focus {
  border-color: #93bc9a;
  background: #fff;
}

.primary-btn {
  width: 100%;
  height: 50px;
  margin-top: 22px;
  border: 0;
  border-radius: 18px;
  background: linear-gradient(135deg, #2f6f3f, #4a8c58);
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
}

.primary-btn[disabled] {
  opacity: 0.72;
  cursor: not-allowed;
}

.message-text {
  margin: 16px 0 0;
  font-size: 13px;
  line-height: 1.6;
}

.message-text.error {
  color: #cf2e53;
}

.message-text.ok {
  color: #2f6f3f;
}

@media (max-width: 980px) {
  .login-shell {
    min-height: auto;
    grid-template-columns: 1fr;
  }

  .credential-card {
    margin-top: 30px;
  }
}

@media (max-width: 640px) {
  .login-page {
    padding: 16px;
  }

  .hero-panel,
  .form-panel {
    padding: 20px 18px;
  }

  .login-card {
    padding: 22px 18px;
  }
}
</style>
