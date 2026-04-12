import axios from "axios";
import { AUTH_STORAGE_KEYS } from "../utils/constants";

const configuredUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";
const finalBaseUrl = configuredUrl.replace(/localhost|127\.0\.0\.1/, globalThis.location.hostname);

const api = axios.create({
  baseURL: finalBaseUrl,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(AUTH_STORAGE_KEYS.token);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(AUTH_STORAGE_KEYS.token);
      globalThis.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
