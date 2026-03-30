import { createBrowserRouter, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import ProtectedRoute from './components/auth/ProtectedRoute';
import App from './App';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import VerifyEmail from './pages/auth/VerifyEmail';
import ForgotPassword from './pages/auth/ForgotPassword';
import ResetPassword from './pages/auth/ResetPassword';
import ProblemListPage from './pages/problems/ProblemListPage';
import ProblemDetailPage from './pages/problems/ProblemDetailPage';
import ContestListPage from './pages/contests/ContestListPage';
import ContestDetailPage from './pages/contests/ContestDetailPage';
import ScoreboardPage from './pages/contests/ScoreboardPage';
import SubmissionListPage from './pages/submissions/SubmissionListPage';
import SubmissionDetailPage from './pages/submissions/SubmissionDetailPage';
import UserProfilePage from './pages/users/UserProfilePage';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminEditProblemPage from './pages/admin/AdminEditProblemPage';
import AdminCreateProblemPage from './pages/admin/AdminCreateProblemPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <App /> },
      { path: 'problems', element: <ProblemListPage /> },
      { path: 'problems/:id', element: <ProblemDetailPage /> },
      { path: 'contests', element: <ContestListPage /> },
      { path: 'contests/:id', element: <ContestDetailPage /> },
      { path: 'contests/:id/scoreboard', element: <ScoreboardPage /> },
      { path: 'users/:id', element: <ProtectedRoute><UserProfilePage /></ProtectedRoute> },
      {
        path: 'submissions',
        element: (
          <ProtectedRoute>
            <SubmissionListPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'submissions/:id',
        element: (
          <ProtectedRoute>
            <SubmissionDetailPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin',
        element: (
          <ProtectedRoute requireAdmin>
            <AdminDashboard />
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin/problems/create',
        element: (
          <ProtectedRoute requireAdmin>
            <AdminCreateProblemPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin/problems/:id/edit',
        element: (
          <ProtectedRoute requireAdmin>
            <AdminEditProblemPage />
          </ProtectedRoute>
        ),
      },
    ],
  },
  { path: '/login', element: <Login /> },
  { path: '/register', element: <Register /> },
  { path: '/verify-email', element: <VerifyEmail /> },
  { path: '/forgot-password', element: <ForgotPassword /> },
  { path: '/reset-password', element: <ResetPassword /> },
  { path: '*', element: <Navigate to="/" replace /> },
]);
