"""
Generate Synthetic Thyroid Dataset — 1200 samples, realistic clinical distributions
"""
import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)
N = 1200
DATASETS_DIR = Path(__file__).resolve().parent.parent / "datasets"
DATASETS_DIR.mkdir(parents=True, exist_ok=True)

# ── Class distribution ─────────────────────────────────────────────────────────
# 0=Healthy, 1=Hypothyroidism, 2=Hyperthyroidism, 3=Thyroid Nodules
labels = np.random.choice([0, 1, 2, 3], N, p=[0.35, 0.30, 0.20, 0.15])

def noisy(arr, std):
    return arr + np.random.normal(0, std, len(arr))

data = {}

# Age
data['age'] = noisy(
    np.where(labels == 0, np.random.uniform(20, 55, N),
    np.where(labels == 1, np.random.uniform(35, 70, N),
    np.where(labels == 2, np.random.uniform(25, 60, N),
             np.random.uniform(40, 75, N)))), 5
).clip(18, 90).astype(int)

# Gender (1=male, 0=female) — thyroid diseases more in females
data['gender_enc'] = np.where(labels == 0,
    np.random.choice([0, 1], N, p=[0.5, 0.5]),
    np.random.choice([0, 1], N, p=[0.75, 0.25])
)

# Weight
base_weight = np.where(data['gender_enc'] == 1, 75, 62)
weight_offset = np.where(labels == 1, 5, np.where(labels == 2, -5, 0))
data['weight'] = noisy(base_weight + weight_offset, 10).clip(40, 150)

# Height
data['height'] = noisy(np.where(data['gender_enc'] == 1, 172, 160), 8).clip(140, 200)

# BMI
data['bmi'] = (data['weight'] / ((data['height'] / 100) ** 2)).round(2)

# Pulse rate
pulse_offset = np.where(labels == 2, 20, np.where(labels == 1, -5, 0))
data['pulse_rate'] = noisy(75 + pulse_offset, 10).clip(45, 130).astype(int)

# ── Symptoms ───────────────────────────────────────────────────────────────────
def symptom_prob(cond_probs):
    # cond_probs: dict {condition_label: probability}
    p = np.zeros(N)
    for cond, prob in cond_probs.items():
        p = np.where(labels == cond, prob, p)
    return (np.random.uniform(0, 1, N) < p).astype(int)

data['fatigue']               = symptom_prob({0: 0.10, 1: 0.85, 2: 0.30, 3: 0.50})
data['weight_gain']           = symptom_prob({0: 0.05, 1: 0.78, 2: 0.05, 3: 0.20})
data['weight_loss']           = symptom_prob({0: 0.05, 1: 0.05, 2: 0.82, 3: 0.15})
data['hair_loss']             = symptom_prob({0: 0.10, 1: 0.70, 2: 0.20, 3: 0.25})
data['constipation']          = symptom_prob({0: 0.08, 1: 0.72, 2: 0.05, 3: 0.15})
data['anxiety']               = symptom_prob({0: 0.12, 1: 0.20, 2: 0.80, 3: 0.25})
data['depression']            = symptom_prob({0: 0.10, 1: 0.65, 2: 0.15, 3: 0.30})
data['sweating']              = symptom_prob({0: 0.08, 1: 0.10, 2: 0.78, 3: 0.15})
data['neck_swelling']         = symptom_prob({0: 0.05, 1: 0.25, 2: 0.20, 3: 0.88})
data['voice_changes']         = symptom_prob({0: 0.03, 1: 0.15, 2: 0.10, 3: 0.65})
data['cold_intolerance']      = symptom_prob({0: 0.08, 1: 0.80, 2: 0.05, 3: 0.15})
data['heat_intolerance']      = symptom_prob({0: 0.06, 1: 0.05, 2: 0.82, 3: 0.10})
data['difficulty_swallowing'] = symptom_prob({0: 0.03, 1: 0.10, 2: 0.08, 3: 0.78})
data['sleep_disturbance']     = symptom_prob({0: 0.12, 1: 0.55, 2: 0.70, 3: 0.40})

# ── Hormone Values ─────────────────────────────────────────────────────────────
# TSH: Normal 0.4-4.5 | Hypo: >4.5 | Hyper: <0.4
data['tsh'] = noisy(
    np.where(labels == 0, np.random.uniform(0.5, 4.0, N),
    np.where(labels == 1, np.random.uniform(5.0, 20.0, N),
    np.where(labels == 2, np.random.uniform(0.01, 0.35, N),
             np.random.uniform(0.5, 5.5, N)))), 0.5
).clip(0.001, 40)

# T3: Normal 0.8-2.0 nmol/L
data['t3'] = noisy(
    np.where(labels == 0, np.random.uniform(0.9, 1.8, N),
    np.where(labels == 1, np.random.uniform(0.4, 0.9, N),
    np.where(labels == 2, np.random.uniform(2.2, 4.5, N),
             np.random.uniform(1.0, 2.5, N)))), 0.2
).clip(0.1, 6)

# T4: Normal 60-120 nmol/L
data['t4'] = noisy(
    np.where(labels == 0, np.random.uniform(65, 115, N),
    np.where(labels == 1, np.random.uniform(30, 60, N),
    np.where(labels == 2, np.random.uniform(125, 200, N),
             np.random.uniform(80, 140, N)))), 10
).clip(10, 250)

# FT3: Normal 2.3-6.3 pmol/L
data['ft3'] = noisy(
    np.where(labels == 0, np.random.uniform(2.5, 5.5, N),
    np.where(labels == 1, np.random.uniform(1.0, 2.2, N),
    np.where(labels == 2, np.random.uniform(6.5, 12.0, N),
             np.random.uniform(2.5, 6.5, N)))), 0.5
).clip(0.5, 15)

# FT4: Normal 0.7-1.8 ng/dL
data['ft4'] = noisy(
    np.where(labels == 0, np.random.uniform(0.8, 1.7, N),
    np.where(labels == 1, np.random.uniform(0.3, 0.75, N),
    np.where(labels == 2, np.random.uniform(1.9, 3.5, N),
             np.random.uniform(0.9, 2.0, N)))), 0.15
).clip(0.1, 5)

# ── Blood Tests ────────────────────────────────────────────────────────────────
data['hemoglobin'] = noisy(
    np.where(data['gender_enc'] == 1, 14.5, 13.0), 1.5
).clip(8, 18)

data['wbc'] = noisy(7.0 * np.ones(N), 1.5).clip(3, 15)
data['rbc'] = noisy(4.7 * np.ones(N), 0.5).clip(3, 7)
data['platelets'] = noisy(250 * np.ones(N), 50).clip(100, 500)

# Hypothyroid often has low Vitamin D
data['vitamin_d'] = noisy(
    np.where(labels == 1, np.random.uniform(10, 25, N), np.random.uniform(25, 60, N)), 5
).clip(5, 100)

data['calcium'] = noisy(9.5 * np.ones(N), 0.7).clip(7, 12)

# ── Medical History ────────────────────────────────────────────────────────────
data['diabetes']       = symptom_prob({0: 0.08, 1: 0.20, 2: 0.10, 3: 0.15})
data['hypertension']   = symptom_prob({0: 0.15, 1: 0.30, 2: 0.25, 3: 0.25})
data['family_history'] = symptom_prob({0: 0.10, 1: 0.45, 2: 0.40, 3: 0.50})
data['smoking']        = symptom_prob({0: 0.20, 1: 0.18, 2: 0.22, 3: 0.25})
data['alcohol']        = symptom_prob({0: 0.15, 1: 0.12, 2: 0.18, 3: 0.15})

data['label'] = labels

df = pd.DataFrame(data)
out_path = DATASETS_DIR / "thyroid_dataset.csv"
df.to_csv(out_path, index=False)
print(f"[Dataset] Generated {len(df)} samples -> {out_path}")
print(df['label'].value_counts().rename({0:'Healthy',1:'Hypothyroidism',2:'Hyperthyroidism',3:'Thyroid Nodules'}))
