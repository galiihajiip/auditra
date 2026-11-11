import type { CaseDetail, User } from "../../api/client";

export interface TabProps {
  c: CaseDetail;
  user: User;
  busy: boolean;
  act: (fn: () => Promise<CaseDetail | void>, ok?: string) => Promise<boolean>;
}
