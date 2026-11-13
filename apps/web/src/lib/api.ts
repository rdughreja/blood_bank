/**
 * Typed resource functions over the generated openapi-fetch client.
 * Server state is consumed through React Query; this module holds no cache.
 */
import { client, unwrap, unwrapPage, type PageMeta } from "./api-client";
import type { components } from "./api-generated/types";

export type Branch = components["schemas"]["BranchOut"];
export type BranchCreate = components["schemas"]["BranchCreate"];
export type BranchUpdate = components["schemas"]["BranchUpdate"];
export type User = components["schemas"]["UserOut"];
export type UserCreate = components["schemas"]["UserCreate"];
export type UserUpdate = components["schemas"]["UserUpdate"];
export type Role = components["schemas"]["RoleOut"];
export type Master = components["schemas"]["MasterOut"];
export type MasterCreate = components["schemas"]["MasterCreate"];
export type MasterUpdate = components["schemas"]["MasterUpdate"];
export type Setting = components["schemas"]["SettingOut"];
export type SettingUpsert = components["schemas"]["SettingUpsert"];
export type AuditLog = components["schemas"]["AuditOut"];
export type LoginOut = components["schemas"]["LoginOut"];
export type MfaSetupOut = components["schemas"]["MfaSetupOut"];
export type TokenPair = components["schemas"]["TokenPair"];

export interface ListResult<T> {
  items: T[];
  meta: PageMeta;
}

// --- Auth ---

export async function login(
  email: string,
  password: string,
): Promise<LoginOut> {
  const res = await client.POST("/auth/login", {
    body: { email, password },
  });
  return unwrap<LoginOut>(res);
}

export async function logout(refreshToken: string): Promise<void> {
  await client.POST("/auth/logout", { body: { refresh_token: refreshToken } });
}

/** MFA setup: authenticated with the short-lived mfa_token as Bearer. Returns the TOTP secret + otpauth URI. */
export async function mfaSetup(mfaToken: string): Promise<MfaSetupOut> {
  const res = await client.POST("/auth/mfa/setup", {
    headers: { Authorization: `Bearer ${mfaToken}` },
  });
  return unwrap<MfaSetupOut>(res);
}

/** MFA setup confirmation: Bearer mfa_token, body {code}. Returns tokens. */
export async function mfaConfirm(
  mfaToken: string,
  code: string,
): Promise<TokenPair> {
  const res = await client.POST("/auth/mfa/confirm", {
    headers: { Authorization: `Bearer ${mfaToken}` },
    body: { code },
  });
  return unwrap<TokenPair>(res);
}

/** MFA verify for an already-enabled account: body {mfa_token, code}. Returns tokens. */
export async function mfaVerify(
  mfaToken: string,
  code: string,
): Promise<TokenPair> {
  const res = await client.POST("/auth/mfa/verify", {
    body: { mfa_token: mfaToken, code },
  });
  return unwrap<TokenPair>(res);
}

export async function switchBranch(branchId: string): Promise<{
  access_token: string;
  branch_id: string;
}> {
  const res = await client.POST("/auth/switch-branch", {
    body: { branch_id: branchId },
  });
  return unwrap(res);
}

// --- Branches ---

export async function listBranches(
  page = 1,
  pageSize = 20,
): Promise<ListResult<Branch>> {
  const res = await client.GET("/branches", {
    params: { query: { page, pageSize } },
  });
  return unwrapPage<Branch>(res);
}

export async function createBranch(body: BranchCreate): Promise<Branch> {
  const res = await client.POST("/branches", { body });
  return unwrap<Branch>(res);
}

export async function updateBranch(
  branchId: string,
  body: BranchUpdate,
): Promise<Branch> {
  const res = await client.PUT("/branches/{branch_id}", {
    params: { path: { branch_id: branchId } },
    body,
  });
  return unwrap<Branch>(res);
}

export async function deleteBranch(
  branchId: string,
  reason: string,
): Promise<Branch> {
  const res = await client.DELETE("/branches/{branch_id}", {
    params: { path: { branch_id: branchId } },
    body: { reason },
  });
  return unwrap<Branch>(res);
}

// --- Users & roles ---

export async function listUsers(
  page = 1,
  pageSize = 20,
): Promise<ListResult<User>> {
  const res = await client.GET("/users", {
    params: { query: { page, pageSize } },
  });
  return unwrapPage<User>(res);
}

export async function createUser(body: UserCreate): Promise<User> {
  const res = await client.POST("/users", { body });
  return unwrap<User>(res);
}

export async function updateUser(
  userId: string,
  body: UserUpdate,
): Promise<User> {
  const res = await client.PUT("/users/{user_id}", {
    params: { path: { user_id: userId } },
    body,
  });
  return unwrap<User>(res);
}

export async function deleteUser(
  userId: string,
  reason: string,
): Promise<User> {
  const res = await client.DELETE("/users/{user_id}", {
    params: { path: { user_id: userId } },
    body: { reason },
  });
  return unwrap<User>(res);
}

export async function resetUserPassword(
  userId: string,
  newPassword: string,
): Promise<User> {
  const res = await client.POST("/users/{user_id}/reset-password", {
    params: { path: { user_id: userId } },
    body: { new_password: newPassword },
  });
  return unwrap<User>(res);
}

export async function listRoles(): Promise<Role[]> {
  const res = await client.GET("/roles");
  return unwrap<Role[]>(res);
}

// --- Masters ---

export async function listMasterTypes(): Promise<string[]> {
  const res = await client.GET("/masters/types");
  return unwrap<string[]>(res);
}

export async function listMasters(
  masterType: string,
  page = 1,
  pageSize = 20,
): Promise<ListResult<Master>> {
  const res = await client.GET("/masters/{master_type}", {
    params: { path: { master_type: masterType }, query: { page, pageSize } },
  });
  return unwrapPage<Master>(res);
}

export async function createMaster(
  masterType: string,
  body: MasterCreate,
): Promise<Master> {
  const res = await client.POST("/masters/{master_type}", {
    params: { path: { master_type: masterType } },
    body,
  });
  return unwrap<Master>(res);
}

export async function updateMaster(
  masterId: string,
  body: MasterUpdate,
): Promise<Master> {
  const res = await client.PUT("/masters/{master_id}", {
    params: { path: { master_id: masterId } },
    body,
  });
  return unwrap<Master>(res);
}

export async function deleteMaster(
  masterId: string,
  reason: string,
): Promise<Master> {
  const res = await client.DELETE("/masters/{master_id}", {
    params: { path: { master_id: masterId } },
    body: { reason },
  });
  return unwrap<Master>(res);
}

// --- Settings ---

export async function listSettings(branchId?: string): Promise<Setting[]> {
  const res = await client.GET("/settings", {
    params: { query: branchId ? { branch_id: branchId } : {} },
  });
  return unwrap<Setting[]>(res);
}

export async function upsertSetting(body: SettingUpsert): Promise<Setting> {
  const res = await client.PUT("/settings", { body });
  return unwrap<Setting>(res);
}

// --- Audit log (read-only) ---

export async function listAuditLogs(
  page = 1,
  pageSize = 20,
  filters: { entity?: string; action?: string } = {},
): Promise<ListResult<AuditLog>> {
  const res = await client.GET("/audit-logs", {
    params: {
      query: {
        page,
        pageSize,
        ...(filters.entity ? { entity: filters.entity } : {}),
        ...(filters.action ? { action: filters.action } : {}),
      },
    },
  });
  return unwrapPage<AuditLog>(res);
}
