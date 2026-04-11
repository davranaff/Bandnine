/** Active app roles used by the IELTS mock platform. */
export type UserRole = 'student' | 'teacher';

/** Matches DRF `UserSerializer` response (camelCase). */
export type TenantUser = {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  tenantId: string | null;
  createdAt: string;
  targetBand?: number | null;
};

/** Login + register responses from Django JWT / register view. */
export type TokenPairResponse = {
  access: string;
  refresh: string;
  user: TenantUser;
};

export type LoginRequest = {
  email: string;
  password: string;
  mockRole?: UserRole;
};

/** Matches `RegisterSerializer` (camelCase request body). */
export type RegisterRequest = {
  tenantName?: string;
  name: string;
  email: string;
  password: string;
  passwordConfirm: string;
  targetBand?: number;
  mockRole?: UserRole;
};
