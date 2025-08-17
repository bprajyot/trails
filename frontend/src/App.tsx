import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

import { store } from './store';
import Header from './components/common/Header';
import HomePage from './pages/HomePage';
import ProblemsPage from './pages/ProblemsPage';
import ProblemDetailPage from './pages/ProblemDetailPage';
import LoginPage from './pages/LoginPage';
import ProfilePage from './pages/ProfilePage';
import ContestsPage from './pages/ContestsPage';
import LeaderboardPage from './pages/LeaderboardPage';
import ProtectedRoute from './components/auth/ProtectedRoute';

import './styles/globals.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <Router>
          <div className="min-h-screen bg-gray-50">
            <Header />
            
            <main className="container mx-auto px-4 py-8">
              <Routes>
                {/* Public routes */}
                <Route path="/" element={<HomePage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/problems" element={<ProblemsPage />} />
                <Route path="/contests" element={<ContestsPage />} />
                <Route path="/leaderboard" element={<LeaderboardPage />} />
                
                {/* Problem detail - can be viewed by anyone but features require auth */}
                <Route path="/problems/:slug" element={<ProblemDetailPage />} />
                
                {/* Protected routes */}
                <Route
                  path="/profile"
                  element={
                    <ProtectedRoute>
                      <ProfilePage />
                    </ProtectedRoute>
                  }
                />
                
                {/* Redirect unknown routes to home */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>

            {/* Global toast notifications */}
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
                success: {
                  iconTheme: {
                    primary: '#10b981',
                    secondary: '#fff',
                  },
                },
                error: {
                  iconTheme: {
                    primary: '#ef4444',
                    secondary: '#fff',
                  },
                },
              }}
            />
          </div>
        </Router>
      </QueryClientProvider>
    </Provider>
  );
}

export default App;