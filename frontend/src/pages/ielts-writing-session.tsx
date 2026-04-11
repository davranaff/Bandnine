import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsWritingSessionView from 'src/sections/ielts/writing/session/view';

export default function IeltsWritingSessionPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.writing.session_document_title')}</title>
      </Helmet>
      <IeltsWritingSessionView />
    </>
  );
}
