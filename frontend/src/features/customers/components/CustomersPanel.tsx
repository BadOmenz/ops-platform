import { CustomerForm } from "./CustomerForm";
import { CustomerTable } from "./CustomerTable";
import { useCustomers } from "../hooks/useCustomers";
import type { CustomerStatusFilter } from "../types";

type CustomersPanelProps = {
  tenantId: string;
};

export function CustomersPanel({ tenantId }: CustomersPanelProps) {
  const customers = useCustomers(tenantId);

  return (
    <section id="customers" className="panel feature-panel" aria-label="Customers">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Organization role</p>
          <h2>Customers</h2>
        </div>
        <div className="panel-actions">
          <button type="button" onClick={customers.refreshCustomers}>
            Refresh
          </button>
          <select
            value={customers.status}
            onChange={(event) => customers.setStatus(event.target.value as CustomerStatusFilter)}
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="all">All</option>
          </select>
        </div>
      </div>

      {customers.errorMessage && <div className="error-banner">{customers.errorMessage}</div>}

      <CustomerForm organizations={customers.organizations} onCreate={customers.createNewCustomer} />
      <CustomerTable customers={customers.customers} onToggleActive={customers.toggleCustomerActive} />
    </section>
  );
}
