import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsListeningCatalogView from 'src/sections/ielts/listening/view';

export default function IeltsListeningPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.listening.document_title')}</title>
      </Helmet>
      <IeltsListeningCatalogView />
    </>
  );
}
