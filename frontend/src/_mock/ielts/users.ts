import type { MockStudent, MockTeacher } from './types'

export const IELTS_TEACHERS: MockTeacher[] = [
  {
    id: 'teacher-1',
    name: 'Sophie Bennett',
    email: 'teacher@ieltsmock.dev',
    role: 'teacher',
    createdAt: '2026-01-08T08:00:00.000Z',
    bio: 'IELTS mentor focused on turning mock-test analytics into weekly study plans.',
    studentIds: ['student-1', 'student-2', 'student-3'],
  },
]

export const IELTS_STUDENTS: MockStudent[] = [
  {
    id: 'student-1',
    name: 'Amina Karimova',
    email: 'student@ieltsmock.dev',
    role: 'student',
    teacherId: 'teacher-1',
    createdAt: '2026-01-10T10:00:00.000Z',
    targetBand: 7.5,
    currentEstimatedBand: 6.5,
    weeklyStudyMinutes: 228,
    streakDays: 6,
    activePlan: {
      name: 'Plus Mock Plan',
      attemptsLimit: 24,
      attemptsUsed: 4,
      renewalDate: '2026-05-12T00:00:00.000Z',
    },
  },
  {
    id: 'student-2',
    name: 'Bekzod Rakhimov',
    email: 'bekzod@ieltsmock.dev',
    role: 'student',
    teacherId: 'teacher-1',
    createdAt: '2026-01-22T09:30:00.000Z',
    targetBand: 6.5,
    currentEstimatedBand: 5.5,
    weeklyStudyMinutes: 164,
    streakDays: 3,
    activePlan: {
      name: 'Starter Plan',
      attemptsLimit: 12,
      attemptsUsed: 8,
      renewalDate: '2026-04-28T00:00:00.000Z',
    },
  },
  {
    id: 'student-3',
    name: 'Dilnoza Usmonova',
    email: 'dilnoza@ieltsmock.dev',
    role: 'student',
    teacherId: 'teacher-1',
    createdAt: '2026-02-02T07:15:00.000Z',
    targetBand: 8,
    currentEstimatedBand: 7,
    weeklyStudyMinutes: 301,
    streakDays: 9,
    activePlan: {
      name: 'Mentor Intensive',
      attemptsLimit: 30,
      attemptsUsed: 11,
      renewalDate: '2026-05-20T00:00:00.000Z',
    },
  },
]
