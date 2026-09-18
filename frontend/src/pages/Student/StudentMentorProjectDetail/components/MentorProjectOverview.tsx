import type { ProjectDefinitionCatalogItem } from '@/lib/api/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';

interface MentorProjectOverviewProps {
  definition: ProjectDefinitionCatalogItem;
}

export function MentorProjectOverview({ definition }: MentorProjectOverviewProps) {
  return (
    <Card as="section" className="gf-detail-section" variant="bordered" aria-labelledby="section-overview-title">
      <CardHeader className="gf-detail-section__header">
        <CardTitle as="h2" id="section-overview-title" className="gf-detail-section__title">
          Project Overview &amp; Brief
        </CardTitle>
      </CardHeader>

      <CardContent className="gf-detail-section__content">
        {/* Core Problem Statement */}
        <div className="gf-detail-block">
          <h3 className="gf-detail-block__heading">Core Problem</h3>
          {definition.problem ? (
            <p className="gf-detail-block__text">{definition.problem}</p>
          ) : (
            <p className="gf-detail-block__empty">No problem statement provided.</p>
          )}
        </div>

        {/* Proposed Solution Direction */}
        <div className="gf-detail-block">
          <h3 className="gf-detail-block__heading">Proposed Solution Direction</h3>
          {definition.proposed_solution ? (
            <p className="gf-detail-block__text">{definition.proposed_solution}</p>
          ) : (
            <p className="gf-detail-block__empty">No proposed solution direction provided.</p>
          )}
        </div>

        {/* Detailed Description */}
        <div className="gf-detail-block">
          <h3 className="gf-detail-block__heading">Detailed Brief</h3>
          {definition.description ? (
            <p className="gf-detail-block__text">{definition.description}</p>
          ) : (
            <p className="gf-detail-block__empty">No detailed brief provided.</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
