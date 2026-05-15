import { useEffect, useMemo, useState } from "react";

import { useItemCategories } from "../hooks/useItemCategories";
import type { ItemCategory, ItemCategoryStatusFilter } from "../types";

type ItemCategoriesPanelProps = {
  tenantId: string;
  onBackToSetup: () => void;
};

export function ItemCategoriesPanel({ tenantId, onBackToSetup }: ItemCategoriesPanelProps) {
  const itemCategories = useItemCategories(tenantId);
  const [selectedPublicId, setSelectedPublicId] = useState("");
  const selectedCategory =
    itemCategories.categories.find((category) => category.public_id === selectedPublicId) || null;
  const hierarchicalCategories = useMemo(
    () => buildHierarchicalCategoryRows(itemCategories.categories),
    [itemCategories.categories],
  );

  useEffect(() => {
    if (
      selectedPublicId &&
      !itemCategories.categories.some((category) => category.public_id === selectedPublicId)
    ) {
      setSelectedPublicId("");
    }
  }, [itemCategories.categories, selectedPublicId]);

  return (
    <section className="panel feature-panel setup-panel setup-module-page" aria-label="Item categories">
      <div className="setup-module-header">
        <div>
          <button className="link-button" type="button" onClick={onBackToSetup}>
            Back to setup
          </button>
          <p className="eyebrow">Setup module</p>
          <h2>Item Categories</h2>
          <p className="muted">
            Maintain category records used for vendor item grouping, reporting, and classification.
          </p>
        </div>
      </div>

      <div className="setup-module-toolbar">
        <div>
          <p className="eyebrow">Results</p>
          <span className="muted">{itemCategories.categories.length} categories</span>
        </div>
        <div className="panel-actions">
          <button type="button" onClick={itemCategories.refreshCategories}>
            Refresh
          </button>
          <select
            value={itemCategories.status}
            onChange={(event) =>
              itemCategories.setStatus(event.target.value as ItemCategoryStatusFilter)
            }
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="all">All</option>
          </select>
        </div>
      </div>

      {itemCategories.errorMessage && <div className="error-banner">{itemCategories.errorMessage}</div>}

      <div className="setup-grid">
        <section className="setup-form-section" aria-label="Item category form">
          <ItemCategoryForm
            category={selectedCategory}
            categories={itemCategories.parentOptions}
            onCancel={() => setSelectedPublicId("")}
            onCreate={itemCategories.createNewCategory}
            onSave={itemCategories.saveCategory}
          />
        </section>

        <section className="setup-results-section" aria-label="Item category results">
          <div className="table-shell setup-table">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Parent</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {hierarchicalCategories.map((category) => (
                  <tr
                    key={category.public_id}
                    className={[
                      category.parent_id ? "category-child-row" : "category-parent-row",
                      selectedPublicId === category.public_id ? "selected-row" : "",
                    ]
                      .filter(Boolean)
                      .join(" ")}
                    onClick={() => setSelectedPublicId(category.public_id)}
                  >
                    <td>
                      <span className="category-name-cell">{category.display_name}</span>
                    </td>
                    <td>{category.parent_display_name || "Top level"}</td>
                    <td>
                      <span className={`status-label ${category.is_active ? "is-success" : "is-danger"}`}>
                        {category.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td>
                      <button
                        type="button"
                        onClick={(event) => {
                          event.stopPropagation();
                          itemCategories.toggleCategoryActive(category);
                        }}
                      >
                        {category.is_active ? "Deactivate" : "Reactivate"}
                      </button>
                    </td>
                  </tr>
                ))}
                {itemCategories.categories.length === 0 && (
                  <tr>
                    <td colSpan={4}>
                      {itemCategories.loadState === "loading"
                        ? "Loading item categories..."
                        : "No item categories yet."}
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

type ItemCategoryFormProps = {
  category: ItemCategory | null;
  categories: ItemCategory[];
  onCancel: () => void;
  onCreate: (payload: { display_name: string; parent_id: string | null }) => Promise<void>;
  onSave: (
    categoryPublicId: string,
    payload: { display_name: string; parent_id: string | null },
  ) => Promise<void>;
};

function ItemCategoryForm({
  category,
  categories,
  onCancel,
  onCreate,
  onSave,
}: ItemCategoryFormProps) {
  const [displayName, setDisplayName] = useState("");
  const [parentId, setParentId] = useState("");
  const [validationMessage, setValidationMessage] = useState("");
  const [saveState, setSaveState] = useState<"idle" | "saving">("idle");

  useEffect(() => {
    setDisplayName(category?.display_name || "");
    setParentId(category?.parent_id || "");
    setValidationMessage("");
  }, [category]);

  const availableParents = useMemo(
    () =>
      categories.filter(
        (candidate) => candidate.public_id !== category?.public_id && candidate.parent_id === null,
      ),
    [categories, category?.public_id],
  );

  const hasChanges =
    !category ||
    displayName !== category.display_name ||
    parentId !== (category.parent_id || "");
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
      parent_id: parentId || null,
    };
    const request = category ? onSave(category.public_id, payload) : onCreate(payload);
    request
      .then(() => {
        if (!category) {
          setDisplayName("");
          setParentId("");
        }
      })
      .finally(() => setSaveState("idle"));
  };

  return (
    <div className="setup-form" aria-label={category ? "Edit item category" : "Create item category"}>
      <div>
        <p className="eyebrow">{category ? "Edit category" : "New category"}</p>
        <h3>{category?.display_name || "Category details"}</h3>
      </div>

      {validationMessage && <div className="error-banner">{validationMessage}</div>}

      <label className="field">
        <span>Display name</span>
        <input value={displayName} onChange={(event) => setDisplayName(event.target.value)} />
      </label>

      <label className="field">
        <span>Parent category</span>
        <select value={parentId} onChange={(event) => setParentId(event.target.value)}>
          <option value="">Top level</option>
          {availableParents.map((parentCategory) => (
            <option key={parentCategory.public_id} value={parentCategory.public_id}>
              {parentCategory.display_name}
            </option>
          ))}
        </select>
      </label>

      <div className="editor-actions">
        <button type="button" onClick={handleSave} disabled={!canSave}>
          {saveState === "saving" ? "Saving..." : "Save"}
        </button>
        {category && (
          <button className="secondary-button" type="button" onClick={onCancel}>
            New
          </button>
        )}
      </div>
    </div>
  );
}

function buildHierarchicalCategoryRows(categories: ItemCategory[]) {
  const alphabetically = (first: ItemCategory, second: ItemCategory) =>
    first.display_name.localeCompare(second.display_name, undefined, { sensitivity: "base" });
  const parents = categories.filter((category) => category.parent_id === null).sort(alphabetically);
  const children = categories.filter((category) => category.parent_id !== null).sort(alphabetically);
  const childrenByParentId = new Map<string, ItemCategory[]>();
  children.forEach((category) => {
    if (!category.parent_id) {
      return;
    }
    const groupedChildren = childrenByParentId.get(category.parent_id) || [];
    groupedChildren.push(category);
    childrenByParentId.set(category.parent_id, groupedChildren);
  });

  const rows: ItemCategory[] = [];
  const includedChildren = new Set<string>();
  parents.forEach((parent) => {
    rows.push(parent);
    const parentChildren = childrenByParentId.get(parent.public_id) || [];
    rows.push(...parentChildren);
    parentChildren.forEach((child) => includedChildren.add(child.public_id));
  });

  children
    .filter((child) => !includedChildren.has(child.public_id))
    .forEach((child) => rows.push(child));
  return rows;
}
