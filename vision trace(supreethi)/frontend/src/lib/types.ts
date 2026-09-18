export interface IncidentDetails {
  id?: string;
  incident_type: string;
  incident_date: string;
  incident_time: string;
  location: string;
  police_station: string;
  investigator_name: string;
  case_description?: string;
}

export interface Video {
  id: string;
  camera_id: string;
  location?: string;
  filename: string;
  filepath: string;
  duration_seconds: number;
  resolution: string;
  fps: number;
  file_size_mb: number;
  processed: boolean;
}

export interface ReferenceImage {
  id: string;
  image_type: string;
  filename: string;
  filepath: string;
}

export interface GaitProfile {
  id: string;
  track_id: number;
  walking_speed: string;
  stride_pattern: string;
  step_frequency: string;
  arm_swing: string;
  leg_movement: string;
  body_posture: string;
  gait_signature: string;
  cadence_score: number;
  stride_symmetry: number;
  arm_swing_amplitude: number;
  keypoint_summary?: {
    avg_torso_lean_deg?: number;
    arm_swing_norm?: number;
    ankle_span_norm?: number;
  };
}

export interface DetectedPerson {
  id: string;
  track_id: number;
  label: string;
  confidence_score: number;
  similarity_score: number;
  ai_relevance_score: number;
  face_visibility: 'Visible' | 'Masked' | 'Partially Covered' | 'Occluded';
  alternative_pipeline_active: boolean;
  first_seen?: string;
  last_seen?: string;
  total_duration?: string;
  camera_locations: string[];
  appearance_description?: string;
  clothing_upper?: string;
  clothing_lower?: string;
  snapshot_url?: string;
  is_person_of_interest: boolean;
  gait_profile?: GaitProfile;
}

export interface TimelineEvent {
  id: string;
  timestamp: string;
  camera_id: string;
  event_type: string;
  description: string;
  relevance_level: string;
  track_id?: number;
  thumbnail_url?: string;
}

export interface EvidenceItem {
  id: string;
  investigation_id: string;
  title: string;
  category: string;
  timestamp?: string;
  camera_id?: string;
  frame_url?: string;
  clip_url?: string;
  notes?: string;
  created_at: string;
}

export interface Report {
  id: string;
  investigation_id: string;
  report_number: string;
  title: string;
  pdf_path?: string;
  executive_summary?: string;
  ai_findings?: any;
  disclaimer: string;
  created_at: string;
}

export interface ProcessingJob {
  id: string;
  investigation_id: string;
  status: 'QUEUED' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  progress_percentage: number;
  current_step: string;
  logs: string[];
}

export interface Investigation {
  id: string;
  case_id: string;
  title: string;
  status: 'Pending' | 'Processing' | 'Completed' | 'Failed';
  priority: 'Low' | 'Medium' | 'High' | 'Critical';
  created_at: string;
  updated_at: string;
  incident?: IncidentDetails;
  videos: Video[];
  reference_images: ReferenceImage[];
  detected_persons: DetectedPerson[];
  timeline_events: TimelineEvent[];
  evidence_items: EvidenceItem[];
  reports: Report[];
}

export interface DashboardStats {
  active_investigations: number;
  total_videos_processed: number;
  persons_detected: number;
  evidence_items: number;
  reports_generated: number;
  recent_investigations: Array<{
    id: string;
    case_id: string;
    title: string;
    incident_type: string;
    location: string;
    date: string;
    status: string;
    priority: string;
    videos_count: number;
    persons_count: number;
  }>;
}

export interface ANPRPlate {
  plate_number: string;
  vehicle_type: string;
  confidence: number;
  timestamp: string;
  camera_id: string;
  image_url?: string;
}
