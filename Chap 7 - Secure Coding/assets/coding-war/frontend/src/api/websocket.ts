import { io, Socket } from 'socket.io-client';
import { useAuthStore } from '../stores/authStore';
import type { Submission, ScoreboardEntry } from '../types/api';

// WebSocket event types
export interface SubmissionUpdateEvent {
  submissionId: string;
  status: Submission['status'];
  verdict?: Submission['verdict'];
  executionTime?: number;
  memoryUsed?: number;
  testCaseResults?: Submission['testCaseResults'];
  compilationError?: string;
}

export interface ScoreboardUpdateEvent {
  contestId: string;
  entries: ScoreboardEntry[];
  isFrozen: boolean;
}

class WebSocketClient {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private isConnecting = false;

  /**
   * Establish WebSocket connection with JWT authentication
   */
  connect(): void {
    if (this.socket?.connected || this.isConnecting) {
      return;
    }

    this.isConnecting = true;
    const token = useAuthStore.getState().accessToken;

    if (!token) {
      console.warn('Cannot connect to WebSocket: No access token available');
      this.isConnecting = false;
      return;
    }

    const wsUrl = import.meta.env.VITE_WS_URL || 'http://localhost:3000';

    this.socket = io(wsUrl, {
      auth: { token },
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: this.maxReconnectAttempts,
    });

    this.setupEventHandlers();
    this.isConnecting = false;
  }

  /**
   * Setup event handlers for connection lifecycle
   */
  private setupEventHandlers(): void {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.reconnectAttempts++;

      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('Max reconnection attempts reached. Consider falling back to polling.');
      }
    });
  }

  /**
   * Subscribe to submission status updates
   */
  subscribeToSubmission(
    submissionId: string,
    callback: (data: SubmissionUpdateEvent) => void
  ): void {
    if (!this.socket?.connected) {
      console.warn('Cannot subscribe: WebSocket not connected');
      return;
    }

    this.socket.emit('subscribe:submission', { submissionId });
    this.socket.on('submission:update', callback);
    this.socket.on('submission:complete', callback);
  }

  /**
   * Unsubscribe from submission status updates
   */
  unsubscribeFromSubmission(submissionId: string): void {
    if (!this.socket) return;

    this.socket.emit('unsubscribe:submission', { submissionId });
    this.socket.off('submission:update');
    this.socket.off('submission:complete');
  }

  /**
   * Subscribe to contest scoreboard updates
   */
  subscribeToScoreboard(
    contestId: string,
    callback: (data: ScoreboardUpdateEvent) => void
  ): void {
    if (!this.socket?.connected) {
      console.warn('Cannot subscribe: WebSocket not connected');
      return;
    }

    this.socket.emit('subscribe:scoreboard', { contestId });
    this.socket.on('scoreboard:update', callback);
  }

  /**
   * Unsubscribe from contest scoreboard updates
   */
  unsubscribeFromScoreboard(contestId: string): void {
    if (!this.socket) return;

    this.socket.emit('unsubscribe:scoreboard', { contestId });
    this.socket.off('scoreboard:update');
  }

  /**
   * Disconnect and cleanup WebSocket connection
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.reconnectAttempts = 0;
    }
  }

  /**
   * Check if WebSocket is currently connected
   */
  isConnected(): boolean {
    return this.socket?.connected ?? false;
  }

  /**
   * Get current reconnection attempt count
   */
  getReconnectAttempts(): number {
    return this.reconnectAttempts;
  }
}

export const wsClient = new WebSocketClient();
