export interface User {
  id: number
  username: string
  role: 'student' | 'teacher'
  display_name: string
  real_name?: string
  grade?: string
  school?: string
}

export interface EssayTopic {
  id: number
  title: string
  type: '命题' | '半命题' | '材料' | '话题'
  genre: '记叙文' | '议论文'
  difficulty: number
  source: 'system' | 'teacher'
  creator_id?: number
  tips?: string
  word_requirement: number
  time_minutes: number
  extra_requirements?: string
  created_at: string
}

export interface Essay {
  id: number
  student_id: number
  topic_id: number
  topic?: EssayTopic
  title: string
  content: string
  word_count: number
  status: 'draft' | 'submitted' | 'grading' | 'graded'
  submitted_at: string
  graded_at?: string
  graded_by?: number
  grading_requested_at?: string
}

export interface BasicErrors {
  typos: { text: string; correction: string; position: number }[]
  grammar: { text: string; suggestion: string; position: number }[]
  punctuation: { text: string; correction: string; position: number }[]
}

export interface ParagraphReview {
  paragraph_index: number
  original: string
  comment: string
  suggestion?: string
}

export interface EssayReport {
  id: number
  essay_id: number
  total_score: number
  score_thesis: number
  score_content: number
  score_language: number
  score_structure: number
  score_penmanship: number
  level?: string
  deduction_reason?: string
  word_count_actual?: number
  basic_errors: BasicErrors
  paragraph_reviews: ParagraphReview[]
  overall_comment: string
  suggestions: string[]
  model_used: string
  processing_time_ms: number
  created_at: string
}

export interface AIConfig {
  id: number
  user_id: number
  provider: string
  model_name: string
  grading_model_name?: string
  ocr_model_name?: string
  routing_strategy: 'smart' | 'cloud' | 'local'
  is_active: boolean
}

// v2.0 types
export interface OCRConfig {
  id: number
  user_id: number
  model_name: string
  base_url?: string
  is_active: boolean
}

export interface GradingConfig {
  id: number
  user_id: number
  provider: string
  grading_model_name: string
  ability_model_name?: string
  base_url?: string
  local_endpoint_url?: string
  is_active: boolean
}

export interface ClassInfo {
  id: number
  name: string
  teacher_id: number
  created_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}
