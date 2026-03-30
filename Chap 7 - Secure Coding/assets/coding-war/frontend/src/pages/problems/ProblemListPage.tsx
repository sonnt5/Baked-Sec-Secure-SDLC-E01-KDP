import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useProblems } from '../../hooks/queries/useProblems';

export default function ProblemListPage() {
  const [searchParams, setSearchParams] = useSearchParams();

  const [difficulty, setDifficulty] = useState<string>(searchParams.get('difficulty') || '');
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [page, setPage] = useState(() => {
    const p = searchParams.get('page');
    return p ? parseInt(p, 10) : 1;
  });

  const { data, isLoading, isError } = useProblems({
    difficulty: (difficulty.toUpperCase() as 'EASY' | 'MEDIUM' | 'HARD') || undefined,
    search: search || undefined,
    page,
    limit: 25,
  });

  // Sync URL params
  useEffect(() => {
    const params = new URLSearchParams();
    if (difficulty) params.set('difficulty', difficulty);
    if (search) params.set('search', search);
    if (page > 1) params.set('page', page.toString());
    setSearchParams(params, { replace: true });
  }, [difficulty, search, page, setSearchParams]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
  };

  return (
    <div className="content">
      <h1>Problems</h1>

      {/* Filters */}
      <div className="panel" style={{ marginBottom: 15 }}>
        <div className="panel-body" style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
          <form onSubmit={handleSearch} style={{ display: 'flex', gap: 8, flex: 1, minWidth: 200 }}>
            <input
              type="text"
              className="form-input"
              placeholder="Search by title..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ maxWidth: 300 }}
            />
            <button type="submit" className="btn btn-primary btn-sm">Search</button>
          </form>
          <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
            <span style={{ fontSize: 13, color: '#666', marginRight: 4 }}>Difficulty:</span>
            {['', 'EASY', 'MEDIUM', 'HARD'].map((d) => (
              <button
                key={d}
                className={`btn btn-sm ${difficulty === d ? 'btn-primary' : ''}`}
                onClick={() => { setDifficulty(d); setPage(1); }}
              >
                {d || 'All'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="panel">
          <div className="panel-body" style={{ textAlign: 'center', padding: 40, color: '#999' }}>
            <span className="spinner" style={{ marginRight: 8 }}></span> Loading problems...
          </div>
        </div>
      )}

      {/* Error */}
      {isError && (
        <div className="alert alert-error">Failed to load problems. Please try again later.</div>
      )}

      {/* Table */}
      {!isLoading && !isError && data && (
        <>
          {data.problems.length === 0 ? (
            <div className="panel">
              <div className="panel-body" style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                No problems found.
                {(search || difficulty) && (
                  <button
                    className="btn btn-sm"
                    style={{ marginLeft: 10 }}
                    onClick={() => { setSearch(''); setDifficulty(''); setPage(1); }}
                  >
                    Clear filters
                  </button>
                )}
              </div>
            </div>
          ) : (
            <>
              <div className="panel">
                <table>
                  <thead>
                    <tr>
                      <th style={{ width: '50%' }}>Title</th>
                      <th>Difficulty</th>
                      <th>Tags</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.problems.map((problem: any) => (
                      <tr key={problem.id}>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            {problem.userSolved && (
                              <span
                                title="Solved"
                                style={{
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  width: 18,
                                  height: 18,
                                  borderRadius: '50%',
                                  background: '#22c55e',
                                  color: '#fff',
                                  fontSize: 11,
                                  fontWeight: 700,
                                  flexShrink: 0,
                                }}
                              >✓</span>
                            )}
                            <Link to={`/problems/${problem.id}`} style={{ fontWeight: 500 }}>
                              {problem.title}
                            </Link>
                          </div>
                        </td>
                        <td>
                          <span className={`badge ${
                            problem.difficulty === 'EASY' ? 'badge-green' :
                            problem.difficulty === 'MEDIUM' ? 'badge-yellow' :
                            'badge-red'
                          }`}>
                            {problem.difficulty}
                          </span>
                        </td>
                        <td>
                          {problem.tags?.map((tag: string) => (
                            <span key={tag} className="badge badge-gray" style={{ marginRight: 4 }}>{tag}</span>
                          ))}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {data.totalPages > 1 && (
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 10, fontSize: 13 }}>
                  <span style={{ color: '#666' }}>Page {page} of {data.totalPages} ({data.total} problems)</span>
                  <div style={{ display: 'flex', gap: 4 }}>
                    <button className="btn btn-sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
                      ← Prev
                    </button>
                    {Array.from({ length: Math.min(data.totalPages, 7) }, (_, i) => {
                      let p: number;
                      if (data.totalPages <= 7) {
                        p = i + 1;
                      } else if (page <= 4) {
                        p = i + 1;
                      } else if (page >= data.totalPages - 3) {
                        p = data.totalPages - 6 + i;
                      } else {
                        p = page - 3 + i;
                      }
                      return (
                        <button
                          key={p}
                          className={`btn btn-sm ${p === page ? 'btn-primary' : ''}`}
                          onClick={() => setPage(p)}
                        >
                          {p}
                        </button>
                      );
                    })}
                    <button className="btn btn-sm" disabled={page >= data.totalPages} onClick={() => setPage(page + 1)}>
                      Next →
                    </button>
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
