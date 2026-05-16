import type { Organization } from "../types";
import type { OrganizationSortDirection, OrganizationSortField } from "../hooks/useOrganizations";
import type { OrganizationStatusFilter } from "../types";

type OrganizationTableProps = {
  contactFilter: string;
  displayNameFilter: string;
  notesFilter: string;
  organizations: Organization[];
  selectedOrganizationId: string;
  sortDirection: OrganizationSortDirection;
  sortField: OrganizationSortField;
  status: OrganizationStatusFilter;
  typeFilter: string;
  onClearFilters: () => void;
  onContactFilterChange: (value: string) => void;
  onDisplayNameFilterChange: (value: string) => void;
  onNewOrganization: () => void;
  onNotesFilterChange: (value: string) => void;
  onRefresh: () => void;
  onSelectOrganization: (organizationId: string) => void;
  onSort: (field: OrganizationSortField) => void;
  onStatusChange: (status: OrganizationStatusFilter) => void;
  onTypeFilterChange: (value: string) => void;
};

export function OrganizationTable({
  contactFilter,
  displayNameFilter,
  notesFilter,
  organizations,
  selectedOrganizationId,
  sortDirection,
  sortField,
  status,
  typeFilter,
  onClearFilters,
  onContactFilterChange,
  onDisplayNameFilterChange,
  onNewOrganization,
  onNotesFilterChange,
  onRefresh,
  onSelectOrganization,
  onSort,
  onStatusChange,
  onTypeFilterChange,
}: OrganizationTableProps) {
  const sortableHeader = (label: string, field: OrganizationSortField) => (
    <button className="table-sort" type="button" onClick={() => onSort(field)}>
      {label}
      {sortField === field ? (sortDirection === "asc" ? " ▲" : " ▼") : ""}
    </button>
  );

  return (
    <>
      <div className="setup-module-toolbar organizations-toolbar">
        <div>
          <p className="eyebrow">Results</p>
          <span className="muted">{organizations.length} organizations</span>
        </div>
        <div className="panel-actions organizations-filters">
          <button type="button" onClick={onNewOrganization}>
            New
          </button>
          <button type="button" onClick={onRefresh}>
            Refresh
          </button>
          <button className="secondary-button" type="button" onClick={onClearFilters}>
            Clear Filters
          </button>
          <select value={status} onChange={(event) => onStatusChange(event.target.value as OrganizationStatusFilter)}>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="all">All</option>
          </select>
          <input
            value={displayNameFilter}
            onChange={(event) => onDisplayNameFilterChange(event.target.value)}
            placeholder="Name"
          />
          <input value={typeFilter} onChange={(event) => onTypeFilterChange(event.target.value)} placeholder="Type" />
          <input
            value={contactFilter}
            onChange={(event) => onContactFilterChange(event.target.value)}
            placeholder="Contact"
          />
          <input
            value={notesFilter}
            onChange={(event) => onNotesFilterChange(event.target.value)}
            placeholder="Notes"
          />
        </div>
      </div>
      <div className="table-shell setup-table organizations-table">
        <table>
          <thead>
            <tr>
              <th>{sortableHeader("Name", "display_name")}</th>
              <th>{sortableHeader("Types", "type")}</th>
              <th>{sortableHeader("Contact", "contact")}</th>
              <th>{sortableHeader("Notes", "notes")}</th>
            </tr>
          </thead>
          <tbody>
            {organizations.map((organization) => (
              <tr
                key={organization.id}
                className={selectedOrganizationId === organization.id ? "selected-row" : undefined}
                onClick={() => onSelectOrganization(organization.id)}
              >
                <td>
                  <strong>{organization.display_name}</strong>
                </td>
                <td>{organization.organization_types.map((type) => type.name).join(", ") || "None"}</td>
                <td>
                  {[organization.legal_name, organization.main_phone, organization.main_email, organization.website]
                    .filter(Boolean)
                    .join(" | ")}
                </td>
                <td>{organization.notes || ""}</td>
              </tr>
            ))}
            {organizations.length === 0 && (
              <tr>
                <td colSpan={4}>No organizations</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}
