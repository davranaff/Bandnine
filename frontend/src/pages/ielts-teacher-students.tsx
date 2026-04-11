import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsTeacherStudentsView from 'src/sections/ielts/teacher-students/view';

export default function IeltsTeacherStudentsPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.teacher.students_document_title')}</title>
      </Helmet>
      <IeltsTeacherStudentsView />
    </>
  );
}
