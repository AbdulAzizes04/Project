import type {
  Company, CompanyDetail, DashboardSummary, TrendPoint, RiskDistribution,
  RiskFactor, NetworkGraph, TDAFeatures, ModelMetrics, PredictionResult,
  DatasetInfo, PredictionInput, NetworkPosition, ContributingFactor, ShapValue,
  CompanyFinancials, LoanInfo, VesselInfo, RiskTimelinePoint, ROCPoint,
  PRPoint, ConfusionMatrix, FeatureImportance,
} from '@/types';

// ============================================================
// HELPERS
// ============================================================
const rand = (min: number, max: number, dec = 2) =>
  parseFloat((Math.random() * (max - min) + min).toFixed(dec));

const randInt = (min: number, max: number) =>
  Math.floor(Math.random() * (max - min + 1)) + min;

const randomChoice = <T>(arr: T[]): T => arr[Math.floor(Math.random() * arr.length)];

const companyNames = [
  'Oceanic Shipping Ltd.', 'Nordic Maritime Corp.', 'Pacific Bulk Carriers',
  'Atlantic Freight Solutions', 'Mediterranean Sea Lines', 'Gulf Marine Partners',
  'Eastern Star Logistics', 'Blue Horizon Tankers', 'Coral Sea Transport',
  'Viking Maritime Group', 'Poseidon Fleet Management', 'Triton Shipping Co.',
  'Harbor Light Industries', 'Mariner Global Corp.', 'SeaPath Ventures',
  'Neptune Cargo Ltd.', 'Thalassa Marine Group', 'Albatross Bulk Lines',
  'Sirocco Tankers Inc.', 'Meridian Ocean Freight', 'Caspian Maritime LLC',
  'Pelagic Ship Holdings', 'Adriatic Bulk Corp.', 'Indus Maritime Services',
  'Baltic Star Lines',
];

const countries = ['Greece', 'Norway', 'Germany', 'Singapore', 'Japan', 'South Korea', 'China', 'USA', 'Denmark', 'UK'];
const segments = ['Bulk Carrier', 'Container Shipping', 'Tanker', 'LNG Carrier', 'Ro-Ro', 'General Cargo'];

const getRiskCategory = (prob: number): 'LOW' | 'MEDIUM' | 'HIGH' => {
  if (prob < 0.35) return 'LOW';
  if (prob < 0.65) return 'MEDIUM';
  return 'HIGH';
};

const getNetworkExposure = (centrality: number): 'LOW' | 'MODERATE' | 'ELEVATED' | 'HIGH' => {
  if (centrality < 0.3) return 'LOW';
  if (centrality < 0.5) return 'MODERATE';
  if (centrality < 0.7) return 'ELEVATED';
  return 'HIGH';
};

// ============================================================
// COMPANIES
// ============================================================
export const mockCompanies: Company[] = companyNames.map((name, i) => {
  const prob = rand(0.08, 0.95);
  const centrality = rand(0.2, 0.9);
  return {
    id: `COMP-${String(i + 1).padStart(4, '0')}`,
    name,
    country: randomChoice(countries),
    segment: randomChoice(segments),
    loanAmount: rand(5, 80, 1) * 1_000_000,
    vesselValue: rand(10, 120, 1) * 1_000_000,
    debtToEquity: rand(1.2, 5.8),
    defaultProbability: prob,
    riskCategory: getRiskCategory(prob),
    networkRisk: getNetworkExposure(centrality),
    fleetSize: randInt(1, 15),
    status: prob > 0.65 ? 'monitoring' : 'active',
    createdAt: new Date(Date.now() - randInt(30, 730) * 86400000).toISOString(),
    updatedAt: new Date(Date.now() - randInt(0, 30) * 86400000).toISOString(),
  };
});

export const getMockCompanyDetail = (id: string): CompanyDetail => {
  const base = mockCompanies.find(c => c.id === id) || mockCompanies[0];

  const financials: CompanyFinancials = {
    revenue: rand(20, 200) * 1_000_000,
    netIncome: rand(2, 30) * 1_000_000,
    totalAssets: rand(50, 400) * 1_000_000,
    totalLiabilities: rand(30, 250) * 1_000_000,
    equity: rand(20, 150) * 1_000_000,
    currentRatio: rand(0.8, 2.5),
    quickRatio: rand(0.6, 2.0),
    interestCoverageRatio: rand(1.2, 5.0),
    returnOnAssets: rand(2, 12),
    returnOnEquity: rand(5, 25),
  };

  const loan: LoanInfo = {
    loanId: `LOAN-${base.id}`,
    amount: base.loanAmount,
    interestRate: rand(3.5, 9.5),
    termMonths: randomChoice([36, 48, 60, 84, 120]),
    outstandingAmount: base.loanAmount * rand(0.4, 0.9),
    disbursementDate: new Date(Date.now() - randInt(180, 1000) * 86400000).toISOString().split('T')[0],
    maturityDate: new Date(Date.now() + randInt(365, 1825) * 86400000).toISOString().split('T')[0],
    loanType: randomChoice(['Term Loan', 'Revolving Credit', 'Ship Mortgage', 'Bridge Loan']),
    collateralValue: base.vesselValue,
    ltvRatio: base.loanAmount / base.vesselValue,
  };

  const vessels: VesselInfo[] = Array.from({ length: base.fleetSize > 0 ? base.fleetSize : 1 }).map((_, i) => ({
    id: `VES-${base.id}-${i + 1}`,
    name: `MV ${base.name.split(' ')[0]} ${String.fromCharCode(65 + i)}`,
    type: base.segment as VesselInfo['type'],
    age: randInt(1, 25),
    value: rand(5, 50) * 1_000_000,
    utilization: rand(0.55, 0.98),
    flag: randomChoice(['Panama', 'Marshall Islands', 'Liberia', 'Bahamas', 'Malta']),
    dwt: randInt(10000, 200000),
  }));

  const networkPosition: NetworkPosition = {
    centrality: rand(0.2, 0.9),
    degree: randInt(3, 20),
    betweenness: rand(0.05, 0.45),
    closeness: rand(0.3, 0.8),
    clusteringCoefficient: rand(0.3, 0.9),
    connectedCompanies: randInt(4, 22),
    networkExposure: base.networkRisk,
  };

  const tdaFeatures: TDAFeatures = {
    bettiNumbers: { b0: randInt(1, 4), b1: randInt(0, 5), b2: randInt(0, 2) },
    persistentHomology: {
      h0: Array.from({ length: 8 }).map(() => ({ birth: rand(0, 1), death: rand(1, 3), dimension: 0, persistence: rand(0.5, 2.5) })),
      h1: Array.from({ length: 5 }).map(() => ({ birth: rand(0.5, 2), death: rand(2, 4), dimension: 1, persistence: rand(0.3, 2.0) })),
      h2: Array.from({ length: 2 }).map(() => ({ birth: rand(1, 3), death: rand(3, 5), dimension: 2, persistence: rand(0.2, 1.5) })),
    },
    totalPersistence: rand(5, 20),
    averagePersistence: rand(1, 4),
    maxPersistence: rand(3, 8),
    topologicalComplexity: rand(0.4, 0.9),
    connectedComponents: randInt(1, 4),
    cycles: randInt(0, 5),
    voids: randInt(0, 2),
    wasserstein: rand(0.5, 3),
    bottleneck: rand(0.3, 2),
  };

  const riskTimeline: RiskTimelinePoint[] = Array.from({ length: 12 }).map((_, i) => {
    const prob = Math.max(0.05, Math.min(0.99, base.defaultProbability + rand(-0.15, 0.15)));
    return {
      date: new Date(Date.now() - (11 - i) * 30 * 86400000).toISOString().split('T')[0],
      probability: prob,
      category: getRiskCategory(prob),
    };
  });

  return {
    ...base,
    financials,
    loan,
    vessels,
    networkPosition,
    tdaFeatures,
    predictionHistory: [],
    riskTimeline,
  };
};

// ============================================================
// DASHBOARD
// ============================================================
export const mockDashboardSummary: DashboardSummary = {
  totalCompanies: 1248,
  loansAssessed: 3842,
  highRiskCompanies: 186,
  avgDefaultProbability: 27.4,
  modelAccuracy: 92.6,
  networkRiskAlerts: 74,
  changes: {
    totalCompanies: 3.2,
    loansAssessed: 8.7,
    highRiskCompanies: -2.1,
    avgDefaultProbability: -0.8,
  },
};

const generateTrendData = (days: number): TrendPoint[] => {
  let prob = 0.28;
  return Array.from({ length: days }).map((_, i) => {
    prob = Math.max(0.10, Math.min(0.60, prob + rand(-0.03, 0.03)));
    return {
      date: new Date(Date.now() - (days - 1 - i) * 86400000).toISOString().split('T')[0],
      probability: parseFloat((prob * 100).toFixed(1)),
      volume: randInt(20, 120),
    };
  });
};

export const mockTrendData: Record<string, TrendPoint[]> = {
  '7d':  generateTrendData(7),
  '30d': generateTrendData(30),
  '90d': generateTrendData(90),
  '1y':  generateTrendData(365),
};

export const mockRiskDistribution: RiskDistribution = {
  low: 642,
  medium: 420,
  high: 186,
  total: 1248,
};

export const mockRiskFactors: RiskFactor[] = [
  { name: 'Debt-to-Equity Ratio', contribution: 82, rank: 1 },
  { name: 'Vessel Age', contribution: 68, rank: 2 },
  { name: 'Interest Rate', contribution: 61, rank: 3 },
  { name: 'Vessel Value', contribution: 48, rank: 4 },
  { name: 'Freight Market Index', contribution: 43, rank: 5 },
  { name: 'Loan Amount', contribution: 37, rank: 6 },
  { name: 'Economic Growth Rate', contribution: 31, rank: 7 },
  { name: 'Network Centrality', contribution: 26, rank: 8 },
];

// ============================================================
// NETWORK
// ============================================================
export const generateMockNetwork = (): NetworkGraph => {
  const nodes = mockCompanies.slice(0, 20).map(c => ({
    id: c.id,
    name: c.name,
    riskCategory: c.riskCategory,
    defaultProbability: c.defaultProbability,
    centrality: rand(0.2, 0.9),
    degree: randInt(2, 10),
    x: rand(50, 750),
    y: rand(50, 550),
  }));

  const edges = [];
  for (let i = 0; i < 35; i++) {
    const src = randomChoice(nodes);
    const tgt = randomChoice(nodes.filter(n => n.id !== src.id));
    edges.push({
      source: src.id,
      target: tgt.id,
      weight: rand(0.2, 0.95),
      type: randomChoice(['financial', 'correlation', 'contractual'] as const),
    });
  }

  return {
    nodes,
    edges,
    metadata: {
      totalNodes: nodes.length,
      totalEdges: edges.length,
      avgCentrality: 0.54,
      density: 0.18,
    },
  };
};

export const mockNetworkGraph = generateMockNetwork();

// ============================================================
// TDA ANALYSIS (page-level)
// ============================================================
export const generateMockTDA = (): TDAFeatures => ({
  bettiNumbers: { b0: 3, b1: 4, b2: 1 },
  persistentHomology: {
    h0: Array.from({ length: 12 }).map(() => ({ birth: rand(0, 0.5), death: rand(0.5, 2.5), dimension: 0, persistence: rand(0.3, 2.0) })),
    h1: Array.from({ length: 8 }).map(() => ({ birth: rand(0.3, 1.5), death: rand(1.5, 4.0), dimension: 1, persistence: rand(0.5, 2.5) })),
    h2: Array.from({ length: 3 }).map(() => ({ birth: rand(1, 2.5), death: rand(2.5, 5.0), dimension: 2, persistence: rand(0.3, 2.0) })),
  },
  totalPersistence: 14.7,
  averagePersistence: 2.3,
  maxPersistence: 6.8,
  topologicalComplexity: 0.74,
  connectedComponents: 3,
  cycles: 4,
  voids: 1,
  wasserstein: 1.85,
  bottleneck: 1.24,
});

// ============================================================
// MODELS
// ============================================================
export const mockModelMetrics: ModelMetrics[] = [
  { model: 'logistic_regression', modelName: 'Logistic Regression', accuracy: 0.831, precision: 0.814, recall: 0.798, f1Score: 0.806, rocAuc: 0.874, aucPr: 0.842, trainingTime: 0.4, parameters: 24 },
  { model: 'svm', modelName: 'Support Vector Machine', accuracy: 0.857, precision: 0.841, recall: 0.823, f1Score: 0.832, rocAuc: 0.898, aucPr: 0.869, trainingTime: 12.3, parameters: 0 },
  { model: 'xgboost', modelName: 'XGBoost', accuracy: 0.913, precision: 0.897, recall: 0.882, f1Score: 0.889, rocAuc: 0.951, aucPr: 0.934, trainingTime: 45.2, parameters: 240000 },
  { model: 'gnn', modelName: 'Graph Neural Network', accuracy: 0.926, precision: 0.918, recall: 0.901, f1Score: 0.909, rocAuc: 0.967, aucPr: 0.952, trainingTime: 284.6, parameters: 1820000 },
];

export const generateROCCurve = (): ROCPoint[] => {
  const pts: ROCPoint[] = [{ fpr: 0, tpr: 0 }];
  let fpr = 0; let tpr = 0;
  for (let i = 1; i <= 20; i++) {
    fpr = Math.min(1, fpr + rand(0.02, 0.07));
    tpr = Math.min(1, tpr + rand(0.05, 0.12));
    pts.push({ fpr: parseFloat(fpr.toFixed(3)), tpr: parseFloat(tpr.toFixed(3)) });
  }
  pts.push({ fpr: 1, tpr: 1 });
  return pts;
};

export const generatePRCurve = (): PRPoint[] => {
  return Array.from({ length: 20 }).map((_, i) => {
    const recall = i / 19;
    const precision = Math.max(0.5, 0.98 - recall * 0.4 + rand(-0.03, 0.03));
    return { precision: parseFloat(precision.toFixed(3)), recall: parseFloat(recall.toFixed(3)) };
  });
};

export const mockConfusionMatrix: ConfusionMatrix = { tn: 412, fp: 38, fn: 52, tp: 298 };

export const mockFeatureImportance: FeatureImportance[] = [
  { feature: 'Debt-to-Equity Ratio', importance: 0.187, rank: 1 },
  { feature: 'Network Centrality', importance: 0.142, rank: 2 },
  { feature: 'Vessel Age', importance: 0.128, rank: 3 },
  { feature: 'Loan Amount', importance: 0.114, rank: 4 },
  { feature: 'Interest Rate', importance: 0.098, rank: 5 },
  { feature: 'TDA Topology Score', importance: 0.087, rank: 6 },
  { feature: 'Freight Rate Index', importance: 0.076, rank: 7 },
  { feature: 'Vessel Value', importance: 0.068, rank: 8 },
  { feature: 'Clustering Coefficient', importance: 0.054, rank: 9 },
  { feature: 'Economic Growth', importance: 0.046, rank: 10 },
];

// ============================================================
// PREDICTION
// ============================================================
export const generatePredictionResult = (input: PredictionInput): PredictionResult => {
  // Simple heuristic scoring (frontend mock)
  let score = 0;
  score += Math.min(1, input.debtToEquityRatio / 6) * 0.25;
  score += Math.min(1, input.vesselAge / 30) * 0.15;
  score += Math.min(1, (input.loanAmount / Math.max(1, input.vesselValue))) * 0.15;
  score += (1 - Math.min(1, input.avgUtilization)) * 0.1;
  score += Math.min(1, input.interestRate / 12) * 0.1;
  score += (1 - Math.min(1, input.freightRate / 2000)) * 0.1;
  score += Math.min(1, input.networkCentrality) * 0.15;
  const prob = Math.max(0.05, Math.min(0.97, score + rand(-0.05, 0.05)));

  const factors: ContributingFactor[] = [
    { name: 'Debt-to-Equity Ratio', value: input.debtToEquityRatio, impact: input.debtToEquityRatio > 3 ? 'HIGH' : 'MEDIUM', direction: 'positive', contribution: Math.min(40, input.debtToEquityRatio * 6) },
    { name: 'Vessel Age', value: `${input.vesselAge} years`, impact: input.vesselAge > 15 ? 'HIGH' : 'MEDIUM', direction: 'positive', contribution: Math.min(30, input.vesselAge * 1.5) },
    { name: 'Interest Rate', value: `${input.interestRate}%`, impact: input.interestRate > 6 ? 'HIGH' : 'MEDIUM', direction: 'positive', contribution: Math.min(25, input.interestRate * 3) },
    { name: 'Vessel Utilization', value: `${(input.avgUtilization * 100).toFixed(0)}%`, impact: input.avgUtilization < 0.7 ? 'MEDIUM' : 'LOW', direction: input.avgUtilization > 0.8 ? 'negative' : 'positive', contribution: Math.min(20, (1 - input.avgUtilization) * 30) },
    { name: 'Freight Market Rate', value: `$${input.freightRate}`, impact: input.freightRate < 800 ? 'HIGH' : 'LOW', direction: input.freightRate > 1000 ? 'negative' : 'positive', contribution: Math.min(20, (2000 - input.freightRate) / 100) },
    { name: 'Network Centrality', value: input.networkCentrality.toFixed(2), impact: input.networkCentrality > 0.6 ? 'HIGH' : 'MEDIUM', direction: 'positive', contribution: Math.min(25, input.networkCentrality * 30) },
  ];

  const shapValues: ShapValue[] = factors.map(f => ({
    feature: f.name,
    value: typeof f.value === 'number' ? f.value : parseFloat(String(f.value)),
    shapValue: parseFloat(((f.direction === 'positive' ? 1 : -1) * f.contribution / 100 * prob).toFixed(4)),
    direction: f.direction === 'positive' ? 'increases' : 'decreases',
  }));

  return {
    id: `PRED-${Date.now()}`,
    companyName: input.companyName,
    defaultProbability: prob,
    riskCategory: getRiskCategory(prob),
    confidence: rand(0.82, 0.97),
    modelUsed: 'gnn',
    timestamp: new Date().toISOString(),
    contributingFactors: factors,
    networkRisk: {
      centrality: input.networkCentrality,
      degree: input.connectedCompanies,
      betweenness: rand(0.1, 0.5),
      closeness: rand(0.3, 0.8),
      clusteringCoefficient: input.clusteringCoefficient,
      connectedCompanies: input.connectedCompanies,
      networkExposure: input.networkExposure,
    },
    shapValues,
  };
};

// ============================================================
// PREDICTION HISTORY
// ============================================================
export const mockPredictionHistory = Array.from({ length: 45 }).map((_, i) => {
  const prob = rand(0.08, 0.95);
  const company = randomChoice(mockCompanies);
  return {
    id: `PRED-${String(i + 1).padStart(5, '0')}`,
    date: new Date(Date.now() - randInt(0, 180) * 86400000).toISOString(),
    companyName: company.name,
    companyId: company.id,
    defaultProbability: prob,
    riskCategory: getRiskCategory(prob),
    modelUsed: randomChoice(['logistic_regression', 'svm', 'xgboost', 'gnn'] as const),
    status: randomChoice(['completed', 'completed', 'completed', 'pending'] as const),
    confidence: rand(0.80, 0.97),
    analyst: 'Maritime Risk Team',
  };
}).sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

// ============================================================
// DATA MANAGEMENT
// ============================================================
export const mockDatasets: DatasetInfo[] = [
  {
    id: 'DS-001',
    filename: 'maritime_loan_data_2024.csv',
    rows: 3842,
    columns: 47,
    missingValues: 124,
    numericalFeatures: 38,
    categoricalFeatures: 9,
    uploadedAt: new Date(Date.now() - 5 * 86400000).toISOString(),
    status: 'ready',
    preview: Array.from({ length: 5 }).map((_, i) => ({
      company_id: `COMP-${String(i + 1).padStart(4, '0')}`,
      loan_amount: rand(5, 80) * 1_000_000,
      vessel_age: randInt(1, 25),
      default: i === 0 ? 1 : 0,
    })),
  },
];
