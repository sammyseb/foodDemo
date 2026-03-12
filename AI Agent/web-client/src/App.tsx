import { useAuthStore } from '@/features/auth/stores/authStore';
import { HomePage, LoginPage, SearchPage } from '@/pages';
import { ToastProvider } from '@/shared/components';
import { LogOut, MessageCircle, Search } from 'lucide-react';
import { BrowserRouter, Link, Navigate, Outlet, Route, Routes } from 'react-router-dom';

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

function Layout() {
  const logout = useAuthStore((state) => state.logout);
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-6">
              <Link to="/" className="text-lg font-bold text-primary-600">
                Restaurant Agent
              </Link>
              <nav className="flex gap-1">
                <Link
                  to="/"
                  className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100"
                >
                  <MessageCircle className="w-4 h-4" />
                  Chat
                </Link>
                <Link
                  to="/search"
                  className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100"
                >
                  <Search className="w-4 h-4" />
                  Search
                </Link>
              </nav>
            </div>
            <button
              onClick={logout}
              className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main>
        <Outlet />
      </main>
    </div>
  );
}

function App() {
  return (
    <ToastProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            element={
              <PrivateRoute>
                <Layout />
              </PrivateRoute>
            }
          >
            <Route path="/" element={<HomePage />} />
            <Route path="/search" element={<SearchPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ToastProvider>
  );
}

export default App;
