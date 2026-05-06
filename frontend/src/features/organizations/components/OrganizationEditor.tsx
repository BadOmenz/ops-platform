import { useEffect, useState } from "react";

import type { Organization, OrganizationType, UpdateOrganizationPayload } from "../types";

type OrganizationEditorProps = {
  organization: Organization | null;
  organizationTypes: OrganizationType[];
  onSave: (organizationId: string, payload: UpdateOrganizationPayload) => Promise<void>;
  onToggleActive: (organization: Organization) => Promise<void>;
};

export function OrganizationEditor({
  organization,
  organizationTypes,
  onSave,
  onToggleActive,
}: OrganizationEditorProps) {
  const [displayName, setDisplayName] = useState("");
  const [legalName, setLegalName] = useState("");
  const [mainPhone, setMainPhone] = useState("");
  const [mainEmail, setMainEmail] = useState("");
  const [website, setWebsite] = useState("");
  const [notes, setNotes] = useState("");
  const [selectedTypeIds, setSelectedTypeIds] = useState<string[]>([]);

  useEffect(() => {
    setDisplayName(organization?.display_name || "");
    setLegalName(organization?.legal_name || "");
    setMainPhone(organization?.main_phone || "");
    setMainEmail(organization?.main_email || "");
    setWebsite(organization?.website || "");
    setNotes(organization?.notes || "");
    setSelectedTypeIds(organization?.organization_types.map((type) => type.id) || []);
  }, [organization]);

  if (!organization) {
    return (
      <section className="organization-editor" aria-label="Organization editor">
        <h3>Editor</h3>
        <p className="muted">Select an organization.</p>
      </section>
    );
  }

  const toggleType = (typeId: string) => {
    setSelectedTypeIds((current) =>
      current.includes(typeId) ? current.filter((id) => id !== typeId) : [...current, typeId],
    );
  };

  const handleSave = () => {
    onSave(organization.id, {
      display_name: displayName,
      legal_name: legalName || null,
      main_phone: mainPhone || null,
      main_email: mainEmail || null,
      website: website || null,
      notes: notes || null,
      organization_type_ids: selectedTypeIds,
    });
  };

  return (
    <section className="organization-editor" aria-label="Organization editor">
      <div className="panel-header">
        <div>
          <p className="eyebrow">{organization.is_active ? "Active" : "Inactive"}</p>
          <h3>Editor</h3>
        </div>
        <button type="button" onClick={() => onToggleActive(organization)}>
          {organization.is_active ? "Deactivate" : "Reactivate"}
        </button>
      </div>

      <div className="editor-grid">
        <label className="field">
          <span>Name</span>
          <input value={displayName} onChange={(event) => setDisplayName(event.target.value)} />
        </label>
        <label className="field">
          <span>Legal Name</span>
          <input value={legalName} onChange={(event) => setLegalName(event.target.value)} />
        </label>
        <label className="field">
          <span>Main Phone</span>
          <input value={mainPhone} type="tel" onChange={(event) => setMainPhone(event.target.value)} />
        </label>
        <label className="field">
          <span>Main Email</span>
          <input value={mainEmail} type="email" onChange={(event) => setMainEmail(event.target.value)} />
        </label>
        <label className="field">
          <span>Website</span>
          <input value={website} type="url" onChange={(event) => setWebsite(event.target.value)} />
        </label>
        <label className="field">
          <span>Notes</span>
          <input value={notes} onChange={(event) => setNotes(event.target.value)} />
        </label>
      </div>

      <div className="checkbox-group" aria-label="Organization types">
        {organizationTypes.map((type) => (
          <label className="checkbox-field" key={type.id}>
            <input
              checked={selectedTypeIds.includes(type.id)}
              type="checkbox"
              onChange={() => toggleType(type.id)}
            />
            <span>{type.name}</span>
          </label>
        ))}
      </div>

      <button type="button" onClick={handleSave}>
        Save
      </button>
    </section>
  );
}
