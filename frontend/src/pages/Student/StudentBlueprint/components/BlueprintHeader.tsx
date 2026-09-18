import { Link } from 'react-router';
import { Badge } from '@/components/ui/Badge';
import type { BlueprintStatus, BlueprintQAStatus } from '@/lib/api/types';

interface BlueprintHeaderProps {
  projectId: string;
  projectTitle: string;
  status: BlueprintStatus;
  qaStatus?: BlueprintQAStatus;
}

export function BlueprintHeader({
  projectId,
  projectTitle,
  status,
  qaStatus,
}: BlueprintHeaderProps) {
  const getStatusBadge = () => {
    switch (status) {
      case 'APPROVED':
        return <Badge variant="success" dot>Stage 3 Approved</Badge>;
      case 'READY_FOR_APPROVAL':
      case 'COMPLETED':
      case 'GENERATED':
        if (qaStatus === 'PASSED' || (qaStatus as string) === 'PASS') {
          return <Badge variant="success" dot>QA Passed • Ready for Approval</Badge>;
        }
        if (qaStatus === 'FAILED' || (qaStatus as string) === 'FAIL') {
          return <Badge variant="danger" dot>QA Failed • Revisions Needed</Badge>;
        }
        return <Badge variant="warning" dot>Under QA Evaluation</Badge>;
      case 'QA_REJECTED':
        return <Badge variant="danger" dot>QA Rejected • Revisions Needed</Badge>;
      case 'VALIDATING':
        return <Badge variant="info" dot>QA Evaluation Active...</Badge>;
      case 'GENERATING':
        return <Badge variant="info" dot>Synthesizing Blueprint...</Badge>;
      case 'FAILED':
        return <Badge variant="danger" dot>Synthesis Halted</Badge>;
      case 'NOT_STARTED':
      default:
        return <Badge variant="neutral" dot>Stage 3: Blueprint</Badge>;
    }
  };

  return (
    <header className="gf-blueprint-header">
      <div className="gf-blueprint-header__top">
        <Link
          to={`/student/projects/${projectId}/profile`}
          className="gf-blueprint-header__back"
          aria-label="Back to project profile"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            width="16"
            height="16"
            aria-hidden="true"
          >
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          <span>Back to Project Profile</span>
        </Link>
        <div className="gf-blueprint-header__status">{getStatusBadge()}</div>
      </div>

      <div className="gf-blueprint-header__main">
        <div className="gf-blueprint-header__meta">
          <span className="gf-blueprint-header__eyebrow">STAGE 3 WORKFLOW</span>
          <h1 className="gf-blueprint-header__title">{projectTitle}</h1>
          <p className="gf-blueprint-header__subtitle">
            Autonomous synthesis of your complete technical blueprint, specifications, work breakdown, and QA evaluation.
          </p>
        </div>
      </div>
    </header>
  );
}
