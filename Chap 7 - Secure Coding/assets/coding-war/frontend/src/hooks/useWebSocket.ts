import { useEffect, useRef } from 'react';
import { wsClient } from '../api/websocket';
import type { SubmissionUpdateEvent, ScoreboardUpdateEvent } from '../api/websocket';

/**
 * Base WebSocket hook that manages connection lifecycle
 * Connects on mount and disconnects on unmount
 */
export function useWebSocket() {
  const isConnectedRef = useRef(false);

  useEffect(() => {
    if (!isConnectedRef.current) {
      wsClient.connect();
      isConnectedRef.current = true;
    }

    return () => {
      // Only disconnect if this is the last component using WebSocket
      // In a real app, you might want to implement reference counting
      wsClient.disconnect();
      isConnectedRef.current = false;
    };
  }, []);

  return {
    isConnected: wsClient.isConnected(),
    reconnectAttempts: wsClient.getReconnectAttempts(),
  };
}

/**
 * Hook for subscribing to submission status updates
 * Automatically manages subscription lifecycle
 * 
 * @param submissionId - The ID of the submission to track
 * @param onUpdate - Callback function called when submission updates are received
 * @param enabled - Whether the subscription is active (default: true)
 */
export function useSubmissionWebSocket(
  submissionId: string | undefined,
  onUpdate: (data: SubmissionUpdateEvent) => void,
  enabled: boolean = true
) {
  const { isConnected, reconnectAttempts } = useWebSocket();
  const callbackRef = useRef(onUpdate);

  // Keep callback ref up to date
  useEffect(() => {
    callbackRef.current = onUpdate;
  }, [onUpdate]);

  useEffect(() => {
    if (!enabled || !submissionId || !isConnected) {
      return;
    }

    // Wrapper to use the latest callback
    const handleUpdate = (data: SubmissionUpdateEvent) => {
      callbackRef.current(data);
    };

    wsClient.subscribeToSubmission(submissionId, handleUpdate);

    return () => {
      wsClient.unsubscribeFromSubmission(submissionId);
    };
  }, [submissionId, enabled, isConnected]);

  return {
    isConnected,
    reconnectAttempts,
  };
}

/**
 * Hook for subscribing to contest scoreboard updates
 * Automatically manages subscription lifecycle
 * 
 * @param contestId - The ID of the contest to track
 * @param onUpdate - Callback function called when scoreboard updates are received
 * @param enabled - Whether the subscription is active (default: true)
 */
export function useScoreboardWebSocket(
  contestId: string | undefined,
  onUpdate: (data: ScoreboardUpdateEvent) => void,
  enabled: boolean = true
) {
  const { isConnected, reconnectAttempts } = useWebSocket();
  const callbackRef = useRef(onUpdate);

  // Keep callback ref up to date
  useEffect(() => {
    callbackRef.current = onUpdate;
  }, [onUpdate]);

  useEffect(() => {
    if (!enabled || !contestId || !isConnected) {
      return;
    }

    // Wrapper to use the latest callback
    const handleUpdate = (data: ScoreboardUpdateEvent) => {
      callbackRef.current(data);
    };

    wsClient.subscribeToScoreboard(contestId, handleUpdate);

    return () => {
      wsClient.unsubscribeFromScoreboard(contestId);
    };
  }, [contestId, enabled, isConnected]);

  return {
    isConnected,
    reconnectAttempts,
  };
}
