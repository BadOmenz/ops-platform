import { useState } from "react";

import { OrganizationEditor } from "./OrganizationEditor";
import { OrganizationForm } from "./OrganizationForm";
import { OrganizationTable } from "./OrganizationTable";
import { useOrganizations } from "../hooks/useOrganizations";
import { CustomerWorkspace } from "../../customers/components/CustomerWorkspace";
import { VendorWorkspace } from "../../vendors/components/VendorWorkspace";

type OrganizationsPanelProps = {
  tenantId: string;
};

export function OrganizationsPanel({ tenantId }: OrganizationsPanelProps) {
  const organizations = useOrganizations(tenantId);
  const [view, setView] = useState<"list" | "vendor" | "customer">("list");
  const [editorMode, setEditorMode] = useState<"create" | "edit">("edit");
  const [selectedCustomerPublicId, setSelectedCustomerPublicId] = useState("");
  const [selectedVendorPublicId, setSelectedVendorPublicId] = useState("");

  const selectOrganization = (organizationId: string) => {
    organizations.setSelectedOrganizationId(organizationId);
    setEditorMode("edit");
  };

  const openVendor = (vendorPublicId: string) => {
    setSelectedVendorPublicId(vendorPublicId);
    setView("vendor");
  };

  const openCustomer = (customerPublicId: string) => {
    setSelectedCustomerPublicId(customerPublicId);
    setView("customer");
  };

  const backToOrganization = (organizationId: string) => {
    organizations.setSelectedOrganizationId(organizationId);
    setEditorMode("edit");
    setView("list");
  };

  if (view === "customer" && selectedCustomerPublicId) {
    return (
      <section className="panel feature-panel" aria-label="Customer workspace">
        <CustomerWorkspace
          tenantId={tenantId}
          customerPublicId={selectedCustomerPublicId}
          onBackToOrganization={backToOrganization}
        />
      </section>
    );
  }

  if (view === "vendor" && selectedVendorPublicId) {
    return (
      <section className="panel feature-panel" aria-label="Vendor workspace">
        <VendorWorkspace
          tenantId={tenantId}
          vendorPublicId={selectedVendorPublicId}
          onBackToOrganization={backToOrganization}
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
      </div>

      {organizations.errorMessage && <div className="error-banner">{organizations.errorMessage}</div>}

      <div className="organizations-layout">
        <section className="setup-form-section" aria-label="Organization form">
          {editorMode === "create" ? (
            <OrganizationForm
              organizationTypes={organizations.organizationTypes}
              onCreate={(payload) =>
                organizations.createNewOrganization(payload).then(() => setEditorMode("edit"))
              }
            />
          ) : (
            <OrganizationEditor
              tenantId={tenantId}
              organization={organizations.selectedOrganization}
              organizationTypes={organizations.organizationTypes}
              onOpenCustomer={openCustomer}
              onOpenVendor={openVendor}
              onSave={organizations.saveOrganization}
              onToggleActive={organizations.toggleOrganizationActive}
            />
          )}
        </section>

        <section className="setup-results-section" aria-label="Organization results">
          <OrganizationTable
            contactFilter={organizations.contactFilter}
            displayNameFilter={organizations.displayNameFilter}
            notesFilter={organizations.notesFilter}
            organizations={organizations.visibleOrganizations}
            selectedOrganizationId={organizations.selectedOrganizationId}
            sortDirection={organizations.sortDirection}
            sortField={organizations.sortField}
            status={organizations.status}
            typeFilter={organizations.typeFilter}
            onClearFilters={organizations.clearFilters}
            onContactFilterChange={organizations.setContactFilter}
            onDisplayNameFilterChange={organizations.setDisplayNameFilter}
            onNewOrganization={() => setEditorMode("create")}
            onNotesFilterChange={organizations.setNotesFilter}
            onRefresh={organizations.refreshOrganizations}
            onSelectOrganization={selectOrganization}
            onSort={organizations.handleSort}
            onStatusChange={organizations.setStatus}
            onTypeFilterChange={organizations.setTypeFilter}
          />
        </section>
      </div>
    </section>
  );
}
