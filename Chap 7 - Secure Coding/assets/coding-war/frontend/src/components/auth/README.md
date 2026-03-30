# Authentication Components

This directory contains all authentication-related components for the Coding War platform.

## Components

### LoginForm
Form component for user login with email and password validation.

**Props:**
- `onSubmit: (data: LoginFormData) => Promise<void>` - Callback for form submission
- `isLoading?: boolean` - Loading state indicator

**Features:**
- Email validation (RFC 5322 standard)
- Password validation
- Inline error display
- Loading state handling
- Error message display

### RegisterForm
Form component for user registration with username, email, and password.

**Props:**
- `onSubmit: (data: RegisterFormData) => Promise<void>` - Callback for form submission
- `isLoading?: boolean` - Loading state indicator

**Features:**
- Username validation (3-20 alphanumeric characters)
- Email validation (RFC 5322 standard)
- Password strength validation (min 8 chars, mixed case, numbers)
- Inline error display
- Loading state handling

### PasswordResetForm
Form component for resetting password with new password and confirmation.

**Props:**
- `onSubmit: (password: string) => Promise<void>` - Callback for form submission
- `isLoading?: boolean` - Loading state indicator

**Features:**
- Password strength validation
- Password confirmation matching
- Inline error display
- Loading state handling

### ProtectedRoute
Route wrapper component that requires authentication.

**Props:**
- `children: React.ReactNode` - Child components to render
- `requireAdmin?: boolean` - Whether admin role is required

**Features:**
- Redirects to login if not authenticated
- Redirects to home if admin required but user is not admin
- Preserves intended destination for redirect after login

## Validation Schemas

All forms use Zod schemas defined in `src/utils/validation.ts`:

- `usernameSchema` - 3-20 alphanumeric characters
- `emailSchema` - RFC 5322 email format
- `passwordSchema` - Min 8 chars, mixed case, numbers
- `registerSchema` - Combined username, email, password
- `loginSchema` - Email and password
- `forgotPasswordSchema` - Email only
- `resetPasswordSchema` - Password and confirmation with matching validation

## Usage Examples

### Login
```tsx
import { LoginForm } from '@/components/auth';
import { authAPI } from '@/api/endpoints/auth';
import { useAuthStore } from '@/stores/authStore';

function LoginPage() {
  const { setUser, setTokens } = useAuthStore();
  
  const handleLogin = async (data) => {
    const response = await authAPI.login(data);
    setUser(response.user);
    setTokens(response.accessToken, response.refreshToken);
  };
  
  return <LoginForm onSubmit={handleLogin} />;
}
```

### Protected Route
```tsx
import { ProtectedRoute } from '@/components/auth';

<Route path="/dashboard" element={
  <ProtectedRoute>
    <Dashboard />
  </ProtectedRoute>
} />

// Admin only route
<Route path="/admin" element={
  <ProtectedRoute requireAdmin>
    <AdminPanel />
  </ProtectedRoute>
} />
```

## Integration with Backend

All forms integrate with the backend API through `src/api/endpoints/auth.ts`:

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/verify-email` - Email verification
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password with token
- `POST /api/auth/refresh` - Refresh access token

## State Management

Authentication state is managed through Zustand store (`src/stores/authStore.ts`):

- `user` - Current user object
- `accessToken` - JWT access token
- `refreshToken` - JWT refresh token
- `isAuthenticated` - Boolean authentication status
- `setUser()` - Set current user
- `setTokens()` - Set access and refresh tokens
- `logout()` - Clear authentication state

Tokens are persisted to localStorage and automatically restored on page reload.
