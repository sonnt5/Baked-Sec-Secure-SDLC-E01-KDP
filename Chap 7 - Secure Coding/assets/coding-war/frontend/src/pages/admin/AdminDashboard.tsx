import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAdminStatistics, useAdminUsers, useUpdateUserRole } from '../../hooks/queries/useAdmin';
import { problemsAPI } from '../../api/endpoints/problems';
import { contestsAPI } from '../../api/endpoints/contests';
import { useProblems } from '../../hooks/queries/useProblems';
import { useContests } from '../../hooks/queries/useContests';
import { useToast } from '../../contexts/ToastContext';

type AdminTab = 'dashboard' | 'users' | 'problems' | 'contests';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState<AdminTab>('dashboard');
  const { data: stats, isLoading: statsLoading } = useAdminStatistics();

  return (
    <div className="content">
      <h1 style={{ marginBottom: 4 }}>Admin Panel</h1>
      <p style={{ fontSize: 13, color: '#666', marginBottom: 15 }}>System management and monitoring</p>

      <div style={{ display: 'flex', gap: 0, borderBottom: '2px solid #ddd', marginBottom: 20 }}>
        {(['dashboard', 'users', 'problems', 'contests'] as AdminTab[]).map((tab) => (
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

      {activeTab === 'dashboard' && <DashboardTab stats={stats} loading={statsLoading} />}
      {activeTab === 'users' && <UsersTab />}
      {activeTab === 'problems' && <ProblemsTab />}
      {activeTab === 'contests' && <ContestsTab />}
    </div>
  );
}

/* ─── Dashboard Tab ─── */
function DashboardTab({ stats, loading }: { stats: any; loading: boolean }) {
  if (loading) {
    return (
      <div className="panel">
        <div className="panel-body" style={{ textAlign: 'center', padding: 40, color: '#999' }}>
          <span className="spinner" style={{ marginRight: 8 }}></span> Loading statistics...
        </div>
      </div>
    );
  }

  const cards = [
    { label: 'Total Users', value: stats?.totalUsers ?? 0, icon: '👥', color: '#1a73e8' },
    { label: 'Problems', value: stats?.totalProblems ?? 0, icon: '📝', color: '#28a745' },
    { label: 'Submissions', value: stats?.totalSubmissions ?? 0, icon: '📨', color: '#ffc107' },
    { label: 'Contests', value: stats?.totalContests ?? 0, icon: '🏆', color: '#6f42c1' },
    { label: 'Active Users', value: stats?.activeUsers ?? 0, icon: '🟢', color: '#17a2b8' },
  ];

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12, marginBottom: 20 }}>
        {cards.map((card) => (
          <div key={card.label} className="panel" style={{ textAlign: 'center' }}>
            <div className="panel-body" style={{ padding: '18px 10px' }}>
              <div style={{ fontSize: 28, marginBottom: 4 }}>{card.icon}</div>
              <div style={{ fontSize: 28, fontWeight: 700, color: card.color, lineHeight: 1, marginBottom: 6 }}>
                {card.value}
              </div>
              <div style={{ fontSize: 11, color: '#666', textTransform: 'uppercase', letterSpacing: 0.5 }}>
                {card.label}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="panel">
        <div className="panel-header">Quick Actions</div>
        <div className="panel-body" style={{ display: 'flex', gap: 10 }}>
          <Link to="/problems" className="btn" style={{ fontSize: 13 }}>📝 View Problems</Link>
          <Link to="/contests" className="btn" style={{ fontSize: 13 }}>🏆 View Contests</Link>
          <Link to="/submissions" className="btn" style={{ fontSize: 13 }}>📨 View Submissions</Link>
        </div>
      </div>
    </div>
  );
}

/* ─── Users Tab ─── */
function UsersTab() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const { data, isLoading } = useAdminUsers({ page, limit: 20, search: search || undefined });
  const updateRoleMutation = useUpdateUserRole();

  const handleRoleChange = (userId: string, newRole: string) => {
    updateRoleMutation.mutate({ userId, role: newRole });
  };

  return (
    <div>
      <div style={{ marginBottom: 12 }}>
        <input
          type="text"
          placeholder="Search by username or email..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          style={{ padding: '8px 12px', border: '1px solid #ccc', borderRadius: 4, fontSize: 13, width: 300 }}
        />
      </div>

      {updateRoleMutation.isSuccess && (
        <div className="alert alert-success" style={{ marginBottom: 12 }}>Role updated successfully!</div>
      )}

      <div className="panel">
        {isLoading ? (
          <div className="panel-body" style={{ textAlign: 'center', padding: 30, color: '#999' }}>
            <span className="spinner" style={{ marginRight: 8 }}></span> Loading users...
          </div>
        ) : (
          <>
            <table>
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Verified</th>
                  <th>Joined</th>
                  <th style={{ width: 120 }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {data?.users?.map((u: any) => (
                  <tr key={u.id}>
                    <td><Link to={`/users/${u.id}`} style={{ fontWeight: 500 }}>{u.username}</Link></td>
                    <td style={{ fontSize: 12, color: '#666' }}>{u.email}</td>
                    <td>
                      <select
                        value={u.role}
                        onChange={(e) => handleRoleChange(u.id, e.target.value)}
                        disabled={updateRoleMutation.isPending}
                        style={{ padding: '3px 6px', fontSize: 12, border: '1px solid #ccc', borderRadius: 3, background: u.role === 'ADMIN' ? '#fff5f5' : '#fff' }}
                      >
                        <option value="USER">USER</option>
                        <option value="ADMIN">ADMIN</option>
                      </select>
                    </td>
                    <td>
                      <span className={`badge ${u.isEmailVerified || u.emailVerified ? 'badge-green' : 'badge-gray'}`} style={{ fontSize: 10 }}>
                        {u.isEmailVerified || u.emailVerified ? 'Yes' : 'No'}
                      </span>
                    </td>
                    <td style={{ fontSize: 12, color: '#666' }}>
                      {new Date(u.createdAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                    </td>
                    <td>
                      <Link to={`/users/${u.id}`} className="btn" style={{ fontSize: 11, padding: '2px 8px' }}>View</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {(data?.totalPages ?? 0) > 1 && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', fontSize: 13 }}>
                <span style={{ color: '#666' }}>Page {page} of {data?.totalPages ?? 0} ({data?.total ?? 0} users)</span>
                <div style={{ display: 'flex', gap: 4 }}>
                  <button className="btn btn-sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>← Prev</button>
                  <button className="btn btn-sm" disabled={page >= (data?.totalPages ?? 0)} onClick={() => setPage(page + 1)}>Next →</button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

/* ─── Problems Tab ─── */
function ProblemsTab() {
  const navigate = useNavigate();
  const showToast = useToast();
  const { data: problems, isLoading, refetch } = useProblems({});

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Delete problem "${name}"? This will also delete all submissions.`)) return;
    try {
      await problemsAPI.delete(id);
      showToast('Problem deleted!', 'success');
      refetch();
    } catch {
      showToast('Failed to delete problem', 'error');
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', gap: 10, marginBottom: 12 }}>
        <button className="btn btn-primary" style={{ fontSize: 13 }} onClick={() => navigate('/admin/problems/create')}>
          ➕ Create Problem
        </button>
      </div>

      {/* Problems List */}
      <div className="panel">
        <div className="panel-header">All Problems</div>
        {isLoading ? (
          <div className="panel-body" style={{ textAlign: 'center', padding: 30, color: '#999' }}>
            <span className="spinner"></span> Loading...
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th style={{ width: 80 }}>Difficulty</th>
                <th style={{ width: 80 }}>Time (ms)</th>
                <th style={{ width: 80 }}>Mem (MB)</th>
                <th style={{ width: 100 }}>Visibility</th>
                <th style={{ width: 140 }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {(problems as any)?.problems?.map((p: any) => (
                <tr key={p.id}>
                  <td><Link to={`/problems/${p.id}`} style={{ fontWeight: 500 }}>{p.title}</Link></td>
                  <td>
                    <span className={`badge ${p.difficulty === 'EASY' ? 'badge-green' : p.difficulty === 'MEDIUM' ? 'badge-yellow' : 'badge-red'}`} style={{ fontSize: 10 }}>
                      {p.difficulty}
                    </span>
                  </td>
                  <td style={{ fontSize: 12 }}>{p.timeLimit}</td>
                  <td style={{ fontSize: 12 }}>{p.memoryLimit}</td>
                  <td style={{ fontSize: 12 }}>
                    <span style={{ color: p.visibility === 'PRIVATE' ? '#999' : '#333' }}>
                      {p.visibility || 'PUBLIC'}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: 4 }}>
                      <button className="btn btn-sm" style={{ fontSize: 11 }} onClick={() => navigate(`/admin/problems/${p.id}/edit`)}>✏️ Edit</button>
                      <button className="btn btn-sm" style={{ fontSize: 11, color: '#c00' }} onClick={() => handleDelete(p.id, p.title)}>🗑️</button>
                    </div>
                  </td>
                </tr>
              ))}
              {!(problems as any)?.problems?.length && (
                <tr><td colSpan={6} style={{ textAlign: 'center', color: '#999', padding: 20 }}>No problems yet</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

/* ─── Contests Tab ─── */
function ContestsTab() {
  const showToast = useToast();
  const [showForm, setShowForm] = useState(false);
  const { data: contests, isLoading, refetch } = useContests();
  const { data: problems } = useProblems({});
  const [submitting, setSubmitting] = useState(false);

  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [scoringRule, setScoringRule] = useState('ACM');
  const [selectedProblems, setSelectedProblems] = useState<string[]>([]);

  const resetForm = () => {
    setTitle(''); setDescription(''); setStartTime(''); setEndTime('');
    setScoringRule('ACM'); setSelectedProblems([]); setShowForm(false);
  };

  const toggleProblem = (id: string) => {
    setSelectedProblems(prev => prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]);
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      await contestsAPI.create({
        title,
        description,
        startTime: new Date(startTime).toISOString(),
        endTime: new Date(endTime).toISOString(),
        scoringRule: scoringRule as any,
        problems: selectedProblems.map((id, i) => ({ problemId: id, orderIndex: i })),
      } as any);
      showToast('Contest created!', 'success');
      resetForm();
      refetch();
    } catch (err: any) {
      showToast(err?.response?.data?.message || 'Failed', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', gap: 10, marginBottom: 12 }}>
        <button className="btn btn-primary" style={{ fontSize: 13 }} onClick={() => { resetForm(); setShowForm(!showForm); }}>
          {showForm ? '✕ Cancel' : '➕ Create Contest'}
        </button>
      </div>


      {showForm && (
        <div className="panel" style={{ marginBottom: 15 }}>
          <div className="panel-header">Create Contest</div>
          <div className="panel-body">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 10 }}>
              <div>
                <label style={labelStyle}>Title</label>
                <input className="form-input" value={title} onChange={e => setTitle(e.target.value)} placeholder="Weekly Contest #1" />
              </div>
              <div>
                <label style={labelStyle}>Scoring Rule</label>
                <select className="form-input" value={scoringRule} onChange={e => setScoringRule(e.target.value)}>
                  <option value="ACM">ACM</option>
                  <option value="IOI">IOI</option>
                </select>
              </div>
              <div>
                <label style={labelStyle}>Start Time</label>
                <input className="form-input" type="datetime-local" value={startTime} onChange={e => setStartTime(e.target.value)} />
              </div>
              <div>
                <label style={labelStyle}>End Time</label>
                <input className="form-input" type="datetime-local" value={endTime} onChange={e => setEndTime(e.target.value)} />
              </div>
            </div>
            <div style={{ marginBottom: 10 }}>
              <label style={labelStyle}>Description</label>
              <textarea
                className="form-input"
                style={{ minHeight: 80, fontSize: 13, resize: 'vertical' }}
                value={description}
                onChange={e => setDescription(e.target.value)}
                placeholder="Contest description..."
              />
            </div>
            <div style={{ marginBottom: 10 }}>
              <label style={labelStyle}>Select Problems</label>
              <div style={{ border: '1px solid #ddd', borderRadius: 4, padding: 8, maxHeight: 200, overflow: 'auto' }}>
                {(problems as any)?.problems?.map((p: any) => (
                  <label key={p.id} style={{ display: 'flex', gap: 8, alignItems: 'center', padding: '4px 0', cursor: 'pointer', fontSize: 13 }}>
                    <input type="checkbox" checked={selectedProblems.includes(p.id)} onChange={() => toggleProblem(p.id)} />
                    <span style={{ fontWeight: 500 }}>{p.title}</span>
                    <span className={`badge ${p.difficulty === 'EASY' ? 'badge-green' : p.difficulty === 'MEDIUM' ? 'badge-yellow' : 'badge-red'}`} style={{ fontSize: 10 }}>
                      {p.difficulty}
                    </span>
                  </label>
                ))}
                {!(problems as any)?.problems?.length && <span style={{ color: '#999', fontSize: 13 }}>No problems available</span>}
              </div>
              <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>{selectedProblems.length} problem(s) selected</div>
            </div>
            <button className="btn btn-primary" onClick={handleSubmit} disabled={!title || !startTime || !endTime || submitting}>
              {submitting ? '...' : 'Create Contest'}
            </button>
          </div>
        </div>
      )}

      {/* Contests List */}
      <div className="panel">
        <div className="panel-header">All Contests</div>
        {isLoading ? (
          <div className="panel-body" style={{ textAlign: 'center', padding: 30, color: '#999' }}>
            <span className="spinner"></span> Loading...
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th style={{ width: 80 }}>Scoring</th>
                <th style={{ width: 140 }}>Start</th>
                <th style={{ width: 140 }}>End</th>
                <th style={{ width: 80 }}>Problems</th>
                <th style={{ width: 80 }}>Status</th>
                <th style={{ width: 100 }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {(contests as any)?.contests?.map((c: any) => {
                const now = Date.now();
                const start = new Date(c.startTime).getTime();
                const end = new Date(c.endTime).getTime();
                const status = now < start ? 'upcoming' : now > end ? 'ended' : 'active';
                return (
                  <tr key={c.id}>
                    <td><Link to={`/contests/${c.id}`} style={{ fontWeight: 500 }}>{c.title}</Link></td>
                    <td style={{ fontSize: 12 }}>{c.scoringRule || 'ACM'}</td>
                    <td style={{ fontSize: 12 }}>{new Date(c.startTime).toLocaleString()}</td>
                    <td style={{ fontSize: 12 }}>{new Date(c.endTime).toLocaleString()}</td>
                    <td style={{ fontSize: 12 }}>{c.problems?.length ?? c._count?.problems ?? '?'}</td>
                    <td>
                      <span className={`badge ${status === 'active' ? 'badge-green' : status === 'upcoming' ? 'badge-yellow' : 'badge-gray'}`} style={{ fontSize: 10 }}>
                        {status}
                      </span>
                    </td>
                    <td>
                      <Link to={`/contests/${c.id}/scoreboard`} className="btn btn-sm" style={{ fontSize: 11 }}>📊 Board</Link>
                    </td>
                  </tr>
                );
              })}
              {!(contests as any)?.contests?.length && (
                <tr><td colSpan={7} style={{ textAlign: 'center', color: '#999', padding: 20 }}>No contests yet</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: 12,
  fontWeight: 600,
  color: '#555',
  marginBottom: 3,
};
