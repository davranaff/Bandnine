import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsListeningSessionView from 'src/sections/ielts/listening/session/view';

export default function IeltsListeningSessionPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.listening.session_document_title')}</title>
      </Helmet>
      <IeltsListeningSessionView />
    </>
  );
}
