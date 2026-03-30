import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useContest, useRegisterContest } from '../../hooks/queries/useContests';
import { useAuthStore } from '../../stores/authStore';

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

function getTimeRemaining(endTime: string) {
  const diff = new Date(endTime).getTime() - Date.now();
  if (diff <= 0) return 'Ended';
  const hours = Math.floor(diff / 3600000);
  const mins = Math.floor((diff % 3600000) / 60000);
  const secs = Math.floor((diff % 60000) / 1000);
  if (hours > 24) {
    const days = Math.floor(hours / 24);
    return `${days}d ${hours % 24}h`;
  }
  return `${hours}h ${mins}m ${secs}s`;
}

export default function ContestDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { isAuthenticated } = useAuthStore();
  const { data: contest, isLoading, isError } = useContest(id || '');
  const registerMutation = useRegisterContest();
  const [timeLeft, setTimeLeft] = useState('');
  const [activeTab, setActiveTab] = useState<'info' | 'problems' | 'scoreboard'>('info');

  // Update countdown every second
  useEffect(() => {
    if (!contest) return;
    const now = new Date();
    const start = new Date(contest.startTime);
    const end = new Date(contest.endTime);

    if (now < start || (now >= start && now <= end)) {
      const target = now < start ? contest.startTime : contest.endTime;
      const timer = setInterval(() => {
        setTimeLeft(getTimeRemaining(target));
      }, 1000);
      setTimeLeft(getTimeRemaining(target));
      return () => clearInterval(timer);
    } else {
      setTimeLeft('Ended');
    }
  }, [contest]);

  const handleRegister = () => {
    if (id) registerMutation.mutate(id);
  };

  if (isLoading) {
    return (
      <div className="content">
        <div className="panel">
          <div className="panel-body" style={{ textAlign: 'center', padding: 40, color: '#999' }}>
            <span className="spinner" style={{ marginRight: 8 }}></span> Loading contest...
          </div>
        </div>
      </div>
    );
  }

  if (isError || !contest) {
    return (
      <div className="content">
        <div className="alert alert-error">Contest not found or failed to load.</div>
        <Link to="/contests">← Back to contests</Link>
      </div>
    );
  }

  const now = new Date();
  const start = new Date(contest.startTime);
  const end = new Date(contest.endTime);
  const isUpcoming = now < start;
  const isRunning = now >= start && now <= end;
  const isEnded = now > end;

  return (
    <div className="content">
      {/* Breadcrumb */}
      <div style={{ fontSize: 13, marginBottom: 12, color: '#666' }}>
        <Link to="/contests">Contests</Link> / {contest.title}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 15 }}>
        <div>
          <h1 style={{ marginBottom: 4 }}>{contest.title}</h1>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', fontSize: 13 }}>
            <span className={`badge ${isRunning ? 'badge-green' : isUpcoming ? 'badge-blue' : 'badge-gray'}`}>
              {isRunning ? 'Running' : isUpcoming ? 'Upcoming' : 'Ended'}
            </span>
            <span className="badge badge-gray">{contest.scoringType?.toUpperCase() || 'ACM'}</span>
            {timeLeft && timeLeft !== 'Ended' && (
              <span style={{ color: '#666' }}>⏱ {isUpcoming ? 'Starts in' : 'Ends in'}: <strong>{timeLeft}</strong></span>
            )}
          </div>
        </div>
        {isAuthenticated && (isUpcoming || isRunning) && (
          <button
            className="btn btn-primary"
            onClick={handleRegister}
            disabled={registerMutation.isPending}
          >
            {registerMutation.isPending ? 'Registering...' : 'Register'}
          </button>
        )}
      </div>

      {registerMutation.isSuccess && (
        <div className="alert alert-success">Successfully registered for this contest!</div>
      )}
      {registerMutation.isError && (
        <div className="alert alert-error">
          {(registerMutation.error as any)?.response?.data?.message || 'Failed to register.'}
        </div>
      )}

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 0, borderBottom: '2px solid #ddd', marginBottom: 15 }}>
        {(['info', 'problems', 'scoreboard'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '8px 16px',
              fontSize: 13,
              fontWeight: 600,
              background: 'none',
              border: 'none',
              borderBottom: activeTab === tab ? '2px solid #1a73e8' : '2px solid transparent',
              marginBottom: -2,
              color: activeTab === tab ? '#1a73e8' : '#666',
              cursor: 'pointer',
              textTransform: 'capitalize',
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === 'info' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: 20 }}>
          <div className="panel">
            <div className="panel-header">Description</div>
            <div className="panel-body" style={{ lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
              {contest.description || 'No description available.'}
            </div>
          </div>
          <div>
            <div className="panel">
              <div className="panel-header">Details</div>
              <div className="panel-body" style={{ fontSize: 13 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid #eee' }}>
                  <span>Start</span>
                  <strong>{formatDate(contest.startTime)}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid #eee' }}>
                  <span>End</span>
                  <strong>{formatDate(contest.endTime)}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid #eee' }}>
                  <span>Scoring</span>
                  <strong>{contest.scoringType?.toUpperCase() || 'ACM'}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}>
                  <span>Participants</span>
                  <strong>{contest.participantCount ?? 0}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'problems' && (
        <div>
          {contest.problems && contest.problems.length > 0 ? (
            <div className="panel">
              {isUpcoming && (
                <div style={{ padding: '8px 16px', background: '#fff8e1', fontSize: 13, color: '#795548', borderBottom: '1px solid #ffe082' }}>
                  ⏳ Contest hasn't started yet — problems listed below for reference.
                </div>
              )}
              <table>
                <thead>
                  <tr>
                    <th style={{ width: 50 }}>#</th>
                    <th>Problem</th>
                    <th style={{ width: 90 }}>Difficulty</th>
                    {contest.scoringRule === 'IOI' && <th style={{ width: 70 }}>Points</th>}
                  </tr>
                </thead>
                <tbody>
                  {contest.problems.map((p: any, i: number) => (
                    <tr key={p.problemId}>
                      <td style={{ fontWeight: 700, color: '#555' }}>{String.fromCharCode(65 + i)}</td>
                      <td>
                        <Link to={`/problems/${p.problemId}`} style={{ fontWeight: 500 }}>
                          {p.title || `Problem ${String.fromCharCode(65 + i)}`}
                        </Link>
                      </td>
                      <td>
                        <span className={`badge ${p.difficulty === 'EASY' ? 'badge-green' : p.difficulty === 'MEDIUM' ? 'badge-yellow' : 'badge-red'}`} style={{ fontSize: 10 }}>
                          {p.difficulty || 'EASY'}
                        </span>
                      </td>
                      {contest.scoringRule === 'IOI' && <td>{p.points ?? 100}</td>}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="panel">
              <div className="panel-body" style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                No problems assigned to this contest yet.
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'scoreboard' && (
        <div>
          {!isRunning && !isEnded ? (
            <div className="panel">
              <div className="panel-body" style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                Scoreboard will be available when the contest starts.
              </div>
            </div>
          ) : (
            <div>
              <Link
                to={`/contests/${id}/scoreboard`}
                className="btn btn-primary"
                style={{ marginBottom: 15, display: 'inline-block' }}
              >
                📊 Open Full Scoreboard
              </Link>
              <div className="panel">
                <div className="panel-body" style={{ textAlign: 'center', padding: 30, color: '#666', fontSize: 13 }}>
                  Click the button above to view the full real-time scoreboard with rankings and per-problem breakdown.
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
