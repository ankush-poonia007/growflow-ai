import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { getDeterministicNextAction } from '../utils';

interface DeterministicNextActionProps {
  currentPhase: string;
}

export function DeterministicNextAction({ currentPhase }: DeterministicNextActionProps) {
  const nextAction = getDeterministicNextAction(currentPhase);

  return (
    <Card as="section" className="gf-dashboard__next-action" variant="bordered">
      <CardHeader>
        <span className="gf-dashboard__section-eyebrow">WHAT TO DO NEXT</span>
        <CardTitle as="h3" className="gf-dashboard__section-title">
          {nextAction.action}
        </CardTitle>
      </CardHeader>

      <CardContent>
        <p className="gf-dashboard__next-action-desc">
          {nextAction.description}
        </p>

        <div className="gf-dashboard__guidance-box">
          <span className="gf-dashboard__guidance-title">Phase Guidance</span>
          <p className="gf-dashboard__guidance-text">{nextAction.guidance}</p>
        </div>
      </CardContent>

      <CardFooter className="gf-dashboard__next-action-footer">
        <Button as="link" to="/student/projects" variant="secondary">
          Open Projects Collection →
        </Button>
        <span className="gf-dashboard__deterministic-tag">
          Deterministic Rule • Derived from Phase
        </span>
      </CardFooter>
    </Card>
  );
}
