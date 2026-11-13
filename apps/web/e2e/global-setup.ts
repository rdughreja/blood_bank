import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

/**
 * Playwright global setup for the Phase 1 E2E.
 *
 * Resets MFA on every Super Admin in the DEV database so the test can run
 * the in-browser MFA setup flow from a known state on every run. Without
 * this, a previous run leaves MFA enabled on the seed admin and the test
 * has no TOTP secret to verify with.
 *
 * Requires `psql` on PATH and the dev database reachable at
 * E2E_DATABASE_URL (default postgresql://bloodbank:bloodbank_dev@localhost:5432/bloodbank).
 * If the reset cannot run, the test fails later with a clear message in
 * loginAsAdmin — see e2e/phase1.spec.ts.
 */
export default async function globalSetup(): Promise<void> {
  const databaseUrl =
    process.env.E2E_DATABASE_URL ??
    "postgresql://bloodbank:bloodbank_dev@localhost:5432/bloodbank";
  const sql = [
    "UPDATE users",
    "SET mfa_enabled = false, mfa_secret = NULL",
    "FROM roles",
    "WHERE users.role_id = roles.id",
    "AND roles.name = 'Super Admin';",
  ].join(" ");
  try {
    await execFileAsync("psql", [databaseUrl, "-v", "ON_ERROR_STOP=1", "-c", sql]);
    console.log("[e2e global-setup] Reset MFA on Super Admin accounts.");
  } catch (err) {
    console.warn(
      "[e2e global-setup] Could not reset admin MFA (psql/DB unavailable). " +
        "The E2E test will fail at the admin MFA step unless MFA was already reset. " +
        `(${String(err).split("\n")[0]})`,
    );
  }
}
