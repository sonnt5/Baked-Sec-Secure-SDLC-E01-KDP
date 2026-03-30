import { useParams, Link, useNavigate } from 'react-router-dom';
import { useSubmission } from '../../hooks/queries/useSubmissions';

const VERDICT_MAP: Record<string, { label: string; short: string; cls: string; color: string; desc: string }> = {
  ACCEPTED: { label: 'Accepted', short: 'AC', cls: 'badge-green', color: '#28a745', desc: 'All test cases passed.' },
  WRONG_ANSWER: { label: 'Wrong Answer', short: 'WA', cls: 'badge-red', color: '#dc3545', desc: 'Output did not match expected.' },
  TIME_LIMIT_EXCEEDED: { label: 'Time Limit Exceeded', short: 'TLE', cls: 'badge-yellow', color: '#ffc107', desc: 'Exceeded time limit.' },
  MEMORY_LIMIT_EXCEEDED: { label: 'Memory Limit Exceeded', short: 'MLE', cls: 'badge-yellow', color: '#ffc107', desc: 'Exceeded memory limit.' },
  RUNTIME_ERROR: { label: 'Runtime Error', short: 'RE', cls: 'badge-red', color: '#dc3545', desc: 'Program crashed.' },
  COMPILATION_ERROR: { label: 'Compilation Error', short: 'CE', cls: 'badge-red', color: '#dc3545', desc: 'Code failed to compile.' },
  QUEUED: { label: 'Queued', short: '...', cls: 'badge-gray', color: '#999', desc: 'Waiting in judge queue...' },
  COMPILING: { label: 'Compiling', short: '⟳', cls: 'badge-blue', color: '#007bff', desc: 'Compiling source code...' },
  RUNNING: { label: 'Running', short: '▶', cls: 'badge-blue', color: '#007bff', desc: 'Running test cases...' },
};

const FINAL_STATUSES = ['ACCEPTED', 'WRONG_ANSWER', 'TIME_LIMIT_EXCEEDED', 'MEMORY_LIMIT_EXCEEDED', 'RUNTIME_ERROR', 'COMPILATION_ERROR'];

export default function SubmissionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: sub, isLoading, isError } = useSubmission(id || '');

  if (isLoading) {
    return (
      <div className="content">
        <div className="panel">
          <div className="panel-body" style={{ textAlign: 'center', padding: 40, color: '#999' }}>
            <span className="spinner" style={{ marginRight: 8 }}></span> Loading submission...
          </div>
        </div>
      </div>
    );
  }

  if (isError || !sub) {
    return (
      <div className="content">
        <div className="alert alert-error">Submission not found.</div>
        <Link to="/submissions">← Back to submissions</Link>
      </div>
    );
  }

  const verdict = VERDICT_MAP[sub.status] || VERDICT_MAP[sub.verdict || ''] || { label: sub.status, short: '?', cls: 'badge-gray', color: '#999', desc: '' };
  const isFinal = FINAL_STATUSES.includes(sub.status);
  const testCases: any[] = sub.testCaseResults || [];
  const passedCount = testCases.filter((tc: any) => tc.status === 'ACCEPTED').length;
  const totalCount = testCases.length;

  return (
    <div className="content">
      {/* Breadcrumb */}
      <div style={{ fontSize: 13, marginBottom: 12, color: '#666' }}>
        <Link to="/submissions">Submissions</Link> / {id?.slice(0, 8)}
      </div>

      {/* ── Main verdict banner (DMOJ-style) ── */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        padding: '14px 18px',
        marginBottom: 16,
        background: `${verdict.color}11`,
        border: `2px solid ${verdict.color}44`,
        borderRadius: 6,
      }}>
        <div style={{
          fontSize: 28,
          fontWeight: 700,
          color: verdict.color,
          minWidth: 60,
          textAlign: 'center',
          letterSpacing: 1,
        }}>
          {verdict.short}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 16, fontWeight: 600, color: '#333' }}>
            {verdict.label}
            {!isFinal && <span className="spinner" style={{ marginLeft: 8 }}></span>}
          </div>
          <div style={{ fontSize: 13, color: '#666', marginTop: 2 }}>{verdict.desc}</div>
        </div>
        <div style={{ display: 'flex', gap: 24, fontSize: 13 }}>
          {sub.executionTime != null && (
            <div style={{ textAlign: 'center' }}>
              <div style={{ color: '#999', fontSize: 11 }}>TIME</div>
              <div style={{ fontWeight: 700, fontSize: 18, color: '#333' }}>{sub.executionTime}<span style={{ fontSize: 11, color: '#999' }}>ms</span></div>
            </div>
          )}
          {sub.memoryUsed != null && (
            <div style={{ textAlign: 'center' }}>
              <div style={{ color: '#999', fontSize: 11 }}>MEMORY</div>
              <div style={{ fontWeight: 700, fontSize: 18, color: '#333' }}>{sub.memoryUsed}<span style={{ fontSize: 11, color: '#999' }}>MB</span></div>
            </div>
          )}
        </div>
        {/* Resubmit button for non-accepted final verdicts */}
        {isFinal && sub.status !== 'ACCEPTED' && sub.problemId && (
          <button
            className="btn btn-primary"
            style={{ whiteSpace: 'nowrap', fontSize: 13 }}
            onClick={() => navigate(`/problems/${sub.problemId}`, {
              state: { prefillCode: sub.sourceCode, prefillLanguage: sub.language }
            })}
          >
            🔄 Resubmit
          </button>
        )}
      </div>

      {/* ── Test case mini-grid (DMOJ-style visual blocks) ── */}
      {totalCount > 0 && (
        <div className="panel" style={{ marginBottom: 16 }}>
          <div className="panel-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>Test Cases</span>
            <span style={{ fontWeight: 400, fontSize: 12, color: '#666' }}>
              {passedCount}/{totalCount} passed
            </span>
          </div>
          <div className="panel-body">
            {/* Visual blocks row */}
            <div style={{ display: 'flex', gap: 3, marginBottom: 12, flexWrap: 'wrap' }}>
              {testCases.map((tc: any, i: number) => {
                const tcv = VERDICT_MAP[tc.status] || { short: '?', color: '#999' };
                return (
                  <div
                    key={tc.id || i}
                    title={`Case ${i + 1}: ${tcv.label || tc.status}${tc.executionTime != null ? ` (${tc.executionTime}ms)` : ''}`}
                    style={{
                      width: 32,
                      height: 32,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      borderRadius: 3,
                      fontSize: 11,
                      fontWeight: 700,
                      color: '#fff',
                      background: tcv.color,
                      cursor: 'default',
                    }}
                  >
                    {tcv.short}
                  </div>
                );
              })}
            </div>

            {/* Progress bar */}
            <div style={{
              height: 6,
              borderRadius: 3,
              background: '#eee',
              marginBottom: 16,
              overflow: 'hidden',
            }}>
              <div style={{
                height: '100%',
                borderRadius: 3,
                width: totalCount > 0 ? `${(passedCount / totalCount) * 100}%` : '0%',
                background: passedCount === totalCount ? '#28a745' : '#ffc107',
                transition: 'width 0.3s ease',
              }} />
            </div>

            {/* Detailed table */}
            <table>
              <thead>
                <tr>
                  <th style={{ width: 50 }}>Case</th>
                  <th style={{ width: 100 }}>Verdict</th>
                  <th>Time</th>
                  <th>Memory</th>
                  <th style={{ width: '40%' }}>Time Bar</th>
                </tr>
              </thead>
              <tbody>
                {testCases.map((tc: any, i: number) => {
                  const tcv = VERDICT_MAP[tc.status] || { label: tc.status, short: '?', cls: 'badge-gray', color: '#999' };
                  const timePct = tc.executionTime != null && sub.executionTime != null
                    ? Math.min((tc.executionTime / Math.max(sub.executionTime * 3, 1)) * 100, 100)
                    : 0;
                  return (
                    <tr key={tc.id || i}>
                      <td style={{ fontWeight: 600, color: '#666' }}>{i + 1}</td>
                      <td>
                        <span
                          style={{
                            display: 'inline-block',
                            padding: '2px 8px',
                            borderRadius: 3,
                            fontSize: 12,
                            fontWeight: 700,
                            color: '#fff',
                            background: tcv.color,
                            minWidth: 32,
                            textAlign: 'center',
                          }}
                        >
                          {tcv.short}
                        </span>
                      </td>
                      <td style={{ fontSize: 13 }}>
                        {tc.executionTime != null ? (
                          <span style={{ fontWeight: 600 }}>{tc.executionTime}<span style={{ color: '#999', fontWeight: 400 }}>ms</span></span>
                        ) : '—'}
                      </td>
                      <td style={{ fontSize: 13 }}>
                        {tc.memoryUsed != null ? (
                          <span style={{ fontWeight: 600 }}>{tc.memoryUsed}<span style={{ color: '#999', fontWeight: 400 }}>MB</span></span>
                        ) : '—'}
                      </td>
                      <td>
                        <div style={{ height: 8, borderRadius: 4, background: '#f0f0f0', overflow: 'hidden' }}>
                          <div style={{
                            height: '100%',
                            borderRadius: 4,
                            width: `${timePct}%`,
                            background: tc.status === 'ACCEPTED' ? '#28a745' : tcv.color,
                            transition: 'width 0.3s ease',
                          }} />
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 250px', gap: 20 }}>
        <div>
          {/* Compilation Error */}
          {sub.compilationError && (
            <div className="panel" style={{ marginBottom: 15 }}>
              <div className="panel-header" style={{ color: '#dc3545' }}>Compilation Error</div>
              <div className="panel-body">
                <pre style={{
                  background: '#fff5f5',
                  border: '1px solid #f5c6cb',
                  borderRadius: 3,
                  padding: '10px',
                  fontSize: 12,
                  fontFamily: 'Consolas, monospace',
                  whiteSpace: 'pre-wrap',
                  margin: 0,
                  color: '#c00',
                }}>
                  {sub.compilationError}
                </pre>
              </div>
            </div>
          )}

          {/* Source Code */}
          <div className="panel">
            <div className="panel-header" style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Source Code</span>
              <span style={{ fontWeight: 400, fontSize: 12, color: '#666' }}>{sub.language} · {sub.sourceCode?.length || 0} bytes</span>
            </div>
            <div className="panel-body" style={{ padding: 0 }}>
              <pre style={{
                background: '#fafafa',
                padding: '12px 14px',
                fontSize: 13,
                fontFamily: 'Consolas, Monaco, "Courier New", monospace',
                whiteSpace: 'pre-wrap',
                margin: 0,
                maxHeight: 500,
                overflow: 'auto',
                lineHeight: 1.6,
                borderTop: '1px solid #eee',
              }}>
                {sub.sourceCode}
              </pre>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div>
          <div className="panel">
            <div className="panel-header">Details</div>
            <div className="panel-body" style={{ fontSize: 13 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #eee' }}>
                <span style={{ color: '#666' }}>Problem</span>
                <Link to={`/problems/${sub.problemId}`} style={{ fontWeight: 500 }}>{sub.problemTitle || 'View'}</Link>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #eee' }}>
                <span style={{ color: '#666' }}>Language</span>
                <strong>{sub.language}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #eee' }}>
                <span style={{ color: '#666' }}>Submitted</span>
                <span>{new Date(sub.submittedAt || sub.createdAt).toLocaleString()}</span>
              </div>
              {sub.judgedAt && (
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #eee' }}>
                  <span style={{ color: '#666' }}>Judged</span>
                  <span>{new Date(sub.judgedAt).toLocaleString()}</span>
                </div>
              )}
              {sub.executionTime != null && (
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #eee' }}>
                  <span style={{ color: '#666' }}>Avg Time</span>
                  <strong>{sub.executionTime}ms</strong>
                </div>
              )}
              {sub.memoryUsed != null && (
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0' }}>
                  <span style={{ color: '#666' }}>Peak Memory</span>
                  <strong>{sub.memoryUsed}MB</strong>
                </div>
              )}
            </div>
          </div>

          {/* Submission User */}
          {sub.username && (
            <div className="panel" style={{ marginTop: 12 }}>
              <div className="panel-header">Author</div>
              <div className="panel-body" style={{ fontSize: 13 }}>
                <strong>{sub.username}</strong>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
