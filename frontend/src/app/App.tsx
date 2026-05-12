import { useEffect, useState } from "react";

import { createDemoSession } from "../features/demo/api";
import { getStoredDemoSession, storeDemoSession } from "../features/demo/session";
import type { DemoSession } from "../features/demo/types";
import { OrganizationsPanel } from "../features/organizations/components/OrganizationsPanel";
import { TenantSelector } from "../features/tenancy/TenantSelector";
import type { Tenant } from "../features/tenancy/types";
import { getApiBaseUrl } from "../shared/api/config";

type ThemeMode = "light" | "dark";

export function App() {
  const [demoSession, setDemoSession] = useState<DemoSession | null>(() => getStoredDemoSession());
  const [tenants, setTenants] = useState<Tenant[]>(() =>
    demoSession ? [buildDemoTenant(demoSession)] : [],
  );
  const [selectedTenantId, setSelectedTenantId] = useState(demoSession?.tenant_id || "");
  const [themeMode, setThemeMode] = useState<ThemeMode>(() => {
    const storedTheme = window.localStorage.getItem("project05-theme");
    return storedTheme === "dark" ? "dark" : "light";
  });
  const [tenantLoadState, setTenantLoadState] = useState<"idle" | "loading" | "ready" | "error">(
    demoSession ? "ready" : "idle",
  );
  const [demoEntryState, setDemoEntryState] = useState<"idle" | "loading" | "error">("idle");

  const enterDemoWorkspace = () => {
    if (demoEntryState === "loading") {
      return;
    }

    setDemoEntryState("loading");
    setTenantLoadState("loading");
    setSelectedTenantId("");
    setTenants([]);
    createDemoSession()
      .then((session) => {
        storeDemoSession(session);
        setDemoSession(session);
        setTenants([buildDemoTenant(session)]);
        setSelectedTenantId(session.tenant_id);
        setTenantLoadState("ready");
        setDemoEntryState("idle");
      })
      .catch(() => {
        setTenantLoadState("error");
        setDemoEntryState("error");
      });
  };

  const toggleTheme = () => {
    setThemeMode((currentTheme) => {
      const nextTheme = currentTheme === "light" ? "dark" : "light";
      window.localStorage.setItem("project05-theme", nextTheme);
      return nextTheme;
    });
  };

  if (!demoSession) {
    return (
      <main className="app-shell demo-entry-shell" data-theme={themeMode}>
        <section className="demo-entry">
          <div className="brand">Ops Platform</div>
          <section className="panel demo-entry-panel" aria-label="Demo workspace entry">
            <p className="eyebrow">Portfolio demo</p>
            <h1>Operations workspace</h1>
            <p className="muted">
              Start an isolated temporary workspace with sample organization and vendor data.
            </p>
            {demoEntryState === "error" && (
              <div className="error-banner">Unable to start a demo workspace.</div>
            )}
            <div className="demo-entry-actions">
              <button
                type="button"
                onClick={enterDemoWorkspace}
                disabled={demoEntryState === "loading"}
              >
                {demoEntryState === "loading" ? "Starting..." : "Enter Demo Workspace"}
              </button>
              <button className="theme-toggle" type="button" onClick={toggleTheme}>
                {themeMode === "light" ? "Dark" : "Light"}
              </button>
            </div>
          </section>
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell" data-theme={themeMode}>
      <aside className="sidebar">
        <div className="brand">Ops Platform</div>
        <nav aria-label="Primary navigation">
          <a href="/">Home</a>
          <a href="/tenants">Tenants</a>
          <a href="/settings">Settings</a>
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Azure-ready foundation</p>
            <h1>Operations workspace</h1>
          </div>
          <div className="topbar-actions">
            <TenantSelector
              tenants={tenants}
              selectedTenantId={selectedTenantId}
              onSelectTenant={setSelectedTenantId}
            />
            <button className="secondary-button" type="button" onClick={enterDemoWorkspace}>
              Start New Demo Workspace
            </button>
            <button className="theme-toggle" type="button" onClick={toggleTheme}>
              {themeMode === "light" ? "Dark" : "Light"}
            </button>
            <span className="status-label">Demo Mode</span>
          </div>
        </header>

        <div className="demo-mode-banner">Demo mode — changes may be reset.</div>

        <section className="panel" aria-label="Platform status">
          <h2>Foundation checkpoint</h2>
          <dl>
            <div>
              <dt>API base URL</dt>
              <dd>{getApiBaseUrl()}</dd>
            </div>
            <div>
              <dt>Tenant model</dt>
              <dd>{tenantLoadState === "error" ? "API unavailable" : "API connected"}</dd>
            </div>
            <div>
              <dt>Workspace</dt>
              <dd>{demoSession.tenant_name}</dd>
            </div>
            <div>
              <dt>Authentication</dt>
              <dd>Demo User</dd>
            </div>
          </dl>
        </section>

        {selectedTenantId && <OrganizationsPanel key={selectedTenantId} tenantId={selectedTenantId} />}
      </section>
    </main>
  );
}

function buildDemoTenant(session: DemoSession): Tenant {
  return {
    id: session.tenant_id,
    name: session.tenant_name,
    slug: "demo-workspace",
    is_active: true,
    created_at: session.expires_at,
    updated_at: null,
  };
}
