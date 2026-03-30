import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useSubmissions } from '../../hooks/queries/useSubmissions';

const VERDICT_BADGES: Record<string, { label: string; cls: string }> = {
  ACCEPTED: { label: 'AC', cls: 'badge-green' },
  WRONG_ANSWER: { label: 'WA', cls: 'badge-red' },
  TIME_LIMIT_EXCEEDED: { label: 'TLE', cls: 'badge-yellow' },
  MEMORY_LIMIT_EXCEEDED: { label: 'MLE', cls: 'badge-yellow' },
  RUNTIME_ERROR: { label: 'RE', cls: 'badge-red' },
  COMPILATION_ERROR: { label: 'CE', cls: 'badge-red' },
  QUEUED: { label: 'Queued', cls: 'badge-gray' },
  COMPILING: { label: 'Compiling', cls: 'badge-blue' },
  RUNNING: { label: 'Running', cls: 'badge-blue' },
};

function formatTime(dateStr: string) {
  return new Date(dateStr).toLocaleString('en-US', {
    month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

export default function SubmissionListPage() {
  const [searchParams] = useSearchParams();
  const [page, setPage] = useState(1);

  const { data, isLoading, isError } = useSubmissions({
    page,
    limit: 25,
    problemId: searchParams.get('problemId') || undefined,
  });

  return (
    <div className="content">
      <h1>My Submissions</h1>

      {isLoading && (
        <div className="panel">
          <div className="panel-body" style={{ textAlign: 'center', padding: 40, color: '#999' }}>
            <span className="spinner" style={{ marginRight: 8 }}></span> Loading submissions...
          </div>
        </div>
      )}

      {isError && (
        <div className="alert alert-error">Failed to load submissions.</div>
      )}

      {!isLoading && !isError && data && (
        <>
          {data.submissions?.length === 0 ? (
            <div className="panel">
              <div className="panel-body" style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                No submissions yet. <Link to="/problems">Solve a problem</Link> to get started!
              </div>
            </div>
          ) : (
            <>
              <div className="panel">
                <table>
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>Problem</th>
                      <th>Language</th>
                      <th>Verdict</th>
                      <th>Time</th>
                      <th>Memory</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.submissions?.map((sub: any) => {
                      const vb = VERDICT_BADGES[sub.status] || VERDICT_BADGES[sub.verdict] || { label: sub.status, cls: 'badge-gray' };
                      return (
                        <tr key={sub.id}>
                          <td style={{ fontSize: 12, color: '#666' }}>{formatTime(sub.submittedAt || sub.createdAt)}</td>
                          <td>
                            <Link to={`/problems/${sub.problemId}`} style={{ fontWeight: 500 }}>
                              {sub.problemTitle || sub.problem?.title || sub.problemId.slice(0, 8)}
                            </Link>
                          </td>
                          <td><span className="badge badge-gray">{sub.language}</span></td>
                          <td>
                            <Link to={`/submissions/${sub.id}`}>
                              <span className={`badge ${vb.cls}`}>{vb.label}</span>
                            </Link>
                          </td>
                          <td style={{ fontSize: 12 }}>{sub.executionTime != null ? `${sub.executionTime}ms` : '—'}</td>
                          <td style={{ fontSize: 12 }}>{sub.memoryUsed != null ? `${sub.memoryUsed}MB` : '—'}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {data.totalPages > 1 && (
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 10, fontSize: 13 }}>
                  <span style={{ color: '#666' }}>Page {page} of {data.totalPages}</span>
                  <div style={{ display: 'flex', gap: 4 }}>
                    <button className="btn btn-sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>← Prev</button>
                    <button className="btn btn-sm" disabled={page >= data.totalPages} onClick={() => setPage(page + 1)}>Next →</button>
                  </div>
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}
