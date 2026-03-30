/**
 * Example usage of WebSocket hooks
 * This file demonstrates how to use the WebSocket hooks in components
 */

import { useSubmissionWebSocket, useScoreboardWebSocket } from './useWebSocket';
import type { SubmissionUpdateEvent, ScoreboardUpdateEvent } from '../api/websocket';

// Example 1: Tracking submission status in real-time
export function SubmissionDetailExample({ submissionId }: { submissionId: string }) {
  const handleSubmissionUpdate = (data: SubmissionUpdateEvent) => {
    console.log('Submission update received:', data);
    // Update UI with new submission status
    // e.g., setSubmission(prev => ({ ...prev, ...data }))
  };

  const { isConnected, reconnectAttempts } = useSubmissionWebSocket(
    submissionId,
    handleSubmissionUpdate
  );

  return (
    <div>
      <p>WebSocket Status: {isConnected ? 'Connected' : 'Disconnected'}</p>
      {reconnectAttempts > 0 && (
        <p>Reconnection attempts: {reconnectAttempts}</p>
      )}
      {/* Submission details UI */}
    </div>
  );
}

// Example 2: Tracking contest scoreboard in real-time
export function ContestScoreboardExample({ contestId }: { contestId: string }) {
  const handleScoreboardUpdate = (data: ScoreboardUpdateEvent) => {
    console.log('Scoreboard update received:', data);
    // Update scoreboard UI with new data
    // e.g., setScoreboard(data.entries)
  };

  const { isConnected } = useScoreboardWebSocket(
    contestId,
    handleScoreboardUpdate
  );

  return (
    <div>
      <p>Live Scoreboard {isConnected ? '🟢' : '🔴'}</p>
      {/* Scoreboard table UI */}
    </div>
  );
}

// Example 3: Conditional subscription (only when needed)
export function ConditionalSubscriptionExample({ 
  submissionId, 
  isJudging 
}: { 
  submissionId: string;
  isJudging: boolean;
}) {
  const handleUpdate = (data: SubmissionUpdateEvent) => {
    console.log('Update:', data);
  };

  // Only subscribe when submission is being judged
  useSubmissionWebSocket(submissionId, handleUpdate, isJudging);

  return <div>Submission Status</div>;
}
