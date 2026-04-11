import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsWritingResultView from 'src/sections/ielts/writing/result/view';

export default function IeltsWritingResultPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.writing.result_document_title')}</title>
      </Helmet>
      <IeltsWritingResultView />
    </>
  );
}
