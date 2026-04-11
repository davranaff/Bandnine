import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsWritingCatalogView from 'src/sections/ielts/writing/view';

export default function IeltsWritingPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.writing.document_title')}</title>
      </Helmet>
      <IeltsWritingCatalogView />
    </>
  );
}
