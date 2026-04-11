import { useForm } from 'react-hook-form';
import { useCallback, useState } from 'react';
import { yupResolver } from '@hookform/resolvers/yup';
// @mui
import LoadingButton from '@mui/lab/LoadingButton';
import Link from '@mui/material/Link';
import Alert from '@mui/material/Alert';
import Stack from '@mui/material/Stack';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import InputAdornment from '@mui/material/InputAdornment';
// hooks
import { useBoolean } from 'src/hooks/use-boolean';
// routes
import { paths } from 'src/routes/paths';
import { useSearchParams } from 'src/routes/hook';
import { RouterLink } from 'src/routes/components';
// auth
import { useRegisterMutation } from 'src/auth/api';
import { useLocales } from 'src/locales';
// components
import Iconify from 'src/components/iconify';
import FormProvider, { RHFTextField } from 'src/components/hook-form';
import { getAuthFormErrorMessage } from 'src/utils/api-error-messages';
import { createRegisterSchema } from './utils/auth-form-schemas';

// ----------------------------------------------------------------------

type FormValuesProps = {
  name: string;
  email: string;
  targetBand: number;
  password: string;
  passwordConfirm: string;
};

export default function JwtRegisterView() {
  const { tx } = useLocales();
  const registerMutation = useRegisterMutation();
  const [errorMsg, setErrorMsg] = useState('');
  const searchParams = useSearchParams();
  const returnTo = searchParams.get('returnTo');
  const password = useBoolean();

  const methods = useForm<FormValuesProps>({
    resolver: yupResolver(createRegisterSchema(tx)),
    defaultValues: {
      name: '',
      email: '',
      targetBand: 7,
      password: '',
      passwordConfirm: '',
    },
  });

  const {
    handleSubmit,
    formState: { isSubmitting },
  } = methods;

  const onSubmit = useCallback(
    async (data: FormValuesProps) => {
      try {
        setErrorMsg('');
        const payload = await registerMutation.mutateAsync({
          tenantName: 'IELTS Mock Platform',
          name: data.name,
          email: data.email,
          password: data.password,
          passwordConfirm: data.passwordConfirm,
          targetBand: Number(data.targetBand),
          mockRole: 'student',
        });
        window.location.href = returnTo || paths.afterLogin(payload.user.role);
      } catch (error) {
        setErrorMsg(getAuthFormErrorMessage(error, 'register'));
      }
    },
    [registerMutation, returnTo]
  );

  return (
    <>
      <Stack spacing={2} sx={{ mb: 5, position: 'relative' }}>
        <Typography variant="h4">{tx('auth.register.title')}</Typography>

        <Stack direction="row" spacing={0.5}>
          <Typography variant="body2">{tx('auth.register.have_account')}</Typography>

          <Link href={paths.login} component={RouterLink} variant="subtitle2">
            {tx('auth.register.sign_in')}
          </Link>
        </Stack>
      </Stack>

      <FormProvider methods={methods} onSubmit={handleSubmit(onSubmit)}>
        <Stack spacing={2.5}>
          {!!errorMsg && (
            <Alert severity="error" onClose={() => setErrorMsg('')}>
              {errorMsg}
            </Alert>
          )}

          <RHFTextField name="name" label={tx('auth.shared.full_name')} />

          <RHFTextField name="email" label={tx('auth.shared.email')} />

          <RHFTextField
            name="targetBand"
            label={tx('auth.register.target_band')}
            type="number"
            inputProps={{ min: 4.5, max: 9, step: 0.5 }}
          />

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

          <RHFTextField
            name="passwordConfirm"
            label={tx('auth.shared.confirm_password')}
            type={password.value ? 'text' : 'password'}
          />

          <LoadingButton
            fullWidth
            color="inherit"
            size="large"
            type="submit"
            variant="contained"
            loading={isSubmitting || registerMutation.isPending}
          >
            {tx('auth.register.submit')}
          </LoadingButton>
        </Stack>
      </FormProvider>

      <Typography
        component="div"
        sx={{ color: 'text.secondary', mt: 2.5, typography: 'caption', textAlign: 'center' }}
      >
        {tx('auth.register.terms')}
      </Typography>
    </>
  );
}
