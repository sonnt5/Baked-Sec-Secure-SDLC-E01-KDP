import { useState, useEffect, useRef } from 'react';
import { useParams, Link, useNavigate, useLocation } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useProblem } from '../../hooks/queries/useProblems';
import { useSubmitSolution } from '../../hooks/queries/useSubmissions';
import { useAuthStore } from '../../stores/authStore';

const LANGUAGES = [
  { value: 'CPP', label: 'C++ (G++)' },
  { value: 'C', label: 'C (GCC)' },
  { value: 'PYTHON', label: 'Python 3' },
  { value: 'JAVA', label: 'Java (OpenJDK)' },
];

export default function ProblemDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const prefill = (location.state as any) || {};
  const { isAuthenticated } = useAuthStore();
  const { data: problem, isLoading, isError } = useProblem(id || '');
  const submitMutation = useSubmitSolution();

  const [showSubmit, setShowSubmit] = useState(!!prefill.prefillCode);
  const [language, setLanguage] = useState(prefill.prefillLanguage || 'CPP');
  const [sourceCode, setSourceCode] = useState(prefill.prefillCode || '');
  const [cooldownSec, setCooldownSec] = useState(0);
  const [rateLimitMsg, setRateLimitMsg] = useState('');
  const cooldownRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const startCooldown = (seconds: number) => {
    setCooldownSec(seconds);
    if (cooldownRef.current) clearInterval(cooldownRef.current);
    cooldownRef.current = setInterval(() => {
      setCooldownSec((prev) => {
        if (prev <= 1) {
          if (cooldownRef.current) clearInterval(cooldownRef.current);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  useEffect(() => {
    return () => { if (cooldownRef.current) clearInterval(cooldownRef.current); };
  }, []);

  const handleSubmit = async () => {
    if (!id || !sourceCode.trim() || cooldownSec > 0) return;
    setRateLimitMsg('');
    try {
      const result = await submitMutation.mutateAsync({
        problemId: id,
        language: language as any,
        sourceCode,
      });
      // Cooldown 10s
      startCooldown(10);
      // Navigate to submission detail
      navigate(`/submissions/${result.submissionId}`);
    } catch (err: any) {
      // Handle 429 rate limit
      if (err?.response?.status === 429) {
        setRateLimitMsg(err.response.data?.message || 'Too many submissions. Please wait.');
        startCooldown(30);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="content">
        <div className="panel">
          <div className="panel-body" style={{ textAlign: 'center', padding: 40, color: '#999' }}>
            <span className="spinner" style={{ marginRight: 8 }}></span> Loading problem...
          </div>
        </div>
      </div>
    );
  }

  if (isError || !problem) {
    return (
      <div className="content">
        <div className="alert alert-error">Problem not found or failed to load.</div>
        <Link to="/problems">← Back to problems</Link>
      </div>
    );
  }

  return (
    <div className="content">
      {/* Breadcrumb */}
      <div style={{ fontSize: 13, marginBottom: 12, color: '#666' }}>
        <Link to="/problems">Problems</Link> / {problem.title}
      </div>

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 15 }}>
        <div>
          <h1 style={{ marginBottom: 6 }}>{problem.title}</h1>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', fontSize: 13 }}>
            <span className={`badge ${
              problem.difficulty === 'EASY' ? 'badge-green' :
              problem.difficulty === 'MEDIUM' ? 'badge-yellow' :
              'badge-red'
            }`}>
              {problem.difficulty}
            </span>
            {problem.tags?.map((tag: string) => (
              <span key={tag} className="badge badge-gray">{tag}</span>
            ))}
          </div>
        </div>
        {isAuthenticated && (
          <button
            className={`btn ${showSubmit ? '' : 'btn-primary'} btn-sm`}
            onClick={() => setShowSubmit(!showSubmit)}
          >
            {showSubmit ? 'Hide Submit' : '📝 Submit Solution'}
          </button>
        )}
      </div>

      {/* Submit Form */}
      {showSubmit && (
        <div className="panel" style={{ marginBottom: 15 }}>
          <div className="panel-header">Submit Solution</div>
          <div className="panel-body">
            {rateLimitMsg && (
              <div className="alert alert-error" style={{ marginBottom: 10, display: 'flex', alignItems: 'center', gap: 8 }}>
                ⚠️ {rateLimitMsg} {cooldownSec > 0 && <strong>({cooldownSec}s)</strong>}
              </div>
            )}
            {submitMutation.isError && !rateLimitMsg && (
              <div className="alert alert-error" style={{ marginBottom: 10 }}>
                {(submitMutation.error as any)?.response?.data?.message || 'Submission failed. Please try again.'}
              </div>
            )}
            <div style={{ display: 'flex', gap: 10, marginBottom: 10, alignItems: 'center' }}>
              <label style={{ fontSize: 13, fontWeight: 600 }}>Language:</label>
              <select
                className="form-input"
                style={{ width: 200 }}
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
              >
                {LANGUAGES.map((l) => (
                  <option key={l.value} value={l.value}>{l.label}</option>
                ))}
              </select>
            </div>
            <textarea
              className="form-input"
              style={{
                fontFamily: 'Consolas, Monaco, monospace',
                fontSize: 13,
                minHeight: 250,
                resize: 'vertical',
              }}
              placeholder="Paste your source code here..."
              value={sourceCode}
              onChange={(e) => setSourceCode(e.target.value)}
            />
            <div style={{ marginTop: 10, display: 'flex', gap: 10, alignItems: 'center' }}>
              <button
                className="btn btn-primary"
                onClick={handleSubmit}
                disabled={!sourceCode.trim() || submitMutation.isPending || cooldownSec > 0}
              >
                {submitMutation.isPending ? (
                  <><span className="spinner"></span> Submitting...</>
                ) : cooldownSec > 0 ? (
                  `Cooldown (${cooldownSec}s)`
                ) : (
                  'Submit'
                )}
              </button>
              <span style={{ fontSize: 12, color: '#999' }}>
                Max 64KB · C, C++, Python, Java
              </span>
            </div>
          </div>
        </div>
      )}

      {!showSubmit && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 250px', gap: 20 }}>
          {/* Main content */}
          <div>
            {/* Problem statement */}
            <div className="panel">
              <div className="panel-header">Problem Statement</div>
              <div className="panel-body prose">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {problem.description}
                </ReactMarkdown>
              </div>
            </div>

            {/* Sample test cases */}
            {problem.sampleTestCases && problem.sampleTestCases.length > 0 && (
              <div className="panel">
                <div className="panel-header">Sample Test Cases</div>
                <div className="panel-body">
                  {problem.sampleTestCases.map((tc: any, i: number) => (
                    <div key={i} style={{ marginBottom: i < problem.sampleTestCases.length - 1 ? 16 : 0 }}>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                        <div>
                          <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 4, color: '#666' }}>Input #{i + 1}</div>
                          <pre style={{
                            background: '#f5f5f5',
                            border: '1px solid #ddd',
                            borderRadius: 3,
                            padding: '8px 10px',
                            fontSize: 13,
                            fontFamily: 'Consolas, monospace',
                            margin: 0,
                            whiteSpace: 'pre-wrap',
                          }}>
                            {tc.input}
                          </pre>
                        </div>
                        <div>
                          <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 4, color: '#666' }}>Output #{i + 1}</div>
                          <pre style={{
                            background: '#f5f5f5',
                            border: '1px solid #ddd',
                            borderRadius: 3,
                            padding: '8px 10px',
                            fontSize: 13,
                            fontFamily: 'Consolas, monospace',
                            margin: 0,
                            whiteSpace: 'pre-wrap',
                          }}>
                            {tc.output}
                          </pre>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div>
            <div className="panel">
              <div className="panel-header">Limits</div>
              <div className="panel-body" style={{ fontSize: 13 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid #eee' }}>
                  <span>Time Limit</span>
                  <strong>{problem.timeLimit}ms</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}>
                  <span>Memory Limit</span>
                  <strong>{problem.memoryLimit}MB</strong>
                </div>
              </div>
            </div>

            {problem.statistics && (
              <div className="panel">
                <div className="panel-header">Statistics</div>
                <div className="panel-body" style={{ fontSize: 13 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid #eee' }}>
                    <span>Submissions</span>
                    <strong>{problem.statistics.totalSubmissions}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid #eee' }}>
                    <span>Accepted</span>
                    <strong style={{ color: '#28a745' }}>{problem.statistics.acceptedSubmissions}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}>
                    <span>Acceptance</span>
                    <strong>{problem.statistics.acceptanceRate}%</strong>
                  </div>
                </div>
              </div>
            )}

          </div>
        </div>
      )}
    </div>
  );
}
