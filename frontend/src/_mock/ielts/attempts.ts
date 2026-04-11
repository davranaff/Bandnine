import {
  IELTS_QUESTIONS,
  IELTS_TESTS,
} from './tests'
import type {
  MockAnswer,
  MockAttempt,
  MockActivity,
  MockIntegrityEvent,
  MockQuestionAnswerValue,
  QuestionType,
  MockWritingSubmission,
} from './types'

function nowOffset(days: number, hours = 0) {
  const date = new Date('2026-04-10T09:00:00.000Z')
  date.setDate(date.getDate() + days)
  date.setHours(date.getHours() + hours)
  return date.toISOString()
}

function flattenAnswerValue(value: MockQuestionAnswerValue) {
  if (typeof value === 'string') return value
  if (Array.isArray(value)) return value[0] || ''
  const first = Object.values(value)[0]
  return first || ''
}

function wrongValue(type: QuestionType, correct: MockQuestionAnswerValue): MockQuestionAnswerValue {
  if (type === 'true_false_not_given') {
    return flattenAnswerValue(correct) === 'True' ? 'False' : 'True'
  }

  if (typeof correct === 'string') {
    return `${correct} x`
  }

  if (Array.isArray(correct)) {
    return [...correct].reverse()
  }

  return Object.keys(correct).reduce<Record<string, string>>((acc, key) => {
    acc[key] = `${correct[key]} x`
    return acc
  }, {})
}

function buildAttemptAnswers(testId: string, wrongNumbers: number[]) {
  const relevantQuestions = IELTS_QUESTIONS.filter((question) => question.testId === testId)

  return relevantQuestions.reduce<Record<string, MockAnswer>>((acc, question) => {
    const value = wrongNumbers.includes(question.number)
      ? wrongValue(question.type, question.correctAnswer)
      : question.correctAnswer

    acc[question.id] = {
      questionId: question.id,
      value,
      updatedAt: nowOffset(-6, question.number),
    }

    return acc
  }, {})
}

const readingDuration = IELTS_TESTS.find((test) => test.id === 'reading-test-1')?.durationMinutes || 60
const listeningDuration = IELTS_TESTS.find((test) => test.id === 'listening-test-1')?.durationMinutes || 40
const writingDuration = IELTS_TESTS.find((test) => test.id === 'writing-test-1')?.durationMinutes || 60

export const IELTS_ATTEMPTS: MockAttempt[] = [
  {
    id: 'attempt-reading-1',
    testId: 'reading-test-1',
    module: 'reading',
    studentId: 'student-1',
    status: 'completed',
    finishReason: 'completed',
    startedAt: nowOffset(-8),
    updatedAt: nowOffset(-8, 1),
    submittedAt: nowOffset(-8, 1),
    durationMinutes: readingDuration,
    remainingTimeSec: 460,
    currentSectionId: 'reading-1-sec-3',
    answers: buildAttemptAnswers('reading-test-1', [2, 7, 11]),
    integrityEventIds: [],
    autosaveCount: 7,
  },
  {
    id: 'attempt-listening-1',
    testId: 'listening-test-1',
    module: 'listening',
    studentId: 'student-1',
    status: 'completed',
    finishReason: 'manual_submit',
    startedAt: nowOffset(-4),
    updatedAt: nowOffset(-4, 1),
    submittedAt: nowOffset(-4, 1),
    durationMinutes: listeningDuration,
    remainingTimeSec: 180,
    currentSectionId: 'listening-1-sec-2',
    answers: buildAttemptAnswers('listening-test-1', [5, 9]),
    integrityEventIds: [],
    autosaveCount: 5,
  },
  {
    id: 'attempt-writing-1',
    testId: 'writing-test-1',
    module: 'writing',
    studentId: 'student-1',
    status: 'completed',
    finishReason: 'completed',
    startedAt: nowOffset(-2),
    updatedAt: nowOffset(-2, 1),
    submittedAt: nowOffset(-2, 1),
    durationMinutes: writingDuration,
    remainingTimeSec: 320,
    answers: {},
    integrityEventIds: [],
    autosaveCount: 4,
  },
  {
    id: 'attempt-bekzod-reading',
    testId: 'reading-test-1',
    module: 'reading',
    studentId: 'student-2',
    status: 'terminated',
    finishReason: 'tab_switch',
    startedAt: nowOffset(-3),
    updatedAt: nowOffset(-3),
    terminatedAt: nowOffset(-3),
    durationMinutes: readingDuration,
    remainingTimeSec: 3120,
    currentSectionId: 'reading-1-sec-1',
    answers: buildAttemptAnswers('reading-test-1', [1, 2, 3, 4, 5, 6, 7]),
    integrityEventIds: ['integrity-1'],
    autosaveCount: 3,
  },
  {
    id: 'attempt-bekzod-listening',
    testId: 'listening-test-1',
    module: 'listening',
    studentId: 'student-2',
    status: 'completed',
    finishReason: 'completed',
    startedAt: nowOffset(-7),
    updatedAt: nowOffset(-7, 1),
    submittedAt: nowOffset(-7, 1),
    durationMinutes: listeningDuration,
    remainingTimeSec: 60,
    currentSectionId: 'listening-1-sec-2',
    answers: buildAttemptAnswers('listening-test-1', [1, 2, 3, 6, 8]),
    integrityEventIds: [],
    autosaveCount: 5,
  },
  {
    id: 'attempt-dilnoza-writing',
    testId: 'writing-test-2',
    module: 'writing',
    studentId: 'student-3',
    status: 'completed',
    finishReason: 'completed',
    startedAt: nowOffset(-5),
    updatedAt: nowOffset(-5, 1),
    submittedAt: nowOffset(-5, 1),
    durationMinutes: 60,
    remainingTimeSec: 110,
    answers: {},
    integrityEventIds: [],
    autosaveCount: 6,
  },
  {
    id: 'attempt-dilnoza-reading',
    testId: 'reading-test-2',
    module: 'reading',
    studentId: 'student-3',
    status: 'completed',
    finishReason: 'completed',
    startedAt: nowOffset(-1),
    updatedAt: nowOffset(-1, 1),
    submittedAt: nowOffset(-1, 1),
    durationMinutes: 60,
    remainingTimeSec: 720,
    currentSectionId: 'reading-2-sec-3',
    answers: buildAttemptAnswers('reading-test-2', [6, 8]),
    integrityEventIds: [],
    autosaveCount: 8,
  },
]

export const IELTS_INTEGRITY_EVENTS: MockIntegrityEvent[] = [
  {
    id: 'integrity-1',
    attemptId: 'attempt-bekzod-reading',
    studentId: 'student-2',
    type: 'visibility_hidden',
    severity: 'high',
    createdAt: nowOffset(-3),
    description: 'Exam tab was hidden during an active reading session. Attempt terminated immediately.',
  },
]

export const IELTS_WRITING_SUBMISSIONS: MockWritingSubmission[] = [
  {
    id: 'submission-writing-1',
    attemptId: 'attempt-writing-1',
    studentId: 'student-1',
    responses: {
      'writing-1-task-1':
        'The process begins when used paper is collected and sorted before it is turned into pulp. After that, the material is cleaned to remove unwanted particles, pressed into sheets, and dried before being reused. Overall, the system transforms waste paper into a usable product through a clear sequence of mechanical stages.',
      'writing-1-task-2':
        'Universities should keep academic depth at the center of their mission, but practical skills also deserve a firm place in higher education. Academic subjects train students to think critically, whereas practical work helps them transfer knowledge into real contexts. In my view, the strongest programs combine both instead of treating them as competing priorities.',
    },
    wordCounts: {
      'writing-1-task-1': 56,
      'writing-1-task-2': 64,
    },
    draftSavedAt: nowOffset(-2, 1),
    submittedAt: nowOffset(-2, 1),
    rubric: {
      taskAchievement: 6.5,
      coherence: 6.5,
      lexicalResource: 6,
      grammarRangeAccuracy: 6.5,
    },
    evaluatorSummary:
      'Clear structure and relevant ideas, but both tasks need fuller development and more precise vocabulary to reach a stronger band.',
  },
  {
    id: 'submission-dilnoza-writing',
    attemptId: 'attempt-dilnoza-writing',
    studentId: 'student-3',
    responses: {
      'writing-2-task-1':
        'The chart illustrates changes in transport use between 2005 and 2025. Overall, private cars became less dominant, while public transport and cycling gained a larger share. Walking changed very little across the period.',
      'writing-2-task-2':
        'A shortage of affordable housing creates pressure on families, public services, and labor mobility. People may be forced to move far from work, live in overcrowded conditions, or postpone important decisions such as marriage and education. Cities can respond by reforming zoning, accelerating social housing, and supporting transport links to new residential areas.',
    },
    wordCounts: {
      'writing-2-task-1': 37,
      'writing-2-task-2': 55,
    },
    draftSavedAt: nowOffset(-5, 1),
    submittedAt: nowOffset(-5, 1),
    rubric: {
      taskAchievement: 7.5,
      coherence: 7,
      lexicalResource: 7,
      grammarRangeAccuracy: 6.5,
    },
    evaluatorSummary:
      'Strong control of overview and paragraphing. Grammar accuracy softened slightly under time pressure, but the response remains consistent and well targeted.',
  },
]

export const IELTS_ACTIVITIES: MockActivity[] = [
  {
    id: 'activity-1',
    studentId: 'student-1',
    module: 'reading',
    title: 'Reading mock completed',
    description: 'Academic Reading Mock 01 finished with band 7.0 estimate.',
    createdAt: nowOffset(-8, 1),
  },
  {
    id: 'activity-2',
    studentId: 'student-1',
    module: 'listening',
    title: 'Listening session submitted',
    description: 'Listening Mock 01 saved with strong note completion accuracy.',
    createdAt: nowOffset(-4, 1),
  },
  {
    id: 'activity-3',
    studentId: 'student-1',
    module: 'writing',
    title: 'Writing feedback received',
    description: 'Task response is improving, but lexical range still needs work.',
    createdAt: nowOffset(-2, 1),
  },
  {
    id: 'activity-4',
    studentId: 'student-2',
    module: 'reading',
    title: 'Integrity alert recorded',
    description: 'Reading session terminated after exam tab was hidden.',
    createdAt: nowOffset(-3),
  },
  {
    id: 'activity-5',
    studentId: 'student-3',
    module: 'reading',
    title: 'New personal best',
    description: 'Academic Reading Mock 02 lifted estimated band to 8.0.',
    createdAt: nowOffset(-1, 1),
  },
]
