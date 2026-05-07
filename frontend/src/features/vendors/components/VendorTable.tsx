import type { Vendor } from "../types";

type VendorTableProps = {
  vendors: Vendor[];
  onToggleActive: (vendor: Vendor) => Promise<void>;
};

export function VendorTable({ vendors, onToggleActive }: VendorTableProps) {
  return (
    <div className="table-shell">
      <table>
        <thead>
          <tr>
            <th>Organization</th>
            <th>Vendor</th>
            <th>Ordering Contact</th>
            <th>Notes</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {vendors.map((vendor) => (
            <tr key={vendor.public_id}>
              <td>{vendor.organization_display_name}</td>
              <td>{[vendor.vendor_code, vendor.account_number].filter(Boolean).join(" | ")}</td>
              <td>{[vendor.ordering_email, vendor.ordering_phone, vendor.website].filter(Boolean).join(" | ")}</td>
              <td>{vendor.notes || ""}</td>
              <td>
                <button type="button" onClick={() => onToggleActive(vendor)}>
                  {vendor.is_active ? "Deactivate" : "Reactivate"}
                </button>
              </td>
            </tr>
          ))}
          {vendors.length === 0 && (
            <tr>
              <td colSpan={5}>No vendors</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
