import type { ProjectDefinitionCatalogItem } from '@/lib/api/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';

interface MentorProjectTechnologyProps {
  technologies: ProjectDefinitionCatalogItem['technology_snapshot'];
}

export function MentorProjectTechnology({ technologies }: MentorProjectTechnologyProps) {
  const hasTechnologies = Array.isArray(technologies) && technologies.length > 0;

  return (
    <Card as="section" className="gf-detail-section" variant="bordered" aria-labelledby="section-tech-title">
      <CardHeader className="gf-detail-section__header">
        <CardTitle as="h2" id="section-tech-title" className="gf-detail-section__title">
          Technology Snapshot
        </CardTitle>
      </CardHeader>

      <CardContent className="gf-detail-section__content">
        {hasTechnologies ? (
          <div className="gf-detail-tech-grid" aria-label="Suggested technologies">
            {technologies.map((tech, index) => {
              const name =
                typeof tech === 'string'
                  ? tech
                  : String(tech?.name || tech?.title || 'Unspecified Technology');
              const version =
                typeof tech === 'object' && tech && 'version' in tech ? String(tech.version) : null;
              const category =
                typeof tech === 'object' && tech && 'category' in tech ? String(tech.category) : null;
              const purpose =
                typeof tech === 'object' && tech && 'purpose' in tech ? String(tech.purpose) : null;

              return (
                <div key={`${name}-${index}`} className="gf-detail-tech-badge">
                  <div className="gf-detail-tech-badge__main">
                    <span className="gf-detail-tech-badge__name">{name}</span>
                    {version && <span className="gf-detail-tech-badge__version">v{version}</span>}
                  </div>
                  {category && <span className="gf-detail-tech-badge__category">{category}</span>}
                  {purpose && <p className="gf-detail-tech-badge__purpose">{purpose}</p>}
                </div>
              );
            })}
          </div>
        ) : (
          <p className="gf-detail-block__empty">No specific technologies pre-selected by mentor.</p>
        )}
      </CardContent>
    </Card>
  );
}
