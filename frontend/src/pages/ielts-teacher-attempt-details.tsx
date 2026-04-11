import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsTeacherAttemptDetailsView from 'src/sections/ielts/teacher-attempt-details/view';

export default function IeltsTeacherAttemptDetailsPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.teacher.attempt_document_title')}</title>
      </Helmet>
      <IeltsTeacherAttemptDetailsView />
    </>
  );
}
