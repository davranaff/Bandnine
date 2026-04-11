import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
import IeltsProfileView from 'src/sections/ielts/profile/view';

export default function IeltsProfilePage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('pages.ielts.profile.document_title')}</title>
      </Helmet>
      <IeltsProfileView />
    </>
  );
}
