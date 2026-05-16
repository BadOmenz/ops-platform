import { useEffect, useState } from "react";

import { getVendor, updateVendor } from "../api";
import type { Vendor } from "../types";
import { VendorItemsPanel } from "../../vendorItems/components/VendorItemsPanel";

type VendorWorkspaceProps = {
  tenantId: string;
  vendorPublicId: string;
  onBackToOrganization: (organizationId: string) => void;
};

type VendorSnapshot = {
  vendor_code: string | null;
  account_number: string | null;
  ordering_email: string | null;
  ordering_phone: string | null;
  website: string | null;
  notes: string | null;
};

type VendorFieldErrors = Partial<Record<keyof VendorSnapshot, string>>;

export function VendorWorkspace({
  tenantId,
  vendorPublicId,
  onBackToOrganization,
}: VendorWorkspaceProps) {
  const [vendor, setVendor] = useState<Vendor | null>(null);
  const [vendorCode, setVendorCode] = useState("");
  const [accountNumber, setAccountNumber] = useState("");
  const [orderingEmail, setOrderingEmail] = useState("");
  const [orderingPhone, setOrderingPhone] = useState("");
  const [website, setWebsite] = useState("");
  const [notes, setNotes] = useState("");
  const [savedSnapshot, setSavedSnapshot] = useState<VendorSnapshot | null>(null);
  const [fieldErrors, setFieldErrors] = useState<VendorFieldErrors>({});
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [loadState, setLoadState] = useState<"loading" | "ready" | "error">("loading");

  const applyVendor = (record: Vendor) => {
    setVendorCode(record.vendor_code || "");
    setAccountNumber(record.account_number || "");
    setOrderingEmail(record.ordering_email || "");
    setOrderingPhone(record.ordering_phone || "");
    setWebsite(record.website || "");
    setNotes(record.notes || "");
    setSavedSnapshot(buildVendorSnapshot(record));
  };

  useEffect(() => {
    let isMounted = true;

    setLoadState("loading");
    setVendor(null);
    setSavedSnapshot(null);
    setErrorMessage("");
    setSuccessMessage("");
    getVendor(tenantId, vendorPublicId)
      .then((record) => {
        if (!isMounted) {
          return;
        }
        setVendor(record);
        applyVendor(record);
        setLoadState("ready");
      })
      .catch(() => {
        if (isMounted) {
          setVendor(null);
          setSavedSnapshot(null);
          setLoadState("error");
          setErrorMessage("Unable to load vendor.");
        }
      });

    return () => {
      isMounted = false;
    };
  }, [tenantId, vendorPublicId]);

  useEffect(() => {
    if (!successMessage) {
      return;
    }

    const timeoutId = window.setTimeout(() => setSuccessMessage(""), 2500);
    return () => window.clearTimeout(timeoutId);
  }, [successMessage]);

  const handleSave = () => {
    if (!vendor) {
      return;
    }

    const clientErrors = validateVendorFields({
      vendor_code: vendorCode || null,
      account_number: accountNumber || null,
      ordering_email: orderingEmail || null,
      ordering_phone: orderingPhone || null,
      website: website || null,
      notes: notes || null,
    });
    setFieldErrors(clientErrors);
    if (Object.keys(clientErrors).length > 0) {
      setErrorMessage("");
      return;
    }

    setErrorMessage("");
    setSuccessMessage("");
    updateVendor(tenantId, vendor.public_id, {
      vendor_code: vendorCode || null,
      account_number: accountNumber || null,
      ordering_email: orderingEmail || null,
      ordering_phone: orderingPhone || null,
      website: website || null,
      notes: notes || null,
    })
      .then((updatedVendor) => {
        setVendor(updatedVendor);
        applyVendor(updatedVendor);
        setFieldErrors({});
        setSuccessMessage("Vendor saved.");
      })
      .catch((error) => {
        const parsedError = parseVendorApiError(error);
        setFieldErrors(parsedError.fieldErrors);
        setErrorMessage(parsedError.message);
      });
  };

  const handleCancel = () => {
    if (vendor) {
      applyVendor(vendor);
      setFieldErrors({});
      setErrorMessage("");
      setSuccessMessage("");
    }
  };

  const currentSnapshot = normalizeVendorSnapshot({
    vendor_code: vendorCode || null,
    account_number: accountNumber || null,
    ordering_email: orderingEmail || null,
    ordering_phone: orderingPhone || null,
    website: website || null,
    notes: notes || null,
  });
  const hasChanges =
    savedSnapshot !== null && JSON.stringify(currentSnapshot) !== JSON.stringify(savedSnapshot);

  if (loadState === "loading") {
    return <p className="muted">Loading vendor...</p>;
  }

  if (!vendor) {
    return <div className="error-banner">{errorMessage || "Vendor unavailable."}</div>;
  }

  return (
    <section className="vendor-workspace" aria-label="Vendor workspace">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Vendor</p>
          <h2>{vendor.organization_display_name}</h2>
        </div>
        <button
          className="secondary-button"
          type="button"
          onClick={() => onBackToOrganization(vendor.organization_id)}
        >
          Back to Organization
        </button>
      </div>

      {errorMessage && <div className="error-banner">{errorMessage}</div>}
      {successMessage && <div className="success-banner">{successMessage}</div>}

      <section className="vendor-profile">
        <div>
          <p className="eyebrow">Profile</p>
          <h3>Vendor details</h3>
        </div>
        <p className="muted">
          Linked organization: {vendor.organization_display_name}
        </p>

        <div className="editor-grid">
          <label className="field">
            <span>Vendor Code</span>
            <input
              aria-invalid={Boolean(fieldErrors.vendor_code)}
              className={fieldErrors.vendor_code ? "input-error" : undefined}
              value={vendorCode}
              onChange={(event) =>
                updateField("vendor_code", event.target.value, setVendorCode, fieldErrors, setFieldErrors)
              }
            />
            {fieldErrors.vendor_code && <small className="field-error">{fieldErrors.vendor_code}</small>}
          </label>
          <label className="field">
            <span>Account Number</span>
            <input
              aria-invalid={Boolean(fieldErrors.account_number)}
              className={fieldErrors.account_number ? "input-error" : undefined}
              value={accountNumber}
              onChange={(event) =>
                updateField("account_number", event.target.value, setAccountNumber, fieldErrors, setFieldErrors)
              }
            />
            {fieldErrors.account_number && <small className="field-error">{fieldErrors.account_number}</small>}
          </label>
          <label className="field">
            <span>Ordering Email</span>
            <input
              aria-invalid={Boolean(fieldErrors.ordering_email)}
              className={fieldErrors.ordering_email ? "input-error" : undefined}
              value={orderingEmail}
              type="email"
              onChange={(event) =>
                updateField("ordering_email", event.target.value, setOrderingEmail, fieldErrors, setFieldErrors)
              }
            />
            {fieldErrors.ordering_email && <small className="field-error">{fieldErrors.ordering_email}</small>}
          </label>
          <label className="field">
            <span>Ordering Phone</span>
            <input
              aria-invalid={Boolean(fieldErrors.ordering_phone)}
              className={fieldErrors.ordering_phone ? "input-error" : undefined}
              value={orderingPhone}
              type="tel"
              onChange={(event) =>
                updateField("ordering_phone", event.target.value, setOrderingPhone, fieldErrors, setFieldErrors)
              }
            />
            {fieldErrors.ordering_phone && <small className="field-error">{fieldErrors.ordering_phone}</small>}
          </label>
          <label className="field">
            <span>Website</span>
            <input
              aria-invalid={Boolean(fieldErrors.website)}
              className={fieldErrors.website ? "input-error" : undefined}
              value={website}
              type="url"
              onChange={(event) =>
                updateField("website", event.target.value, setWebsite, fieldErrors, setFieldErrors)
              }
            />
            {fieldErrors.website && <small className="field-error">{fieldErrors.website}</small>}
          </label>
          <label className="field">
            <span>Notes</span>
            <input
              aria-invalid={Boolean(fieldErrors.notes)}
              className={fieldErrors.notes ? "input-error" : undefined}
              value={notes}
              onChange={(event) =>
                updateField("notes", event.target.value, setNotes, fieldErrors, setFieldErrors)
              }
            />
            {fieldErrors.notes && <small className="field-error">{fieldErrors.notes}</small>}
          </label>
        </div>

        <div className="editor-actions">
          <button type="button" onClick={handleSave} disabled={!hasChanges}>
            Save Vendor
          </button>
          <button
            className="secondary-button"
            type="button"
            onClick={handleCancel}
            disabled={!hasChanges}
          >
            Cancel
          </button>
        </div>
      </section>

      <section className="vendor-items-section">
        <VendorItemsPanel
          tenantId={tenantId}
          vendorPublicId={vendor.public_id}
          vendorDisplayName={vendor.organization_display_name}
          mode="vendor"
        />
      </section>
    </section>
  );
}

function buildVendorSnapshot(vendor: Vendor): VendorSnapshot {
  return normalizeVendorSnapshot({
    vendor_code: vendor.vendor_code,
    account_number: vendor.account_number,
    ordering_email: vendor.ordering_email,
    ordering_phone: vendor.ordering_phone,
    website: vendor.website,
    notes: vendor.notes,
  });
}

function normalizeVendorSnapshot(snapshot: VendorSnapshot): VendorSnapshot {
  return {
    vendor_code: normalizeNullableText(snapshot.vendor_code),
    account_number: normalizeNullableText(snapshot.account_number),
    ordering_email: normalizeNullableText(snapshot.ordering_email),
    ordering_phone: normalizeNullableText(snapshot.ordering_phone),
    website: normalizeNullableText(snapshot.website),
    notes: normalizeNullableText(snapshot.notes),
  };
}

function normalizeNullableText(value: string | null) {
  return value?.trim() || null;
}

function validateVendorFields(snapshot: VendorSnapshot): VendorFieldErrors {
  const errors: VendorFieldErrors = {};
  const email = snapshot.ordering_email?.trim() || "";
  const phone = snapshot.ordering_phone?.trim() || "";
  const website = snapshot.website?.trim() || "";

  if (email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    errors.ordering_email = "Ordering email must be a valid email address.";
  }
  if (phone) {
    const digitCount = Array.from(phone).filter((character) => /\d/.test(character)).length;
    if (digitCount < 7 || digitCount > 20 || !/^[0-9\s()+.-]+$/.test(phone)) {
      errors.ordering_phone = "Ordering phone must be a valid phone number.";
    }
  }
  if (website && !isValidWebsite(website)) {
    errors.website = "Website must be a valid URL.";
  }

  return errors;
}

function isValidWebsite(value: string) {
  const candidate = value.includes("://") ? value : `https://${value}`;
  try {
    const parsedUrl = new URL(candidate);
    return (
      ["http:", "https:"].includes(parsedUrl.protocol) &&
      parsedUrl.hostname.includes(".") &&
      !/\s/.test(candidate)
    );
  } catch {
    return false;
  }
}

function updateField(
  field: keyof VendorSnapshot,
  value: string,
  setter: (value: string) => void,
  currentErrors: VendorFieldErrors,
  setFieldErrors: (errors: VendorFieldErrors) => void,
) {
  setter(value);
  if (!currentErrors[field]) {
    return;
  }

  const nextSnapshot = {
    vendor_code: null,
    account_number: null,
    ordering_email: null,
    ordering_phone: null,
    website: null,
    notes: null,
    [field]: value || null,
  };
  if (!validateVendorFields(nextSnapshot)[field]) {
    const remainingErrors = { ...currentErrors };
    delete remainingErrors[field];
    setFieldErrors(remainingErrors);
  }
}

function parseVendorApiError(error: unknown): { fieldErrors: VendorFieldErrors; message: string } {
  const detail = getApiErrorDetail(error);
  const fieldErrors: VendorFieldErrors = {};

  if (Array.isArray(detail)) {
    for (const item of detail) {
      if (typeof item !== "object" || item === null) {
        continue;
      }
      const issue = item as { loc?: unknown[]; msg?: unknown };
      const field = issue.loc?.[issue.loc.length - 1];
      const message = typeof issue.msg === "string" ? issue.msg : "Invalid value.";
      assignFieldError(fieldErrors, field, humanizeValidationMessage(message));
    }
  }

  if (typeof detail === "string") {
    assignStringDetail(fieldErrors, detail);
  }

  return {
    fieldErrors,
    message: Object.keys(fieldErrors).length > 0 ? "" : "Unable to save vendor.",
  };
}

function getApiErrorDetail(error: unknown) {
  if (
    typeof error === "object" &&
    error !== null &&
    "response" in error &&
    typeof error.response === "object" &&
    error.response !== null &&
    "data" in error.response
  ) {
    return (error.response.data as { detail?: unknown }).detail;
  }
  return undefined;
}

function assignStringDetail(fieldErrors: VendorFieldErrors, detail: string) {
  const lowerDetail = detail.toLowerCase();
  if (lowerDetail.includes("phone")) {
    fieldErrors.ordering_phone = "Ordering phone must be a valid phone number.";
    return;
  }
  if (lowerDetail.includes("email")) {
    fieldErrors.ordering_email = "Ordering email must be a valid email address.";
    return;
  }
  if (lowerDetail.includes("website") || lowerDetail.includes("url")) {
    fieldErrors.website = "Website must be a valid URL.";
  }
}

function assignFieldError(
  fieldErrors: VendorFieldErrors,
  field: unknown,
  message: string,
) {
  if (field === "ordering_phone") {
    fieldErrors.ordering_phone = message;
  }
  if (field === "ordering_email") {
    fieldErrors.ordering_email = message;
  }
  if (field === "website") {
    fieldErrors.website = message;
  }
  if (field === "vendor_code") {
    fieldErrors.vendor_code = message;
  }
  if (field === "account_number") {
    fieldErrors.account_number = message;
  }
  if (field === "notes") {
    fieldErrors.notes = message;
  }
}

function humanizeValidationMessage(message: string) {
  const lowerMessage = message.toLowerCase();
  if (lowerMessage.includes("email")) {
    return "Ordering email must be a valid email address.";
  }
  if (lowerMessage.includes("phone")) {
    return "Ordering phone must be a valid phone number.";
  }
  if (lowerMessage.includes("url") || lowerMessage.includes("website")) {
    return "Website must be a valid URL.";
  }
  if (lowerMessage.includes("string_too_long")) {
    return "Value is too long.";
  }
  return message;
}
