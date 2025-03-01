<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import Card from 'primevue/card';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import axios from 'axios';

const name = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const phone = ref('');
const errorMessage = ref('');
const isLoading = ref(false);
const router = useRouter();

const passwordsMatch = computed(() => 
  !password.value || !confirmPassword.value || password.value === confirmPassword.value
);

const register = async () => {
  try {
    isLoading.value = true;
    errorMessage.value = '';
    
    // Validate form
    if (!name.value || !email.value || !password.value || !confirmPassword.value) {
      errorMessage.value = 'Please fill in all required fields';
      return;
    }
    
    if (password.value !== confirmPassword.value) {
      errorMessage.value = 'Passwords do not match';
      return;
    }
    
    if (password.value.length < 6) {
      errorMessage.value = 'Password must be at least 6 characters long';
      return;
    }
    
    // In a real application, you would make an API call here
    // For now, we'll simulate registration and store in localStorage
    const apiUrl = import.meta.env.VITE_API_URL;
    
    try {
      // You can uncomment this when you have a real API endpoint
      // const response = await axios.post(`${apiUrl}/api/auth/register`, {
      //   name: name.value,
      //   email: email.value,
      //   password: password.value,
      //   phone: phone.value || null
      // });
      
      // For now, we'll simulate a successful registration
      const user = {
        name: name.value,
        email: email.value,
        phone: phone.value || null,
        token: 'simulated-jwt-token'
      };
      
      // Store user data in localStorage
      localStorage.setItem('user', JSON.stringify(user));
      
      // Redirect to home
      router.push('/');
    } catch (error) {
      console.error('Registration error:', error);
      errorMessage.value = error.response?.data?.message || 'Registration failed. Please try again.';
    }
  } finally {
    isLoading.value = false;
  }
};

const goToLogin = () => {
  router.push('/login');
};
</script>

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