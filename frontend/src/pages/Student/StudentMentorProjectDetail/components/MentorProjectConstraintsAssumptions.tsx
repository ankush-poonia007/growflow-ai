import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';

interface MentorProjectConstraintsAssumptionsProps {
  constraints?: string | null;
  assumptions?: string | null;
}

export function MentorProjectConstraintsAssumptions({
  constraints,
  assumptions,
}: MentorProjectConstraintsAssumptionsProps) {
  const trimmedConstraints = constraints?.trim();
  const trimmedAssumptions = assumptions?.trim();

  return (
    <div className="gf-detail-dual-grid">
      {/* Constraints */}
      <Card as="section" className="gf-detail-section" variant="bordered" aria-labelledby="section-constraints-title">
        <CardHeader className="gf-detail-section__header">
          <CardTitle as="h2" id="section-constraints-title" className="gf-detail-section__title">
            Project Constraints
          </CardTitle>
        </CardHeader>
        <CardContent className="gf-detail-section__content">
          {trimmedConstraints ? (
            <p className="gf-detail-block__text">{trimmedConstraints}</p>
          ) : (
            <p className="gf-detail-block__empty">No specific constraints provided</p>
          )}
        </CardContent>
      </Card>

      {/* Assumptions */}
      <Card as="section" className="gf-detail-section" variant="bordered" aria-labelledby="section-assumptions-title">
        <CardHeader className="gf-detail-section__header">
          <CardTitle as="h2" id="section-assumptions-title" className="gf-detail-section__title">
            Assumptions &amp; Prerequisites
          </CardTitle>
        </CardHeader>
        <CardContent className="gf-detail-section__content">
          {trimmedAssumptions ? (
            <p className="gf-detail-block__text">{trimmedAssumptions}</p>
          ) : (
            <p className="gf-detail-block__empty">No specific assumptions provided</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
