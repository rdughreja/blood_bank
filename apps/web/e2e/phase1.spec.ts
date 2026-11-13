import { createHmac } from "node:crypto";
import { expect, test, type Page } from "@playwright/test";

/**
 * Phase 1 E2E (BUILD_PLAN.md Phase 1 tests):
 * login -> create branch -> create user -> that user logs in and sees only
 * the menus their role is allowed (and the API still blocks the rest).
 *
 * Runs against the seeded dev API at http://127.0.0.1:8000. Test data uses
 * a timestamp suffix so re-runs never collide with a previous run, and the
 * test soft-deletes what it created (best-effort) at the end.
 *
 * The seed Super Admin is an MFA-required role, so the admin login goes
 * through the in-browser MFA setup (first login) / verify (later logins)
 * steps. The TOTP code is computed here from the secret the setup screen
 * shows — the secret itself is never written to disk or the report.
 * MFA enforcement itself is also covered by the backend API tests
 * (test_auth_api.py).
 */

const ADMIN_EMAIL = "admin@bloodbank.local";
const ADMIN_PASSWORD = "Admin@123456";

/** RFC 6238 TOTP (SHA-1, 30 s step, 6 digits) — same parameters as pyotp. */
function base32Decode(input: string): Buffer {
  const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
  const clean = input.replace(/=+$/, "").toUpperCase();
  let bits = 0;
  let value = 0;
  const bytes: number[] = [];
  for (const char of clean) {
    const idx = alphabet.indexOf(char);
    if (idx === -1) throw new Error(`Invalid base32 character: ${char}`);
    value = (value << 5) | idx;
    bits += 5;
    if (bits >= 8) {
      bytes.push((value >>> (bits - 8)) & 0xff);
      bits -= 8;
    }
  }
  return Buffer.from(bytes);
}

function totp(secret: string): string {
  const key = base32Decode(secret);
  const counter = Math.floor(Date.now() / 1000 / 30);
  const msg = Buffer.alloc(8);
  msg.writeBigUInt64BE(BigInt(counter));
  const hmac = createHmac("sha1", key).update(msg).digest();
  const offset = hmac[hmac.length - 1] & 0x0f;
  const code =
    ((hmac[offset] & 0x7f) << 24) |
    ((hmac[offset + 1] & 0xff) << 16) |
    ((hmac[offset + 2] & 0xff) << 8) |
    (hmac[offset + 3] & 0xff);
  return String(code % 1_000_000).padStart(6, "0");
}

/** TOTP secret issued to the seed admin during this run (not persisted). */
let adminTotpSecret: string | null = null;

async function loginAsAdmin(page: Page) {
  await page.goto("/login");
  await page.locator("#email").fill(ADMIN_EMAIL);
  await page.locator("#password").fill(ADMIN_PASSWORD);
  await page.getByRole("button", { name: "Log in" }).click();
  // MFA-required role: the setup step (first login) or the verify step.
  const codeInput = page.locator("#code");
  await expect(codeInput).toBeVisible({ timeout: 10_000 });
  if (adminTotpSecret === null) {
    // Setup step shows the secret; the verify-only step does not. If we land
    // on verify-only with no secret, a previous run left MFA enabled and the
    // global setup reset did not run — fail with a clear pointer.
    const setupBox = page.locator("text=MFA setup required for your role.");
    if (await setupBox.isVisible()) {
      const texts = await page.locator("p.font-mono").allTextContents();
      const secret = texts
        .map((t) => t.trim())
        .find((t) => /^[A-Z2-7]{32}$/.test(t));
      expect(secret).toBeTruthy();
      adminTotpSecret = secret as string;
    } else {
      throw new Error(
        "Admin MFA verify step shown but this run has no TOTP secret " +
          "(a previous run left MFA enabled and e2e/global-setup.ts did not " +
          "reset it). Reset Super Admin MFA in the dev DB and re-run.",
      );
    }
  }
  await codeInput.fill(totp(adminTotpSecret));
  await page.getByRole("button", { name: "Verify and log in" }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
}

async function loginAs(page: Page, email: string, password: string) {
  await page.goto("/login");
  await page.locator("#email").fill(email);
  await page.locator("#password").fill(password);
  await page.getByRole("button", { name: "Log in" }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
}

async function logout(page: Page) {
  await page.getByRole("button", { name: "Log out" }).click();
  await expect(page).toHaveURL(/\/login$/);
}

test("phase 1: admin creates branch + donor-staff user; new user sees only permitted menus", async ({
  page,
}) => {
  const suffix = Date.now().toString().slice(-6);
  const branchCode = `E2E${suffix}`;
  const branchName = `E2E Test Branch ${suffix}`;
  const userEmail = `e2e.donor.${suffix}@demo.local`;
  const userPassword = "E2e@12345678";

  // 1. Admin logs in (password + MFA setup on first login).
  await loginAsAdmin(page);
  await expect(page.getByRole("link", { name: "Users" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Audit Log" })).toBeVisible();

  // 2. Admin creates a branch.
  await page.getByRole("link", { name: "Branches" }).click();
  await expect(page).toHaveURL(/\/branches$/);
  await page.getByRole("button", { name: "New branch" }).click();
  await page.locator("#code").fill(branchCode);
  await page.locator("#name").fill(branchName);
  await page.getByRole("button", { name: "Create branch" }).click();
  await expect(page.locator("tr", { hasText: branchName })).toBeVisible();

  // 3. Admin creates a Donor Staff user assigned to that branch.
  await page.getByRole("link", { name: "Users" }).click();
  await expect(page).toHaveURL(/\/users$/);
  await page.getByRole("button", { name: "New user" }).click();
  await page.locator("#email").fill(userEmail);
  await page.locator("#full_name").fill("E2E Donor");
  await page.locator("#role_id").selectOption({ label: "Donor Staff / Counsellor" });
  await page.locator("#password").fill(userPassword);
  await page.getByLabel(`${branchName} (${branchCode})`).check();
  await page.locator("#primary_branch_id").selectOption({ label: branchName });
  await page.getByRole("button", { name: "Create user" }).click();
  await expect(page.locator("tr", { hasText: userEmail })).toBeVisible();

  // 4. New user logs in and sees only the menus Donor Staff may use.
  await logout(page);
  await loginAs(page, userEmail, userPassword);
  await expect(page.getByText("Donor Staff / Counsellor", { exact: true }).first()).toBeVisible();
  for (const label of ["Dashboard", "Branches", "Masters", "Settings"]) {
    await expect(page.getByRole("link", { name: label })).toBeVisible();
  }
  await expect(page.getByRole("link", { name: "Users" })).toHaveCount(0);
  await expect(page.getByRole("link", { name: "Audit Log" })).toHaveCount(0);

  // 5. Menu hiding is not security: the API still blocks /users for this role.
  // (getByRole('alert') also matches Next.js's route announcer, so assert on
  // the error text itself.)
  await page.goto("/users");
  await expect(page.getByText("Error code: FORBIDDEN")).toBeVisible();

  // 6. Best-effort cleanup: soft-delete the user and the branch as admin.
  try {
    await logout(page);
    await loginAsAdmin(page);
    await page.getByRole("link", { name: "Users" }).click();
    await page
      .locator("tr", { hasText: userEmail })
      .getByRole("button", { name: "Delete" })
      .click();
    await page.locator("#delete-reason").fill("E2E cleanup");
    await page.getByRole("button", { name: "Confirm delete" }).click();
    await expect(page.locator("tr", { hasText: userEmail })).toHaveCount(0);
    await page.getByRole("link", { name: "Branches" }).click();
    await page
      .locator("tr", { hasText: branchName })
      .getByRole("button", { name: "Delete" })
      .click();
    await page.locator("#delete-reason").fill("E2E cleanup");
    await page.getByRole("button", { name: "Confirm delete" }).click();
    await expect(page.locator("tr", { hasText: branchName })).toHaveCount(0);
  } catch (err) {
    // Cleanup failure must not fail the test; the dev DB rows are harmless
    // and identifiable by the E2E prefix.
    console.log("E2E cleanup failed (non-fatal):", String(err));
  }
});
