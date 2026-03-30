import { useState, useCallback } from 'react';
import { useSubmissionWebSocket, useScoreboardWebSocket } from '../hooks/useWebSocket';
import type { SubmissionUpdateEvent, ScoreboardUpdateEvent } from '../api/websocket';

export default function WebSocketTest() {
  const [submissionId, setSubmissionId] = useState('');
  const [contestId, setContestId] = useState('');
  const [submissionEnabled, setSubmissionEnabled] = useState(false);
  const [scoreboardEnabled, setScoreboardEnabled] = useState(false);
  const [submissionUpdates, setSubmissionUpdates] = useState<SubmissionUpdateEvent[]>([]);
  const [scoreboardUpdates, setScoreboardUpdates] = useState<ScoreboardUpdateEvent[]>([]);

  // Submission WebSocket
  const handleSubmissionUpdate = useCallback((data: SubmissionUpdateEvent) => {
    console.log('📨 Submission update received:', data);
    setSubmissionUpdates(prev => [...prev, { ...data, timestamp: new Date().toISOString() } as any]);
  }, []);

  const submissionWS = useSubmissionWebSocket(
    submissionEnabled ? submissionId : undefined,
    handleSubmissionUpdate,
    submissionEnabled
  );

  // Scoreboard WebSocket
  const handleScoreboardUpdate = useCallback((data: ScoreboardUpdateEvent) => {
    console.log('📊 Scoreboard update received:', data);
    setScoreboardUpdates(prev => [...prev, { ...data, timestamp: new Date().toISOString() } as any]);
  }, []);

  const scoreboardWS = useScoreboardWebSocket(
    scoreboardEnabled ? contestId : undefined,
    handleScoreboardUpdate,
    scoreboardEnabled
  );

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">WebSocket Test Page</h1>

        {/* Connection Status */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Connection Status</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Submission WebSocket</p>
              <div className="flex items-center gap-2 mt-1">
                <div className={`w-3 h-3 rounded-full ${submissionWS.isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="font-medium">{submissionWS.isConnected ? 'Connected' : 'Disconnected'}</span>
                {submissionWS.reconnectAttempts > 0 && (
                  <span className="text-sm text-orange-600">
                    (Reconnect attempts: {submissionWS.reconnectAttempts})
                  </span>
                )}
              </div>
            </div>
            <div>
              <p className="text-sm text-gray-600">Scoreboard WebSocket</p>
              <div className="flex items-center gap-2 mt-1">
                <div className={`w-3 h-3 rounded-full ${scoreboardWS.isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="font-medium">{scoreboardWS.isConnected ? 'Connected' : 'Disconnected'}</span>
                {scoreboardWS.reconnectAttempts > 0 && (
                  <span className="text-sm text-orange-600">
                    (Reconnect attempts: {scoreboardWS.reconnectAttempts})
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Submission Test */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Test Submission Updates</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Submission ID
              </label>
              <input
                type="text"
                value={submissionId}
                onChange={(e) => setSubmissionId(e.target.value)}
                placeholder="Enter submission ID (e.g., sub_123)"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button
              onClick={() => {
                setSubmissionEnabled(!submissionEnabled);
                if (!submissionEnabled) {
                  setSubmissionUpdates([]);
                }
              }}
              disabled={!submissionId}
              className={`px-6 py-2 rounded-lg font-medium ${
                submissionEnabled
                  ? 'bg-red-500 hover:bg-red-600 text-white'
                  : 'bg-blue-500 hover:bg-blue-600 text-white disabled:bg-gray-300 disabled:cursor-not-allowed'
              }`}
            >
              {submissionEnabled ? 'Stop Listening' : 'Start Listening'}
            </button>
          </div>

          {/* Submission Updates Log */}
          <div className="mt-6">
            <h3 className="font-semibold mb-2">Updates Received ({submissionUpdates.length})</h3>
            <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
              {submissionUpdates.length === 0 ? (
                <p className="text-gray-500 text-sm">No updates yet. Start listening to receive updates.</p>
              ) : (
                <div className="space-y-2">
                  {submissionUpdates.map((update: any, index) => (
                    <div key={index} className="bg-white p-3 rounded border border-gray-200">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-mono text-xs text-gray-500">{update.timestamp}</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          update.status === 'accepted' ? 'bg-green-100 text-green-800' :
                          update.status === 'running' ? 'bg-blue-100 text-blue-800' :
                          update.status === 'queued' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {update.status}
                        </span>
                      </div>
                      <pre className="text-xs overflow-x-auto">{JSON.stringify(update, null, 2)}</pre>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Scoreboard Test */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Test Scoreboard Updates</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Contest ID
              </label>
              <input
                type="text"
                value={contestId}
                onChange={(e) => setContestId(e.target.value)}
                placeholder="Enter contest ID (e.g., contest_123)"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button
              onClick={() => {
                setScoreboardEnabled(!scoreboardEnabled);
                if (!scoreboardEnabled) {
                  setScoreboardUpdates([]);
                }
              }}
              disabled={!contestId}
              className={`px-6 py-2 rounded-lg font-medium ${
                scoreboardEnabled
                  ? 'bg-red-500 hover:bg-red-600 text-white'
                  : 'bg-blue-500 hover:bg-blue-600 text-white disabled:bg-gray-300 disabled:cursor-not-allowed'
              }`}
            >
              {scoreboardEnabled ? 'Stop Listening' : 'Start Listening'}
            </button>
          </div>

          {/* Scoreboard Updates Log */}
          <div className="mt-6">
            <h3 className="font-semibold mb-2">Updates Received ({scoreboardUpdates.length})</h3>
            <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
              {scoreboardUpdates.length === 0 ? (
                <p className="text-gray-500 text-sm">No updates yet. Start listening to receive updates.</p>
              ) : (
                <div className="space-y-2">
                  {scoreboardUpdates.map((update: any, index) => (
                    <div key={index} className="bg-white p-3 rounded border border-gray-200">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-mono text-xs text-gray-500">{update.timestamp}</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          update.isFrozen ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                        }`}>
                          {update.isFrozen ? 'Frozen' : 'Live'}
                        </span>
                      </div>
                      <pre className="text-xs overflow-x-auto">{JSON.stringify(update, null, 2)}</pre>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-6">
          <h3 className="font-semibold text-blue-900 mb-2">📝 Testing Instructions</h3>
          <ol className="list-decimal list-inside space-y-2 text-sm text-blue-800">
            <li>Make sure backend is running on port 3000</li>
            <li>Open browser console (F12) to see WebSocket connection logs</li>
            <li>Enter a submission ID and click "Start Listening"</li>
            <li>Use backend API or Postman to trigger submission updates</li>
            <li>Watch real-time updates appear on this page</li>
            <li>Check connection status indicators at the top</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
