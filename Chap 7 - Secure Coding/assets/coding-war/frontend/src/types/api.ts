// Authentication Types
export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  role: 'USER' | 'ADMIN';
  createdAt: string;
}

// Problem Types
export interface Problem {
  id: string;
  title: string;
  slug?: string;
  description: string;
  difficulty: 'EASY' | 'MEDIUM' | 'HARD';
  timeLimit: number;
  memoryLimit: number;
  tags: string[];
  userSolved?: boolean;
  sampleTestCases: TestCase[];
  statistics?: {
    totalSubmissions: number;
    acceptedSubmissions: number;
    acceptanceRate: number;
  };
  createdAt: string;
  updatedAt: string;
}

export interface TestCase {
  input: string;
  output: string;
  explanation?: string;
}

export interface ProblemFilters {
  page?: number;
  limit?: number;
  difficulty?: 'EASY' | 'MEDIUM' | 'HARD';
  tags?: string[];
  search?: string;
}

export interface ProblemListResponse {
  problems: Problem[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// Submission Types
export interface CreateSubmissionRequest {
  problemId: string;
  language: 'C' | 'CPP' | 'PYTHON' | 'JAVA';
  sourceCode: string;
  contestId?: string;
}

export interface Submission {
  id: string;
  problemId: string;
  problemTitle?: string;
  problem?: { title: string };
  userId: string;
  username?: string;
  language: 'C' | 'CPP' | 'PYTHON' | 'JAVA';
  sourceCode: string;
  status: SubmissionStatus;
  verdict?: SubmissionVerdict;
  executionTime?: number;
  memoryUsed?: number;
  testCaseResults?: TestCaseResult[];
  compilationError?: string;
  contestId?: string;
  score?: number;
  submittedAt: string;
  judgedAt?: string;
  createdAt: string;
  updatedAt: string;
}

export type SubmissionStatus = 
  | 'QUEUED' | 'COMPILING' | 'RUNNING'
  | 'ACCEPTED' | 'WRONG_ANSWER'
  | 'TIME_LIMIT_EXCEEDED' | 'MEMORY_LIMIT_EXCEEDED'
  | 'RUNTIME_ERROR' | 'COMPILATION_ERROR';

export type SubmissionVerdict = 
  | 'ACCEPTED' | 'WRONG_ANSWER'
  | 'TIME_LIMIT_EXCEEDED' | 'MEMORY_LIMIT_EXCEEDED'
  | 'RUNTIME_ERROR' | 'COMPILATION_ERROR';

export interface TestCaseResult {
  testCaseNumber: number;
  status: SubmissionVerdict;
  executionTime: number;
  memoryUsed: number;
}

export interface SubmissionFilters {
  page?: number;
  limit?: number;
  userId?: string;
  problemId?: string;
  status?: SubmissionVerdict;
  startDate?: string;
  endDate?: string;
}

export interface SubmissionListResponse {
  submissions: Submission[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// Contest Types
export interface Contest {
  id: string;
  title: string;
  description: string;
  startTime: string;
  endTime: string;
  freezeTime?: string;
  scoringType: 'ioi' | 'acm';
  scoringRule?: 'IOI' | 'ACM';
  isPublic: boolean;
  participantCount: number;
  problems: ContestProblem[];
  createdAt: string;
  updatedAt: string;
}

export interface ContestProblem {
  problemId: string;
  points?: number;
  order: number;
}

export interface ContestListResponse {
  contests: Contest[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface ScoreboardEntry {
  rank: number;
  userId: string;
  username: string;
  solved: number;
  score: number;
  penalty?: number;
  problemResults: ProblemResult[];
}

export interface ProblemResult {
  problemId: string;
  status: 'accepted' | 'attempted' | 'not_attempted';
  score?: number;
  attempts?: number;
  time?: number;
}

export interface ProblemScoreEntry {
  problemId: string;
  score: number;
  attempts: number;
  solvedAt: string | null;
  penaltyMinutes: number;
}

export interface ScoreboardParticipant {
  rank: number;
  userId: string;
  username: string;
  totalScore: number;
  solvedCount: number;
  penaltyTime: number;
  problems: ProblemScoreEntry[];
}

export interface ScoreboardResponse {
  participants: ScoreboardParticipant[];
  isFrozen: boolean;
  freezeTime?: string;
}

// User Types
export interface UserProfile {
  id: string;
  username: string;
  email?: string;
  role: 'USER' | 'ADMIN';
  statistics: UserStatistics;
  recentSubmissions?: any[];
  createdAt: string;
}

export interface UserStatistics {
  totalSubmissions: number;
  acceptedSubmissions: number;
  acceptanceRate: number;
  solvedProblems: number;
  contestsParticipated: number;
}

export interface UpdateUserRequest {
  email?: string;
  currentPassword?: string;
  newPassword?: string;
}

// Admin Types
export interface AdminUserListResponse {
  users: User[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface AdminStatistics {
  totalUsers: number;
  totalProblems: number;
  totalSubmissions: number;
  totalContests: number;
  activeUsers: number;
}

// Generic API Response
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}
