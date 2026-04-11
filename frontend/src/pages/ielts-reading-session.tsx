import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsReadingSessionView from 'src/sections/ielts/reading/session/view';

export default function IeltsReadingSessionPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.reading.session_document_title')}</title>
      </Helmet>
      <IeltsReadingSessionView />
    </>
  );
}
