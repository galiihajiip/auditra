import type { CasePhase } from "../api/client";
import { PHASE_COLOR, PHASE_LABEL } from "../utils/caseLabels";

export default function StatusPill({ status }: { status: CasePhase }) {
  return (
    <span className="status-pill" style={{ color: PHASE_COLOR[status] }}>
      {PHASE_LABEL[status]}
    </span>
  );
}
