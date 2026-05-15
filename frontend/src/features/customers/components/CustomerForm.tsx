import { useMemo, useState } from "react";

import type { Organization } from "../../organizations/types";
import type { CreateCustomerPayload } from "../types";

type CustomerFormProps = {
  organizations: Organization[];
  onCreate: (payload: CreateCustomerPayload) => Promise<void>;
};

export function CustomerForm({ organizations, onCreate }: CustomerFormProps) {
  const [organizationId, setOrganizationId] = useState("");
  const [customerCode, setCustomerCode] = useState("");
  const [billingEmail, setBillingEmail] = useState("");
  const [billingPhone, setBillingPhone] = useState("");
  const [accountsPayableEmail, setAccountsPayableEmail] = useState("");
  const [accountsPayablePhone, setAccountsPayablePhone] = useState("");
  const [primaryContactName, setPrimaryContactName] = useState("");
  const [notes, setNotes] = useState("");

  const selectedOrganizationId = organizationId || organizations[0]?.id || "";
  const canCreate = useMemo(() => selectedOrganizationId.length > 0, [selectedOrganizationId]);

  const handleCreate = () => {
    if (!canCreate) {
      return;
    }

    onCreate({
      organization_id: selectedOrganizationId,
      customer_code: customerCode || null,
      billing_email: billingEmail || null,
      billing_phone: billingPhone || null,
      accounts_payable_email: accountsPayableEmail || null,
      accounts_payable_phone: accountsPayablePhone || null,
      primary_contact_name: primaryContactName || null,
      notes: notes || null,
    }).then(() => {
      setCustomerCode("");
      setBillingEmail("");
      setBillingPhone("");
      setAccountsPayableEmail("");
      setAccountsPayablePhone("");
      setPrimaryContactName("");
      setNotes("");
    });
  };

  return (
    <div className="vendor-form">
      <select value={selectedOrganizationId} onChange={(event) => setOrganizationId(event.target.value)}>
        {organizations.map((organization) => (
          <option key={organization.id} value={organization.id}>
            {organization.display_name}
          </option>
        ))}
      </select>
      <input value={customerCode} onChange={(event) => setCustomerCode(event.target.value)} placeholder="Customer code" />
      <input
        value={billingEmail}
        type="email"
        onChange={(event) => setBillingEmail(event.target.value)}
        placeholder="Billing email"
      />
      <input
        value={billingPhone}
        type="tel"
        onChange={(event) => setBillingPhone(event.target.value)}
        placeholder="Billing phone"
      />
      <input
        value={accountsPayableEmail}
        type="email"
        onChange={(event) => setAccountsPayableEmail(event.target.value)}
        placeholder="AP email"
      />
      <input
        value={accountsPayablePhone}
        type="tel"
        onChange={(event) => setAccountsPayablePhone(event.target.value)}
        placeholder="AP phone"
      />
      <input
        value={primaryContactName}
        onChange={(event) => setPrimaryContactName(event.target.value)}
        placeholder="Primary contact"
      />
      <input value={notes} onChange={(event) => setNotes(event.target.value)} placeholder="Notes" />
      <button type="button" onClick={handleCreate} disabled={!canCreate}>
        Add
      </button>
    </div>
  );
}
