import type { Organization } from "../types";
import type { OrganizationSortDirection, OrganizationSortField } from "../hooks/useOrganizations";

type OrganizationTableProps = {
  contactFilter: string;
  displayNameFilter: string;
  notesFilter: string;
  organizations: Organization[];
  sortDirection: OrganizationSortDirection;
  sortField: OrganizationSortField;
  typeFilter: string;
  onContactFilterChange: (value: string) => void;
  onDisplayNameFilterChange: (value: string) => void;
  onNotesFilterChange: (value: string) => void;
  onOpenOrganization: (organizationId: string) => void;
  onSort: (field: OrganizationSortField) => void;
  onTypeFilterChange: (value: string) => void;
};

export function OrganizationTable({
  contactFilter,
  displayNameFilter,
  notesFilter,
  organizations,
  sortDirection,
  sortField,
  typeFilter,
  onContactFilterChange,
  onDisplayNameFilterChange,
  onNotesFilterChange,
  onOpenOrganization,
  onSort,
  onTypeFilterChange,
}: OrganizationTableProps) {
  const sortableHeader = (label: string, field: OrganizationSortField) => (
    <button className="table-sort" type="button" onClick={() => onSort(field)}>
      {label}
      {sortField === field ? (sortDirection === "asc" ? " ▲" : " ▼") : ""}
    </button>
  );

  return (
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
  );
}
