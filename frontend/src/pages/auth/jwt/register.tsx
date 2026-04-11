import { Helmet } from 'react-helmet-async';
import { useLocales } from 'src/locales';
// sections
import { JwtRegisterView } from 'src/sections/auth/jwt';

// ----------------------------------------------------------------------

export default function RegisterPage() {
  const { tx } = useLocales();

  return (
    <>
      <Helmet>
        <title>{tx('auth.register.title')}</title>
      </Helmet>

      <JwtRegisterView />
    </>
  );
}
