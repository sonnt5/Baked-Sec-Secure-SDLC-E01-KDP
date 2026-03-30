# WebSocket Integration

This module provides WebSocket connectivity for real-time features in the Coding War frontend application.

## Overview

The WebSocket client uses Socket.io to establish real-time bidirectional communication with the backend server. It supports:

- JWT token authentication
- Automatic reconnection with exponential backoff (max 5 attempts)
- Subscription-based event handling
- Connection lifecycle management

## Architecture

### WebSocket Client (`src/api/websocket.ts`)

The `WebSocketClient` class manages the WebSocket connection and provides methods for subscribing to real-time events.

**Key Features:**
- Singleton pattern via exported `wsClient` instance
- Automatic JWT token attachment from auth store
- Configurable WebSocket URL via `VITE_WS_URL` environment variable
- Connection state tracking
- Reconnection attempt counting

**Methods:**
- `connect()` - Establish WebSocket connection
- `disconnect()` - Close connection and cleanup
- `subscribeToSubmission(submissionId, callback)` - Subscribe to submission updates
- `unsubscribeFromSubmission(submissionId)` - Unsubscribe from submission updates
- `subscribeToScoreboard(contestId, callback)` - Subscribe to scoreboard updates
- `unsubscribeFromScoreboard(contestId)` - Unsubscribe from scoreboard updates
- `isConnected()` - Check connection status
- `getReconnectAttempts()` - Get current reconnection attempt count

### WebSocket Hooks (`src/hooks/useWebSocket.ts`)

React hooks that provide a declarative API for WebSocket subscriptions with automatic lifecycle management.

#### `useWebSocket()`

Base hook that manages WebSocket connection lifecycle. Connects on mount and disconnects on unmount.

**Returns:**
```typescript
{
  isConnected: boolean;
  reconnectAttempts: number;
}
```

#### `useSubmissionWebSocket(submissionId, onUpdate, enabled?)`

Hook for subscribing to submission status updates.

**Parameters:**
- `submissionId: string | undefined` - The submission ID to track
- `onUpdate: (data: SubmissionUpdateEvent) => void` - Callback for updates
- `enabled: boolean` - Whether subscription is active (default: true)

**Returns:**
```typescript
{
  isConnected: boolean;
  reconnectAttempts: number;
}
```

**Example:**
```typescript
function SubmissionDetail({ submissionId }) {
  const handleUpdate = (data) => {
    console.log('Status:', data.status);
    console.log('Verdict:', data.verdict);
  };

  const { isConnected } = useSubmissionWebSocket(
    submissionId,
    handleUpdate
  );

  return <div>Connected: {isConnected ? '✓' : '✗'}</div>;
}
```

#### `useScoreboardWebSocket(contestId, onUpdate, enabled?)`

Hook for subscribing to contest scoreboard updates.

**Parameters:**
- `contestId: string | undefined` - The contest ID to track
- `onUpdate: (data: ScoreboardUpdateEvent) => void` - Callback for updates
- `enabled: boolean` - Whether subscription is active (default: true)

**Returns:**
```typescript
{
  isConnected: boolean;
  reconnectAttempts: number;
}
```

**Example:**
```typescript
function ContestScoreboard({ contestId }) {
  const [scoreboard, setScoreboard] = useState([]);

  const handleUpdate = (data) => {
    setScoreboard(data.entries);
  };

  useScoreboardWebSocket(contestId, handleUpdate);

  return <ScoreboardTable entries={scoreboard} />;
}
```

## Event Types

### SubmissionUpdateEvent

Emitted when a submission status changes during judging.

```typescript
interface SubmissionUpdateEvent {
  submissionId: string;
  status: 'queued' | 'compiling' | 'running' | 'judged';
  verdict?: 'accepted' | 'wrong_answer' | 'time_limit_exceeded' | 
            'memory_limit_exceeded' | 'runtime_error' | 'compilation_error';
  executionTime?: number;
  memoryUsed?: number;
  testCaseResults?: TestCaseResult[];
  compilationError?: string;
}
```

### ScoreboardUpdateEvent

Emitted when contest scoreboard changes (new submission, rank change, etc.).

```typescript
interface ScoreboardUpdateEvent {
  contestId: string;
  entries: ScoreboardEntry[];
  isFrozen: boolean;
}
```

## Configuration

Set the WebSocket URL in your `.env` file:

```env
VITE_WS_URL=http://localhost:3000
```

For production:
```env
VITE_WS_URL=https://api.codingwar.com
```

## Connection Lifecycle

1. **Connect**: Call `wsClient.connect()` or use `useWebSocket()` hook
2. **Authenticate**: JWT token automatically attached from auth store
3. **Subscribe**: Subscribe to specific events (submission, scoreboard)
4. **Receive Updates**: Callbacks invoked when events are received
5. **Unsubscribe**: Automatically handled by hooks on unmount
6. **Disconnect**: Connection closed when component unmounts

## Reconnection Strategy

The client implements exponential backoff for reconnection:

- Initial delay: 1000ms
- Max delay: 5000ms
- Max attempts: 5

After 5 failed attempts, the client stops trying. The UI should fall back to polling in this case.

## Error Handling

Connection errors are logged to the console. The hooks expose `reconnectAttempts` to allow UI feedback:

```typescript
const { isConnected, reconnectAttempts } = useSubmissionWebSocket(
  submissionId,
  handleUpdate
);

if (reconnectAttempts >= 3) {
  return <div>Connection issues. Falling back to polling...</div>;
}
```

## Best Practices

1. **Use hooks for automatic cleanup**: Prefer `useSubmissionWebSocket` and `useScoreboardWebSocket` over direct `wsClient` usage
2. **Conditional subscriptions**: Use the `enabled` parameter to control when subscriptions are active
3. **Stable callbacks**: Use `useCallback` for update handlers to prevent unnecessary resubscriptions
4. **Fallback to polling**: Implement polling fallback when `reconnectAttempts >= maxReconnectAttempts`
5. **Connection status UI**: Show connection status to users for transparency

## Testing

To test WebSocket functionality:

1. Start the backend server with WebSocket support
2. Set `VITE_WS_URL` in `.env.local`
3. Use browser DevTools Network tab (filter by WS) to inspect WebSocket traffic
4. Submit a solution and watch for real-time status updates
5. Open multiple browser tabs to test scoreboard updates

## Troubleshooting

**Connection fails immediately:**
- Check `VITE_WS_URL` is correct
- Verify backend WebSocket server is running
- Check JWT token is valid in auth store

**No updates received:**
- Verify subscription was successful (check console logs)
- Check backend is emitting events correctly
- Inspect WebSocket frames in DevTools

**Memory leaks:**
- Ensure hooks are used (automatic cleanup)
- If using `wsClient` directly, always call unsubscribe methods
- Verify `disconnect()` is called when appropriate
