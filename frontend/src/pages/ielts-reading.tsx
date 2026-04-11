import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsReadingCatalogView from 'src/sections/ielts/reading/view';

export default function IeltsReadingPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.reading.document_title')}</title>
      </Helmet>
      <IeltsReadingCatalogView />
    </>
  );
}
