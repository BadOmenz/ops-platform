import type { DemoSession } from "./types";

const DEMO_SESSION_STORAGE_KEY = "ops-platform-demo-session";

export function getStoredDemoSession(): DemoSession | null {
  const rawSession = window.localStorage.getItem(DEMO_SESSION_STORAGE_KEY);
  if (!rawSession) {
    return null;
  }

  try {
    const session = JSON.parse(rawSession) as DemoSession;
    if (!isDemoSession(session) || isDemoSessionExpired(session)) {
      clearStoredDemoSession();
      return null;
    }
    return session;
  } catch {
    clearStoredDemoSession();
    return null;
  }
}

export function storeDemoSession(session: DemoSession) {
  window.localStorage.setItem(DEMO_SESSION_STORAGE_KEY, JSON.stringify(session));
}

export function clearStoredDemoSession() {
  window.localStorage.removeItem(DEMO_SESSION_STORAGE_KEY);
}

function isDemoSession(session: DemoSession) {
  return Boolean(
    session &&
      typeof session.tenant_id === "string" &&
      typeof session.tenant_name === "string" &&
      typeof session.session_token === "string" &&
      typeof session.expires_at === "string",
  );
}

function isDemoSessionExpired(session: DemoSession) {
  return Date.now() >= new Date(session.expires_at).getTime();
}
