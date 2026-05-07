import { useMemo, useState } from "react";

import type { Organization } from "../../organizations/types";
import type { CreateVendorPayload } from "../types";

type VendorFormProps = {
  organizations: Organization[];
  onCreate: (payload: CreateVendorPayload) => Promise<void>;
};

export function VendorForm({ organizations, onCreate }: VendorFormProps) {
  const [organizationId, setOrganizationId] = useState("");
  const [vendorCode, setVendorCode] = useState("");
  const [accountNumber, setAccountNumber] = useState("");
  const [orderingEmail, setOrderingEmail] = useState("");
  const [orderingPhone, setOrderingPhone] = useState("");
  const [website, setWebsite] = useState("");
  const [notes, setNotes] = useState("");

  const selectedOrganizationId = organizationId || organizations[0]?.id || "";
  const canCreate = useMemo(() => selectedOrganizationId.length > 0, [selectedOrganizationId]);

  const handleCreate = () => {
    if (!canCreate) {
      return;
    }

    onCreate({
      organization_id: selectedOrganizationId,
      vendor_code: vendorCode || null,
      account_number: accountNumber || null,
      ordering_email: orderingEmail || null,
      ordering_phone: orderingPhone || null,
      website: website || null,
      notes: notes || null,
    }).then(() => {
      setVendorCode("");
      setAccountNumber("");
      setOrderingEmail("");
      setOrderingPhone("");
      setWebsite("");
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
      <input value={vendorCode} onChange={(event) => setVendorCode(event.target.value)} placeholder="Vendor code" />
      <input
        value={accountNumber}
        onChange={(event) => setAccountNumber(event.target.value)}
        placeholder="Account number"
      />
      <input
        value={orderingEmail}
        type="email"
        onChange={(event) => setOrderingEmail(event.target.value)}
        placeholder="Ordering email"
      />
      <input
        value={orderingPhone}
        type="tel"
        onChange={(event) => setOrderingPhone(event.target.value)}
        placeholder="Ordering phone"
      />
      <input value={website} type="url" onChange={(event) => setWebsite(event.target.value)} placeholder="Website" />
      <input value={notes} onChange={(event) => setNotes(event.target.value)} placeholder="Notes" />
      <button type="button" onClick={handleCreate} disabled={!canCreate}>
        Add
      </button>
    </div>
  );
}
