import { Link } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'

function App() {
  const { isAuthenticated, user } = useAuthStore()

  return (
    <div className="content">
      <div className="home-layout">
        {/* Main content */}
        <div>
          <div className="home-welcome">
            <h1>Welcome to Coding War</h1>
            <p>An online judge for competitive programming practice and contests.</p>
          </div>

          {isAuthenticated && user && (
            <div className="panel">
              <div className="panel-header">👋 Hi, {user.username}</div>
              <div className="panel-body">
                <p style={{ marginBottom: 10 }}>Ready to solve some problems?</p>
                <Link to="/problems" className="btn btn-primary btn-sm" style={{ marginRight: 8 }}>Browse Problems</Link>
                <Link to="/contests" className="btn btn-sm">View Contests</Link>
              </div>
            </div>
          )}

          <div className="panel">
            <div className="panel-header">📢 Announcements</div>
            <div className="panel-body">
              <div className="news-item">
                <h4><a href="#">Platform Launch</a></h4>
                <div className="date">March 2026</div>
                <p style={{ fontSize: 13, color: '#666', marginTop: 2 }}>Coding War is now live! Start by solving practice problems or join an upcoming contest.</p>
              </div>
              <div className="news-item">
                <h4><a href="#">Judge System Ready</a></h4>
                <div className="date">March 2026</div>
                <p style={{ fontSize: 13, color: '#666', marginTop: 2 }}>Support for C, C++, Python, and Java with Docker-based sandboxing.</p>
              </div>
            </div>
          </div>

          {!isAuthenticated && (
            <div className="panel">
              <div className="panel-header">🚀 Getting Started</div>
              <div className="panel-body">
                <p style={{ fontSize: 13 }}>
                  <Link to="/register">Create an account</Link> to start submitting solutions and tracking your progress.
                  Already have an account? <Link to="/login">Log in</Link>.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="sidebar">
          <div className="panel">
            <div className="panel-header">Quick Links</div>
            <div className="panel-body quick-links">
              <Link to="/problems">📋 Problem List</Link>
              <Link to="/contests">🏆 Contests</Link>
              {isAuthenticated && <Link to="/submissions">📝 My Submissions</Link>}
              {user?.role === 'ADMIN' && <Link to="/admin">⚙️ Admin Panel</Link>}
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">Platform Stats</div>
            <div className="panel-body" style={{ fontSize: 13 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid #eee' }}>
                <span>Problems</span>
                <strong>500+</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid #eee' }}>
                <span>Languages</span>
                <strong>4</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid #eee' }}>
                <span>Scoring</span>
                <strong>IOI / ACM</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}>
                <span>Judge</span>
                <strong>Real-time</strong>
              </div>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">Supported Languages</div>
            <div className="panel-body" style={{ fontSize: 13 }}>
              <div>• C (GCC)</div>
              <div>• C++ (G++)</div>
              <div>• Python 3</div>
              <div>• Java (OpenJDK)</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
