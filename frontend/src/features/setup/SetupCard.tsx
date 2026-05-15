type SetupCardProps = {
  title: string;
  description: string;
  actionLabel: string;
  disabled?: boolean;
  onOpen?: () => void;
};

export function SetupCard({
  title,
  description,
  actionLabel,
  disabled = false,
  onOpen,
}: SetupCardProps) {
  return (
    <article className={disabled ? "setup-card is-disabled" : "setup-card"}>
      <div>
        <h3>{title}</h3>
        <p className="muted">{description}</p>
      </div>
      <button
        className={disabled ? "secondary-button" : undefined}
        type="button"
        disabled={disabled}
        onClick={onOpen}
      >
        {actionLabel}
      </button>
    </article>
  );
}
