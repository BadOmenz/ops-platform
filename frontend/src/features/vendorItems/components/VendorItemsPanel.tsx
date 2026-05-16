import { useEffect, useMemo, useState, type Dispatch, type SetStateAction } from "react";

import type { ItemCategory } from "../../itemCategories/types";
import type { StorageLocation } from "../../storageLocations/types";
import type { Vendor } from "../../vendors/types";
import { useVendorItems } from "../hooks/useVendorItems";
import type {
  CreateVendorItemPayload,
  UpdateVendorItemPayload,
  VendorItem,
  VendorItemStatusFilter,
} from "../types";

type VendorItemsPanelProps = {
  tenantId: string;
  vendorPublicId?: string;
  vendorDisplayName?: string;
  mode: "global" | "vendor";
};

type VendorItemFormState = {
  vendor_public_id: string;
  vendor_item_code: string;
  vendor_description: string;
  canonical_name: string;
  category_public_id: string;
  default_storage_location_public_id: string;
  purchase_unit: string;
  pack_size: string;
  pack_unit: string;
  case_quantity: string;
  case_unit: string;
  last_price: string;
  last_price_date: string;
  estimated_price: string;
  price_unit: string;
  notes: string;
};

const emptyFormState: VendorItemFormState = {
  vendor_public_id: "",
  vendor_item_code: "",
  vendor_description: "",
  canonical_name: "",
  category_public_id: "",
  default_storage_location_public_id: "",
  purchase_unit: "",
  pack_size: "",
  pack_unit: "",
  case_quantity: "",
  case_unit: "",
  last_price: "",
  last_price_date: "",
  estimated_price: "",
  price_unit: "",
  notes: "",
};

export function VendorItemsPanel({
  tenantId,
  vendorPublicId = "",
  vendorDisplayName,
  mode,
}: VendorItemsPanelProps) {
  const vendorItems = useVendorItems({
    tenantId,
    fixedVendorPublicId: mode === "vendor" ? vendorPublicId : "",
  });
  const [selectedPublicId, setSelectedPublicId] = useState("");
  const selectedItem =
    vendorItems.items.find((item) => item.public_id === selectedPublicId) || null;
  const visibleItems = useMemo(
    () => sortVendorItems(vendorItems.items),
    [vendorItems.items],
  );

  useEffect(() => {
    if (
      selectedPublicId &&
      !vendorItems.items.some((item) => item.public_id === selectedPublicId)
    ) {
      setSelectedPublicId("");
    }
  }, [selectedPublicId, vendorItems.items]);

  const isGlobal = mode === "global";
  const panelClassName = isGlobal
    ? "panel feature-panel vendor-items-panel"
    : "vendor-items-panel vendor-items-embedded";

  return (
    <section className={panelClassName} aria-label="Vendor items">
      <div className="setup-module-header vendor-items-header">
        <div>
          <p className="eyebrow">{isGlobal ? "Operations" : "Vendor workspace"}</p>
          <h2>Vendor Items</h2>
          <p className="muted">
            {isGlobal
              ? "Find and maintain purchasable supplier items across vendors."
              : `Maintain purchasable items for ${vendorDisplayName || "this vendor"}.`}
          </p>
        </div>
      </div>

      <VendorItemsToolbar
        canonicalName={vendorItems.canonicalName}
        categories={vendorItems.categories}
        categoryPublicId={vendorItems.categoryPublicId}
        isGlobal={isGlobal}
        itemCount={vendorItems.items.length}
        onCanonicalNameChange={vendorItems.setCanonicalName}
        onCategoryChange={vendorItems.setCategoryPublicId}
        onRefresh={vendorItems.refreshItems}
        onStatusChange={vendorItems.setStatus}
        onStorageLocationChange={vendorItems.setStorageLocationPublicId}
        onVendorChange={vendorItems.setVendorPublicId}
        status={vendorItems.status}
        storageLocationPublicId={vendorItems.storageLocationPublicId}
        storageLocations={vendorItems.storageLocations}
        vendorPublicId={vendorItems.vendorPublicId}
        vendors={vendorItems.vendors}
      />

      {vendorItems.errorMessage && <div className="error-banner">{vendorItems.errorMessage}</div>}

      <div className="vendor-items-layout">
        <section className="setup-form-section" aria-label="Vendor item form">
          <VendorItemForm
            categories={vendorItems.categories}
            fixedVendorPublicId={mode === "vendor" ? vendorPublicId : ""}
            item={selectedItem}
            onCancel={() => setSelectedPublicId("")}
            onCreate={vendorItems.createNewItem}
            onSaved={(item) => setSelectedPublicId(item.public_id)}
            onSave={vendorItems.saveItem}
            storageLocations={vendorItems.storageLocations}
            vendors={vendorItems.vendors}
          />
        </section>

        <section className="setup-results-section" aria-label="Vendor item results">
          <VendorItemsTable
            isGlobal={isGlobal}
            items={visibleItems}
            loadState={vendorItems.loadState}
            onSelect={setSelectedPublicId}
            onToggleActive={vendorItems.toggleItemActive}
            selectedPublicId={selectedPublicId}
          />
        </section>
      </div>
    </section>
  );
}

type VendorItemsToolbarProps = {
  canonicalName: string;
  categories: ItemCategory[];
  categoryPublicId: string;
  isGlobal: boolean;
  itemCount: number;
  onCanonicalNameChange: (value: string) => void;
  onCategoryChange: (value: string) => void;
  onRefresh: () => void;
  onStatusChange: (value: VendorItemStatusFilter) => void;
  onStorageLocationChange: (value: string) => void;
  onVendorChange: (value: string) => void;
  status: VendorItemStatusFilter;
  storageLocationPublicId: string;
  storageLocations: StorageLocation[];
  vendorPublicId: string;
  vendors: Vendor[];
};

function VendorItemsToolbar({
  canonicalName,
  categories,
  categoryPublicId,
  isGlobal,
  itemCount,
  onCanonicalNameChange,
  onCategoryChange,
  onRefresh,
  onStatusChange,
  onStorageLocationChange,
  onVendorChange,
  status,
  storageLocationPublicId,
  storageLocations,
  vendorPublicId,
  vendors,
}: VendorItemsToolbarProps) {
  return (
    <div className="setup-module-toolbar vendor-items-toolbar">
      <div>
        <p className="eyebrow">Results</p>
        <span className="muted">{itemCount} items</span>
      </div>
      <div className="panel-actions vendor-items-filters">
        <button type="button" onClick={onRefresh}>
          Refresh
        </button>
        <select value={status} onChange={(event) => onStatusChange(event.target.value as VendorItemStatusFilter)}>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="all">All</option>
        </select>
        {isGlobal && (
          <select value={vendorPublicId} onChange={(event) => onVendorChange(event.target.value)}>
            <option value="">All vendors</option>
            {vendors.map((vendor) => (
              <option key={vendor.public_id} value={vendor.public_id}>
                {formatVendorName(vendor)}
              </option>
            ))}
          </select>
        )}
        <input
          aria-label="Canonical name filter"
          placeholder="Canonical name"
          value={canonicalName}
          onChange={(event) => onCanonicalNameChange(event.target.value)}
        />
        <select value={categoryPublicId} onChange={(event) => onCategoryChange(event.target.value)}>
          <option value="">All categories</option>
          {categories.map((category) => (
            <option key={category.public_id} value={category.public_id}>
              {category.display_name}
            </option>
          ))}
        </select>
        <select
          value={storageLocationPublicId}
          onChange={(event) => onStorageLocationChange(event.target.value)}
        >
          <option value="">All storage</option>
          {storageLocations.map((location) => (
            <option key={location.public_id} value={location.public_id}>
              {location.display_name}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}

type VendorItemFormProps = {
  categories: ItemCategory[];
  fixedVendorPublicId: string;
  item: VendorItem | null;
  onCancel: () => void;
  onCreate: (payload: CreateVendorItemPayload) => Promise<VendorItem>;
  onSaved: (item: VendorItem) => void;
  onSave: (vendorItemPublicId: string, payload: UpdateVendorItemPayload) => Promise<VendorItem>;
  storageLocations: StorageLocation[];
  vendors: Vendor[];
};

function VendorItemForm({
  categories,
  fixedVendorPublicId,
  item,
  onCancel,
  onCreate,
  onSaved,
  onSave,
  storageLocations,
  vendors,
}: VendorItemFormProps) {
  const [formState, setFormState] = useState<VendorItemFormState>(emptyFormState);
  const [validationMessage, setValidationMessage] = useState("");
  const [saveState, setSaveState] = useState<"idle" | "saving">("idle");

  useEffect(() => {
    setFormState(item ? buildFormState(item) : { ...emptyFormState, vendor_public_id: fixedVendorPublicId });
    setValidationMessage("");
  }, [fixedVendorPublicId, item]);

  const activeVendors = vendors.filter((vendor) => vendor.is_active);
  const categoryOptions = useMemo(
    () => mergeSelectedCategory(categories, item),
    [categories, item],
  );
  const storageLocationOptions = useMemo(
    () => mergeSelectedStorageLocation(storageLocations, item),
    [item, storageLocations],
  );
  const hasChanges = !item || JSON.stringify(formState) !== JSON.stringify(buildFormState(item));
  const canSave =
    saveState !== "saving" &&
    hasChanges &&
    Boolean((fixedVendorPublicId || formState.vendor_public_id).trim()) &&
    formState.vendor_description.trim().length > 0 &&
    formState.canonical_name.trim().length > 0;

  const handleSave = () => {
    const clientError = validateFormState(formState, fixedVendorPublicId);
    if (clientError) {
      setValidationMessage(clientError);
      return;
    }

    setValidationMessage("");
    setSaveState("saving");
    const payload = item
      ? buildChangedPayload(formState, item, fixedVendorPublicId)
      : buildPayload(formState, fixedVendorPublicId);
    const request = item ? onSave(item.public_id, payload) : onCreate(payload as CreateVendorItemPayload);
    request
      .then((savedItem) => {
        onSaved(savedItem);
        if (!item) {
          setFormState({ ...emptyFormState, vendor_public_id: fixedVendorPublicId });
        }
      })
      .finally(() => setSaveState("idle"));
  };

  return (
    <div className="setup-form vendor-item-form" aria-label={item ? "Edit vendor item" : "Create vendor item"}>
      <div>
        <p className="eyebrow">{item ? "Edit item" : "New item"}</p>
        <h3>{item?.vendor_description || "Vendor item details"}</h3>
      </div>

      {validationMessage && <div className="error-banner">{validationMessage}</div>}

      {!fixedVendorPublicId && (
        <label className="field">
          <span>Vendor</span>
          <select
            value={formState.vendor_public_id}
            onChange={(event) => updateField("vendor_public_id", event.target.value, setFormState)}
          >
            <option value="">Choose vendor</option>
            {activeVendors.map((vendor) => (
              <option key={vendor.public_id} value={vendor.public_id}>
                {formatVendorName(vendor)}
              </option>
            ))}
          </select>
        </label>
      )}

      <label className="field">
        <span>Vendor item code</span>
        <input
          value={formState.vendor_item_code}
          onChange={(event) => updateField("vendor_item_code", event.target.value, setFormState)}
        />
      </label>

      <label className="field">
        <span>Vendor description</span>
        <input
          value={formState.vendor_description}
          onChange={(event) => updateField("vendor_description", event.target.value, setFormState)}
        />
      </label>

      <label className="field">
        <span>Canonical name</span>
        <input
          value={formState.canonical_name}
          onChange={(event) => updateField("canonical_name", event.target.value, setFormState)}
        />
      </label>

      <label className="field">
        <span>Category</span>
        <select
          value={formState.category_public_id}
          onChange={(event) => updateField("category_public_id", event.target.value, setFormState)}
        >
          <option value="">None</option>
          {categoryOptions.map((category) => (
            <option key={category.public_id} value={category.public_id}>
              {category.display_name}
            </option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Default storage</span>
        <select
          value={formState.default_storage_location_public_id}
          onChange={(event) =>
            updateField("default_storage_location_public_id", event.target.value, setFormState)
          }
        >
          <option value="">None</option>
          {storageLocationOptions.map((location) => (
            <option key={location.public_id} value={location.public_id}>
              {location.display_name}
            </option>
          ))}
        </select>
      </label>

      <div className="vendor-item-form-grid">
        <TextField label="Purchase unit" name="purchase_unit" state={formState} setState={setFormState} />
        <NumberField label="Pack size" name="pack_size" state={formState} setState={setFormState} />
        <TextField label="Pack unit" name="pack_unit" state={formState} setState={setFormState} />
        <NumberField label="Case quantity" name="case_quantity" state={formState} setState={setFormState} />
        <TextField label="Case unit" name="case_unit" state={formState} setState={setFormState} />
        <NumberField label="Last price" name="last_price" state={formState} setState={setFormState} />
        <label className="field">
          <span>Last price date</span>
          <input
            type="date"
            value={formState.last_price_date}
            onChange={(event) => updateField("last_price_date", event.target.value, setFormState)}
          />
        </label>
        <NumberField label="Estimated price" name="estimated_price" state={formState} setState={setFormState} />
        <TextField label="Price unit" name="price_unit" state={formState} setState={setFormState} />
      </div>

      <label className="field">
        <span>Notes</span>
        <textarea value={formState.notes} onChange={(event) => updateField("notes", event.target.value, setFormState)} />
      </label>

      <div className="editor-actions">
        <button type="button" onClick={handleSave} disabled={!canSave}>
          {saveState === "saving" ? "Saving..." : "Save"}
        </button>
        {item && (
          <button className="secondary-button" type="button" onClick={onCancel}>
            New
          </button>
        )}
      </div>
    </div>
  );
}

function TextField({
  label,
  name,
  state,
  setState,
}: {
  label: string;
  name: keyof VendorItemFormState;
  state: VendorItemFormState;
  setState: Dispatch<SetStateAction<VendorItemFormState>>;
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <input value={state[name]} onChange={(event) => updateField(name, event.target.value, setState)} />
    </label>
  );
}

function NumberField({
  label,
  name,
  state,
  setState,
}: {
  label: string;
  name: keyof VendorItemFormState;
  state: VendorItemFormState;
  setState: Dispatch<SetStateAction<VendorItemFormState>>;
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <input
        min="0"
        step="0.0001"
        type="number"
        value={state[name]}
        onChange={(event) => updateField(name, event.target.value, setState)}
      />
    </label>
  );
}

type VendorItemsTableProps = {
  isGlobal: boolean;
  items: VendorItem[];
  loadState: "idle" | "loading" | "ready" | "error";
  onSelect: (publicId: string) => void;
  onToggleActive: (item: VendorItem) => Promise<VendorItem>;
  selectedPublicId: string;
};

function VendorItemsTable({
  isGlobal,
  items,
  loadState,
  onSelect,
  onToggleActive,
  selectedPublicId,
}: VendorItemsTableProps) {
  return (
    <div className="table-shell setup-table vendor-items-table">
      <table>
        <thead>
          <tr>
            <th>Canonical</th>
            {isGlobal && <th>Vendor</th>}
            <th>Vendor Item</th>
            <th>Category</th>
            <th>Storage</th>
            <th>Package</th>
            <th>Price</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr
              key={item.public_id}
              className={selectedPublicId === item.public_id ? "selected-row" : undefined}
              onClick={() => onSelect(item.public_id)}
            >
              <td>
                <strong>{item.canonical_name}</strong>
              </td>
              {isGlobal && <td>{item.vendor_display_name}</td>}
              <td>
                <div>{item.vendor_description}</div>
                <span className="muted">{item.vendor_item_code || ""}</span>
              </td>
              <td>{item.category_display_name || ""}</td>
              <td>{item.default_storage_location_display_name || ""}</td>
              <td>{formatPackage(item)}</td>
              <td>{formatPrice(item)}</td>
              <td>
                <span className={`status-label ${item.is_active ? "is-success" : "is-danger"}`}>
                  {item.is_active ? "Active" : "Inactive"}
                </span>
              </td>
              <td>
                <button
                  type="button"
                  onClick={(event) => {
                    event.stopPropagation();
                    onToggleActive(item);
                  }}
                >
                  {item.is_active ? "Deactivate" : "Reactivate"}
                </button>
              </td>
            </tr>
          ))}
          {items.length === 0 && (
            <tr>
              <td colSpan={isGlobal ? 9 : 8}>
                {loadState === "loading" ? "Loading vendor items..." : "No vendor items yet."}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

function updateField(
  field: keyof VendorItemFormState,
  value: string,
  setState: Dispatch<SetStateAction<VendorItemFormState>>,
) {
  setState((current) => ({ ...current, [field]: value }));
}

function buildFormState(item: VendorItem): VendorItemFormState {
  return {
    vendor_public_id: item.vendor_public_id,
    vendor_item_code: item.vendor_item_code || "",
    vendor_description: item.vendor_description,
    canonical_name: item.canonical_name,
    category_public_id: item.category_public_id || "",
    default_storage_location_public_id: item.default_storage_location_public_id || "",
    purchase_unit: item.purchase_unit || "",
    pack_size: item.pack_size || "",
    pack_unit: item.pack_unit || "",
    case_quantity: item.case_quantity || "",
    case_unit: item.case_unit || "",
    last_price: item.last_price || "",
    last_price_date: item.last_price_date || "",
    estimated_price: item.estimated_price || "",
    price_unit: item.price_unit || "",
    notes: item.notes || "",
  };
}

function buildPayload(
  formState: VendorItemFormState,
  fixedVendorPublicId: string,
): CreateVendorItemPayload | UpdateVendorItemPayload {
  return {
    vendor_public_id: fixedVendorPublicId || formState.vendor_public_id,
    vendor_item_code: normalizeOptionalText(formState.vendor_item_code),
    vendor_description: formState.vendor_description.trim(),
    canonical_name: formState.canonical_name.trim(),
    category_public_id: normalizeOptionalText(formState.category_public_id),
    default_storage_location_public_id: normalizeOptionalText(formState.default_storage_location_public_id),
    purchase_unit: normalizeOptionalText(formState.purchase_unit),
    pack_size: normalizeOptionalNumber(formState.pack_size),
    pack_unit: normalizeOptionalText(formState.pack_unit),
    case_quantity: normalizeOptionalNumber(formState.case_quantity),
    case_unit: normalizeOptionalText(formState.case_unit),
    last_price: normalizeOptionalNumber(formState.last_price),
    last_price_date: normalizeOptionalText(formState.last_price_date),
    estimated_price: normalizeOptionalNumber(formState.estimated_price),
    price_unit: normalizeOptionalText(formState.price_unit),
    notes: normalizeOptionalText(formState.notes),
  };
}

function buildChangedPayload(
  formState: VendorItemFormState,
  item: VendorItem,
  fixedVendorPublicId: string,
): UpdateVendorItemPayload {
  const baseline = buildFormState(item);
  const fullPayload = buildPayload(formState, fixedVendorPublicId) as UpdateVendorItemPayload;
  const changedPayload: UpdateVendorItemPayload = {};

  for (const field of Object.keys(formState) as Array<keyof VendorItemFormState>) {
    if (formState[field] === baseline[field]) {
      continue;
    }
    const payloadField = field as keyof UpdateVendorItemPayload;
    changedPayload[payloadField] = fullPayload[payloadField] as never;
  }

  return changedPayload;
}

function validateFormState(formState: VendorItemFormState, fixedVendorPublicId: string) {
  if (!(fixedVendorPublicId || formState.vendor_public_id).trim()) {
    return "Vendor is required.";
  }
  if (!formState.vendor_description.trim()) {
    return "Vendor description is required.";
  }
  if (!formState.canonical_name.trim()) {
    return "Canonical name is required.";
  }

  const numericFields: Array<[keyof VendorItemFormState, string]> = [
    ["pack_size", "Pack size"],
    ["case_quantity", "Case quantity"],
    ["last_price", "Last price"],
    ["estimated_price", "Estimated price"],
  ];
  for (const [field, label] of numericFields) {
    const value = formState[field].trim();
    if (value && Number(value) < 0) {
      return `${label} must be non-negative.`;
    }
  }
  return "";
}

function normalizeOptionalText(value: string) {
  return value.trim() || null;
}

function normalizeOptionalNumber(value: string) {
  return value.trim() || null;
}

function formatVendorName(vendor: Vendor) {
  return [vendor.organization_display_name, vendor.vendor_code].filter(Boolean).join(" | ");
}

function mergeSelectedCategory(categories: ItemCategory[], item: VendorItem | null) {
  if (
    !item?.category_public_id ||
    categories.some((category) => category.public_id === item.category_public_id)
  ) {
    return categories;
  }
  return [
    ...categories,
    {
      public_id: item.category_public_id,
      tenant_id: item.tenant_id,
      parent_id: null,
      parent_display_name: null,
      display_name: `${item.category_display_name || "Inactive category"} (inactive)`,
      normalized_name: "",
      is_active: false,
      created_at: item.created_at,
      updated_at: item.updated_at,
    },
  ];
}

function mergeSelectedStorageLocation(storageLocations: StorageLocation[], item: VendorItem | null) {
  if (
    !item?.default_storage_location_public_id ||
    storageLocations.some((location) => location.public_id === item.default_storage_location_public_id)
  ) {
    return storageLocations;
  }
  return [
    ...storageLocations,
    {
      public_id: item.default_storage_location_public_id,
      tenant_id: item.tenant_id,
      display_name: `${item.default_storage_location_display_name || "Inactive storage"} (inactive)`,
      normalized_name: "",
      storage_type: "other" as const,
      is_active: false,
      created_at: item.created_at,
      updated_at: item.updated_at,
    },
  ];
}

function sortVendorItems(items: VendorItem[]) {
  return [...items].sort((first, second) => {
    const canonicalCompare = first.canonical_name.localeCompare(second.canonical_name, undefined, {
      sensitivity: "base",
    });
    if (canonicalCompare !== 0) {
      return canonicalCompare;
    }
    const vendorCompare = first.vendor_display_name.localeCompare(second.vendor_display_name, undefined, {
      sensitivity: "base",
    });
    if (vendorCompare !== 0) {
      return vendorCompare;
    }
    return first.vendor_description.localeCompare(second.vendor_description, undefined, {
      sensitivity: "base",
    });
  });
}

function formatPackage(item: VendorItem) {
  const pack = [item.pack_size, item.pack_unit].filter(Boolean).join(" ");
  const caseQuantity = [item.case_quantity, item.case_unit].filter(Boolean).join(" ");
  return [item.purchase_unit, pack, caseQuantity].filter(Boolean).join(" | ");
}

function formatPrice(item: VendorItem) {
  const confirmedPrice = [item.last_price, item.price_unit].filter(Boolean).join(" / ");
  if (confirmedPrice && item.last_price_date) {
    return `${confirmedPrice} (${item.last_price_date})`;
  }
  return confirmedPrice || (item.estimated_price ? `Est. ${item.estimated_price}` : "");
}
