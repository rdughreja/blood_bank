"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ErrorAlert } from "@/components/error-alert";
import { login, mfaConfirm, mfaSetup, mfaVerify, type MfaSetupOut } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { loginSchema, mfaSchema } from "@/lib/validation";

type Step = "login" | "mfa" | "mfa-setup";

export default function LoginPage() {
  const router = useRouter();
  const setSession = useAuthStore((s) => s.setSession);
  const [step, setStep] = useState<Step>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const [mfaToken, setMfaToken] = useState<string | null>(null);
  const [setup, setSetup] = useState<MfaSetupOut | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  function finishLogin(accessToken: string | null | undefined, refreshToken: string | null | undefined) {
    if (!accessToken || !refreshToken) {
      setError(new Error("Login did not return tokens."));
      return;
    }
    setSession(accessToken, refreshToken);
    router.push("/dashboard");
  }

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const parsed = loginSchema.safeParse({ email, password });
    if (!parsed.success) {
      const errors: Record<string, string> = {};
      for (const issue of parsed.error.issues) {
        errors[String(issue.path[0])] = issue.message;
      }
      setFieldErrors(errors);
      return;
    }
    setFieldErrors({});
    setBusy(true);
    try {
      const result = await login(email, password);
      if (result.mfa_required) {
        if (!result.mfa_token) {
          setError(new Error("Login asked for MFA but returned no MFA token."));
          return;
        }
        setMfaToken(result.mfa_token);
        if (result.mfa_setup_required) {
          const setupOut = await mfaSetup(result.mfa_token);
          setSetup(setupOut);
          setStep("mfa-setup");
        } else {
          setStep("mfa");
        }
      } else {
        finishLogin(result.access_token, result.refresh_token);
      }
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  async function handleMfa(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const parsed = mfaSchema.safeParse({ code });
    if (!parsed.success) {
      setFieldErrors({ code: parsed.error.issues[0]?.message ?? "Invalid code." });
      return;
    }
    setFieldErrors({});
    if (!mfaToken) return;
    setBusy(true);
    try {
      const tokens =
        step === "mfa-setup"
          ? await mfaConfirm(mfaToken, code)
          : await mfaVerify(mfaToken, code);
      finishLogin(tokens.access_token, tokens.refresh_token);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Blood Bank — Log in</CardTitle>
          <CardDescription>
            Phase 1 foundation. Use your staff account to continue.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {step === "login" ? (
            <form onSubmit={(e) => void handleLogin(e)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@bloodbank.local"
                />
                {fieldErrors.email && (
                  <p className="text-xs text-red-600">{fieldErrors.email}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                {fieldErrors.password && (
                  <p className="text-xs text-red-600">{fieldErrors.password}</p>
                )}
              </div>
              <ErrorAlert error={error} />
              <Button type="submit" className="w-full" disabled={busy}>
                {busy ? "Logging in…" : "Log in"}
              </Button>
            </form>
          ) : (
            <form onSubmit={(e) => void handleMfa(e)} className="space-y-4">
              {step === "mfa-setup" && setup && (
                <div className="space-y-3 rounded-md border border-amber-300 bg-amber-50 p-4 text-sm">
                  <p className="font-medium">
                    MFA setup required for your role.
                  </p>
                  <p>
                    Add this account to your authenticator app, then enter the
                    6-digit code it shows.
                  </p>
                  <div>
                    <p className="text-xs font-medium text-slate-500">Secret</p>
                    <p className="break-all font-mono text-xs">{setup.secret}</p>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-slate-500">
                      Provisioning URI
                    </p>
                    <p className="break-all font-mono text-xs">
                      {setup.provisioning_uri}
                    </p>
                  </div>
                </div>
              )}
              {step === "mfa" && (
                <p className="text-sm text-slate-600">
                  Enter the 6-digit code from your authenticator app.
                </p>
              )}
              <div className="space-y-2">
                <Label htmlFor="code">Authenticator code</Label>
                <Input
                  id="code"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  maxLength={6}
                  value={code}
                  onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
                  placeholder="123456"
                />
                {fieldErrors.code && (
                  <p className="text-xs text-red-600">{fieldErrors.code}</p>
                )}
              </div>
              <ErrorAlert error={error} />
              <Button type="submit" className="w-full" disabled={busy}>
                {busy ? "Verifying…" : "Verify and log in"}
              </Button>
              <Button
                variant="ghost"
                className="w-full"
                onClick={() => {
                  setStep("login");
                  setError(null);
                  setCode("");
                }}
              >
                Back to email / password
              </Button>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
