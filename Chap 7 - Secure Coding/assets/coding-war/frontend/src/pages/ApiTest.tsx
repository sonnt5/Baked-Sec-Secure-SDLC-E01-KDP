import { useState } from 'react';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/Tabs';
import { useAuthStore } from '../stores/authStore';
import { useThemeStore } from '../stores/themeStore';
import { useNotificationStore } from '../stores/notificationStore';
import { authAPI, problemsAPI, submissionsAPI, contestsAPI, usersAPI, adminAPI } from '../api/endpoints';

interface LogEntry {
  id: string;
  timestamp: string;
  type: 'request' | 'response' | 'error';
  endpoint: string;
  data?: any;
  status?: number;
}

export function ApiTest() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState<string | null>(null);

  // Store states
  const authState = useAuthStore();
  const themeState = useThemeStore();
  const notificationState = useNotificationStore();

  const addLog = (entry: Omit<LogEntry, 'id' | 'timestamp'>) => {
    const newLog: LogEntry = {
      ...entry,
      id: `${Date.now()}-${Math.random()}`,
      timestamp: new Date().toLocaleTimeString(),
    };
    setLogs((prev) => [newLog, ...prev]);
  };

  const clearLogs = () => setLogs([]);

  const testEndpoint = async (
    name: string,
    endpoint: string,
    apiCall: () => Promise<any>
  ) => {
    setLoading(name);
    addLog({ type: 'request', endpoint, data: { message: 'Sending request...' } });

    try {
      const response = await apiCall();
      addLog({
        type: 'response',
        endpoint,
        data: response,
        status: 200,
      });
      useNotificationStore.getState().addNotification({
        type: 'success',
        message: `${name} succeeded`,
      });
    } catch (error: any) {
      addLog({
        type: 'error',
        endpoint,
        data: error.response?.data || error.message,
        status: error.response?.status,
      });
      useNotificationStore.getState().addNotification({
        type: 'error',
        message: `${name} failed: ${error.message}`,
      });
    } finally {
      setLoading(null);
    }
  };

  // API Configuration Display
  const apiConfig = {
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: '1s (exponential backoff)',
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            API & State Management Test Page
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Test API integration, authentication, and Zustand store state management
          </p>
        </div>

        {/* API Configuration */}
        <Card>
          <h2 className="text-xl font-semibold mb-4">API Client Configuration</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-gray-600 dark:text-gray-400">Base URL:</span>
              <p className="font-mono text-sm">{apiConfig.baseURL}</p>
            </div>
            <div>
              <span className="text-sm text-gray-600 dark:text-gray-400">Timeout:</span>
              <p className="font-mono text-sm">{apiConfig.timeout}ms</p>
            </div>
            <div>
              <span className="text-sm text-gray-600 dark:text-gray-400">Retry Attempts:</span>
              <p className="font-mono text-sm">{apiConfig.retryAttempts}</p>
            </div>
            <div>
              <span className="text-sm text-gray-600 dark:text-gray-400">Retry Delay:</span>
              <p className="font-mono text-sm">{apiConfig.retryDelay}</p>
            </div>
          </div>
        </Card>

        {/* Store States */}
        <Card>
          <h2 className="text-xl font-semibold mb-4">Zustand Store States (Real-time)</h2>
          <Tabs defaultValue="auth">
            <TabsList>
              <TabsTrigger value="auth">Auth Store</TabsTrigger>
              <TabsTrigger value="theme">Theme Store</TabsTrigger>
              <TabsTrigger value="notifications">Notification Store</TabsTrigger>
            </TabsList>
            
            <TabsContent value="auth">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Authenticated:</span>
                  <Badge variant={authState.isAuthenticated ? 'success' : 'gray'}>
                    {authState.isAuthenticated ? 'Yes' : 'No'}
                  </Badge>
                </div>
                <div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">User:</span>
                  <pre className="mt-1 p-2 bg-gray-100 dark:bg-gray-800 rounded text-xs overflow-auto">
                    {JSON.stringify(authState.user, null, 2)}
                  </pre>
                </div>
                <div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">Access Token:</span>
                  <p className="font-mono text-xs break-all">
                    {authState.accessToken ? `${authState.accessToken.substring(0, 50)}...` : 'null'}
                  </p>
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="theme">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Current Theme:</span>
                  <Badge>{themeState.theme}</Badge>
                </div>
                <div className="flex gap-2 mt-4">
                  <Button size="sm" onClick={() => themeState.setTheme('light')}>
                    Set Light
                  </Button>
                  <Button size="sm" onClick={() => themeState.setTheme('dark')}>
                    Set Dark
                  </Button>
                  <Button size="sm" onClick={() => themeState.setTheme('system')}>
                    Set System
                  </Button>
                  <Button size="sm" onClick={() => themeState.toggleTheme()}>
                    Toggle
                  </Button>
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="notifications">
              <div className="space-y-2">
                <div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    Active Notifications: {notificationState.notifications.length}
                  </span>
                </div>
                <div className="flex gap-2 mt-4">
                  <Button
                    size="sm"
                    onClick={() =>
                      notificationState.addNotification({
                        type: 'success',
                        message: 'Test success notification',
                      })
                    }
                  >
                    Add Success
                  </Button>
                  <Button
                    size="sm"
                    onClick={() =>
                      notificationState.addNotification({
                        type: 'error',
                        message: 'Test error notification',
                      })
                    }
                  >
                    Add Error
                  </Button>
                  <Button size="sm" onClick={() => notificationState.clearAll()}>
                    Clear All
                  </Button>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </Card>

        {/* API Endpoint Tests */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">API Endpoint Tests</h2>
            <Button size="sm" variant="secondary" onClick={clearLogs}>
              Clear Logs
            </Button>
          </div>

          <Tabs defaultValue="auth">
            <TabsList>
              <TabsTrigger value="auth">Authentication</TabsTrigger>
              <TabsTrigger value="problems">Problems</TabsTrigger>
              <TabsTrigger value="submissions">Submissions</TabsTrigger>
              <TabsTrigger value="contests">Contests</TabsTrigger>
              <TabsTrigger value="users">Users</TabsTrigger>
              <TabsTrigger value="admin">Admin</TabsTrigger>
            </TabsList>

            <TabsContent value="auth">
              <div className="space-y-3">
                <Button
                  onClick={() =>
                    testEndpoint('Register', 'POST /api/auth/register', () =>
                      authAPI.register({
                        username: 'testuser',
                        email: 'test@example.com',
                        password: 'Test1234',
                      })
                    )
                  }
                  disabled={loading === 'Register'}
                  isLoading={loading === 'Register'}
                >
                  Test Register
                </Button>
                <Button
                  onClick={() =>
                    testEndpoint('Login', 'POST /api/auth/login', () =>
                      authAPI.login({
                        email: 'test@example.com',
                        password: 'Test1234',
                      })
                    )
                  }
                  disabled={loading === 'Login'}
                  isLoading={loading === 'Login'}
                >
                  Test Login
                </Button>
                <Button
                  onClick={() =>
                    testEndpoint('Forgot Password', 'POST /api/auth/forgot-password', () =>
                      authAPI.forgotPassword('test@example.com')
                    )
                  }
                  disabled={loading === 'Forgot Password'}
                  isLoading={loading === 'Forgot Password'}
                >
                  Test Forgot Password
                </Button>
              </div>
            </TabsContent>

            <TabsContent value="problems">
              <div className="space-y-3">
                <Button
                  onClick={() =>
                    testEndpoint('List Problems', 'GET /api/problems', () =>
                      problemsAPI.list({ page: 1, limit: 10 })
                    )
                  }
                  disabled={loading === 'List Problems'}
                  isLoading={loading === 'List Problems'}
                >
                  Test List Problems
                </Button>
                <Button
                  onClick={() =>
                    testEndpoint('Get Problem', 'GET /api/problems/:id', () =>
                      problemsAPI.getById('1')
                    )
                  }
                  disabled={loading === 'Get Problem'}
                  isLoading={loading === 'Get Problem'}
                >
                  Test Get Problem by ID
                </Button>
                <Button
                  onClick={() =>
                    testEndpoint('Create Problem', 'POST /api/problems', () =>
                      problemsAPI.create({
                        title: 'Test Problem',
                        difficulty: 'easy',
                        description: 'Test description',
                      })
                    )
                  }
                  disabled={loading === 'Create Problem'}
                  isLoading={loading === 'Create Problem'}
                >
                  Test Create Problem (Admin)
                </Button>
              </div>
            </TabsContent>

            <TabsContent value="submissions">
              <div className="space-y-3">
                <Button
                  onClick={() =>
                    testEndpoint('List Submissions', 'GET /api/submissions', () =>
                      submissionsAPI.list({ page: 1, limit: 10 })
                    )
                  }
                  disabled={loading === 'List Submissions'}
                  isLoading={loading === 'List Submissions'}
                >
                  Test List Submissions
                </Button>
                <Button
                  onClick={() =>
                    testEndpoint('Get Submission', 'GET /api/submissions/:id', () =>
                      submissionsAPI.getById('1')
                    )
                  }
                  disabled={loading === 'Get Submission'}
                  isLoading={loading === 'Get Submission'}
                >
                  Test Get Submission by ID
                </Button>
                <Button
                  onClick={() =>
                    testEndpoint('Create Submission', 'POST /api/submissions', () =>
                      submissionsAPI.create({
                        problemId: '1',
                        language: 'python',
                        sourceCode: 'print("Hello World")',
                      })
                    )
                  }
                  disabled={loading === 'Create Submission'}
                  isLoading={loading === 'Create Submission'}
                >
                  Test Create Submission
                </Button>
              </div>
            </TabsContent>

            <TabsContent value="contests">
              <div className="space-y-3">
                <Button
                  onClick={() =>
                    testEndpoint('List Contests', 'GET /api/contests', () =>
                      contestsAPI.list()
                    )
                  }
                  disabled={loading === 'List Contests'}
                  isLoading={loading === 'List Contests'}
                >
                  Test List Contests
                </Button>
                <Button
                  onClick={() =>
                    testEndpoint('Get Contest', 'GET /api/contests/:id', () =>
                      contestsAPI.getById('1')
                    )
                  }
                  disabled={loading === 'Get Contest'}
                  isLoading={loading === 'Get Contest'}
                >
                  Test Get Contest by ID
                </Button>
                <Button
                  onClick={() =>
                    testEndpoint('Register for Contest', 'POST /api/contests/:id/register', () =>
                      contestsAPI.register('1')
                    )
                  }
                  disabled={loading === 'Register for Contest'}
                  isLoading={loading === 'Register for Contest'}
                >
                  Test Contest Registration
                </Button>
              </div>
            </TabsContent>

            <TabsContent value="users">
              <div className="space-y-3">
                <Button
                  onClick={() =>
                    testEndpoint('Get User', 'GET /api/users/:id', () =>
                      usersAPI.getById('1')
                    )
                  }
                  disabled={loading === 'Get User'}
                  isLoading={loading === 'Get User'}
                >
                  Test Get User by ID
                </Button>
                <Button
                  onClick={() =>
                    testEndpoint('Get User Statistics', 'GET /api/users/:id/statistics', () =>
                      usersAPI.statistics('1')
                    )
                  }
                  disabled={loading === 'Get User Statistics'}
                  isLoading={loading === 'Get User Statistics'}
                >
                  Test Get User Statistics
                </Button>
              </div>
            </TabsContent>

            <TabsContent value="admin">
              <div className="space-y-3">
                <Button
                  onClick={() =>
                    testEndpoint('List Users (Admin)', 'GET /api/admin/users', () =>
                      adminAPI.users({ page: 1, limit: 10 })
                    )
                  }
                  disabled={loading === 'List Users (Admin)'}
                  isLoading={loading === 'List Users (Admin)'}
                >
                  Test List Users (Admin)
                </Button>
                <Button
                  onClick={() =>
                    testEndpoint('Get Statistics (Admin)', 'GET /api/admin/statistics', () =>
                      adminAPI.statistics()
                    )
                  }
                  disabled={loading === 'Get Statistics (Admin)'}
                  isLoading={loading === 'Get Statistics (Admin)'}
                >
                  Test Get Statistics (Admin)
                </Button>
              </div>
            </TabsContent>
          </Tabs>
        </Card>

        {/* Request/Response Logs */}
        <Card>
          <h2 className="text-xl font-semibold mb-4">Request/Response Logs</h2>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {logs.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                No logs yet. Click a test button to see request/response logs.
              </p>
            ) : (
              logs.map((log) => (
                <div
                  key={log.id}
                  className="p-3 rounded border border-gray-200 dark:border-gray-700"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge
                        variant={
                          log.type === 'response'
                            ? 'success'
                            : log.type === 'error'
                            ? 'error'
                            : 'gray'
                        }
                      >
                        {log.type.toUpperCase()}
                      </Badge>
                      <span className="text-sm font-mono">{log.endpoint}</span>
                      {log.status && (
                        <Badge variant={log.status < 400 ? 'success' : 'error'}>
                          {log.status}
                        </Badge>
                      )}
                    </div>
                    <span className="text-xs text-gray-500">{log.timestamp}</span>
                  </div>
                  <pre className="text-xs bg-gray-100 dark:bg-gray-800 p-2 rounded overflow-auto max-h-40">
                    {JSON.stringify(log.data, null, 2)}
                  </pre>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
