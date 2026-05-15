import { useEffect, useState } from "react";

import { VendorRoleCard } from "../../vendors/components/VendorRoleCard";
import type { Organization, OrganizationType, UpdateOrganizationPayload } from "../types";

type OrganizationEditorProps = {
  tenantId: string;
  organization: Organization | null;
  organizationTypes: OrganizationType[];
  onSave: (organizationId: string, payload: UpdateOrganizationPayload) => Promise<void>;
  onOpenCustomer: (customerPublicId: string) => void;
  onOpenVendor: (vendorPublicId: string) => void;
  onToggleActive: (organization: Organization) => Promise<void>;
};

export function OrganizationEditor({
  tenantId,
  organization,
  organizationTypes,
  onSave,
  onOpenCustomer,
  onOpenVendor,
  onToggleActive,
}: OrganizationEditorProps) {
  const [displayName, setDisplayName] = useState("");
  const [legalName, setLegalName] = useState("");
  const [mainPhone, setMainPhone] = useState("");
  const [mainEmail, setMainEmail] = useState("");
  const [website, setWebsite] = useState("");
  const [notes, setNotes] = useState("");
  const [selectedTypeIds, setSelectedTypeIds] = useState<string[]>([]);
  const [savedSnapshot, setSavedSnapshot] = useState<OrganizationEditorSnapshot | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    setDisplayName(organization?.display_name || "");
    setLegalName(organization?.legal_name || "");
    setMainPhone(organization?.main_phone || "");
    setMainEmail(organization?.main_email || "");
    setWebsite(organization?.website || "");
    setNotes(organization?.notes || "");
    const nextSnapshot = organization ? buildSnapshot(organization) : null;
    setSelectedTypeIds(nextSnapshot?.organization_type_ids || []);
    setSavedSnapshot(nextSnapshot);
    setErrorMessage("");
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
    const payload = {
      display_name: displayName,
      legal_name: legalName || null,
      main_phone: mainPhone || null,
      main_email: mainEmail || null,
      website: website || null,
      notes: notes || null,
      organization_type_ids: selectedTypeIds,
    };

    setIsSaving(true);
    setErrorMessage("");

    onSave(organization.id, payload)
      .then(() => {
        setSavedSnapshot(normalizeSnapshot(payload));
      })
      .catch(() => {
        setErrorMessage("Unable to save organization changes.");
      })
      .finally(() => setIsSaving(false));
  };

  const handleCancel = () => {
    if (!savedSnapshot) {
      return;
    }

    setDisplayName(savedSnapshot.display_name);
    setLegalName(savedSnapshot.legal_name || "");
    setMainPhone(savedSnapshot.main_phone || "");
    setMainEmail(savedSnapshot.main_email || "");
    setWebsite(savedSnapshot.website || "");
    setNotes(savedSnapshot.notes || "");
    setSelectedTypeIds(savedSnapshot.organization_type_ids);
    setErrorMessage("");
  };

  const currentSnapshot = normalizeSnapshot({
    display_name: displayName,
    legal_name: legalName || null,
    main_phone: mainPhone || null,
    main_email: mainEmail || null,
    website: website || null,
    notes: notes || null,
    organization_type_ids: selectedTypeIds,
  });
  const hasOrganizationChanges =
    savedSnapshot !== null && JSON.stringify(currentSnapshot) !== JSON.stringify(savedSnapshot);

  return (
    <section className="organization-editor" aria-label="Organization editor">
      <div className="panel-header">
        <div>
          <p className="eyebrow">{organization.is_active ? "Active" : "Inactive"}</p>
          <h3>Editor</h3>
        </div>
        <button type="button" onClick={() => onToggleActive(organization)}>
          {organization.is_active ? "Deactivate this organization" : "Reactivate this organization"}
        </button>
      </div>

      {errorMessage && <div className="error-banner">{errorMessage}</div>}

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

      {hasOrganizationChanges && (
        <div className="editor-actions">
          <button type="button" onClick={handleSave} disabled={isSaving}>
            Save
          </button>
          <button
            className="secondary-button"
            type="button"
            onClick={handleCancel}
            disabled={isSaving}
          >
            Cancel
          </button>
        </div>
      )}

      <VendorRoleCard
        tenantId={tenantId}
        organizationId={organization.id}
        organizationWebsite={organization.website}
        onOpenCustomer={onOpenCustomer}
        onOpenVendor={onOpenVendor}
      />
    </section>
  );
}

type OrganizationEditorSnapshot = {
  display_name: string;
  legal_name: string | null;
  main_phone: string | null;
  main_email: string | null;
  website: string | null;
  notes: string | null;
  organization_type_ids: string[];
};

function buildSnapshot(organization: Organization): OrganizationEditorSnapshot {
  return normalizeSnapshot({
    display_name: organization.display_name,
    legal_name: organization.legal_name,
    main_phone: organization.main_phone,
    main_email: organization.main_email,
    website: organization.website,
    notes: organization.notes,
    organization_type_ids: organization.organization_types.map((type) => type.id),
  });
}

function normalizeSnapshot(snapshot: OrganizationEditorSnapshot): OrganizationEditorSnapshot {
  return {
    ...snapshot,
    display_name: snapshot.display_name.trim(),
    legal_name: normalizeNullableText(snapshot.legal_name),
    main_phone: normalizeNullableText(snapshot.main_phone),
    main_email: normalizeNullableText(snapshot.main_email),
    website: normalizeNullableText(snapshot.website),
    notes: normalizeNullableText(snapshot.notes),
    organization_type_ids: [...snapshot.organization_type_ids].sort(),
  };
}

function normalizeNullableText(value: string | null) {
  return value?.trim() || null;
}
