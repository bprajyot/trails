export interface User {
  id: number;
  username: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  rating: number;
  total_submissions: number;
  accepted_submissions: number;
  success_rate: number;
  created_at: string;
  is_active: boolean;
  is_admin?: boolean;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface AuthResponse {
  message: string;
  user: User;
  access_token: string;
  refresh_token: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}