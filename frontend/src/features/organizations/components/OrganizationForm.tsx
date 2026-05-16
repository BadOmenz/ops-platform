import { useMemo, useState } from "react";

import type { CreateOrganizationPayload, OrganizationType } from "../types";

type OrganizationFormProps = {
  organizationTypes: OrganizationType[];
  onCreate: (payload: CreateOrganizationPayload) => Promise<void>;
};

export function OrganizationForm({ organizationTypes, onCreate }: OrganizationFormProps) {
  const [displayName, setDisplayName] = useState("");
  const [legalName, setLegalName] = useState("");
  const [mainPhone, setMainPhone] = useState("");
  const [mainEmail, setMainEmail] = useState("");
  const [website, setWebsite] = useState("");
  const [notes, setNotes] = useState("");
  const [selectedTypeId, setSelectedTypeId] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  const selectedOrganizationTypeId = selectedTypeId || organizationTypes[0]?.id || "";

  const canCreate = useMemo(() => displayName.trim().length > 0, [displayName]);

  const handleCreate = () => {
    if (!canCreate || isSaving) {
      return;
    }

    setIsSaving(true);
    onCreate({
      display_name: displayName,
      legal_name: legalName || null,
      main_phone: mainPhone || null,
      main_email: mainEmail || null,
      website: website || null,
      notes: notes || null,
      organization_type_ids: selectedOrganizationTypeId ? [selectedOrganizationTypeId] : [],
    }).then(() => {
      setDisplayName("");
      setLegalName("");
      setMainPhone("");
      setMainEmail("");
      setWebsite("");
      setNotes("");
    }).finally(() => setIsSaving(false));
  };

  return (
    <div className="setup-form organization-form" aria-label="Create organization">
      <div>
        <p className="eyebrow">New organization</p>
        <h3>Organization details</h3>
      </div>

      <label className="field">
        <span>Name</span>
        <input value={displayName} onChange={(event) => setDisplayName(event.target.value)} />
      </label>
      <label className="field">
        <span>Legal name</span>
        <input value={legalName} onChange={(event) => setLegalName(event.target.value)} />
      </label>
      <label className="field">
        <span>Main phone</span>
        <input value={mainPhone} type="tel" onChange={(event) => setMainPhone(event.target.value)} />
      </label>
      <label className="field">
        <span>Main email</span>
        <input value={mainEmail} type="email" onChange={(event) => setMainEmail(event.target.value)} />
      </label>
      <label className="field">
        <span>Website</span>
        <input value={website} type="url" onChange={(event) => setWebsite(event.target.value)} />
      </label>
      <label className="field">
        <span>Type</span>
        <select value={selectedOrganizationTypeId} onChange={(event) => setSelectedTypeId(event.target.value)}>
          {organizationTypes.map((type) => (
            <option key={type.id} value={type.id}>
              {type.name}
            </option>
          ))}
        </select>
      </label>
      <label className="field">
        <span>Notes</span>
        <input value={notes} onChange={(event) => setNotes(event.target.value)} />
      </label>
      <div className="editor-actions">
        <button type="button" onClick={handleCreate} disabled={!canCreate || isSaving}>
          {isSaving ? "Adding..." : "Add"}
        </button>
      </div>
    </div>
  );
}
