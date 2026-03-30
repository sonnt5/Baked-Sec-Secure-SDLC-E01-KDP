import { Outlet } from 'react-router-dom';
import Header from './Header';

export default function Layout() {
  return (
    <>
      <Header />
      <main style={{ flex: 1 }}>
        <Outlet />
      </main>
      <footer className="footer">
        © 2026 Coding War · Built with ❤️ for competitive programmers
      </footer>
    </>
  );
}
