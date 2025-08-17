export type SubmissionStatus = 
  | 'Pending' 
  | 'Running' 
  | 'Accepted' 
  | 'Wrong Answer' 
  | 'Time Limit Exceeded' 
  | 'Memory Limit Exceeded' 
  | 'Runtime Error' 
  | 'Compilation Error' 
  | 'System Error';

export type ProgrammingLanguage = 'python' | 'javascript' | 'java' | 'cpp' | 'go';

export interface Submission {
  id: number;
  user_id: number;
  problem_id: number;
  language: ProgrammingLanguage;
  code?: string;
  status: SubmissionStatus;
  status_color: string;
  runtime?: number;
  memory_used?: number;
  score: number;
  test_cases_passed: number;
  total_test_cases: number;
  success_rate: number;
  submitted_at: string;
  judged_at?: string;
  contest_id?: number;
  compiler_output?: string;
  error_message?: string;
  execution_id?: string;
}

export interface SubmissionRequest {
  problem_id: number;
  language: ProgrammingLanguage;
  code: string;
  contest_id?: number;
}

export interface SubmissionsResponse {
  submissions: Submission[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

export interface SubmissionStats {
  total_submissions: number;
  accepted_submissions: number;
  success_rate: number;
  language_distribution: Array<{
    language: string;
    count: number;
  }>;
  status_distribution: Array<{
    status: string;
    count: number;
  }>;
}

export interface CodeExecutionResult {
  status: string;
  output: string;
  error?: string;
  runtime: number;
  memory_used: number;
}