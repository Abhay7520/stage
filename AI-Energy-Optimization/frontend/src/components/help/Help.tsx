import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import { createPortal } from "react-dom";
import { Info, X } from "lucide-react";
import { pageHelp, termHelp } from "./helpContent";
import type { HelpContent } from "./helpContent";
import "./Help.css";
function HelpDialog({
  content,
  onClose,
}: {
  content: HelpContent;
  onClose: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const node = dialog.current;
    if (node && !node.open) node.showModal();
    return () => {
      node?.close();
    };
  }, []);
  return createPortal(
    <dialog
      ref={dialog}
      className="help-dialog"
      aria-labelledby="active-help-title"
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <article className="help-dialog-panel">
        <header>
          <div>
            <span className="eyebrow">HOW TO USE THIS SIMULATION</span>
            <h2 id="active-help-title">{content.title}</h2>
          </div>
          <button
            type="button"
            className="help-close"
            aria-label="Close help"
            onClick={onClose}
            autoFocus
          >
            <X size={20} />
          </button>
        </header>
        <p className="help-summary">{content.summary}</p>
        {content.sections.map((s, i) => (
          <section key={i}>
            <h3>{s.heading}</h3>
            {s.text && <p>{s.text}</p>}
            {s.steps && (
              <ol>
                {s.steps.map((t, j) => (
                  <li key={j}>{t}</li>
                ))}
              </ol>
            )}
          </section>
        ))}
        <button type="button" className="help-done" onClick={onClose}>
          Got it
        </button>
      </article>
    </dialog>,
    document.body,
  );
}
export function InfoButton({
  title,
  content,
  label,
}: {
  title: string;
  content?: HelpContent;
  label?: string;
}) {
  const [open, setOpen] = useState(false);
  const trigger = useRef<HTMLButtonElement>(null);
  function closeHelp() {
    setOpen(false);
    requestAnimationFrame(() => trigger.current?.focus());
  }
  return (
    <>
      <button
        type="button"
        ref={trigger}
        className="info-button"
        aria-label={label || `Help: ${title}`}
        aria-haspopup="dialog"
        title={`Explain ${title}`}
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setOpen(true);
        }}
      >
        <Info size={17} />
      </button>
      {open && (
        <HelpDialog content={content || termHelp(title)} onClose={closeHelp} />
      )}
    </>
  );
}
export function PageHelp({ page }: { page: string }) {
  const content = pageHelp[page];
  return (
    <div className="page-help-toolbar">
      <span>New to this page?</span>
      <InfoButton title={page} label={`About ${page}`} content={content} />
      <span>
        {page === "Dashboard"
          ? "Overall project workflow"
          : "What this page does & how to use it"}
      </span>
    </div>
  );
}
export function Explained({
  title,
  children,
  action = false,
}: {
  title: string;
  children: ReactNode;
  action?: boolean;
}) {
  return (
    <div className={action ? "explained-action" : "explained-field"}>
      {children}
      <InfoButton title={title} />
    </div>
  );
}
export function HelpText({
  title,
  children,
}: {
  title: string;
  children?: ReactNode;
}) {
  return (
    <span className="help-text">
      {children || title}
      <InfoButton title={title} />
    </span>
  );
}
