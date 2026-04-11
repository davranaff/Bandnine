import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsListeningResultView from 'src/sections/ielts/listening/result/view';

export default function IeltsListeningResultPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.listening.result_document_title')}</title>
      </Helmet>
      <IeltsListeningResultView />
    </>
  );
}
