import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'
import axios, { AxiosInstance } from 'axios'
import jwtDecode from 'jwt-decode'

export type User = {
  id: number
  email: string
  username: string
  rating: number
}

export type AuthContextType = {
  user: User | null
  token: string | null
  api: AxiosInstance
  login: (token: string, user: User) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'))
  const [user, setUser] = useState<User | null>(() => {
    const raw = localStorage.getItem('user')
    return raw ? JSON.parse(raw) : null
  })

  const apiBase = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

  const api = useMemo(() => {
    const instance = axios.create({ baseURL: apiBase })
    instance.interceptors.request.use((config) => {
      if (token) config.headers.Authorization = `Bearer ${token}`
      return config
    })
    return instance
  }, [apiBase, token])

  function login(newToken: string, newUser: User) {
    setToken(newToken)
    setUser(newUser)
    localStorage.setItem('token', newToken)
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  function logout() {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return (
    <AuthContext.Provider value={{ user, token, api, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('AuthContext missing')
  return ctx
}