// ============================================================
// CORE ENUMS
// ============================================================

export type RiskCategory = 'LOW' | 'MEDIUM' | 'HIGH';
export type RiskLevel = 'low' | 'medium' | 'high';
export type NetworkExposure = 'LOW' | 'MODERATE' | 'ELEVATED' | 'HIGH';
export type ModelType = 'logistic_regression' | 'svm' | 'xgboost' | 'gnn';
export type VesselType = 'Bulk Carrier' | 'Container Ship' | 'Tanker' | 'General Cargo' | 'LNG Carrier' | 'Ro-Ro';
export type PredictionStatus = 'completed' | 'pending' | 'failed';

// ============================================================
// USER / AUTH
// ============================================================

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'analyst' | 'viewer';
  avatar?: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// ============================================================
// COMPANY
// ============================================================

export interface Company {
  id: string;
  name: string;
  country: string;
  segment: string;
  loanAmount: number;
  vesselValue: number;
  debtToEquity: number;
  defaultProbability: number;
  riskCategory: RiskCategory;
  networkRisk: NetworkExposure;
  fleetSize: number;
  status: 'active' | 'monitoring' | 'default';
  createdAt: string;
  updatedAt: string;
}

export interface CompanyDetail extends Company {
  financials: CompanyFinancials;
  loan: LoanInfo;
  vessels: VesselInfo[];
  networkPosition: NetworkPosition;
  tdaFeatures: TDAFeatures;
  predictionHistory: PredictionResult[];
  riskTimeline: RiskTimelinePoint[];
}

export interface CompanyFinancials {
  revenue: number;
  netIncome: number;
  totalAssets: number;
  totalLiabilities: number;
  equity: number;
  currentRatio: number;
  quickRatio: number;
  interestCoverageRatio: number;
  returnOnAssets: number;
  returnOnEquity: number;
}

export interface LoanInfo {
  loanId: string;
  amount: number;
  interestRate: number;
  termMonths: number;
  outstandingAmount: number;
  disbursementDate: string;
  maturityDate: string;
  loanType: string;
  collateralValue: number;
  ltvRatio: number;
}

export interface VesselInfo {
  id: string;
  name: string;
  type: VesselType;
  age: number;
  value: number;
  utilization: number;
  flag: string;
  dwt: number;
}

export interface RiskTimelinePoint {
  date: string;
  probability: number;
  category: RiskCategory;
}

// ============================================================
// NETWORK
// ============================================================

export interface NetworkNode {
  id: string;
  name: string;
  riskCategory: RiskCategory;
  defaultProbability: number;
  centrality: number;
  degree: number;
  x?: number;
  y?: number;
}

export interface NetworkEdge {
  source: string;
  target: string;
  weight: number;
  type: 'financial' | 'correlation' | 'contractual';
}

export interface NetworkGraph {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  metadata: {
    totalNodes: number;
    totalEdges: number;
    avgCentrality: number;
    density: number;
  };
}

export interface NetworkPosition {
  centrality: number;
  degree: number;
  betweenness: number;
  closeness: number;
  clusteringCoefficient: number;
  connectedCompanies: number;
  networkExposure: NetworkExposure;
}

// ============================================================
// TDA
// ============================================================

export interface PersistencePair {
  birth: number;
  death: number;
  dimension: 0 | 1 | 2;
  persistence: number;
}

export interface TDAFeatures {
  bettiNumbers: { b0: number; b1: number; b2: number };
  persistentHomology: {
    h0: PersistencePair[];
    h1: PersistencePair[];
    h2: PersistencePair[];
  };
  totalPersistence: number;
  averagePersistence: number;
  maxPersistence: number;
  topologicalComplexity: number;
  connectedComponents: number;
  cycles: number;
  voids: number;
  wasserstein: number;
  bottleneck: number;
}

// ============================================================
// PREDICTION
// ============================================================

export interface PredictionInput {
  // Company
  companyName: string;
  companyId?: string;
  segment: string;
  country: string;

  // Loan
  loanAmount: number;
  interestRate: number;
  loanTermMonths: number;
  outstandingAmount: number;
  debtToEquityRatio: number;

  // Vessel
  vesselAge: number;
  vesselValue: number;
  fleetSize: number;
  vesselType: VesselType;
  avgUtilization: number;

  // Market
  freightRate: number;
  marketIndex: number;
  fuelPrice: number;
  economicGrowth: number;
  inflation: number;
  interestRateEnvironment: number;

  // Network
  networkCentrality: number;
  clusteringCoefficient: number;
  connectedCompanies: number;
  networkExposure: NetworkExposure;
}

export interface PredictionResult {
  id: string;
  companyName: string;
  defaultProbability: number;
  riskCategory: RiskCategory;
  confidence: number;
  modelUsed: ModelType;
  timestamp: string;
  contributingFactors: ContributingFactor[];
  networkRisk: NetworkPosition;
  shapValues?: ShapValue[];
}

export interface ContributingFactor {
  name: string;
  value: number | string;
  impact: 'HIGH' | 'MEDIUM' | 'LOW';
  direction: 'positive' | 'negative';
  contribution: number; // % contribution to risk
}

export interface ShapValue {
  feature: string;
  value: number;
  shapValue: number;
  direction: 'increases' | 'decreases';
}

// ============================================================
// MODEL PERFORMANCE
// ============================================================

export interface ModelMetrics {
  model: ModelType;
  modelName: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  rocAuc: number;
  aucPr: number;
  trainingTime: number;
  parameters: number;
}

export interface ROCPoint { fpr: number; tpr: number; }
export interface PRPoint { precision: number; recall: number; }
export interface ConfusionMatrix {
  tn: number; fp: number;
  fn: number; tp: number;
}

export interface FeatureImportance {
  feature: string;
  importance: number;
  rank: number;
}

// ============================================================
// DASHBOARD
// ============================================================

export interface DashboardSummary {
  totalCompanies: number;
  loansAssessed: number;
  highRiskCompanies: number;
  avgDefaultProbability: number;
  modelAccuracy: number;
  networkRiskAlerts: number;
  changes: {
    totalCompanies: number;
    loansAssessed: number;
    highRiskCompanies: number;
    avgDefaultProbability: number;
  };
}

export interface TrendPoint {
  date: string;
  probability: number;
  volume: number;
}

export interface RiskDistribution {
  low: number;
  medium: number;
  high: number;
  total: number;
}

export interface RiskFactor {
  name: string;
  contribution: number;
  rank: number;
}

// ============================================================
// DATA MANAGEMENT
// ============================================================

export interface DatasetInfo {
  id: string;
  filename: string;
  rows: number;
  columns: number;
  missingValues: number;
  numericalFeatures: number;
  categoricalFeatures: number;
  uploadedAt: string;
  status: 'uploaded' | 'validating' | 'cleaning' | 'processing' | 'ready' | 'error';
  preview?: Record<string, string | number | boolean>[];
}

// ============================================================
// COMMON
// ============================================================

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ApiError {
  message: string;
  code?: string;
  status?: number;
}
