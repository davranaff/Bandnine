import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsDashboardView from 'src/sections/ielts/dashboard/view';

export default function IeltsDashboardPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.document_title')}</title>
      </Helmet>
      <IeltsDashboardView />
    </>
  );
}
