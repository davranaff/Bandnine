import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsTeacherDashboardView from 'src/sections/ielts/teacher-dashboard/view';

export default function IeltsTeacherDashboardPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.teacher.dashboard_document_title')}</title>
      </Helmet>
      <IeltsTeacherDashboardView />
    </>
  );
}
