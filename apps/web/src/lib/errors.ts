/** Typed error thrown by the API wrapper. Frontend branches on `code`, never on message text. */
export class ApiError extends Error {
  code: string;
  details: unknown;

  constructor(code: string, message: string, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.details = details;
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

/** Friendly one-line explanation per stable error code (from apps/api/app/core/errors.py). */
export function friendlyMessage(error: unknown): string {
  if (!isApiError(error)) {
    return error instanceof Error ? error.message : "Something went wrong.";
  }
  switch (error.code) {
    case "INVALID_CREDENTIALS":
      return "Invalid email or password.";
    case "ACCOUNT_LOCKED":
      return "Account locked after too many failed attempts. Try again in 15 minutes.";
    case "ACCOUNT_INACTIVE":
      return "This account is inactive. Contact an administrator.";
    case "MFA_INVALID":
      return "Incorrect authenticator code. Try again.";
    case "FORBIDDEN":
      return "Your role does not allow this action.";
    case "NOT_FOUND":
      return "The requested record was not found.";
    case "VALIDATION_ERROR":
      return "Some fields are invalid. Check the form and try again.";
    case "CONFLICT":
      return "That record already exists or conflicts with the current state.";
    case "RATE_LIMITED":
      return "Too many requests. Wait a moment and try again.";
    case "UNAUTHORIZED":
    case "TOKEN_EXPIRED":
    case "TOKEN_INVALID":
      return "Your session has expired. Please log in again.";
    default:
      return error.message || "Something went wrong.";
  }
}
