import {
  Investigation,
  DashboardStats,
  DetectedPerson,
  ProcessingJob,
  EvidenceItem,
  TimelineEvent,
  Report,
  ANPRPlate
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export async function fetchDashboardStats(): Promise<DashboardStats> {
  try {
    const res = await fetch(`${API_BASE}/api/investigations/dashboard-stats`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch stats');
    return await res.json();
  } catch (err) {
    console.warn('[API] fetchDashboardStats fallback:', err);
    return {
      active_investigations: 3,
      total_videos_processed: 14,
      persons_detected: 48,
      evidence_items: 26,
      reports_generated: 7,
      recent_investigations: [
        {
          id: "demo-01",
          case_id: "CASE-2026-089",
          title: "Armed Jewelry Vault Heist & Perimeter Breach",
          incident_type: "Robbery",
          location: "Grand Metropolitan Exchange, Vault Sector 4",
          date: "2026-09-08",
          status: "Completed",
          priority: "Critical",
          videos_count: 3,
          persons_count: 2
        },
        {
          id: "demo-02",
          case_id: "CASE-2026-074",
          title: "Downtown Metro Station Suspicious Package Incident",
          incident_type: "Suspicious Activity",
          location: "Platform 3 East Wing",
          date: "2026-09-07",
          status: "Completed",
          priority: "High",
          videos_count: 4,
          persons_count: 6
        },
        {
          id: "demo-03",
          case_id: "CASE-2026-092",
          title: "North Commercial Logistics Vehicle Theft",
          incident_type: "Vehicle Crime",
          location: "Terminal Cargo Bay 12",
          date: "2026-09-08",
          status: "Processing",
          priority: "Medium",
          videos_count: 2,
          persons_count: 1
        }
      ]
    };
  }
}

export async function fetchInvestigations(): Promise<Investigation[]> {
  try {
    const res = await fetch(`${API_BASE}/api/investigations`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch investigations');
    return await res.json();
  } catch (err) {
    console.warn('[API] fetchInvestigations fallback:', err);
    return [];
  }
}

export async function fetchInvestigationById(id: string): Promise<Investigation | null> {
  try {
    const res = await fetch(`${API_BASE}/api/investigations/${id}`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch investigation');
    return await res.json();
  } catch (err) {
    console.warn('[API] fetchInvestigationById fallback:', err);
    return null;
  }
}

export async function createInvestigation(payload: {
  case_id: string;
  title: string;
  priority: string;
  incident: any;
}): Promise<Investigation> {
  const res = await fetch(`${API_BASE}/api/investigations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || 'Failed to create investigation');
  }
  return await res.json();
}

export async function uploadVideo(formData: FormData): Promise<any> {
  const res = await fetch(`${API_BASE}/api/videos/upload`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) throw new Error('Failed to upload video');
  return await res.json();
}

export async function uploadReferenceImage(formData: FormData): Promise<any> {
  const res = await fetch(`${API_BASE}/api/videos/reference-image/upload`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) throw new Error('Failed to upload reference image');
  return await res.json();
}

export async function startAnalysis(investigationId: string): Promise<ProcessingJob> {
  const res = await fetch(`${API_BASE}/api/analysis/start/${investigationId}`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to start analysis');
  return await res.json();
}

export async function fetchLatestJob(investigationId: string): Promise<ProcessingJob | null> {
  try {
    const res = await fetch(`${API_BASE}/api/analysis/investigation/${investigationId}/latest-job`, { cache: 'no-store' });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    return null;
  }
}

export async function fetchPersons(investigationId: string): Promise<DetectedPerson[]> {
  try {
    const res = await fetch(`${API_BASE}/api/persons/investigation/${investigationId}`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch persons');
    return await res.json();
  } catch (err) {
    return [];
  }
}

export async function fetchTimeline(investigationId: string): Promise<TimelineEvent[]> {
  try {
    const res = await fetch(`${API_BASE}/api/timeline/${investigationId}`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch timeline');
    return await res.json();
  } catch (err) {
    return [];
  }
}

export async function seedDemoCase(): Promise<any> {
  const res = await fetch(`${API_BASE}/api/investigations/seed-demo`, { method: 'POST' });
  return await res.json();
}

export async function searchSurveillance(query: string, investigationId?: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/search/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, investigation_id: investigationId })
  });
  return await res.json();
}

export async function fetchANPRDetections(): Promise<ANPRPlate[]> {
  try {
    const res = await fetch(`${API_BASE}/api/anpr/detections`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch ANPR');
    return await res.json();
  } catch (err) {
    return [];
  }
}

export async function generateReport(investigationId: string): Promise<Report> {
  const res = await fetch(`${API_BASE}/api/reports/generate/${investigationId}`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to generate report');
  return await res.json();
}
