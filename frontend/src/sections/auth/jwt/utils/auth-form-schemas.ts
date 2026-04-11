import * as Yup from 'yup';

type Translate = (key: string, options?: Record<string, string | number>) => string;

export function createLoginSchema(tx: Translate) {
  return Yup.object({
    email: Yup.string()
      .required(tx('auth.validation.email_required'))
      .email(tx('auth.validation.email_invalid')),
    password: Yup.string().required(tx('auth.validation.password_required')),
  });
}

export function createRegisterSchema(tx: Translate) {
  return Yup.object({
    name: Yup.string().required(tx('auth.validation.full_name_required')),
    email: Yup.string()
      .required(tx('auth.validation.email_required'))
      .email(tx('auth.validation.email_invalid')),
    targetBand: Yup.number()
      .typeError(tx('auth.validation.target_band_required'))
      .required(tx('auth.validation.target_band_required'))
      .min(4.5, tx('auth.validation.target_band_min'))
      .max(9, tx('auth.validation.target_band_max')),
    password: Yup.string()
      .required(tx('auth.validation.password_required'))
      .min(8, tx('auth.validation.password_min', { count: 8 })),
    passwordConfirm: Yup.string()
      .required(tx('auth.validation.confirm_password_required'))
      .oneOf([Yup.ref('password')], tx('auth.validation.passwords_match')),
  });
}
