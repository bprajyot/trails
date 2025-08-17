import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import './index.css'
import { AuthProvider } from './state/AuthContext'
import RootLayout from './ui/RootLayout'
import HomePage from './ui/HomePage'
import LoginPage from './ui/LoginPage'
import RegisterPage from './ui/RegisterPage'
import ChallengePage from './ui/ChallengePage'
import SubmissionsPage from './ui/SubmissionsPage'

const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'register', element: <RegisterPage /> },
      { path: 'challenge/:slug', element: <ChallengePage /> },
      { path: 'submissions', element: <SubmissionsPage /> },
    ],
  },
])

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </React.StrictMode>
)