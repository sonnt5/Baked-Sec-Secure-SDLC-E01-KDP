import { useState, useCallback, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useContest, useScoreboard } from '../../hooks/queries/useContests';
import { useScoreboardWebSocket } from '../../hooks/useWebSocket';
import type { ScoreboardParticipant, ScoreboardResponse } from '../../types/api';

/**
 * ScoreboardPage — DMOJ-style real-time contest leaderboard
 * - Shows ranked participants with score, problems solved, penalty time
 * - Per-problem breakdown columns
 * - Real-time WebSocket updates with flash animation
 * - Search/filter contestants
 * - Freeze indicator
 */
export default function ScoreboardPage() {
  const { id: contestId } = useParams<{ id: string }>();
  const { data: contest, isLoading: contestLoading } = useContest(contestId || '');
  const { data: initialScoreboard, isLoading: scoreboardLoading } = useScoreboard(contestId || '');

  const [scoreboard, setScoreboard] = useState<ScoreboardResponse | null>(null);
  const [search, setSearch] = useState('');
  const [flashedRows, setFlashedRows] = useState<Set<string>>(new Set());
  const prevRanksRef = useRef<Map<string, number>>(new Map());

  // Initialize scoreboard from API query
  useEffect(() => {
    if (initialScoreboard) {
      setScoreboard(initialScoreboard);
      // Initialize prev ranks
      const ranks = new Map<string, number>();
      initialScoreboard.participants?.forEach((p: ScoreboardParticipant) => {
        ranks.set(p.userId, p.rank);
      });
      prevRanksRef.current = ranks;
    }
  }, [initialScoreboard]);

  // WebSocket update handler — flash changed rows
  const handleScoreboardUpdate = useCallback((data: any) => {
    if (data?.scoreboard) {
      const newScoreboard = data.scoreboard as ScoreboardResponse;
      const newFlashed = new Set<string>();

      // Detect rank changes for flash effect
      newScoreboard.participants?.forEach((p: ScoreboardParticipant) => {
        const prevRank = prevRanksRef.current.get(p.userId);
        if (prevRank !== undefined && prevRank !== p.rank) {
          newFlashed.add(p.userId);
        }
      });

      // Update prev ranks
      const ranks = new Map<string, number>();
      newScoreboard.participants?.forEach((p: ScoreboardParticipant) => {
        ranks.set(p.userId, p.rank);
      });
      prevRanksRef.current = ranks;

      setScoreboard(newScoreboard);
      setFlashedRows(newFlashed);

      // Clear flash after animation
      if (newFlashed.size > 0) {
        setTimeout(() => setFlashedRows(new Set()), 1500);
      }
    }
  }, []);

  // Subscribe to WebSocket scoreboard updates
  useScoreboardWebSocket(contestId, handleScoreboardUpdate, !!contestId);

  if (contestLoading || scoreboardLoading) {
    return (
      <div className="content">
        <div className="panel">
          <div className="panel-body" style={{ textAlign: 'center', padding: 40, color: '#999' }}>
            <span className="spinner" style={{ marginRight: 8 }}></span> Loading scoreboard...
          </div>
        </div>
      </div>
    );
  }

  if (!contest) {
    return (
      <div className="content">
        <div className="alert alert-error">Contest not found.</div>
        <Link to="/contests">← Back to contests</Link>
      </div>
    );
  }

  const participants = scoreboard?.participants || [];
  const isFrozen = scoreboard?.isFrozen || false;

  // Get unique problem IDs for column headers
  const problemIds: string[] = [];
  if (participants.length > 0 && participants[0].problems) {
    participants[0].problems.forEach((p) => {
      if (!problemIds.includes(p.problemId)) {
        problemIds.push(p.problemId);
      }
    });
  }

  // Filter participants by search
  const filtered = search.trim()
    ? participants.filter((p) =>
        p.username.toLowerCase().includes(search.toLowerCase())
      )
    : participants;

  // Contest status
  const now = new Date();
  const startTime = new Date(contest.startTime);
  const endTime = new Date(contest.endTime);
  const isRunning = now >= startTime && now < endTime;
  const isEnded = now >= endTime;

  return (
    <div className="content">
      {/* Breadcrumb */}
      <div style={{ fontSize: 13, marginBottom: 12, color: '#666' }}>
        <Link to="/contests">Contests</Link> / <Link to={`/contests/${contestId}`}>{contest.title}</Link> / Scoreboard
      </div>

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 22 }}>{contest.title} — Scoreboard</h1>
          <div style={{ fontSize: 13, color: '#666', marginTop: 4 }}>
            {contest.scoringRule} Scoring
            {isRunning && <span className="badge badge-green" style={{ marginLeft: 8, fontSize: 11 }}>LIVE</span>}
            {isEnded && <span className="badge badge-gray" style={{ marginLeft: 8, fontSize: 11 }}>ENDED</span>}
            {isFrozen && (
              <span className="badge badge-yellow" style={{ marginLeft: 8, fontSize: 11 }}>
                🧊 FROZEN
              </span>
            )}
          </div>
        </div>

        {/* Search bar */}
        <div>
          <input
            type="text"
            placeholder="Search contestant..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              padding: '6px 12px',
              border: '1px solid #ccc',
              borderRadius: 4,
              fontSize: 13,
              width: 200,
            }}
          />
        </div>
      </div>

      {/* Frozen notice */}
      {isFrozen && (
        <div style={{
          background: '#fff9e6',
          border: '1px solid #ffe58f',
          borderRadius: 4,
          padding: '8px 14px',
          marginBottom: 12,
          fontSize: 13,
          color: '#996b00',
        }}>
          🧊 Scoreboard is frozen. Results may not reflect the latest submissions.
        </div>
      )}

      {/* Scoreboard table */}
      <div className="panel">
        <div className="panel-header" style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>Rankings</span>
          <span style={{ fontWeight: 400, fontSize: 12, color: '#666' }}>
            {filtered.length} contestant{filtered.length !== 1 ? 's' : ''}
          </span>
        </div>

        {participants.length === 0 ? (
          <div className="panel-body" style={{ textAlign: 'center', padding: 30, color: '#999' }}>
            No participants yet. Be the first to register!
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th style={{ width: 50, textAlign: 'center' }}>#</th>
                  <th>User</th>
                  <th style={{ width: 80, textAlign: 'center' }}>Score</th>
                  {contest.scoringRule === 'ACM' && (
                    <th style={{ width: 80, textAlign: 'center' }}>Penalty</th>
                  )}
                  {problemIds.map((_, i) => (
                    <th key={i} style={{ width: 70, textAlign: 'center', fontSize: 12 }}>
                      {String.fromCharCode(65 + i)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map((p) => {
                  const isFlashed = flashedRows.has(p.userId);
                  return (
                    <tr
                      key={p.userId}
                      style={{
                        background: isFlashed ? '#fffbe6' : undefined,
                        transition: 'background 0.5s ease',
                      }}
                    >
                      {/* Rank */}
                      <td style={{
                        textAlign: 'center',
                        fontWeight: 700,
                        fontSize: 14,
                        color: p.rank <= 3 ? ['#d4a017', '#a0a0a0', '#cd7f32'][p.rank - 1] : '#666',
                      }}>
                        {p.rank <= 3 ? ['🥇', '🥈', '🥉'][p.rank - 1] : p.rank}
                      </td>

                      {/* Username */}
                      <td style={{ fontWeight: 500 }}>{p.username}</td>

                      {/* Score */}
                      <td style={{
                        textAlign: 'center',
                        fontWeight: 700,
                        fontSize: 15,
                        color: p.solvedCount > 0 ? '#28a745' : '#666',
                      }}>
                        {p.totalScore}
                      </td>

                      {/* Penalty (ACM only) */}
                      {contest.scoringRule === 'ACM' && (
                        <td style={{ textAlign: 'center', fontSize: 12, color: '#666' }}>
                          {p.penaltyTime > 0 ? p.penaltyTime : '—'}
                        </td>
                      )}

                      {/* Per-problem breakdown */}
                      {problemIds.map((pid, i) => {
                        const ps = p.problems?.find((pp) => pp.problemId === pid);
                        if (!ps) return <td key={i} style={{ textAlign: 'center' }}>—</td>;

                        const isAccepted = ps.score > 0;
                        const hasTried = ps.attempts > 0;

                        return (
                          <td key={i} style={{ textAlign: 'center', padding: '4px 6px' }}>
                            {isAccepted ? (
                              <div style={{
                                background: '#d4edda',
                                borderRadius: 3,
                                padding: '2px 6px',
                                display: 'inline-block',
                                minWidth: 40,
                              }}>
                                <div style={{ color: '#28a745', fontWeight: 700, fontSize: 13 }}>
                                  {contest.scoringRule === 'ACM' ? '+' : ps.score}
                                  {ps.attempts > 1 && (
                                    <span style={{ fontSize: 10, color: '#666' }}>/{ps.attempts}</span>
                                  )}
                                </div>
                                {contest.scoringRule === 'ACM' && ps.penaltyMinutes > 0 && (
                                  <div style={{ fontSize: 10, color: '#666' }}>{ps.penaltyMinutes}m</div>
                                )}
                              </div>
                            ) : hasTried ? (
                              <div style={{
                                background: '#f8d7da',
                                borderRadius: 3,
                                padding: '2px 6px',
                                display: 'inline-block',
                                minWidth: 40,
                              }}>
                                <div style={{ color: '#dc3545', fontWeight: 700, fontSize: 13 }}>
                                  -{ps.attempts}
                                </div>
                              </div>
                            ) : (
                              <span style={{ color: '#ccc' }}>·</span>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
