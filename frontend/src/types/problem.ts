export interface Problem {
  id: number;
  title: string;
  slug: string;
  description: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  difficulty_color: string;
  category?: string;
  time_limit: number;
  memory_limit: number;
  tags?: string;
  hints?: string;
  constraints?: string;
  total_submissions: number;
  accepted_submissions: number;
  acceptance_rate: number;
  created_at: string;
  updated_at: string;
  test_cases?: TestCase[];
}

export interface TestCase {
  id: number;
  problem_id: number;
  input_data?: string;
  expected_output?: string;
  input_preview: string;
  output_preview: string;
  is_sample: boolean;
  is_hidden: boolean;
  description?: string;
  weight: number;
  time_limit?: number;
  memory_limit?: number;
  created_at: string;
}

export interface ProblemFilters {
  difficulty?: string;
  category?: string;
  search?: string;
  page?: number;
  per_page?: number;
}

export interface ProblemsResponse {
  problems: Problem[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

export interface ProblemStats {
  total_problems: number;
  difficulty_distribution: Array<{
    difficulty: string;
    count: number;
  }>;
  category_distribution: Array<{
    category: string;
    count: number;
  }>;
}