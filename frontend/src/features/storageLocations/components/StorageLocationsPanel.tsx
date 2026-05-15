import { Fragment, useEffect, useMemo, useState } from "react";

import { useStorageLocations } from "../hooks/useStorageLocations";
import type {
  StorageLocation,
  StorageLocationStatusFilter,
  StorageLocationType,
  StorageLocationTypeFilter,
} from "../types";

type StorageLocationsPanelProps = {
  tenantId: string;
  onBackToSetup: () => void;
};

const storageTypeOptions: Array<{ value: StorageLocationType; label: string }> = [
  { value: "cooler", label: "Cooler" },
  { value: "freezer", label: "Freezer" },
  { value: "dry", label: "Dry Storage" },
  { value: "ambient", label: "Ambient" },
  { value: "other", label: "Other" },
];

const storageTypeOrder = storageTypeOptions.map((option) => option.value);

export function StorageLocationsPanel({ tenantId, onBackToSetup }: StorageLocationsPanelProps) {
  const storageLocations = useStorageLocations(tenantId);
  const [selectedPublicId, setSelectedPublicId] = useState("");
  const selectedLocation =
    storageLocations.locations.find((location) => location.public_id === selectedPublicId) || null;
  const groupedLocations = useMemo(
    () => groupStorageLocations(storageLocations.locations),
    [storageLocations.locations],
  );

  useEffect(() => {
    if (
      selectedPublicId &&
      !storageLocations.locations.some((location) => location.public_id === selectedPublicId)
    ) {
      setSelectedPublicId("");
    }
  }, [storageLocations.locations, selectedPublicId]);

  return (
    <section className="panel feature-panel setup-panel setup-module-page" aria-label="Storage locations">
      <div className="setup-module-header">
        <div>
          <button className="link-button" type="button" onClick={onBackToSetup}>
            Back to setup
          </button>
          <p className="eyebrow">Setup module</p>
          <h2>Storage Locations</h2>
          <p className="muted">
            Maintain operational storage areas used for future vendor item and inventory assignment.
          </p>
        </div>
      </div>

      <div className="setup-module-toolbar">
        <div>
          <p className="eyebrow">Results</p>
          <span className="muted">{storageLocations.locations.length} locations</span>
        </div>
        <div className="panel-actions">
          <button type="button" onClick={storageLocations.refreshLocations}>
            Refresh
          </button>
          <select
            value={storageLocations.status}
            onChange={(event) =>
              storageLocations.setStatus(event.target.value as StorageLocationStatusFilter)
            }
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="all">All</option>
          </select>
          <select
            value={storageLocations.storageType}
            onChange={(event) =>
              storageLocations.setStorageType(event.target.value as StorageLocationTypeFilter)
            }
          >
            <option value="all">All storage types</option>
            {storageTypeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {storageLocations.errorMessage && <div className="error-banner">{storageLocations.errorMessage}</div>}

      <div className="setup-grid">
        <section className="setup-form-section" aria-label="Storage location form">
          <StorageLocationForm
            location={selectedLocation}
            onCancel={() => setSelectedPublicId("")}
            onCreate={storageLocations.createNewLocation}
            onSave={storageLocations.saveLocation}
          />
        </section>

        <section className="setup-results-section" aria-label="Storage location results">
          <div className="table-shell setup-table">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {groupedLocations.map((group) => (
                  <Fragment key={group.storageType}>
                    <tr className="storage-group-row">
                      <td colSpan={3}>{formatStorageType(group.storageType)}</td>
                    </tr>
                    {group.locations.map((location) => (
                      <tr
                        key={location.public_id}
                        className={[
                          "storage-location-row",
                          selectedPublicId === location.public_id ? "selected-row" : "",
                        ]
                          .filter(Boolean)
                          .join(" ")}
                        onClick={() => setSelectedPublicId(location.public_id)}
                      >
                        <td>
                          <span className="storage-location-name">{location.display_name}</span>
                        </td>
                        <td>
                          <span className={`status-label ${location.is_active ? "is-success" : "is-danger"}`}>
                            {location.is_active ? "Active" : "Inactive"}
                          </span>
                        </td>
                        <td>
                          <button
                            type="button"
                            onClick={(event) => {
                              event.stopPropagation();
                              storageLocations.toggleLocationActive(location);
                            }}
                          >
                            {location.is_active ? "Deactivate" : "Reactivate"}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </Fragment>
                ))}
                {storageLocations.locations.length === 0 && (
                  <tr>
                    <td colSpan={3}>
                      {storageLocations.loadState === "loading"
                        ? "Loading storage locations..."
                        : "No storage locations yet."}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </section>
  );
}

type StorageLocationFormProps = {
  location: StorageLocation | null;
  onCancel: () => void;
  onCreate: (payload: { display_name: string; storage_type: StorageLocationType }) => Promise<void>;
  onSave: (
    locationPublicId: string,
    payload: { display_name: string; storage_type: StorageLocationType },
  ) => Promise<void>;
};

function StorageLocationForm({
  location,
  onCancel,
  onCreate,
  onSave,
}: StorageLocationFormProps) {
  const [displayName, setDisplayName] = useState("");
  const [storageType, setStorageType] = useState<StorageLocationType>("cooler");
  const [validationMessage, setValidationMessage] = useState("");
  const [saveState, setSaveState] = useState<"idle" | "saving">("idle");

  useEffect(() => {
    setDisplayName(location?.display_name || "");
    setStorageType(location?.storage_type || "cooler");
    setValidationMessage("");
  }, [location]);

  const hasChanges =
    !location ||
    displayName !== location.display_name ||
    storageType !== location.storage_type;
  const canSave = displayName.trim().length > 0 && hasChanges && saveState !== "saving";

  const handleSave = () => {
    if (!displayName.trim()) {
      setValidationMessage("Display name is required.");
      return;
    }

    setValidationMessage("");
    setSaveState("saving");
    const payload = {
      display_name: displayName.trim(),
      storage_type: storageType,
    };
    const request = location ? onSave(location.public_id, payload) : onCreate(payload);
    request
      .then(() => {
        if (!location) {
          setDisplayName("");
          setStorageType("cooler");
        }
      })
      .finally(() => setSaveState("idle"));
  };

  return (
    <div className="setup-form" aria-label={location ? "Edit storage location" : "Create storage location"}>
      <div>
        <p className="eyebrow">{location ? "Edit location" : "New location"}</p>
        <h3>{location?.display_name || "Location details"}</h3>
      </div>

      {validationMessage && <div className="error-banner">{validationMessage}</div>}

      <label className="field">
        <span>Display name</span>
        <input value={displayName} onChange={(event) => setDisplayName(event.target.value)} />
      </label>

      <label className="field">
        <span>Storage type</span>
        <select
          value={storageType}
          onChange={(event) => setStorageType(event.target.value as StorageLocationType)}
        >
          {storageTypeOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <div className="editor-actions">
        <button type="button" onClick={handleSave} disabled={!canSave}>
          {saveState === "saving" ? "Saving..." : "Save"}
        </button>
        {location && (
          <button className="secondary-button" type="button" onClick={onCancel}>
            New
          </button>
        )}
      </div>
    </div>
  );
}

function formatStorageType(storageType: StorageLocationType) {
  return storageTypeOptions.find((option) => option.value === storageType)?.label || "Other";
}

function groupStorageLocations(locations: StorageLocation[]) {
  const locationsByType = new Map<StorageLocationType, StorageLocation[]>();
  locations.forEach((location) => {
    const groupedLocations = locationsByType.get(location.storage_type) || [];
    groupedLocations.push(location);
    locationsByType.set(location.storage_type, groupedLocations);
  });

  return storageTypeOrder
    .map((storageType) => ({
      storageType,
      locations: (locationsByType.get(storageType) || []).sort((first, second) =>
        first.display_name.localeCompare(second.display_name, undefined, { sensitivity: "base" }),
      ),
    }))
    .filter((group) => group.locations.length > 0);
}
