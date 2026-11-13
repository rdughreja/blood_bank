import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("Enter a valid email address."),
  password: z.string().min(1, "Password is required."),
});

export const mfaSchema = z.object({
  code: z.string().regex(/^\d{6}$/, "Enter the 6-digit code."),
});

export const branchSchema = z.object({
  code: z.string().min(1, "Code is required.").max(20),
  name: z.string().min(1, "Name is required.").max(200),
  address: z.string().max(500).optional(),
  licence_no: z.string().max(100).optional(),
  is_storage_centre: z.boolean(),
});

export const branchUpdateSchema = branchSchema.partial();

/** Password policy (docs/decisions.md): min 12 chars, upper, lower, digit, special. */
export const passwordSchema = z
  .string()
  .min(12, "Password must be at least 12 characters.")
  .regex(/[A-Z]/, "Password must include an uppercase letter.")
  .regex(/[a-z]/, "Password must include a lowercase letter.")
  .regex(/[0-9]/, "Password must include a digit.")
  .regex(/[^A-Za-z0-9]/, "Password must include a special character.");

export const PASSWORD_HINT =
  "Minimum 12 characters, with an uppercase letter, a lowercase letter, a digit, and a special character.";

export const userCreateSchema = z.object({
  email: z.string().email("Enter a valid email address."),
  full_name: z.string().min(1, "Full name is required.").max(200),
  mobile: z.string().max(20).optional(),
  password: passwordSchema,
  role_id: z.string().min(1, "Choose a role."),
  branch_ids: z.array(z.string()),
  primary_branch_id: z.string().optional(),
});

export const userUpdateSchema = z.object({
  full_name: z.string().min(1, "Full name is required.").max(200),
  mobile: z.string().max(20).optional(),
  role_id: z.string().min(1, "Choose a role."),
  branch_ids: z.array(z.string()),
  primary_branch_id: z.string().optional(),
  is_active: z.boolean(),
});

export const masterSchema = z.object({
  code: z.string().min(1, "Code is required.").max(50),
  name: z.string().min(1, "Name is required.").max(200),
});

export const deleteReasonSchema = z.object({
  reason: z.string().min(1, "A reason is required.").max(500),
});

/** Setting value is edited as JSON text; validated as parseable JSON. */
export const settingValueSchema = z.object({
  valueText: z.string().refine(
    (text) => {
      try {
        JSON.parse(text);
        return true;
      } catch {
        return false;
      }
    },
    { message: "Value must be valid JSON (e.g. 72, true, or \"text\")." },
  ),
});
