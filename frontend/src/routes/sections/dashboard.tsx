import { Suspense, lazy } from 'react';
import { Outlet } from 'react-router-dom';
// auth
import { AuthGuard, RoleBasedGuard } from 'src/auth/guard';
// layouts
import DashboardLayout from 'src/layouts/dashboard';
// components
import { LoadingScreen } from 'src/components/loading-screen';

// ----------------------------------------------------------------------

const IeltsDashboardPage = lazy(() => import('../../pages/ielts-dashboard'));
const IeltsReadingPage = lazy(() => import('../../pages/ielts-reading'));
const IeltsReadingTestPage = lazy(() => import('../../pages/ielts-reading-test'));
const IeltsReadingSessionPage = lazy(() => import('../../pages/ielts-reading-session'));
const IeltsReadingResultPage = lazy(() => import('../../pages/ielts-reading-result'));

const IeltsListeningPage = lazy(() => import('../../pages/ielts-listening'));
const IeltsListeningTestPage = lazy(() => import('../../pages/ielts-listening-test'));
const IeltsListeningSessionPage = lazy(() => import('../../pages/ielts-listening-session'));
const IeltsListeningResultPage = lazy(() => import('../../pages/ielts-listening-result'));

const IeltsWritingPage = lazy(() => import('../../pages/ielts-writing'));
const IeltsWritingTestPage = lazy(() => import('../../pages/ielts-writing-test'));
const IeltsWritingSessionPage = lazy(() => import('../../pages/ielts-writing-session'));
const IeltsWritingResultPage = lazy(() => import('../../pages/ielts-writing-result'));

const IeltsMyTestsPage = lazy(() => import('../../pages/ielts-my-tests'));
const IeltsProfilePage = lazy(() => import('../../pages/ielts-profile'));

const IeltsTeacherDashboardPage = lazy(() => import('../../pages/ielts-teacher-dashboard'));
const IeltsTeacherStudentsPage = lazy(() => import('../../pages/ielts-teacher-students'));
const IeltsTeacherStudentDetailsPage = lazy(
  () => import('../../pages/ielts-teacher-student-details')
);
const IeltsTeacherAttemptDetailsPage = lazy(
  () => import('../../pages/ielts-teacher-attempt-details')
);
const IeltsTeacherAnalyticsPage = lazy(() => import('../../pages/ielts-teacher-analytics'));

// ----------------------------------------------------------------------

export const dashboardRoutes = [
  {
    element: (
      <AuthGuard>
        <Suspense fallback={<LoadingScreen />}>
          <Outlet />
        </Suspense>
      </AuthGuard>
    ),
    children: [
      {
        path: 'dashboard/reading/tests/:testId/session',
        element: (
          <RoleBasedGuard roles={['student']}>
            <IeltsReadingSessionPage />
          </RoleBasedGuard>
        ),
      },
      {
        path: 'dashboard/listening/tests/:testId/session',
        element: (
          <RoleBasedGuard roles={['student']}>
            <IeltsListeningSessionPage />
          </RoleBasedGuard>
        ),
      },
      {
        path: 'dashboard/writing/tests/:testId/session',
        element: (
          <RoleBasedGuard roles={['student']}>
            <IeltsWritingSessionPage />
          </RoleBasedGuard>
        ),
      },
    ],
  },
  {
    element: (
      <AuthGuard>
        <DashboardLayout>
          <Suspense fallback={<LoadingScreen />}>
            <Outlet />
          </Suspense>
        </DashboardLayout>
      </AuthGuard>
    ),
    children: [
      {
        path: 'dashboard',
        element: <Outlet />,
        children: [
          {
            index: true,
            element: (
              <RoleBasedGuard roles={['student']}>
                <IeltsDashboardPage />
              </RoleBasedGuard>
            ),
          },
          {
            path: 'reading',
            element: (
              <RoleBasedGuard roles={['student']}>
                <IeltsReadingPage />
              </RoleBasedGuard>
            ),
          },
          {
            path: 'reading/tests/:testId',
            element: (
              <RoleBasedGuard roles={['student']}>
                <IeltsReadingTestPage />
              </RoleBasedGuard>
            ),
          },
          {
            path: 'reading/attempts/:attemptId',
            element: (
              <RoleBasedGuard roles={['student']}>
                <IeltsReadingResultPage />
              </RoleBasedGuard>
            ),
          },
          {
            path: 'listening',
            element: (
              <RoleBasedGuard roles={['student']}>
                <IeltsListeningPage />
              </RoleBasedGuard>
            ),
          },
          {
            path: 'listening/tests/:testId',
            element: (
              <RoleBasedGuard roles={['student']}>
                <IeltsListeningTestPage />
              </RoleBasedGuard>
            ),
          },
          {
            path: 'listening/attempts/:attemptId',
            element: (
              <RoleBasedGuard roles={['student']}>
                <IeltsListeningResultPage />
              </RoleBasedGuard>
            ),
          },
          {
            path: 'writing',
            element: (
              <RoleBasedGuard roles={['student']}>
                <IeltsWritingPage />
              </RoleBasedGuard>
            ),
          },
          {
            path: 'writing/tests/:testId',
            element: (
              <RoleBasedGuard roles={['student']}>
                <IeltsWritingTestPage />
              </RoleBasedGuard>
            ),
          },
          {
            path: 'writing/attempts/:attemptId',
            element: (
              <RoleBasedGuard roles={['student']}>
                <IeltsWritingResultPage />
              </RoleBasedGuard>
            ),
          },
          {
            path: 'my-tests',
            element: (
              <RoleBasedGuard roles={['student']}>
                <IeltsMyTestsPage />
              </RoleBasedGuard>
            ),
          },
          {
            path: 'profile',
            element: (
              <RoleBasedGuard roles={['student']}>
                <IeltsProfilePage />
              </RoleBasedGuard>
            ),
          },
          {
            path: 'teacher',
            element: (
              <RoleBasedGuard roles={['teacher']}>
                <IeltsTeacherDashboardPage />
              </RoleBasedGuard>
            ),
          },
          {
            path: 'teacher/students',
            element: (
              <RoleBasedGuard roles={['teacher']}>
                <IeltsTeacherStudentsPage />
              </RoleBasedGuard>
            ),
          },
          {
            path: 'teacher/students/:studentId',
            element: (
              <RoleBasedGuard roles={['teacher']}>
                <IeltsTeacherStudentDetailsPage />
              </RoleBasedGuard>
            ),
          },
          {
            path: 'teacher/attempts/:attemptId',
            element: (
              <RoleBasedGuard roles={['teacher']}>
                <IeltsTeacherAttemptDetailsPage />
              </RoleBasedGuard>
            ),
          },
          {
            path: 'teacher/analytics',
            element: (
              <RoleBasedGuard roles={['teacher']}>
                <IeltsTeacherAnalyticsPage />
              </RoleBasedGuard>
            ),
          },
        ],
      },
    ],
  },
];
