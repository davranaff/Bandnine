import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsReadingResultView from 'src/sections/ielts/reading/result/view';

export default function IeltsReadingResultPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.reading.result_document_title')}</title>
      </Helmet>
      <IeltsReadingResultView />
    </>
  );
}
