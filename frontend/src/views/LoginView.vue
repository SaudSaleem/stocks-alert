<template>
  <div class="login-container">
    <Card class="login-card">
      <template #title>
        <h2 class="title">Login</h2>
      </template>
      <template #content>
        <form @submit.prevent="login">
          <div class="field">
            <label for="email">Email</label>
            <InputText id="email" v-model="email" type="email" class="w-full" placeholder="Enter your email" required
              autocomplete="email" />
          </div>

          <div class="field">
            <label for="password">Password</label>
            <Password id="password" v-model="password" toggleMask class="w-full" placeholder="Enter your password"
              required autocomplete="current-password" />
          </div>

          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>

          <div class="actions">
            <Button type="submit" label="Login" :loading="isLoading" class="w-full" />
          </div>

          <div class="register-link">
            <p>Don't have an account?
              <a href="#" @click.prevent="goToRegister">Register</a>
            </p>
          </div>
        </form>
      </template>
    </Card>
  </div>
</template>

<script>
import { useRouter } from 'vue-router';
import Card from 'primevue/card';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import axios from 'axios';

export default {
  components: {
    Card,
    InputText,
    Password,
    Button
  },

  data() {
    return {
      email: '',
      password: '',
      errorMessage: '',
      isLoading: false
    };
  },

  methods: {
    async login() {
      try {
        this.isLoading = true;
        this.errorMessage = '';

        if (!this.email || !this.password) {
          this.errorMessage = 'Please fill in all fields';
          return;
        }

        const apiUrl = import.meta.env.VITE_API_URL;
        console.log('apiUrl', apiUrl)
        try {
          // You can uncomment this when you have a real API endpoint
          const response = await axios.post(`${apiUrl}/login/json`, {
            email: this.email,
            password: this.password
          });

          console.log('login response', response)

          // Store user data in localStorage
          localStorage.setItem('access_token', response.data.access_token);
          localStorage.setItem('token_type', response.data.token_type);
          localStorage.setItem('user', JSON.stringify(response.data.user));

          // Redirect to home
          this.$router.push('/');
        } catch (error) {
          console.error('Login error:', error);
          this.errorMessage = error.response?.data?.message || 'Login failed. Please try again.';
        }
      } finally {
        this.isLoading = false;
      }
    },

    goToRegister() {
      this.$router.push('/register');
    }
  },
  mounted() {
    console.log('mounted', import.meta.env.VITE_API_URL)
  }
};
</script>



<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 1rem;
  background-color: #f5f5f5;
}

.login-card {
  width: 100%;
  max-width: 450px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.title {
  text-align: center;
  margin: 0;
  color: var(--primary-color);
}

.field {
  margin-bottom: 1.5rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.actions {
  margin-top: 2rem;
}

.register-link {
  margin-top: 1.5rem;
  text-align: center;
}

.register-link a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

.register-link a:hover {
  text-decoration: underline;
}

.error-message {
  margin-top: 1rem;
  color: var(--red-500);
  font-size: 0.875rem;
}
</style>