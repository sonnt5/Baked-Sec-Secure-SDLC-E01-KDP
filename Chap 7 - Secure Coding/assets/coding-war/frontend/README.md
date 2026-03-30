# Coding War — Frontend

React + TypeScript frontend for the Coding War online judge platform.

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | React 19 + TypeScript |
| Build Tool | Vite |
| State Management | Zustand |
| Server State | TanStack Query (React Query) |
| Routing | React Router v7 |
| Real-time | Socket.io Client |
| Markdown | react-markdown + remark-gfm |
| HTTP Client | Axios |

## Project Structure

```
src/
├── api/
│   ├── client.ts              # Axios instance with auth interceptors
│   └── endpoints/             # Typed API modules per domain
│       ├── auth.ts
│       ├── problems.ts
│       ├── submissions.ts
│       ├── contests.ts
│       ├── users.ts
│       └── admin.ts
├── components/                # Shared UI components
├── contexts/                  # React contexts (Toast)
├── hooks/
│   └── queries/               # TanStack Query hooks per domain
├── pages/
│   ├── admin/                 # AdminDashboard, AdminCreateProblem, AdminEditProblem
│   ├── auth/                  # Login, Register, ForgotPassword, ResetPassword
│   ├── contests/              # ContestList, ContestDetail, Scoreboard
│   ├── problems/              # ProblemList, ProblemDetail
│   ├── submissions/           # SubmissionList, SubmissionDetail
│   └── users/                 # UserProfile
├── stores/
│   └── authStore.ts           # Zustand auth store (JWT persistence)
└── types/
    └── api.ts                 # Shared TypeScript types
```

## Pages & Features

### Authentication
- Register / Login / Forgot password / Reset password
- JWT stored in `localStorage`, auto-injected by Axios interceptor
- Redirect to login on 401

### Problems
- Paginated, filterable problem list (difficulty, search)
- Problem detail with Markdown + GFM rendering
- Submit solution (C, C++, Python, Java) with 10s cooldown
- **Resubmit** — from submission detail, pre-fills editor with previous code

### Submissions
- Submission list with status polling
- Submission detail: DMOJ-style verdict banner, test case grid, source code viewer
- Real-time status updates via Socket.io

### Contests
- Contest list with status badges (Upcoming / Active / Ended)
- Contest detail: Info / Problems / Scoreboard tabs
- Problem list always visible to admins (warning banner for upcoming contests)
- Problem titles and difficulty badges
- Live scoreboard

### Admin Panel (`/admin`)
- **Dashboard**: system statistics
- **Users**: search, view, change role
- **Problems**: create, edit (with inline test case manager), delete
  - Add individual test cases (input + expected output text)
  - Visualize & delete existing test cases
- **Contests**: create with problem selection, view all

## Quick Start

```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # Production build
npm run lint       # ESLint
```

### Environment Variables

Create `.env.local`:

```env
VITE_API_BASE_URL=http://localhost:3000
```

> If not set, Vite's proxy (`vite.config.ts`) forwards `/api` and `/socket.io` to `localhost:3000`.

## API Integration

All API calls are typed and go through `src/api/client.ts` (Axios). Auth tokens are automatically attached. 401 responses clear the store and redirect to `/login`.

Endpoints are organized by domain in `src/api/endpoints/`:

```ts
problemsAPI.list({ page, limit, difficulty, search })
problemsAPI.getTestCases(problemId)
problemsAPI.addTestCase(problemId, { inputContent, outputContent, isSample })
problemsAPI.deleteTestCase(problemId, testCaseId)

contestsAPI.create({ title, startTime, endTime, scoringRule, problems: [{problemId, orderIndex}] })
contestsAPI.updateProblems(contestId, problems)
```
