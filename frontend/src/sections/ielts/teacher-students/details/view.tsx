// @mui
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
// locales
import { useLocales } from 'src/locales';
// routes
import { useParams } from 'src/routes/hook';
// api
import { useTeacherStudentQuery } from '../../shared/api/use-ielts';
// components
import { InsightListCard, IeltsPageHeader } from '../../shared/components';
import {
  IntegrityHistoryCard,
  LatestAttemptsCard,
  StudentMetricsGrid,
  StudentSummaryCard,
  WritingSubmissionsCard,
} from './components';
import { IeltsTeacherStudentDetailsSkeleton } from './skeleton';

// ----------------------------------------------------------------------

export default function IeltsTeacherStudentDetailsView() {
  const { tx } = useLocales();
  const params = useParams();
  const studentId = String(params.studentId || '');
  const detailsQuery = useTeacherStudentQuery(studentId);

  if (detailsQuery.isLoading || !detailsQuery.data) {
    return (
      <Container maxWidth="lg">
        <IeltsTeacherStudentDetailsSkeleton />
      </Container>
    );
  }

  const { data } = detailsQuery;

  return (
    <Container maxWidth="lg">
      <IeltsPageHeader
        title={data.student.name}
        description={tx('pages.ielts.teacher.student_details_description')}
      />

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <StudentSummaryCard data={data} />
        </Grid>

        <Grid item xs={12} md={8}>
          <StudentMetricsGrid data={data} />
        </Grid>

        <Grid item xs={12} md={6}>
          <InsightListCard
            title={tx('pages.ielts.shared.strengths')}
            items={data.analytics.strengths}
            emptyLabel={tx('pages.ielts.shared.empty_title')}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <InsightListCard
            title={tx('pages.ielts.shared.weaknesses')}
            items={data.analytics.weaknesses}
            emptyLabel={tx('pages.ielts.shared.empty_title')}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <LatestAttemptsCard data={data} />
        </Grid>

        <Grid item xs={12} md={6}>
          <IntegrityHistoryCard data={data} />
        </Grid>

        <Grid item xs={12}>
          <WritingSubmissionsCard data={data} />
        </Grid>
      </Grid>
    </Container>
  );
}
