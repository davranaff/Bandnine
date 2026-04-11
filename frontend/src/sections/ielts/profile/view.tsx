// @mui
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
// locales
import { useLocales } from 'src/locales';
// api
import { useStudentProfileQuery } from '../shared/api/use-ielts';
// components
import { InsightListCard, IeltsPageHeader } from '../shared/components';
import { ProfileMetricsGrid, StudentProfileSummaryCard } from './components';
import { IeltsProfileSkeleton } from './skeleton';

// ----------------------------------------------------------------------

export default function IeltsProfileView() {
  const { tx } = useLocales();
  const profileQuery = useStudentProfileQuery();

  if (profileQuery.isLoading || !profileQuery.data) {
    return (
      <Container maxWidth="lg">
        <IeltsProfileSkeleton />
      </Container>
    );
  }

  const { data } = profileQuery;

  return (
    <Container maxWidth="lg">
      <IeltsPageHeader
        title={tx('pages.ielts.profile.title')}
        description={tx('pages.ielts.profile.description')}
      />

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <StudentProfileSummaryCard data={data} />
        </Grid>

        <Grid item xs={12} md={8}>
          <ProfileMetricsGrid data={data} />
        </Grid>

        <Grid item xs={12} md={6}>
          <InsightListCard
            title={tx('pages.ielts.profile.achievements')}
            items={data.achievements}
            emptyLabel={tx('pages.ielts.shared.empty_title')}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <InsightListCard
            title={tx('pages.ielts.profile.recent_performance')}
            items={data.recentAttempts.map(
              (item) =>
                `${item.test.title} · ${
                  item.result
                    ? item.result.estimatedBand.toFixed(1)
                    : tx('pages.ielts.shared.status_in_progress')
                }`
            )}
            emptyLabel={tx('pages.ielts.shared.empty_title')}
          />
        </Grid>
      </Grid>
    </Container>
  );
}
