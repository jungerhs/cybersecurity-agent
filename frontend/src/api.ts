import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

apiClient.interceptors.request.use(config => {
  console.log('API Request:', config.method?.toUpperCase(), config.url, config.data);
  return config;
});

apiClient.interceptors.response.use(
  response => {
    console.log('API Response:', response.status, response.data);
    return response;
  },
  error => {
    console.error('API Error:', error.message, error.response?.data);
    return Promise.reject(error);
  }
);

export const api = {
  healthCheck: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  initializeSystem: async (forceRebuild = false) => {
    console.log('Initializing system with forceRebuild:', forceRebuild);
    const response = await apiClient.post('/init', {
      force_rebuild: forceRebuild
    });
    return response.data;
  },

  query: async (question, includeSources = true, useWebSearch = true) => {
    console.log('Querying with question:', question);
    const response = await apiClient.post('/query', {
      question,
      include_sources: includeSources,
      use_web_search: useWebSearch
    });
    return response.data;
  },

  getStatus: async () => {
    const response = await apiClient.get('/status');
    return response.data;
  },

  addDocuments: async (filePath, directory) => {
    const response = await apiClient.post('/add-documents', {
      file_path: filePath,
      directory
    });
    return response.data;
  },

  uploadDocument: async (formData) => {
    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  resetSystem: async () => {
    const response = await apiClient.post('/reset');
    return response.data;
  }
};