import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsWritingDetailsView from 'src/sections/ielts/writing/details/view';

export default function IeltsWritingTestPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.writing.test_document_title')}</title>
      </Helmet>
      <IeltsWritingDetailsView />
    </>
  );
}
