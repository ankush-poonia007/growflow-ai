import { useEffect, useState } from 'react';
import { getAdminAIKeys } from '@/lib/api/client';
import type { AdminAIKeysResponse } from '@/lib/api/types';
import { PageHeader } from '@/components/ui/PageHeader';
import { StatTile } from '@/components/ui/StatTile';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { AISubNav } from '@/components/navigation/AISubNav';
import './AIKeyPool.css';

/**
 * AD18 — API Key Pool Monitoring
 *
 * Security-sensitive monitoring instrument verifying configured environment key slots,
 * in-memory rotation posture, and strictly redacted credential identifiers.
 */
export function AIKeyPool() {
  const [data, setData] = useState<AdminAIKeysResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchKeys = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAdminAIKeys();
      setData(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve API key pool data.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKeys();
  }, []);

  const slots = data?.slots || [];
  const configuredCount = data?.configured_key_count ?? 0;
  const totalSlots = data?.total_slots ?? 5;

  return (
    <div className="gf-ai-keys">
      <PageHeader
        eyebrow="CREDENTIAL & POOL GOVERNANCE"
        title="API Key Pool Monitoring"
        description="Operational status and in-memory rotation posture for upstream OpenRouter provider key slots."
        actions={
          <Button variant="secondary" size="sm" onClick={fetchKeys}>
            Refresh
          </Button>
        }
      />

      <AISubNav />

      {error && (
        <div className="gf-ai-keys__alert" role="alert">
          <span>{error}</span>
          <Button variant="tertiary" size="sm" onClick={fetchKeys}>
            Retry
          </Button>
        </div>
      )}

      {/* Security & In-Memory Rotation Notice */}
      <section className="gf-ai-keys__notice-banner" aria-label="Security Notice">
        <div className="gf-ai-keys__notice-header">
          <div className="gf-ai-keys__notice-pills">
            <span className="gf-ai-keys__pill gf-ai-keys__pill--primary">
              ROTATION: {data?.rotation_mechanism || 'In-Memory Round-Robin'}
            </span>
            <span className="gf-ai-keys__pill gf-ai-keys__pill--neutral">
              LIFESPAN: {data?.rotation_runtime_state || 'RUNTIME_IN_MEMORY'}
            </span>
            <span className="gf-ai-keys__pill gf-ai-keys__pill--success">
              CREDENTIAL SECRETS REDACTED
            </span>
          </div>
        </div>
        <p className="gf-ai-keys__notice-text">
          {data?.security_notice ||
            'Raw API keys, authorization headers, and environment secrets are strictly redacted. Key rotation is managed in-memory across configured environment slots. Individual key rate-limit, cooldown, and historical health telemetry is not persisted in the current gateway.'}
        </p>
      </section>

      {/* Pool Capacity KPIs */}
      <section className="gf-ai-keys__kpi-grid" aria-label="Key Pool KPIs">
        {loading ? (
          <>
            <Skeleton height="110px" />
            <Skeleton height="110px" />
            <Skeleton height="110px" />
            <Skeleton height="110px" />
          </>
        ) : (
          <>
            <StatTile
              label="Configured Slots"
              value={`${configuredCount} of ${totalSlots}`}
              subtext={configuredCount > 0 ? 'Active in round-robin rotation' : 'No credentials configured'}
            />
            <StatTile
              label="Provider Vendor"
              value={data?.provider || 'OpenRouter'}
              subtext="Upstream AI provider gateway"
            />
            <StatTile
              label="Rotation Lifecycle"
              value={data?.rotation_runtime_state || 'RUNTIME_IN_MEMORY'}
              subtext="In-memory round-robin pointer"
            />
            <StatTile
              label="Historical Telemetry"
              value="NOT PERSISTED"
              subtext="Rate limits & cooldowns unmetered"
            />
          </>
        )}
      </section>

      {/* Key Slot Inventory Cards */}
      <section className="gf-ai-keys__section" aria-label="Configured Slot Inventory">
        <div className="gf-ai-keys__section-head">
          <h2 className="gf-ai-keys__section-title">OpenRouter Environment Slots</h2>
          <span className="gf-ai-keys__subtext">
            Server-side environment key slots mapped to OpenRouter provider gateway
          </span>
        </div>

        {loading ? (
          <div className="gf-ai-keys__slots-grid">
            <Skeleton height="160px" />
            <Skeleton height="160px" />
            <Skeleton height="160px" />
            <Skeleton height="160px" />
            <Skeleton height="160px" />
          </div>
        ) : (
          <div className="gf-ai-keys__slots-grid">
            {slots.map((slot) => {
              const isConfigured = slot.status === 'CONFIGURED';
              return (
                <Card
                  key={slot.slot_index}
                  className={`gf-ai-keys__slot-card ${
                    isConfigured ? 'gf-ai-keys__slot-card--configured' : 'gf-ai-keys__slot-card--empty'
                  }`}
                >
                  <CardHeader className="gf-ai-keys__slot-header">
                    <div>
                      <span className="gf-ai-keys__slot-index">Slot {slot.slot_index}</span>
                      <CardTitle className="gf-ai-keys__slot-title">{slot.slot_label}</CardTitle>
                    </div>
                    <Badge variant={isConfigured ? 'success' : 'neutral'}>
                      {slot.status}
                    </Badge>
                  </CardHeader>
                  <CardContent className="gf-ai-keys__slot-content">
                    <div className="gf-ai-keys__slot-field">
                      <span className="gf-ai-keys__slot-field-label">Environment Variable</span>
                      <span className="gf-ai-keys__slot-mono">{slot.env_var_name}</span>
                    </div>

                    <div className="gf-ai-keys__slot-field">
                      <span className="gf-ai-keys__slot-field-label">Masked Identifier</span>
                      <span className="gf-ai-keys__slot-mono gf-ai-keys__slot-mono--masked">
                        {slot.masked_identifier || 'Unconfigured (Slot Empty)'}
                      </span>
                    </div>

                    <div className="gf-ai-keys__slot-field">
                      <span className="gf-ai-keys__slot-field-label">Rotation Posture</span>
                      <span className="gf-ai-keys__slot-posture">
                        {slot.rotation_posture}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </section>

      {/* Gateway Configuration Reference */}
      <section className="gf-ai-keys__section" aria-label="Gateway Reference">
        <Card>
          <CardHeader>
            <CardTitle>Gateway Technical Parameters</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="gf-ai-keys__params-grid">
              <div className="gf-ai-keys__param-item">
                <span className="gf-ai-keys__param-label">Gateway API Endpoint</span>
                <span className="gf-ai-keys__param-val gf-ai-keys__slot-mono">
                  {data?.gateway_base_url || 'https://openrouter.ai/api/v1'}
                </span>
              </div>
              <div className="gf-ai-keys__param-item">
                <span className="gf-ai-keys__param-label">Key Pool Failover Mechanism</span>
                <span className="gf-ai-keys__param-val">Sequential In-Memory Round-Robin</span>
              </div>
              <div className="gf-ai-keys__param-item">
                <span className="gf-ai-keys__param-label">Rate-Limit Handling</span>
                <span className="gf-ai-keys__param-val">Runtime Next-Slot Advance</span>
              </div>
              <div className="gf-ai-keys__param-item">
                <span className="gf-ai-keys__param-label">Telemetry Persistence</span>
                <span className="gf-ai-keys__param-val">None (Ephemerally logged in runtime)</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
