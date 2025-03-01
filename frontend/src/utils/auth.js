import axios from 'axios';

// Get API URL from environment variables
const apiUrl = import.meta.env.VITE_API_URL;

/**
 * Check if the user is logged in
 * @returns {boolean}
 */
export const isAuthenticated = () => {
  return localStorage.getItem('user') !== null;
};

/**
 * Get the current user from localStorage
 * @returns {Object|null}
 */
export const getCurrentUser = () => {
  const userJson = localStorage.getItem('user');
  return userJson ? JSON.parse(userJson) : null;
};

/**
 * Get the authentication token
 * @returns {string|null}
 */
export const getToken = () => {
  const user = getCurrentUser();
  return user ? user.token : null;
};

/**
 * Login a user
 * @param {string} email
 * @param {string} password
 * @returns {Promise<Object>}
 */
export const login = async (email, password) => {
  try {
    // In a real application, you would make an API call here
    // const response = await axios.post(`${apiUrl}/api/auth/login`, {
    //   email,
    //   password
    // });
    
    // For now, we'll simulate a successful login
    const user = {
      email,
      token: 'simulated-jwt-token'
    };
    
    // Store user data in localStorage
    localStorage.setItem('user', JSON.stringify(user));
    
    return user;
  } catch (error) {
    throw error;
  }
};

/**
 * Register a new user
 * @param {Object} userData
 * @returns {Promise<Object>}
 */
export const register = async (userData) => {
  try {
    // In a real application, you would make an API call here
    // const response = await axios.post(`${apiUrl}/api/auth/register`, userData);
    
    // For now, we'll simulate a successful registration
    const user = {
      ...userData,
      token: 'simulated-jwt-token'
    };
    
    // Store user data in localStorage
    localStorage.setItem('user', JSON.stringify(user));
    
    return user;
  } catch (error) {
    throw error;
  }
};

/**
 * Logout the current user
 */
export const logout = () => {
  localStorage.removeItem('user');
};

/**
 * Configure axios to use the authentication token in requests
 */
export const setupAxiosInterceptors = () => {
  axios.interceptors.request.use(
    (config) => {
      const token = getToken();
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );
  
  // Handle 401 responses (unauthorized)
  axios.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response && error.response.status === 401) {
        // Clear user data and redirect to login
        logout();
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );
}; 