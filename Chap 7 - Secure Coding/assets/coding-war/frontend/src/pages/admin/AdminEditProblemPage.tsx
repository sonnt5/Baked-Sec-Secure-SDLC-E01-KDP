import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { problemsAPI, type TestCaseItem } from '../../api/endpoints/problems';
import { useToast } from '../../contexts/ToastContext';

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: 12,
  fontWeight: 600,
  color: '#555',
  marginBottom: 3,
};

const tcaStyle: React.CSSProperties = {
  width: '100%',
  fontFamily: 'Consolas, Monaco, monospace',
  fontSize: 12,
  resize: 'vertical',
  minHeight: 90,
};

export default function AdminEditProblemPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const showToast = useToast();

  // ── Problem form state ──────────────────────────────────────────────────────
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [difficulty, setDifficulty] = useState('EASY');
  const [timeLimit, setTimeLimit] = useState('1000');
  const [memoryLimit, setMemoryLimit] = useState('256');
  const [tags, setTags] = useState('');
  const [visibility, setVisibility] = useState('PUBLIC');

  // ── Test cases state ────────────────────────────────────────────────────────
  const [testCases, setTestCases] = useState<TestCaseItem[]>([]);
  const [tcLoading, setTcLoading] = useState(false);
  const [newInput, setNewInput] = useState('');
  const [newOutput, setNewOutput] = useState('');
  const [isSample, setIsSample] = useState(false);
  const [adding, setAdding] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    problemsAPI.getById(id).then((p: any) => {
      setTitle(p.title ?? '');
      setDescription(p.description ?? '');
      setDifficulty(p.difficulty ?? 'EASY');
      setTimeLimit(String(p.time_limit ?? p.timeLimit ?? 1000));
      setMemoryLimit(String(p.memory_limit ?? p.memoryLimit ?? 256));
      setTags((p.tags ?? []).join(', '));
      setVisibility(p.visibility ?? 'PUBLIC');
      setLoading(false);
    }).catch(() => {
      showToast('Failed to load problem.', 'error');
      setLoading(false);
    });
  }, [id]);

  const fetchTestCases = useCallback(async () => {
    if (!id) return;
    setTcLoading(true);
    try {
      const res = await problemsAPI.listTestCases(id);
      setTestCases(res.testCases);
    } catch {
      showToast('Failed to load test cases', 'error');
    } finally {
      setTcLoading(false);
    }
  }, [id]);

  useEffect(() => { fetchTestCases(); }, [fetchTestCases]);

  const handleSubmit = async () => {
    if (!id) return;
    setSubmitting(true);
    try {
      await problemsAPI.update(id, {
        title,
        description,
        difficulty: difficulty as any,
        timeLimit: parseInt(timeLimit),
        memoryLimit: parseInt(memoryLimit),
        tags: tags.split(',').map(t => t.trim()).filter(Boolean),
        visibility: visibility as any,
      });
      showToast('Problem updated successfully!', 'success');
      navigate('/admin');
    } catch (err: any) {
      showToast(err?.response?.data?.message || 'Update failed', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const handleAddTestCase = async () => {
    if (!id || !newInput.trim() || !newOutput.trim()) return;
    setAdding(true);
    try {
      await problemsAPI.addTestCase(id, newInput, newOutput, isSample);
      showToast('Test case added!', 'success');
      setNewInput('');
      setNewOutput('');
      setIsSample(false);
      fetchTestCases();
    } catch (err: any) {
      showToast(err?.response?.data?.message || 'Failed to add test case', 'error');
    } finally {
      setAdding(false);
    }
  };

  const handleDeleteTestCase = async (tcId: string) => {
    if (!id || !confirm('Delete this test case?')) return;
    try {
      await problemsAPI.deleteTestCase(id, tcId);
      showToast('Test case deleted', 'success');
      setTestCases(prev => prev.filter(tc => tc.id !== tcId));
    } catch {
      showToast('Failed to delete test case', 'error');
    }
  };

  if (loading) {
    return (
      <div className="content">
        <div className="panel">
          <div className="panel-body" style={{ textAlign: 'center', padding: 40, color: '#999' }}>
            <span className="spinner" style={{ marginRight: 8 }} /> Loading problem...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="content">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 18 }}>
        <button className="btn btn-sm" onClick={() => navigate('/admin')} style={{ fontSize: 12 }}>
          ← Back to Admin
        </button>
        <h1 style={{ margin: 0, fontSize: 20 }}>Edit: <em style={{ fontWeight: 400 }}>{title}</em></h1>
      </div>

      {/* ── Problem Details Panel ─────────────────────────────────────────── */}
      <div className="panel" style={{ marginBottom: 16 }}>
        <div className="panel-header">Problem Details</div>
        <div className="panel-body">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
            <div style={{ gridColumn: '1 / -1' }}>
              <label style={labelStyle}>Title</label>
              <input className="form-input" value={title} onChange={e => setTitle(e.target.value)} />
            </div>
            <div>
              <label style={labelStyle}>Difficulty</label>
              <select className="form-input" value={difficulty} onChange={e => setDifficulty(e.target.value)}>
                <option value="EASY">EASY</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="HARD">HARD</option>
              </select>
            </div>
            <div>
              <label style={labelStyle}>Visibility</label>
              <select className="form-input" value={visibility} onChange={e => setVisibility(e.target.value)}>
                <option value="PUBLIC">PUBLIC</option>
                <option value="PRIVATE">PRIVATE</option>
              </select>
            </div>
            <div>
              <label style={labelStyle}>Time Limit (ms)</label>
              <input className="form-input" type="number" value={timeLimit} onChange={e => setTimeLimit(e.target.value)} />
            </div>
            <div>
              <label style={labelStyle}>Memory Limit (MB)</label>
              <input className="form-input" type="number" value={memoryLimit} onChange={e => setMemoryLimit(e.target.value)} />
            </div>
            <div style={{ gridColumn: '1 / -1' }}>
              <label style={labelStyle}>Tags (comma-separated)</label>
              <input className="form-input" value={tags} onChange={e => setTags(e.target.value)} placeholder="array, hash-table" />
            </div>
          </div>

          <div style={{ marginBottom: 14 }}>
            <label style={labelStyle}>Description (Markdown)</label>
            <textarea
              className="form-input"
              style={{ minHeight: 280, fontFamily: 'Consolas, Monaco, monospace', fontSize: 13, resize: 'vertical' }}
              value={description}
              onChange={e => setDescription(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', gap: 10 }}>
            <button className="btn btn-primary" onClick={handleSubmit} disabled={!title || !description || submitting}>
              {submitting ? '⏳ Saving...' : '💾 Save Changes'}
            </button>
            <button className="btn" onClick={() => navigate('/admin')}>Cancel</button>
          </div>
        </div>
      </div>

      {/* ── Test Cases Panel ──────────────────────────────────────────────── */}
      <div className="panel">
        <div className="panel-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>🧪 Test Cases ({testCases.length})</span>
          {tcLoading && <span style={{ fontSize: 12, color: '#999' }}>Loading...</span>}
        </div>
        <div className="panel-body">

          {/* Existing test cases list */}
          {testCases.length === 0 && !tcLoading ? (
            <p style={{ color: '#999', fontSize: 13, marginBottom: 16 }}>No test cases yet. Add one below.</p>
          ) : (
            <div style={{ marginBottom: 20 }}>
              {testCases.map((tc, idx) => (
                <div
                  key={tc.id}
                  style={{
                    border: '1px solid #e0e0e0',
                    borderRadius: 6,
                    marginBottom: 8,
                    overflow: 'hidden',
                  }}
                >
                  {/* Test case header */}
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8,
                      padding: '8px 12px',
                      background: '#f8f8f8',
                      cursor: 'pointer',
                      userSelect: 'none',
                    }}
                    onClick={() => setExpandedId(expandedId === tc.id ? null : tc.id)}
                  >
                    <span style={{ fontSize: 12, fontWeight: 600, color: '#333' }}>
                      #{idx + 1}
                    </span>
                    <span
                      style={{
                        fontSize: 11,
                        padding: '2px 7px',
                        borderRadius: 10,
                        background: tc.is_hidden ? '#f0f0f0' : '#e8f5e9',
                        color: tc.is_hidden ? '#888' : '#2e7d32',
                        fontWeight: 600,
                      }}
                    >
                      {tc.is_hidden ? 'Hidden' : 'Sample'}
                    </span>
                    <span style={{ fontSize: 11, color: '#aaa', marginLeft: 'auto' }}>
                      {expandedId === tc.id ? '▲ collapse' : '▼ expand'}
                    </span>
                    <button
                      className="btn btn-sm"
                      style={{ fontSize: 11, color: '#c00', padding: '2px 8px' }}
                      onClick={e => { e.stopPropagation(); handleDeleteTestCase(tc.id); }}
                    >
                      🗑️ Delete
                    </button>
                  </div>

                  {/* Expanded content */}
                  {expandedId === tc.id && (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 0 }}>
                      <div style={{ padding: 12, borderRight: '1px solid #e0e0e0' }}>
                        <label style={{ ...labelStyle, marginBottom: 6, color: '#1565C0' }}>📥 Input</label>
                        <pre style={{
                          margin: 0,
                          background: '#f5f8ff',
                          border: '1px solid #d0ddf5',
                          borderRadius: 4,
                          padding: '8px 10px',
                          fontSize: 12,
                          fontFamily: 'Consolas, Monaco, monospace',
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word',
                          maxHeight: 200,
                          overflowY: 'auto',
                        }}>
                          {tc.input || '(empty)'}
                        </pre>
                      </div>
                      <div style={{ padding: 12 }}>
                        <label style={{ ...labelStyle, marginBottom: 6, color: '#2e7d32' }}>📤 Output</label>
                        <pre style={{
                          margin: 0,
                          background: '#f5fff8',
                          border: '1px solid #c8e6c9',
                          borderRadius: 4,
                          padding: '8px 10px',
                          fontSize: 12,
                          fontFamily: 'Consolas, Monaco, monospace',
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word',
                          maxHeight: 200,
                          overflowY: 'auto',
                        }}>
                          {tc.output || '(empty)'}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Add new test case */}
          <div style={{ borderTop: '2px dashed #e0e0e0', paddingTop: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 10, color: '#444' }}>➕ Add Test Case</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 10 }}>
              <div>
                <label style={{ ...labelStyle, color: '#1565C0' }}>📥 Input</label>
                <textarea
                  className="form-input"
                  style={tcaStyle}
                  value={newInput}
                  onChange={e => setNewInput(e.target.value)}
                  placeholder={"4\n2 7 11 15\n9"}
                />
              </div>
              <div>
                <label style={{ ...labelStyle, color: '#2e7d32' }}>📤 Expected Output</label>
                <textarea
                  className="form-input"
                  style={tcaStyle}
                  value={newOutput}
                  onChange={e => setNewOutput(e.target.value)}
                  placeholder={"0 1"}
                />
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={isSample}
                  onChange={e => setIsSample(e.target.checked)}
                />
                Show as sample (visible to users in problem statement)
              </label>
              <button
                className="btn btn-primary"
                onClick={handleAddTestCase}
                disabled={!newInput.trim() || !newOutput.trim() || adding}
                style={{ marginLeft: 'auto' }}
              >
                {adding ? '⏳ Adding...' : '➕ Add Test Case'}
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
