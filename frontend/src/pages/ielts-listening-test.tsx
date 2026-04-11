import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsListeningDetailsView from 'src/sections/ielts/listening/details/view';

export default function IeltsListeningTestPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.listening.test_document_title')}</title>
      </Helmet>
      <IeltsListeningDetailsView />
    </>
  );
}
