import { SetupCard } from "./SetupCard";

type SetupHomeProps = {
  onOpenItemCategories: () => void;
  onOpenStorageLocations: () => void;
};

export function SetupHome({ onOpenItemCategories, onOpenStorageLocations }: SetupHomeProps) {
  return (
    <section className="panel feature-panel setup-home" aria-label="Setup home">
      <div className="setup-page-header">
        <div>
          <p className="eyebrow">Setup</p>
          <h2>Supporting Tables</h2>
        </div>
        <p className="muted">
          Manage configuration records that support daily operations without becoming daily workspaces.
        </p>
      </div>

      <div className="setup-card-grid">
        <SetupCard
          title="Item Categories"
          description="Organize vendor items for search, reporting, inventory grouping, and AI-assisted classification."
          actionLabel="Manage"
          onOpen={onOpenItemCategories}
        />
        <SetupCard
          title="Storage Locations"
          description="Manage operational storage areas and default storage assignments."
          actionLabel="Manage"
          onOpen={onOpenStorageLocations}
        />
      </div>
    </section>
  );
}
