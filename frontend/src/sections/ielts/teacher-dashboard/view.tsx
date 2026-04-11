// @mui
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
// locales
import { useLocales } from 'src/locales';
// api
import { useTeacherDashboardQuery } from '../shared/api/use-ielts';
// components
import { InsightListCard, IeltsPageHeader } from '../shared/components';
import { CompletionStatsCard, DashboardMetricsGrid, RecentAttemptsCard } from './components';
import { IeltsTeacherDashboardSkeleton } from './skeleton';

// ----------------------------------------------------------------------

export default function IeltsTeacherDashboardView() {
  const { tx } = useLocales();
  const dashboardQuery = useTeacherDashboardQuery();

  if (dashboardQuery.isLoading || !dashboardQuery.data) {
    return (
      <Container maxWidth="lg">
        <IeltsTeacherDashboardSkeleton />
      </Container>
    );
  }

  const { data } = dashboardQuery;

  return (
    <Container maxWidth="lg">
      <IeltsPageHeader
        title={tx('pages.ielts.teacher.dashboard_title')}
        description={tx('pages.ielts.teacher.dashboard_description', {
          name: data.teacher.name,
        })}
      />

      <DashboardMetricsGrid data={data} />

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <InsightListCard
            title={tx('pages.ielts.teacher.students_at_risk')}
            items={data.studentsAtRisk.map(
              (item) => `${item.studentName} · ${item.latestBand.toFixed(1)}`
            )}
            emptyLabel={tx('pages.ielts.shared.empty_title')}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <InsightListCard
            title={tx('pages.ielts.teacher.top_improvers')}
            items={data.topImprovers.map(
              (item) => `${item.studentName} · ${item.latestBand.toFixed(1)}`
            )}
            emptyLabel={tx('pages.ielts.shared.empty_title')}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <CompletionStatsCard data={data} />
        </Grid>

        <Grid item xs={12}>
          <RecentAttemptsCard title={tx('pages.ielts.teacher.recent_attempts')} data={data} />
        </Grid>
      </Grid>
    </Container>
  );
}
