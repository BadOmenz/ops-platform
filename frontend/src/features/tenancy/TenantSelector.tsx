import type { Tenant } from "./types";

type TenantSelectorProps = {
  tenants: Tenant[];
  selectedTenantId: string;
  onSelectTenant: (tenantId: string) => void;
};

export function TenantSelector({
  tenants,
  selectedTenantId,
  onSelectTenant,
}: TenantSelectorProps) {
  return (
    <label className="field">
      <span>Tenant</span>
      <select
        value={selectedTenantId}
        onChange={(event) => onSelectTenant(event.target.value)}
      >
        <option value="">Select tenant</option>
        {tenants.map((tenant) => (
          <option key={tenant.id} value={tenant.id}>
            {tenant.name}
          </option>
        ))}
      </select>
    </label>
  );
}

