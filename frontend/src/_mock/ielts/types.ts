export type IeltsModule = 'reading' | 'listening' | 'writing' | 'speaking'

export type ActiveIeltsModule = Exclude<IeltsModule, 'speaking'>

export type UserRole = 'student' | 'teacher'

export type AttemptStatus =
  | 'not_started'
  | 'in_progress'
  | 'submitted'
  | 'completed'
  | 'terminated'

export type FinishReason = 'manual_submit' | 'timeout' | 'completed' | 'tab_switch'

export type DifficultyLevel = 'foundation' | 'intermediate' | 'advanced'

export type QuestionType =
  | 'multiple_choice'
  | 'true_false_not_given'
  | 'matching_headings'
  | 'matching_information'
  | 'sentence_completion'
  | 'summary_completion'
  | 'short_answer'
  | 'table_completion'
  | 'note_completion'
  | 'list_of_options'

export type RecommendationKind =
  | 'weak_module'
  | 'weak_section'
  | 'weak_question_type'
  | 'time_management'
  | 'integrity'
  | 'writing_criterion'

export type IntegrityEventType =
  | 'visibility_hidden'
  | 'window_blur'
  | 'route_leave'
  | 'before_unload'

export type MockUser = {
  id: string
  name: string
  email: string
  role: UserRole
  createdAt: string
  photoURL?: string
}

export type MockStudent = MockUser & {
  role: 'student'
  teacherId: string
  targetBand: number
  currentEstimatedBand: number
  weeklyStudyMinutes: number
  streakDays: number
  activePlan: {
    name: string
    attemptsLimit: number
    attemptsUsed: number
    renewalDate: string
  }
}

export type MockTeacher = MockUser & {
  role: 'teacher'
  bio: string
  studentIds: string[]
}

export type MockQuestionOption = {
  value: string
  label: string
}

export type MockPassage = {
  id: string
  title: string
  body: string
  supportingNote?: string
}

export type MockQuestionAnswerValue = string | string[] | Record<string, string>

export type MockQuestion = {
  id: string
  testId: string
  sectionId: string
  module: ActiveIeltsModule
  order: number
  number: number
  type: QuestionType
  prompt: string
  instructions?: string
  placeholder?: string
  options?: MockQuestionOption[]
  matchLabels?: string[]
  tableRows?: string[]
  points: number
  correctAnswer: MockQuestionAnswerValue
  explanation?: string
}

export type MockTestSection = {
  id: string
  testId: string
  order: number
  title: string
  instructions: string
  passageId?: string
  audioLabel?: string
  audioDurationSec?: number
  transcript?: string
  questionIds: string[]
}

export type MockWritingPrompt = {
  id: string
  testId: string
  order: number
  taskLabel: 'Task 1' | 'Task 2'
  title: string
  prompt: string
  guidance: string
  minWords: number
  chartSummary?: string
}

export type MockTest = {
  id: string
  module: ActiveIeltsModule
  title: string
  description: string
  overview: string
  durationMinutes: number
  difficulty: DifficultyLevel
  featured: boolean
  tag: string
  questionCount: number
  sectionCount: number
  taskCount: number
  sectionIds: string[]
  writingPromptIds: string[]
  instructions: string[]
}

export type MockAnswer = {
  questionId: string
  value: MockQuestionAnswerValue
  updatedAt: string
}

export type ModuleBandMap = Record<ActiveIeltsModule, number>

export type MockAttempt = {
  id: string
  testId: string
  module: ActiveIeltsModule
  studentId: string
  status: AttemptStatus
  finishReason?: FinishReason
  startedAt: string
  updatedAt: string
  submittedAt?: string
  terminatedAt?: string
  durationMinutes: number
  remainingTimeSec: number
  currentSectionId?: string
  answers: Record<string, MockAnswer>
  integrityEventIds: string[]
  autosaveCount: number
}

export type MockRecommendation = {
  id: string
  kind: RecommendationKind
  severity: 'low' | 'medium' | 'high'
  title: string
  description: string
}

export type MockSectionResult = {
  sectionId: string
  title: string
  correct: number
  total: number
  accuracy: number
  band: number
}

export type MockQuestionTypeResult = {
  type: QuestionType
  correct: number
  total: number
}

export type MockAnswerReviewItem = {
  questionId: string
  number: number
  type: QuestionType
  prompt: string
  userAnswer: string
  correctAnswer: string
  status: 'correct' | 'incorrect' | 'partial' | 'unanswered'
  explanation?: string
}

export type MockWritingRubric = {
  taskAchievement: number
  coherence: number
  lexicalResource: number
  grammarRangeAccuracy: number
}

export type MockWritingSubmission = {
  id: string
  attemptId: string
  studentId: string
  responses: Record<string, string>
  wordCounts: Record<string, number>
  draftSavedAt: string
  submittedAt?: string
  rubric?: MockWritingRubric
  evaluatorSummary?: string
}

export type MockResult = {
  id: string
  attemptId: string
  testId: string
  module: ActiveIeltsModule
  studentId: string
  rawScore: number
  scaledRawScore: number
  totalQuestions: number
  estimatedBand: number
  finishReason: FinishReason
  timeSpentSec: number
  sectionBreakdown: MockSectionResult[]
  questionTypeBreakdown: MockQuestionTypeResult[]
  strengths: string[]
  weaknesses: string[]
  summary: string
  recommendations: MockRecommendation[]
  answerReview: MockAnswerReviewItem[]
  writingCriteria?: MockWritingRubric
  writingSummary?: string
  essayPreview?: Record<string, string>
  strongCriteria?: string[]
  weakCriteria?: string[]
}

export type MockIntegrityEvent = {
  id: string
  attemptId: string
  studentId: string
  type: IntegrityEventType
  severity: 'medium' | 'high'
  createdAt: string
  description: string
}

export type MockTeacherStudentAnalytics = {
  studentId: string
  studentName: string
  studentEmail: string
  targetBand: number
  latestBand: number
  moduleBands: ModuleBandMap
  attemptsCount: number
  weakModule: ActiveIeltsModule
  lastActivity: string
  integrityFlag: boolean
  strengths: string[]
  weaknesses: string[]
  recommendations: string[]
  recentAttemptIds: string[]
}

export type MockActivity = {
  id: string
  studentId: string
  module: ActiveIeltsModule
  title: string
  description: string
  createdAt: string
}

export type MockStore = {
  students: MockStudent[]
  teachers: MockTeacher[]
  attempts: MockAttempt[]
  writingSubmissions: MockWritingSubmission[]
  integrityEvents: MockIntegrityEvent[]
  activities: MockActivity[]
}
