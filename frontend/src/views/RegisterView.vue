<template>
  <div class="register-container">
    <Card class="register-card">
      <template #title>
        <h2 class="title">Create an Account</h2>
      </template>
      <template #content>
        <form @submit.prevent="register">
          <div class="field">
            <label for="name">Name*</label>
            <InputText 
              id="name" 
              v-model="name" 
              class="w-full" 
              placeholder="Enter your name"
              required
            />
          </div>
          
          <div class="field">
            <label for="email">Email*</label>
            <InputText 
              id="email" 
              v-model="email" 
              type="email" 
              class="w-full" 
              placeholder="Enter your email"
              required
            />
          </div>
          
          <div class="field">
            <label for="password">Password*</label>
            <Password 
              id="password" 
              v-model="password" 
              toggleMask 
              class="w-full" 
              placeholder="Create a password"
              required
            />
          </div>
          
          <div class="field">
            <label for="confirmPassword">Confirm Password*</label>
            <Password 
              id="confirmPassword" 
              v-model="confirmPassword" 
              toggleMask 
              class="w-full" 
              placeholder="Confirm your password"
              required
              :class="{'p-invalid': !passwordsMatch}"
            />
            <small v-if="!passwordsMatch" class="p-error">Passwords do not match</small>
          </div>
          
          <div class="field">
            <label for="phone">Phone Number (Optional)</label>
            <InputText 
              id="phone" 
              v-model="phone" 
              class="w-full" 
              placeholder="Enter your phone number"
            />
          </div>
          
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
          
          <div class="actions">
            <Button 
              type="submit" 
              label="Register" 
              :loading="isLoading" 
              class="w-full"
            />
          </div>
          
          <div class="login-link">
            <p>Already have an account? 
              <a href="#" @click.prevent="goToLogin">Login</a>
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
  name: 'RegisterView',
  components: {
    Card,
    InputText,
    Password,
    Button
  },
  data() {
    return {
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      phone: '',
      errorMessage: '',
      isLoading: false
    };
  },
  computed: {
    passwordsMatch() {
      return !this.password || !this.confirmPassword || this.password === this.confirmPassword;
    }
  },
  methods: {
    async register() {
      try {
        this.isLoading = true;
        this.errorMessage = '';
        
        // Validate form
        if (!this.name || !this.email || !this.password || !this.confirmPassword) {
          this.errorMessage = 'Please fill in all required fields';
          return;
        }
        
        if (this.password !== this.confirmPassword) {
          this.errorMessage = 'Passwords do not match';
          return;
        }
        
        if (this.password.length < 6) {
          this.errorMessage = 'Password must be at least 6 characters long';
          return;
        }
        
        // In a real application, you would make an API call here
        // For now, we'll simulate registration and store in localStorage
        const apiUrl = import.meta.env.VITE_API_URL;

        
        try {
          const response = await axios.post(`${apiUrl}/register`, {
            name: this.name,
            email: this.email,
            password: this.password,
            phone: this.phone || null
          });
          // Redirect to home
          this.$router.push('/login');
        } catch (error) {
          console.error('Registration error:', error);
          this.errorMessage = error.response?.data?.message || 'Registration failed. Please try again.';
        }
      } finally {
        this.isLoading = false;
      }
    },
    goToLogin() {
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 1rem;
  background-color: #f5f5f5;
}

.register-card {
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

.login-link {
  margin-top: 1.5rem;
  text-align: center;
}

.login-link a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

.login-link a:hover {
  text-decoration: underline;
}

.error-message {
  margin-top: 1rem;
  color: var(--red-500);
  font-size: 0.875rem;
}
</style> 