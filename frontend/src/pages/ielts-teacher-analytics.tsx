import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsTeacherAnalyticsView from 'src/sections/ielts/teacher-analytics/view';

export default function IeltsTeacherAnalyticsPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.teacher.analytics_document_title')}</title>
      </Helmet>
      <IeltsTeacherAnalyticsView />
    </>
  );
}
