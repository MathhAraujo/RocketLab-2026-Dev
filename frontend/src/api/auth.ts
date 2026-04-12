import type { AuthUser, LoginRequest, TokenResponse } from "../types/auth";
import api from "./client";

export async function login(data: LoginRequest): Promise<TokenResponse> {
  const response = await api.post<TokenResponse>("/auth/login", data);
  return response.data;
}

export async function register(data: LoginRequest): Promise<AuthUser> {
  const response = await api.post<AuthUser>("/auth/register", data);
  return response.data;
}

export async function getMe(): Promise<AuthUser> {
  const response = await api.get<AuthUser>("/auth/me");
  return response.data;
}
