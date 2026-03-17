<template>
  <section class="login-page">
    <div class="login-shell">
      <section class="hero-panel">
        <div class="hero-top">
          <div class="brand-chip">
            <span class="brand-dot"></span>
            <span>灵感画廊</span>
          </div>
        </div>

        <div class="hero-main">
          <div class="hero-copy">
            <h1 class="hero-title">上传图片，开始你的风格创作。</h1>
            <p class="hero-subtitle">从本地选图，生成后可以保存到仓库或发布到大厅。</p>
          </div>
        </div>

        <div class="hero-notes" aria-hidden="true">
          <div class="hero-note">
            <span class="hero-note-label">上传</span>
            <span class="hero-note-text">本地选图即可开始</span>
          </div>
          <div class="hero-note">
            <span class="hero-note-label">生成</span>
            <span class="hero-note-text">支持多种风格效果</span>
          </div>
          <div class="hero-note">
            <span class="hero-note-label">保存</span>
            <span class="hero-note-text">作品可留在仓库或发布展示</span>
          </div>
        </div>
      </section>

      <section class="form-panel">
        <div class="login-card">
          <div class="card-head">
            <h2 class="card-title">登录 / 注册</h2>
          </div>

          <div class="mode-switch">
            <button
              type="button"
              class="mode-btn"
              :class="{ active: mode === 'login' }"
              @click="switchMode('login')"
            >
              登录
            </button>
            <button
              type="button"
              class="mode-btn"
              :class="{ active: mode === 'register' }"
              @click="switchMode('register')"
            >
              注册
            </button>
          </div>

          <form v-if="mode === 'login'" class="auth-form" @submit.prevent="onLogin">
            <label class="field-label" for="login-identifier">用户ID或用户名</label>
            <input
              id="login-identifier"
              v-model.trim="loginForm.identifier"
              class="text-input"
              type="text"
              autocomplete="username"
              placeholder="请输入用户ID或用户名"
              required
            />

            <label class="field-label" for="login-password">密码</label>
            <input
              id="login-password"
              v-model="loginForm.password"
              class="text-input"
              type="password"
              autocomplete="current-password"
              placeholder="请输入密码"
              required
            />

            <button type="submit" class="primary-btn" :disabled="submitting">
              {{ submitting ? '登录中...' : '进入灵感画廊' }}
            </button>
          </form>

          <form v-else class="auth-form" @submit.prevent="onRegister">
            <label class="field-label" for="register-username">用户名</label>
            <input
              id="register-username"
              v-model.trim="registerForm.username"
              class="text-input"
              type="text"
              maxlength="32"
              autocomplete="username"
              placeholder="请输入用户名"
              required
            />

            <label class="field-label" for="register-password">密码</label>
            <input
              id="register-password"
              v-model="registerForm.password"
              class="text-input"
              type="password"
              maxlength="20"
              autocomplete="new-password"
              placeholder="请输入密码"
              required
            />

            <button type="submit" class="primary-btn" :disabled="submitting">
              {{ submitting ? '注册中...' : '创建账号' }}
            </button>
          </form>

          <p v-if="msg" class="message-text" :class="{ error: hasError, ok: !hasError }">{{ msg }}</p>
        </div>
      </section>
    </div>
  </section>
</template>

<script>
import { login, register } from '../api/auth'

const USERNAME_PATTERN = /^[a-zA-Z0-9_]+$/
const ACCOUNT_CODE_PATTERN = /^(lghl\d{8}|admin\d{7})$/
const ADMIN_ACCOUNT_CODE = 'admin1433223'

export default {
  name: 'LoginView',
  data() {
    return {
      mode: 'login',
      loginForm: {
        identifier: '',
        password: ''
      },
      registerForm: {
        username: '',
        password: ''
      },
      msg: '',
      submitting: false,
      hasError: false
    }
  },
  methods: {
    switchMode(nextMode) {
      if (this.submitting) return
      this.mode = nextMode
      this.msg = ''
      this.hasError = false
    },
    validateLoginForm() {
      const identifier = (this.loginForm.identifier || '').trim()
      const password = this.loginForm.password || ''

      if (!identifier || !password) return '请输入用户ID或用户名和密码'

      const normalizedIdentifier = identifier.toLowerCase()
      const isAccountCode = ACCOUNT_CODE_PATTERN.test(normalizedIdentifier)
      const isUsername = USERNAME_PATTERN.test(identifier)

      if (!isAccountCode && !isUsername) {
        return '用户ID或用户名格式不正确'
      }

      this.loginForm.identifier = isAccountCode ? normalizedIdentifier : identifier
      return ''
    },
    validateRegisterForm() {
      const username = (this.registerForm.username || '').trim()
      const password = this.registerForm.password || ''

      if (!username || !password) return '请填写用户名和密码'
      if (username.length < 3 || username.length > 32) return '用户名长度为 3-32 位'
      if (!USERNAME_PATTERN.test(username)) return '用户名只能包含字母、数字和下划线'
      if (password.length < 6 || password.length > 20) return '密码长度为 6-20 位'
      return ''
    },
    async onLogin() {
      if (this.submitting) return

      const validationError = this.validateLoginForm()
      if (validationError) {
        this.msg = validationError
        this.hasError = true
        return
      }

      this.submitting = true
      this.msg = ''
      this.hasError = false

      try {
        const isAccountCode = ACCOUNT_CODE_PATTERN.test(this.loginForm.identifier)
        const res = await login({
          account_code: isAccountCode ? this.loginForm.identifier : undefined,
          username: isAccountCode ? undefined : this.loginForm.identifier,
          password: this.loginForm.password
        })
        const data = (res && res.data && res.data.data) || {}
        const user = data.user || null
        localStorage.setItem('token', data.token)

        if (this.loginForm.identifier === ADMIN_ACCOUNT_CODE || (user && user.role === 'admin')) {
          this.msg = '登录成功，正在进入后台...'
          this.$router.replace('/admin/artworks')
          return
        }

        this.msg = '登录成功，正在进入大厅...'
        this.$router.replace('/hall')
      } catch (error) {
        this.hasError = true
        this.msg = (error && error.response && error.response.data && error.response.data.message) || '登录失败'
      } finally {
        this.submitting = false
      }
    },
    async onRegister() {
      if (this.submitting) return

      const validationError = this.validateRegisterForm()
      if (validationError) {
        this.msg = validationError
        this.hasError = true
        return
      }

      this.submitting = true
      this.msg = ''
      this.hasError = false

      try {
        const res = await register({
          username: this.registerForm.username.trim(),
          password: this.registerForm.password
        })
        const user = res && res.data && res.data.data && res.data.data.user
        const assignedCode = user && user.account_code

        this.loginForm.identifier = assignedCode || this.registerForm.username.trim()
        this.loginForm.password = this.registerForm.password
        this.mode = 'login'
        this.msg = assignedCode
          ? `注册成功，用户ID为 ${assignedCode}。`
          : '注册成功，请登录后继续。'
        this.registerForm = {
          username: '',
          password: ''
        }
      } catch (error) {
        this.hasError = true
        this.msg = (error && error.response && error.response.data && error.response.data.message) || '注册失败'
      } finally {
        this.submitting = false
      }
    }
  }
}
</script>

<style lang="scss" scoped>
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
  width: min(1180px, 100%);
  min-height: min(760px, calc(100vh - 56px));
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  @include panel-surface(
    $radius: $radius-xxl,
    $border: #dde4da,
    $background: rgba(255, 255, 255, 0.84),
    $shadow: $shadow-large
  );
  overflow: hidden;
}

.hero-panel {
  padding: 44px 40px;
  background:
    radial-gradient(circle at top left, rgba(255, 255, 255, 0.9), transparent 34%),
    linear-gradient(160deg, #e8efe4 0%, #f6f8f3 52%, #eef2e9 100%);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 40px;
}

.hero-top {
  display: flex;
  align-items: flex-start;
}

.hero-main {
  flex: 1;
  display: flex;
  align-items: center;
}

.brand-chip {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 22px;
  font-weight: 700;
  color: $color-text;
}

.brand-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ff335f;
  box-shadow: 0 0 0 8px rgba(255, 51, 95, 0.12);
}

.hero-copy {
  max-width: 520px;
}

.hero-title {
  margin: 0;
  color: $color-text-strong;
  font-size: clamp(34px, 4vw, 52px);
  line-height: 1.12;
}

.hero-subtitle {
  margin: 18px 0 0;
  max-width: 460px;
  color: $color-muted;
  font-size: 16px;
  line-height: 1.7;
}

.hero-notes {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.hero-note {
  padding-top: 14px;
  border-top: 1px solid rgba(145, 159, 145, 0.28);

  &-label {
    display: block;
    margin-bottom: 6px;
    color: #2a372c;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.08em;
  }

  &-text {
    display: block;
    color: #70806f;
    font-size: 13px;
    line-height: 1.6;
  }
}

.form-panel {
  padding: 28px;
  background: linear-gradient(180deg, #ffffff 0%, #f8faf6 100%);
  display: grid;
  place-items: center;
}

.login-card {
  width: min(440px, 100%);
  @include panel-surface();
  padding: 28px;
}

.card-head {
  margin-bottom: 20px;
}

.card-title {
  margin: 0;
  color: $color-text;
  font-size: 30px;
}

.mode-switch {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  padding: 6px;
  border-radius: $radius-lg;
  background: $color-surface-muted;
  margin-bottom: 18px;
}

.mode-btn {
  height: 42px;
  border: 0;
  border-radius: $radius-md;
  background: transparent;
  color: #526052;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;

  &.active {
    background: #ffffff;
    color: $color-text;
    box-shadow: 0 8px 18px rgba(35, 44, 37, 0.06);
  }
}

.auth-form {
  display: flex;
  flex-direction: column;
}

.field-label {
  display: block;
  margin: 16px 0 8px;
  color: $color-text-soft;
  font-size: 13px;
}

.text-input {
  @include input-shell($height: 48px, $radius: 16px);
}

.primary-btn {
  width: 100%;
  margin-top: 22px;
  @include solid-button($height: 50px, $radius: $radius-lg, $font-size: 15px);
}

.message-text {
  margin: 16px 0 0;
  font-size: 13px;
  line-height: 1.6;

  &.error {
    color: $color-error-text;
  }

  &.ok {
    color: $color-primary;
  }
}

@media (max-width: 980px) {
  .login-shell {
    min-height: auto;
    grid-template-columns: 1fr;
  }

  .hero-main {
    min-height: 220px;
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

  .hero-notes {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .login-card {
    padding: 22px 18px;
  }

  .hero-title {
    font-size: 34px;
  }
}
</style>
