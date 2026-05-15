import type { Customer } from "../types";

type CustomerTableProps = {
  customers: Customer[];
  onToggleActive: (customer: Customer) => Promise<void>;
};

export function CustomerTable({ customers, onToggleActive }: CustomerTableProps) {
  return (
    <div className="table-shell">
      <table>
        <thead>
          <tr>
            <th>Organization</th>
            <th>Customer</th>
            <th>Billing Contact</th>
            <th>Accounts Payable</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {customers.map((customer) => (
            <tr key={customer.public_id}>
              <td>{customer.organization_display_name}</td>
              <td>{[customer.customer_code, customer.primary_contact_name].filter(Boolean).join(" | ")}</td>
              <td>{[customer.billing_email, customer.billing_phone].filter(Boolean).join(" | ")}</td>
              <td>{[customer.accounts_payable_email, customer.accounts_payable_phone].filter(Boolean).join(" | ")}</td>
              <td>
                <button type="button" onClick={() => onToggleActive(customer)}>
                  {customer.is_active ? "Deactivate" : "Reactivate"}
                </button>
              </td>
            </tr>
          ))}
          {customers.length === 0 && (
            <tr>
              <td colSpan={5}>No customers</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
