import { useEffect, useState } from "react";

import { getCurrentUser } from "../features/auth/api";
import type { CurrentUser } from "../features/auth/types";
import { OrganizationsPanel } from "../features/organizations/components/OrganizationsPanel";
import { getTenants } from "../features/tenancy/api";
import { TenantSelector } from "../features/tenancy/TenantSelector";
import type { Tenant } from "../features/tenancy/types";
import { getApiBaseUrl } from "../shared/api/config";

type ThemeMode = "light" | "dark";

export function App() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [selectedTenantId, setSelectedTenantId] = useState("");
  const [themeMode, setThemeMode] = useState<ThemeMode>(() => {
    const storedTheme = window.localStorage.getItem("project05-theme");
    return storedTheme === "dark" ? "dark" : "light";
  });
  const [tenantLoadState, setTenantLoadState] = useState<"idle" | "loading" | "ready" | "error">(
    "idle",
  );

  useEffect(() => {
    let isMounted = true;

    setTenantLoadState("loading");
    getTenants()
      .then((tenantList) => {
        if (!isMounted) {
          return;
        }
        setTenants(tenantList);
        setSelectedTenantId((currentTenantId) => currentTenantId || tenantList[0]?.id || "");
        setTenantLoadState("ready");
      })
      .catch(() => {
        if (isMounted) {
          setTenantLoadState("error");
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const handleSignIn = () => {
    getCurrentUser().then(setCurrentUser);
  };

  const toggleTheme = () => {
    setThemeMode((currentTheme) => {
      const nextTheme = currentTheme === "light" ? "dark" : "light";
      window.localStorage.setItem("project05-theme", nextTheme);
      return nextTheme;
    });
  };

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
            <button className="theme-toggle" type="button" onClick={toggleTheme}>
              {themeMode === "light" ? "Dark" : "Light"}
            </button>
            <button type="button" onClick={handleSignIn}>
              {currentUser ? currentUser.display_name : "Sign in"}
            </button>
          </div>
        </header>

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
              <dt>Authentication</dt>
              <dd>{currentUser ? currentUser.email : "Dev sign-in ready"}</dd>
            </div>
          </dl>
        </section>

        {selectedTenantId && <OrganizationsPanel tenantId={selectedTenantId} />}
      </section>
    </main>
  );
}
