import type { Organization } from "../types";
import type { OrganizationSortDirection, OrganizationSortField } from "../hooks/useOrganizations";
import type { OrganizationStatusFilter } from "../types";

type OrganizationTableProps = {
  contactFilter: string;
  displayNameFilter: string;
  notesFilter: string;
  organizations: Organization[];
  sortDirection: OrganizationSortDirection;
  sortField: OrganizationSortField;
  status: OrganizationStatusFilter;
  typeFilter: string;
  onClearFilters: () => void;
  onContactFilterChange: (value: string) => void;
  onDisplayNameFilterChange: (value: string) => void;
  onNotesFilterChange: (value: string) => void;
  onOpenOrganization: (organizationId: string) => void;
  onRefresh: () => void;
  onSort: (field: OrganizationSortField) => void;
  onStatusChange: (status: OrganizationStatusFilter) => void;
  onTypeFilterChange: (value: string) => void;
};

export function OrganizationTable({
  contactFilter,
  displayNameFilter,
  notesFilter,
  organizations,
  sortDirection,
  sortField,
  status,
  typeFilter,
  onClearFilters,
  onContactFilterChange,
  onDisplayNameFilterChange,
  onNotesFilterChange,
  onOpenOrganization,
  onRefresh,
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
      <div className="table-toolbar">
        <button type="button" onClick={onRefresh}>
          Refresh
        </button>
        <button type="button" onClick={onClearFilters}>
          Clear Filters
        </button>
        <select value={status} onChange={(event) => onStatusChange(event.target.value as OrganizationStatusFilter)}>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="all">All</option>
        </select>
      </div>
      <div className="table-shell">
        <table>
          <thead>
            <tr>
              <th>{sortableHeader("Name", "display_name")}</th>
              <th>{sortableHeader("Types", "type")}</th>
              <th>{sortableHeader("Contact", "contact")}</th>
              <th>{sortableHeader("Notes", "notes")}</th>
            </tr>
            <tr>
              <th>
                <input
                  value={displayNameFilter}
                  onChange={(event) => onDisplayNameFilterChange(event.target.value)}
                  placeholder="Filter name"
                />
              </th>
              <th>
                <input value={typeFilter} onChange={(event) => onTypeFilterChange(event.target.value)} placeholder="Filter type" />
              </th>
              <th>
                <input
                  value={contactFilter}
                  onChange={(event) => onContactFilterChange(event.target.value)}
                  placeholder="Filter contact"
                />
              </th>
              <th>
                <input
                  value={notesFilter}
                  onChange={(event) => onNotesFilterChange(event.target.value)}
                  placeholder="Filter notes"
                />
              </th>
            </tr>
          </thead>
          <tbody>
            {organizations.map((organization) => (
              <tr key={organization.id}>
                <td>
                  <button className="link-button" type="button" onClick={() => onOpenOrganization(organization.id)}>
                    {organization.display_name}
                  </button>
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
