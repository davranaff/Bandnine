import { useForm } from 'react-hook-form';
import { useCallback, useState } from 'react';
import { yupResolver } from '@hookform/resolvers/yup';
// @mui
import LoadingButton from '@mui/lab/LoadingButton';
import Button from '@mui/material/Button';
import Link from '@mui/material/Link';
import Alert from '@mui/material/Alert';
import Stack from '@mui/material/Stack';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import InputAdornment from '@mui/material/InputAdornment';
// routes
import { paths } from 'src/routes/paths';
import { useSearchParams } from 'src/routes/hook';
import { RouterLink } from 'src/routes/components';
// hooks
import { useBoolean } from 'src/hooks/use-boolean';
import { useLoginMutation } from 'src/auth/api';
import { useLocales } from 'src/locales';
// components
import Iconify from 'src/components/iconify';
import FormProvider, { RHFTextField } from 'src/components/hook-form';
import { getAuthFormErrorMessage } from 'src/utils/api-error-messages';
import { isJwtAuthMock } from 'src/auth/context/jwt/mock-auth';
import { createLoginSchema } from './utils/auth-form-schemas';

// ----------------------------------------------------------------------

type FormValuesProps = {
  email: string;
  password: string;
};

const STUDENT_DEMO = {
  email: 'student@ieltsmock.dev',
  password: 'demo1234',
};

const TEACHER_DEMO = {
  email: 'teacher@ieltsmock.dev',
  password: 'demo1234',
};

export default function JwtLoginView() {
  const { tx } = useLocales();
  const loginMutation = useLoginMutation();
  const password = useBoolean();
  const [errorMsg, setErrorMsg] = useState('');
  const searchParams = useSearchParams();
  const returnTo = searchParams.get('returnTo');

  const methods = useForm<FormValuesProps>({
    resolver: yupResolver(createLoginSchema(tx)),
    defaultValues: STUDENT_DEMO,
  });

  const {
    handleSubmit,
    reset,
    formState: { isSubmitting },
  } = methods;

  const handleSuccessRedirect = useCallback(
    (role: 'student' | 'teacher') => {
      window.location.href = returnTo || paths.afterLogin(role);
    },
    [returnTo]
  );

  const onSubmit = useCallback(
    async (data: FormValuesProps) => {
      try {
        setErrorMsg('');
        const payload = await loginMutation.mutateAsync({
          email: data.email,
          password: data.password,
        });
        handleSuccessRedirect(payload.user.role);
      } catch (error) {
        setErrorMsg(getAuthFormErrorMessage(error, 'login'));
      }
    },
    [handleSuccessRedirect, loginMutation]
  );

  const handleDemoLogin = useCallback(
    async (role: 'student' | 'teacher') => {
      const demo = role === 'teacher' ? TEACHER_DEMO : STUDENT_DEMO;
      reset(demo);

      try {
        setErrorMsg('');
        const payload = await loginMutation.mutateAsync({
          ...demo,
          mockRole: role,
        });
        handleSuccessRedirect(payload.user.role);
      } catch (error) {
        setErrorMsg(getAuthFormErrorMessage(error, 'login'));
      }
    },
    [handleSuccessRedirect, loginMutation, reset]
  );

  return (
    <FormProvider methods={methods} onSubmit={handleSubmit(onSubmit)}>
      <Stack spacing={2} sx={{ mb: 5 }}>
        <Typography variant="h4">{tx('auth.login.title')}</Typography>

        <Stack direction="row" spacing={0.5}>
          <Typography variant="body2">{tx('auth.login.new_user')}</Typography>

          <Link component={RouterLink} href={paths.register} variant="subtitle2">
            {tx('auth.login.create_account')}
          </Link>
        </Stack>
      </Stack>

      {isJwtAuthMock() ? (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Stack spacing={1.5}>
            <Typography variant="body2">{tx('auth.login.demo_hint')}</Typography>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
              <Button
                variant="contained"
                color="inherit"
                onClick={() => handleDemoLogin('student')}
                disabled={loginMutation.isPending}
              >
                {tx('auth.login.student_demo')}
              </Button>
              <Button
                variant="outlined"
                color="inherit"
                onClick={() => handleDemoLogin('teacher')}
                disabled={loginMutation.isPending}
              >
                {tx('auth.login.teacher_demo')}
              </Button>
            </Stack>
          </Stack>
        </Alert>
      ) : null}

      <Stack spacing={2.5}>
        {!!errorMsg && (
          <Alert severity="error" onClose={() => setErrorMsg('')}>
            {errorMsg}
          </Alert>
        )}

        <RHFTextField name="email" label={tx('auth.shared.email')} />

        <RHFTextField
          name="password"
          label={tx('auth.shared.password')}
          type={password.value ? 'text' : 'password'}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton onClick={password.onToggle} edge="end">
                  <Iconify icon={password.value ? 'solar:eye-bold' : 'solar:eye-closed-bold'} />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        <Link variant="body2" color="inherit" underline="always" sx={{ alignSelf: 'flex-end' }}>
          {tx('auth.login.forgot')}
        </Link>

        <LoadingButton
          fullWidth
          color="inherit"
          size="large"
          type="submit"
          variant="contained"
          loading={isSubmitting || loginMutation.isPending}
        >
          {tx('auth.login.submit')}
        </LoadingButton>
      </Stack>

      {isJwtAuthMock() ? (
        <>
          <Divider sx={{ my: 3 }} />
          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
            {tx('auth.login.demo_credentials')}
          </Typography>
        </>
      ) : null}
    </FormProvider>
  );
}
