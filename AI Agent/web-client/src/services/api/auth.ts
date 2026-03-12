import { API_ENDPOINTS } from '@/config';
import type { AuthResponse } from '@/shared/types';
import { request } from './client';

interface LoginRequest {
  username: string;
  password: string;
}

export async function login(credentials: LoginRequest): Promise<AuthResponse> {
  return request<AuthResponse>({
    method: 'POST',
    url: API_ENDPOINTS.AUTH_LOGIN,
    data: credentials,
  });
}

export async function logout(): Promise<void> {
  await request({
    method: 'POST',
    url: API_ENDPOINTS.AUTH_LOGOUT,
  });
}
