import { VendorForm } from "./VendorForm";
import { VendorTable } from "./VendorTable";
import { useVendors } from "../hooks/useVendors";
import type { VendorStatusFilter } from "../types";

type VendorsPanelProps = {
  tenantId: string;
};

export function VendorsPanel({ tenantId }: VendorsPanelProps) {
  const vendors = useVendors(tenantId);

  return (
    <section id="vendors" className="panel feature-panel" aria-label="Vendors">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Organization role</p>
          <h2>Vendors</h2>
        </div>
        <div className="panel-actions">
          <button type="button" onClick={vendors.refreshVendors}>
            Refresh
          </button>
          <select
            value={vendors.status}
            onChange={(event) => vendors.setStatus(event.target.value as VendorStatusFilter)}
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="all">All</option>
          </select>
        </div>
      </div>

      {vendors.errorMessage && <div className="error-banner">{vendors.errorMessage}</div>}

      <VendorForm organizations={vendors.organizations} onCreate={vendors.createNewVendor} />
      <VendorTable vendors={vendors.vendors} onToggleActive={vendors.toggleVendorActive} />
    </section>
  );
}
