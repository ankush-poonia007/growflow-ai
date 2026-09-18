import type { ProjectTechnologyItem } from '@/lib/api/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';

interface ProjectTechnologySectionProps {
  technologies?: ProjectTechnologyItem[];
}

export function ProjectTechnologySection({ technologies = [] }: ProjectTechnologySectionProps) {
  if (!technologies || technologies.length === 0) return null;

  return (
    <Card as="section" className="gf-profile-section" variant="bordered" aria-label="Project Technologies">
      <CardHeader className="gf-profile-section__header">
        <CardTitle as="h2" className="gf-profile-section__title">
          Technologies & Tools
        </CardTitle>
        <p className="gf-profile-section__subtitle">
          Technologies linked canonically to this project execution context.
        </p>
      </CardHeader>

      <CardContent className="gf-profile-section__body">
        <div className="gf-profile-tech-grid">
          {technologies.map((tech) => (
            <div key={tech.id} className="gf-profile-tech-card">
              <div className="gf-profile-tech-header">
                <span className="gf-profile-tech-name">{tech.technology_id}</span>
                {tech.category && (
                  <span className="gf-profile-tech-category">{tech.category}</span>
                )}
              </div>
              {tech.purpose && (
                <p className="gf-profile-tech-desc">
                  <strong>Purpose:</strong> {tech.purpose}
                </p>
              )}
              {tech.why_selected && (
                <p className="gf-profile-tech-desc">
                  <strong>Rationale:</strong> {tech.why_selected}
                </p>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
