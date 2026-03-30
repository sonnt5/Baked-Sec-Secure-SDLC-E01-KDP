import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { problemsAPI } from '../../api/endpoints/problems';
import { useToast } from '../../contexts/ToastContext';

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: 12,
  fontWeight: 600,
  color: '#555',
  marginBottom: 3,
};

export default function AdminCreateProblemPage() {
  const navigate = useNavigate();
  const showToast = useToast();
  const [submitting, setSubmitting] = useState(false);

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [difficulty, setDifficulty] = useState('EASY');
  const [timeLimit, setTimeLimit] = useState('1000');
  const [memoryLimit, setMemoryLimit] = useState('256');
  const [tags, setTags] = useState('');
  const [visibility, setVisibility] = useState('PUBLIC');

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const problem: any = await problemsAPI.create({
        title,
        description,
        difficulty: difficulty as any,
        timeLimit: parseInt(timeLimit),
        memoryLimit: parseInt(memoryLimit),
        tags: tags.split(',').map(t => t.trim()).filter(Boolean),
        visibility: visibility as any,
      } as any);
      showToast('Problem created! You can now upload test cases.', 'success');
      // Redirect to edit page so admin can immediately upload test cases
      navigate(`/admin/problems/${problem.id}/edit`);
    } catch (err: any) {
      showToast(err?.response?.data?.message || 'Creation failed', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="content">
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 18 }}>
        <button className="btn btn-sm" onClick={() => navigate('/admin')} style={{ fontSize: 12 }}>
          ← Back to Admin
        </button>
        <h1 style={{ margin: 0, fontSize: 20 }}>Create Problem</h1>
      </div>

      <div className="panel">
        <div className="panel-header">Problem Details</div>
        <div className="panel-body">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
            <div style={{ gridColumn: '1 / -1' }}>
              <label style={labelStyle}>Title</label>
              <input
                className="form-input"
                value={title}
                onChange={e => setTitle(e.target.value)}
                placeholder="Two Sum"
                autoFocus
              />
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
              <input
                className="form-input"
                value={tags}
                onChange={e => setTags(e.target.value)}
                placeholder="array, hash-table, two-pointers"
              />
            </div>
          </div>

          <div style={{ marginBottom: 14 }}>
            <label style={labelStyle}>Description (Markdown)</label>
            <textarea
              className="form-input"
              style={{
                minHeight: 320,
                fontFamily: 'Consolas, Monaco, monospace',
                fontSize: 13,
                resize: 'vertical',
              }}
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder={'## Problem Statement\n\nGiven an array of integers nums and an integer target...\n\n## Input Format\n\n## Output Format\n\n## Example\n\n## Constraints'}
            />
          </div>

          <div style={{ display: 'flex', gap: 10 }}>
            <button
              className="btn btn-primary"
              onClick={handleSubmit}
              disabled={!title || !description || submitting}
            >
              {submitting ? '⏳ Creating...' : '✅ Create & Continue to Test Cases'}
            </button>
            <button className="btn" onClick={() => navigate('/admin')}>Cancel</button>
          </div>
        </div>
      </div>
    </div>
  );
}
