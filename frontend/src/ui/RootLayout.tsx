import React from 'react'
import { Link, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../state/AuthContext'

const RootLayout: React.FC = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <div className="min-h-screen flex flex-col">
      <nav className="border-b bg-white">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="text-xl font-semibold">Local Coding</Link>
          <div className="flex items-center gap-4">
            <Link to="/" className="hover:underline">Challenges</Link>
            <Link to="/submissions" className="hover:underline">Submissions</Link>
            <Link to="/" className="hover:underline">Leaderboard</Link>
            {user ? (
              <div className="flex items-center gap-2">
                <span className="text-sm">{user.username} ({user.rating})</span>
                <button className="text-sm text-red-600" onClick={() => { logout(); navigate('/'); }}>Logout</button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link to="/login" className="text-sm">Login</Link>
                <Link to="/register" className="text-sm">Register</Link>
              </div>
            )}
          </div>
        </div>
      </nav>
      <main className="flex-1 bg-gray-50">
        <div className="max-w-6xl mx-auto p-4">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

export default RootLayout