import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsReadingDetailsView from 'src/sections/ielts/reading/details/view';

export default function IeltsReadingTestPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.reading.test_document_title')}</title>
      </Helmet>
      <IeltsReadingDetailsView />
    </>
  );
}
