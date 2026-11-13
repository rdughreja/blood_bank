import { defineConfig } from "@playwright/test";

/**
 * Phase 1 E2E. Requires the API running and seeded at
 * http://127.0.0.1:8000 (see repo README). The web server is started
 * automatically from the production build (`npm run build` first).
 */
export default defineConfig({
  testDir: "./e2e",
  globalSetup: "./e2e/global-setup.ts",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL: "http://127.0.0.1:3000",
    trace: "on-first-retry",
  },
  webServer: {
    command: "npm run start -- --port 3000 --hostname 127.0.0.1",
    url: "http://127.0.0.1:3000/login",
    reuseExistingServer: true,
    timeout: 60_000,
  },
});
