import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsTeacherStudentDetailsView from 'src/sections/ielts/teacher-students/details/view';

export default function IeltsTeacherStudentDetailsPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.teacher.student_details_document_title')}</title>
      </Helmet>
      <IeltsTeacherStudentDetailsView />
    </>
  );
}
