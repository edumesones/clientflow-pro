import api from './api';

export const authAPI = {
  login: (email, password) => api.post('/auth/login-json', { email, password }),
  register: (data) => api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
  refresh: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
};

export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getUpcoming: (limit = 5) => api.get(`/dashboard/upcoming-appointments?limit=${limit}`),
  getRecentLeads: (limit = 5) => api.get(`/dashboard/recent-leads?limit=${limit}`),
  getFullData: () => api.get('/dashboard/data'),
};

export const appointmentsAPI = {
  getAll: (params) => api.get('/appointments/', { params }),
  getUpcoming: (limit = 10) => api.get(`/appointments/upcoming?limit=${limit}`),
  getById: (id) => api.get(`/appointments/${id}`),
  create: (data) => api.post('/appointments/', data),
  update: (id, data) => api.put(`/appointments/${id}`, data),
  cancel: (id) => api.post(`/appointments/${id}/cancel`),
};

export const leadsAPI = {
  getAll: (params) => api.get('/leads/', { params }),
  getRecent: (limit = 10) => api.get(`/leads/recent?limit=${limit}`),
  getById: (id) => api.get(`/leads/${id}`),
  create: (data) => api.post('/leads/', data),
  update: (id, data) => api.put(`/leads/${id}`, data),
  markContacted: (id) => api.post(`/leads/${id}/contact`),
};

export const professionalsAPI = {
  getAll: () => api.get('/professionals/'),
  getBySlug: (slug) => api.get(`/professionals/${slug}`),
  getMyProfile: () => api.get('/users/professional/me'),
  updateProfile: (id, data) => api.put(`/users/professional/${id}`, data),
};

export const availabilityAPI = {
  getMySlots: () => api.get('/availability/slots'),
  setSchedule: (data) => api.post('/availability/schedule', data),
  deleteSlot: (id) => api.delete(`/availability/slots/${id}`),
  getAvailable: (professionalId, date) => 
    api.get(`/availability/${professionalId}/available?date=${date}`),
};

export const publicAPI = {
  getProfessional: (slug) => api.get(`/public/professionals/${slug}`),
  getAvailability: (slug, date) => api.get(`/public/professionals/${slug}/availability?date=${date}`),
  bookAppointment: (data) => api.post('/public/book', data),
  submitLead: (data) => api.post('/public/leads', data),
};
