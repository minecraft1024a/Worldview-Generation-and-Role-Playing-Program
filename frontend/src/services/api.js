import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// 创建 axios 实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 秒超时
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.status, error.config?.url, error.message);
    return Promise.reject(error);
  }
);

// API 服务函数
export const apiService = {
  // 获取每日格言
  getDailyQuote: async () => {
    const response = await api.get('/daily-quote');
    return response.data;
  },

  // 生成世界观
  generateWorld: async (background) => {
    const response = await api.post('/generate-world', { background });
    return response.data;
  },

  // 生成角色
  generateCharacter: async (worldDescription, prompt) => {
    const response = await api.post('/generate-character', {
      world_description: worldDescription,
      prompt: prompt
    });
    return response.data;
  },

  // 角色扮演回复
  rolePlay: async (messages, temperature = 0.7) => {
    const response = await api.post('/role-play', {
      messages: messages,
      temperature: temperature
    });
    return response.data;
  },

  // 保存游戏
  saveGame: async (messages, worldDescription, saveName = null, role = null) => {
    const response = await api.post('/save-game', {
      messages: messages,
      world_description: worldDescription,
      save_name: saveName,
      role: role
    });
    return response.data;
  },

  // 加载游戏
  loadGame: async (saveName) => {
    const response = await api.get(`/load-game/${saveName}`);
    return response.data;
  },

  // 获取存档列表
  getSaves: async () => {
    const response = await api.get('/saves');
    return response.data;
  },

  // 删除存档
  deleteSave: async (saveName) => {
    const response = await api.delete(`/saves/${saveName}`);
    return response.data;
  }
};

export default api;
