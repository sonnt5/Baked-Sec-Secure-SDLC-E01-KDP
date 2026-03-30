# API and State Management Test Page

## Overview

The API Test page (`ApiTest.tsx`) is a comprehensive testing interface for validating API integration, authentication flows, and Zustand store state management. This page allows developers to test all backend API endpoints and observe real-time state changes.

## Features

### 1. API Client Configuration Display
- Shows current API configuration:
  - Base URL (from `VITE_API_BASE_URL` environment variable)
  - Request timeout (30 seconds)
  - Retry attempts (3 with exponential backoff)
  - Retry delay strategy

### 2. Zustand Store State Monitoring (Real-time)
Three tabs display live state from Zustand stores:

#### Auth Store
- Authentication status (authenticated/not authenticated)
- Current user object (JSON display)
- Access token (truncated for security)

#### Theme Store
- Current theme setting (light/dark/system)
- Interactive buttons to test theme changes:
  - Set Light
  - Set Dark
  - Set System
  - Toggle (switches between light/dark)

#### Notification Store
- Active notification count
- Test buttons to trigger notifications:
  - Add Success notification
  - Add Error notification
  - Clear All notifications

### 3. API Endpoint Testing
Six tabs organize endpoint tests by category:

#### Authentication
- Test Register (POST /api/auth/register)
- Test Login (POST /api/auth/login)
- Test Forgot Password (POST /api/auth/forgot-password)

#### Problems
- Test List Problems (GET /api/problems)
- Test Get Problem by ID (GET /api/problems/:id)
- Test Create Problem - Admin only (POST /api/problems)

#### Submissions
- Test List Submissions (GET /api/submissions)
- Test Get Submission by ID (GET /api/submissions/:id)
- Test Create Submission (POST /api/submissions)

#### Contests
- Test List Contests (GET /api/contests)
- Test Get Contest by ID (GET /api/contests/:id)
- Test Contest Registration (POST /api/contests/:id/register)

#### Users
- Test Get User by ID (GET /api/users/:id)
- Test Get User Statistics (GET /api/users/:id/statistics)

#### Admin
- Test List Users - Admin only (GET /api/admin/users)
- Test Get Statistics - Admin only (GET /api/admin/statistics)

### 4. Request/Response Logging
- Real-time log display showing:
  - Request type (REQUEST/RESPONSE/ERROR)
  - Endpoint path
  - HTTP status code (color-coded: green for success, red for error)
  - Timestamp
  - Full request/response data (JSON formatted)
- Logs are displayed in reverse chronological order (newest first)
- Clear Logs button to reset the log display
- Maximum height with scrolling for long log lists

## Usage

### Accessing the Page
1. Start the development server: `npm run dev`
2. Navigate to the home page
3. Click the "🔧 API Test" button

### Testing API Endpoints
1. Select a category tab (Authentication, Problems, etc.)
2. Click a test button to send a request
3. Observe the loading state on the button
4. Check the Request/Response Logs section for results
5. Toast notifications will appear for success/error

### Testing State Management
1. Navigate to the "Zustand Store States" section
2. Select a store tab (Auth, Theme, Notifications)
3. Interact with the test buttons
4. Observe real-time state updates in the display

### Testing Authentication Flow
1. Click "Test Register" to create a test account
2. Click "Test Login" to authenticate
3. Observe the Auth Store update with user data and tokens
4. Subsequent API calls will include the JWT token automatically
5. Test token refresh by waiting for expiration or manually triggering

## Technical Details

### State Management
- Uses Zustand stores directly (not through custom hooks)
- Real-time updates via store subscriptions
- Demonstrates state persistence (auth tokens in localStorage)

### API Integration
- All endpoints use the centralized `apiClient`
- Automatic JWT token attachment via request interceptor
- Automatic token refresh on 401 responses
- Retry logic with exponential backoff
- Error handling with user-friendly notifications

### Component Structure
```
ApiTest
├── API Configuration Card
├── Store States Card (Tabs)
│   ├── Auth Store Tab
│   ├── Theme Store Tab
│   └── Notification Store Tab
├── API Endpoint Tests Card (Tabs)
│   ├── Authentication Tab
│   ├── Problems Tab
│   ├── Submissions Tab
│   ├── Contests Tab
│   ├── Users Tab
│   └── Admin Tab
└── Request/Response Logs Card
```

### Dependencies
- `axios` - HTTP client
- `zustand` - State management
- UI components: Button, Card, Badge, Tabs
- API endpoints: authAPI, problemsAPI, submissionsAPI, contestsAPI, usersAPI, adminAPI

## Requirements Validated

This test page validates the following requirements:
- **22.1**: Centralized API client with Axios
- **22.2**: Base URL configuration from environment
- **22.3**: Request timeout (30 seconds)
- **22.4**: JWT token attachment via interceptor
- **22.5**: Response error handling (401, 403, 500)
- **22.6**: Automatic token refresh on 401
- **22.7**: Retry logic with exponential backoff
- **22.8**: TanStack Query integration (via API endpoints)
- **22.9**: Zustand store state management

## Testing Checklist

- [ ] API configuration displays correctly
- [ ] Auth store shows authentication state
- [ ] Theme store updates when theme changes
- [ ] Notification store shows active notifications
- [ ] All authentication endpoints can be tested
- [ ] All problem endpoints can be tested
- [ ] All submission endpoints can be tested
- [ ] All contest endpoints can be tested
- [ ] All user endpoints can be tested
- [ ] All admin endpoints can be tested
- [ ] Request logs display with correct format
- [ ] Response logs show status codes
- [ ] Error logs display error messages
- [ ] Loading states appear during requests
- [ ] Toast notifications appear on success/error
- [ ] Clear Logs button works
- [ ] JWT token is attached to authenticated requests
- [ ] Token refresh works on 401 responses

## Notes

- Some endpoints require authentication (JWT token from login)
- Admin endpoints require admin role
- Sample data is used for testing (may not exist in backend)
- Error responses are expected for non-existent resources
- The page is for development/testing only, not for production use
