import { useState } from "react";

import { createDemoSession } from "../features/demo/api";
import { getStoredDemoSession, storeDemoSession } from "../features/demo/session";
import type { DemoSession } from "../features/demo/types";
import { ItemCategoriesPanel } from "../features/itemCategories/components/ItemCategoriesPanel";
import { OrganizationsPanel } from "../features/organizations/components/OrganizationsPanel";
import { SetupHome } from "../features/setup/SetupHome";
import { StorageLocationsPanel } from "../features/storageLocations/components/StorageLocationsPanel";
import { TenantSelector } from "../features/tenancy/TenantSelector";
import type { Tenant } from "../features/tenancy/types";
import { VendorItemsPanel } from "../features/vendorItems/components/VendorItemsPanel";
import { getApiBaseUrl } from "../shared/api/config";

type ThemeMode = "light" | "dark";
type WorkspaceView = "operations" | "vendorItems" | "setup";
type SetupView = "home" | "itemCategories" | "storageLocations";

export function App() {
  const [demoSession, setDemoSession] = useState<DemoSession | null>(() => getStoredDemoSession());
  const [tenants, setTenants] = useState<Tenant[]>(() =>
    demoSession ? [buildDemoTenant(demoSession)] : [],
  );
  const [selectedTenantId, setSelectedTenantId] = useState(demoSession?.tenant_id || "");
  const [workspaceView, setWorkspaceView] = useState<WorkspaceView>("operations");
  const [setupView, setSetupView] = useState<SetupView>("home");
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

  const openWorkspace = (nextView: WorkspaceView) => {
    setWorkspaceView(nextView);
    if (nextView === "setup") {
      setSetupView("home");
    }
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
          <button
            className={workspaceView === "operations" ? "nav-button is-active" : "nav-button"}
            type="button"
            onClick={() => openWorkspace("operations")}
          >
            Operations
          </button>
          <button
            className={workspaceView === "vendorItems" ? "nav-button is-active" : "nav-button"}
            type="button"
            onClick={() => openWorkspace("vendorItems")}
          >
            Vendor Items
          </button>
          <button
            className={workspaceView === "setup" ? "nav-button is-active" : "nav-button"}
            type="button"
            onClick={() => openWorkspace("setup")}
          >
            Setup
          </button>
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Azure-ready foundation</p>
            <h1>{getWorkspaceTitle(workspaceView)}</h1>
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

        <section className="panel foundation-strip" aria-label="Platform status">
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

        {selectedTenantId && workspaceView === "operations" && (
          <OrganizationsPanel key={`organizations-${selectedTenantId}`} tenantId={selectedTenantId} />
        )}
        {selectedTenantId && workspaceView === "vendorItems" && (
          <VendorItemsPanel
            key={`vendor-items-${selectedTenantId}`}
            tenantId={selectedTenantId}
            mode="global"
          />
        )}
        {selectedTenantId && workspaceView === "setup" && setupView === "home" && (
          <SetupHome
            onOpenItemCategories={() => setSetupView("itemCategories")}
            onOpenStorageLocations={() => setSetupView("storageLocations")}
          />
        )}
        {selectedTenantId && workspaceView === "setup" && setupView === "itemCategories" && (
          <ItemCategoriesPanel
            key={`item-categories-${selectedTenantId}`}
            tenantId={selectedTenantId}
            onBackToSetup={() => setSetupView("home")}
          />
        )}
        {selectedTenantId && workspaceView === "setup" && setupView === "storageLocations" && (
          <StorageLocationsPanel
            key={`storage-locations-${selectedTenantId}`}
            tenantId={selectedTenantId}
            onBackToSetup={() => setSetupView("home")}
          />
        )}
      </section>
    </main>
  );
}

function getWorkspaceTitle(workspaceView: WorkspaceView) {
  if (workspaceView === "setup") {
    return "Setup workspace";
  }
  if (workspaceView === "vendorItems") {
    return "Vendor items workspace";
  }
  return "Operations workspace";
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
