import { createContext, useContext, useState, useCallback, ReactNode } from 'react';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastContextValue {
  toasts: Toast[];
  showToast: (message: string, type?: ToastType) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((message: string, type: ToastType = 'info') => {
    const id = `${Date.now()}-${Math.random()}`;
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4000);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, showToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used inside ToastProvider');
  return ctx.showToast;
}

/* ─── Toast Container ─── */
const ICONS: Record<ToastType, string> = {
  success: '✅',
  error: '❌',
  warning: '⚠️',
  info: 'ℹ️',
};

const COLORS: Record<ToastType, { bg: string; border: string; text: string }> = {
  success: { bg: '#f0fdf4', border: '#86efac', text: '#166534' },
  error:   { bg: '#fef2f2', border: '#fca5a5', text: '#991b1b' },
  warning: { bg: '#fffbeb', border: '#fcd34d', text: '#92400e' },
  info:    { bg: '#eff6ff', border: '#93c5fd', text: '#1e40af' },
};

function ToastContainer({ toasts, onRemove }: { toasts: Toast[]; onRemove: (id: string) => void }) {
  if (!toasts.length) return null;

  return (
    <div
      style={{
        position: 'fixed',
        bottom: 24,
        right: 24,
        zIndex: 9999,
        display: 'flex',
        flexDirection: 'column',
        gap: 10,
        pointerEvents: 'none',
      }}
    >
      {toasts.map(toast => {
        const colors = COLORS[toast.type];
        return (
          <div
            key={toast.id}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              padding: '12px 16px',
              background: colors.bg,
              border: `1px solid ${colors.border}`,
              borderRadius: 8,
              boxShadow: '0 4px 12px rgba(0,0,0,0.12)',
              minWidth: 280,
              maxWidth: 420,
              fontSize: 14,
              color: colors.text,
              fontWeight: 500,
              pointerEvents: 'all',
              animation: 'toast-slide-in 0.25s ease',
            }}
          >
            <span style={{ fontSize: 16 }}>{ICONS[toast.type]}</span>
            <span style={{ flex: 1 }}>{toast.message}</span>
            <button
              onClick={() => onRemove(toast.id)}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                fontSize: 16,
                color: colors.text,
                opacity: 0.5,
                padding: 0,
                lineHeight: 1,
              }}
            >
              ×
            </button>
          </div>
        );
      })}
      <style>{`
        @keyframes toast-slide-in {
          from { opacity: 0; transform: translateX(40px); }
          to   { opacity: 1; transform: translateX(0); }
        }
      `}</style>
    </div>
  );
}
