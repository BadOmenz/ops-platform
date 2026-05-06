import { useState } from "react";

import { OrganizationEditor } from "./OrganizationEditor";
import { OrganizationForm } from "./OrganizationForm";
import { OrganizationTable } from "./OrganizationTable";
import { useOrganizations } from "../hooks/useOrganizations";
import type { OrganizationStatusFilter } from "../types";

type OrganizationsPanelProps = {
  tenantId: string;
};

export function OrganizationsPanel({ tenantId }: OrganizationsPanelProps) {
  const organizations = useOrganizations(tenantId);
  const [view, setView] = useState<"list" | "editor">("list");

  const openOrganization = (organizationId: string) => {
    organizations.setSelectedOrganizationId(organizationId);
    setView("editor");
  };

  if (view === "editor") {
    return (
      <section className="panel feature-panel" aria-label="Organization editor">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Organization</p>
            <h2>{organizations.selectedOrganization?.display_name || "Editor"}</h2>
          </div>
          <button type="button" onClick={() => setView("list")}>
            Back
          </button>
        </div>

        {organizations.errorMessage && <div className="error-banner">{organizations.errorMessage}</div>}

        <OrganizationEditor
          organization={organizations.selectedOrganization}
          organizationTypes={organizations.organizationTypes}
          onSave={(organizationId, payload) =>
            organizations.saveOrganization(organizationId, payload).then(() => setView("list"))
          }
          onToggleActive={organizations.toggleOrganizationActive}
        />
      </section>
    );
  }

  return (
    <section className="panel feature-panel" aria-label="Organizations">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Reference domain</p>
          <h2>Organizations</h2>
        </div>
        <div className="panel-actions">
          <button type="button" onClick={organizations.refreshOrganizations}>
            Refresh
          </button>
          <button type="button" onClick={organizations.clearFilters}>
            Clear Filters
          </button>
          <select
            value={organizations.status}
            onChange={(event) => organizations.setStatus(event.target.value as OrganizationStatusFilter)}
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="all">All</option>
          </select>
        </div>
      </div>

      {organizations.errorMessage && <div className="error-banner">{organizations.errorMessage}</div>}

      <OrganizationForm
        organizationTypes={organizations.organizationTypes}
        onCreate={organizations.createNewOrganization}
      />

      <OrganizationTable
        contactFilter={organizations.contactFilter}
        displayNameFilter={organizations.displayNameFilter}
        notesFilter={organizations.notesFilter}
        organizations={organizations.visibleOrganizations}
        sortDirection={organizations.sortDirection}
        sortField={organizations.sortField}
        typeFilter={organizations.typeFilter}
        onContactFilterChange={organizations.setContactFilter}
        onDisplayNameFilterChange={organizations.setDisplayNameFilter}
        onNotesFilterChange={organizations.setNotesFilter}
        onOpenOrganization={openOrganization}
        onSort={organizations.handleSort}
        onTypeFilterChange={organizations.setTypeFilter}
      />
    </section>
  );
}
