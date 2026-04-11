import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
// sections
import { JwtLoginView } from 'src/sections/auth/jwt';

// ----------------------------------------------------------------------

export default function LoginPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('auth.login.title')}</title>
      </Helmet>

      <JwtLoginView />
    </>
  );
}
