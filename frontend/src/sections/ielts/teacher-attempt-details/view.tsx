// @mui
import Container from '@mui/material/Container';
// locales
import { useParams } from 'src/routes/hook';
// api
import { useAttemptIntegrityEventsQuery } from '../shared/api/use-ielts';
// components
import { AttemptResultView } from '../shared/result/attempt-result-view';
import { MentorNoteCard } from './components';

// ----------------------------------------------------------------------

export default function IeltsTeacherAttemptDetailsView() {
  const params = useParams();
  const attemptId = String(params.attemptId || '');
  const integrityQuery = useAttemptIntegrityEventsQuery(attemptId);

  return (
    <>
      <AttemptResultView attemptId={attemptId} />

      <Container maxWidth="lg" sx={{ mt: 3 }}>
        <MentorNoteCard hasIntegrityEvents={Boolean(integrityQuery.data?.length)} />
      </Container>
    </>
  );
}
