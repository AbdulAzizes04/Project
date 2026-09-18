import { CheckCircle, Loader, Clock } from 'lucide-react';

const STEPS = [
  'Extracting video frames',
  'Detecting persons',
  'Tracking individuals',
  'Person re-identification',
  'Gait analysis',
  'Multi-modal score fusion',
  'Generating evidence timeline',
];

export default function ProcessingPipeline({ status }) {
  if (!status) return null;

  const { current_step, total_steps, progress, message, status: st } = status;
  const progressPct = Math.round((progress || 0) * 100);

  return (
    <div className="forensic-card animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <h3 style={{ fontSize: 14, fontWeight: 700, color: '#00d4ff' }}>
          AI PIPELINE PROCESSING
        </h3>
        {st === 'completed' ? (
          <span className="badge-high" style={{ padding: '3px 10px', borderRadius: 20, fontSize: 11, fontWeight: 700 }}>
            ✓ COMPLETE
          </span>
        ) : st === 'error' ? (
          <span className="badge-low" style={{ padding: '3px 10px', borderRadius: 20, fontSize: 11, fontWeight: 700 }}>
            ✗ ERROR
          </span>
        ) : (
          <span style={{ fontSize: 12, color: '#94a3b8' }}>
            STEP {current_step}/{total_steps}
          </span>
        )}
      </div>

      {/* Overall progress bar */}
      <div className="progress-bar mb-2" style={{ height: 6 }}>
        <div
          className="progress-fill"
          style={{ width: `${st === 'completed' ? 100 : progressPct}%` }}
        />
      </div>
      <div className="flex justify-between mb-4" style={{ fontSize: 11, color: '#4a5568' }}>
        <span>{message}</span>
        <span>{st === 'completed' ? 100 : progressPct}%</span>
      </div>

      {/* Step list */}
      <div className="space-y-2">
        {STEPS.map((step, i) => {
          const stepNum = i + 1;
          let state = 'pending';
          if (st === 'completed') state = 'done';
          else if (stepNum < current_step) state = 'done';
          else if (stepNum === current_step) state = 'active';

          return (
            <div key={step} className="flex items-center gap-3" style={{ opacity: state === 'pending' ? 0.35 : 1 }}>
              {state === 'done' ? (
                <CheckCircle size={16} color="#00ff88" />
              ) : state === 'active' ? (
                <Loader size={16} color="#00d4ff" style={{ animation: 'spin 1s linear infinite' }} />
              ) : (
                <Clock size={16} color="#4a5568" />
              )}
              <span style={{
                fontSize: 12,
                color: state === 'active' ? '#00d4ff' : state === 'done' ? '#e2e8f0' : '#4a5568',
                fontWeight: state === 'active' ? 600 : 400,
              }}>
                STEP {stepNum}/{STEPS.length} — {step}
              </span>
            </div>
          );
        })}
      </div>

      {st === 'error' && (
        <div
          className="mt-4 p-3 rounded-lg"
          style={{ background: '#ff444415', border: '1px solid #ff444433', fontSize: 12, color: '#ff4444' }}
        >
          ⚠️ {message}
        </div>
      )}
    </div>
  );
}
