import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const studentsAPI = {
  create: (studentData) => api.post('/api/students/', studentData),
  get: (id) => api.get(`/api/students/${id}`),
  update: (id, studentData) => api.put(`/api/students/${id}`, studentData),
  list: (params = {}) => api.get('/api/students/', { params }),
};

export const assignmentsAPI = {
  generate: (assignmentData) => api.post('/api/assignments/generate', assignmentData),
  get: (id) => api.get(`/api/assignments/${id}`),
  list: (params = {}) => api.get('/api/assignments/', { params }),
  downloadPDF: (id, type) => {
    return api.get(`/api/assignments/${id}/download/${type}`, {
      responseType: 'blob',
    });
  },
};

export const tasksAPI = {
  import: () => api.post('/api/tasks/import'),
  search: (params) => api.get('/api/tasks/search', { params }),
  get: (id) => api.get(`/api/tasks/${id}`),
  list: (params = {}) => api.get('/api/tasks/', { params }),
};

export default api;



