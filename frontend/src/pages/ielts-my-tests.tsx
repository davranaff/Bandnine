import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsMyTestsView from 'src/sections/ielts/my-tests/view';

export default function IeltsMyTestsPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.my_tests.document_title')}</title>
      </Helmet>
      <IeltsMyTestsView />
    </>
  );
}
