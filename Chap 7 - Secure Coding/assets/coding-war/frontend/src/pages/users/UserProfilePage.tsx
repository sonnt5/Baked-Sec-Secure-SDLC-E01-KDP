import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useUser, useUpdateUser } from '../../hooks/queries/useUsers';
import { useAuthStore } from '../../stores/authStore';

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

export default function UserProfilePage() {
  const { id } = useParams<{ id: string }>();
  const { user: currentUser } = useAuthStore();
  const { data: profile, isLoading, isError } = useUser(id || '');
  const updateMutation = useUpdateUser();

  const [editing, setEditing] = useState(false);
  const [email, setEmail] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');

  const isOwnProfile = currentUser?.id === id;

  if (isLoading) {
    return (
      <div className="content">
        <div className="panel">
          <div className="panel-body" style={{ textAlign: 'center', padding: 40, color: '#999' }}>
            <span className="spinner" style={{ marginRight: 8 }}></span> Loading profile...
          </div>
        </div>
      </div>
    );
  }

  if (isError || !profile) {
    return (
      <div className="content">
        <div className="alert alert-error">User not found.</div>
      </div>
    );
  }

  const stats = profile.statistics;
  const acceptanceRate = stats?.totalSubmissions > 0
    ? ((stats.acceptedSubmissions / stats.totalSubmissions) * 100).toFixed(1)
    : '0.0';

  const handleSave = () => {
    if (!id) return;
    const data: any = {};
    if (email && email !== profile.email) data.email = email;
    if (newPassword) {
      data.currentPassword = currentPassword;
      data.newPassword = newPassword;
    }
    if (Object.keys(data).length === 0) {
      setEditing(false);
      return;
    }
    updateMutation.mutate(
      { id, data },
      {
        onSuccess: () => {
          setEditing(false);
          setCurrentPassword('');
          setNewPassword('');
        },
      }
    );
  };

  const startEdit = () => {
    setEmail(profile.email || '');
    setCurrentPassword('');
    setNewPassword('');
    setEditing(true);
  };

  return (
    <div className="content">
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        padding: '16px 20px',
        marginBottom: 20,
        background: 'linear-gradient(135deg, #667eea22, #764ba222)',
        border: '1px solid #ddd',
        borderRadius: 6,
      }}>
        {/* Avatar placeholder */}
        <div style={{
          width: 64,
          height: 64,
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #667eea, #764ba2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 24,
          fontWeight: 700,
          color: '#fff',
          flexShrink: 0,
        }}>
          {profile.username.charAt(0).toUpperCase()}
        </div>
        <div style={{ flex: 1 }}>
          <h1 style={{ margin: 0, fontSize: 22 }}>{profile.username}</h1>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 4, fontSize: 13 }}>
            <span className={`badge ${profile.role === 'ADMIN' ? 'badge-red' : 'badge-gray'}`}>
              {profile.role}
            </span>
            <span style={{ color: '#666' }}>
              Joined {new Date(profile.createdAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
            </span>
          </div>
        </div>
        {isOwnProfile && !editing && (
          <button className="btn" onClick={startEdit} style={{ fontSize: 13 }}>
            ✏️ Edit Profile
          </button>
        )}
      </div>

      {/* Statistics cards */}
      {stats && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(5, 1fr)',
          gap: 12,
          marginBottom: 20,
        }}>
          {[
            { label: 'Submissions', value: stats.totalSubmissions, color: '#1a73e8' },
            { label: 'Accepted', value: stats.acceptedSubmissions, color: '#28a745' },
            { label: 'Acceptance', value: `${acceptanceRate}%`, color: '#ffc107' },
            { label: 'Solved', value: stats.solvedProblems, color: '#17a2b8' },
            { label: 'Contests', value: stats.contestsParticipated, color: '#6f42c1' },
          ].map((card) => (
            <div key={card.label} className="panel" style={{ textAlign: 'center' }}>
              <div className="panel-body" style={{ padding: '14px 10px' }}>
                <div style={{
                  fontSize: 28,
                  fontWeight: 700,
                  color: card.color,
                  lineHeight: 1,
                  marginBottom: 6,
                }}>
                  {card.value}
                </div>
                <div style={{ fontSize: 12, color: '#666', textTransform: 'uppercase', letterSpacing: 0.5 }}>
                  {card.label}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: editing ? '1fr 350px' : '1fr', gap: 20 }}>
        {/* Recent submissions */}
        <div className="panel">
          <div className="panel-header">Recent Submissions</div>
          {profile.recentSubmissions && profile.recentSubmissions.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>Problem</th>
                  <th>Verdict</th>
                  <th>Language</th>
                  <th>Time</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {profile.recentSubmissions.map((sub: any) => {
                  const vb = VERDICT_BADGES[sub.status] || { label: sub.status, cls: 'badge-gray' };
                  return (
                    <tr key={sub.id}>
                      <td>
                        <Link to={`/problems/${sub.problemId}`} style={{ fontWeight: 500 }}>
                          {sub.problemTitle || sub.problemId?.slice(0, 8)}
                        </Link>
                      </td>
                      <td>
                        <Link to={`/submissions/${sub.id}`}>
                          <span className={`badge ${vb.cls}`}>{vb.label}</span>
                        </Link>
                      </td>
                      <td><span className="badge badge-gray">{sub.language}</span></td>
                      <td style={{ fontSize: 12 }}>{sub.executionTime != null ? `${sub.executionTime}ms` : '—'}</td>
                      <td style={{ fontSize: 12, color: '#666' }}>
                        {new Date(sub.submittedAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <div className="panel-body" style={{ textAlign: 'center', padding: 30, color: '#999' }}>
              No submissions yet.{' '}
              {isOwnProfile && <Link to="/problems">Solve a problem</Link>}
            </div>
          )}
        </div>

        {/* Edit profile form */}
        {editing && (
          <div className="panel">
            <div className="panel-header">Edit Profile</div>
            <div className="panel-body">
              {updateMutation.isSuccess && (
                <div className="alert alert-success" style={{ marginBottom: 12 }}>Profile updated!</div>
              )}
              {updateMutation.isError && (
                <div className="alert alert-error" style={{ marginBottom: 12 }}>
                  {(updateMutation.error as any)?.response?.data?.message || 'Failed to update.'}
                </div>
              )}

              <div style={{ marginBottom: 14 }}>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, marginBottom: 4, color: '#666' }}>
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Email"
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    border: '1px solid #ccc',
                    borderRadius: 4,
                    fontSize: 13,
                    boxSizing: 'border-box',
                  }}
                />
              </div>

              <hr style={{ border: 'none', borderTop: '1px solid #eee', margin: '16px 0' }} />
              <div style={{ fontSize: 12, color: '#999', marginBottom: 12 }}>Change Password (optional)</div>

              <div style={{ marginBottom: 14 }}>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, marginBottom: 4, color: '#666' }}>
                  Current Password
                </label>
                <input
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  placeholder="Current password"
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    border: '1px solid #ccc',
                    borderRadius: 4,
                    fontSize: 13,
                    boxSizing: 'border-box',
                  }}
                />
              </div>

              <div style={{ marginBottom: 16 }}>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, marginBottom: 4, color: '#666' }}>
                  New Password
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="New password"
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    border: '1px solid #ccc',
                    borderRadius: 4,
                    fontSize: 13,
                    boxSizing: 'border-box',
                  }}
                />
              </div>

              <div style={{ display: 'flex', gap: 8 }}>
                <button
                  className="btn btn-primary"
                  onClick={handleSave}
                  disabled={updateMutation.isPending}
                  style={{ flex: 1 }}
                >
                  {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  className="btn"
                  onClick={() => setEditing(false)}
                  style={{ flex: 1 }}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
