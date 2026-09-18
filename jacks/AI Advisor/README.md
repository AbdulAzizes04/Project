# AI Business Advisor: Intelligent Enterprise Analytics Using Machine Learning

AI Business Advisor is a production-ready, full-stack Business Intelligence (BI) platform that enables users to upload business datasets (CSV/Excel) and ask questions in plain English. The application automatically profiles data, identifies segments, trains custom XGBoost machine learning estimators (regression, classification, or time-series forecasting), displays interactive charts, and generates comprehensive PDF business reports.

---

## Key Modules & Features

1. **Authentication**: JWT secure registration, login, and roles.
2. **Dataset Manager Workspace**: Upload CSV/Excel, view data structure, profile column data types (numeric, categorical, datetime), and detect anomalies/duplicates.
3. **Exploratory Data Science (EDA)**: Interactive metric cards, custom Recharts graphs, outlier analysis, and a responsive correlation matrix heatmap.
4. **Model Studio (ML)**: Custom XGBoost pipeline training. Automatically identifies whether target variables require Classification or Regression. Builds lag features for Time-Series forecasting. Includes validation statistics (Accuracy, R², MAE, RMSE), Feature Importance charts, and an **Interactive Prediction Simulator Form** for running real-time inferences.
5. **AI Conversational Agent**: Resolves natural language questions ("Which product generated highest profit?") using a **two-phase execution loop**:
   - **Phase 1**: The LLM parses the user question into a structured JSON query plan.
   - **Phase 2**: Python executes the query spec on the dataset using Pandas.
   - **Phase 3**: The LLM synthesizes the results into a markdown response with strategic business recommendations and renders inline charts inside the chat bubble.
6. **Executive PDF Reports**: Generates styled PDF business packages featuring summaries, stats grids, embedded Python chart images, and ML validation scores.
7. **Robust Fallbacks**: Operates out-of-the-box using local JSON file databases if MongoDB is absent, and rule-based query extraction if LLM API keys are unset.

---

## Technology Stack

- **Frontend**: React (Vite), Tailwind CSS, Framer Motion, Recharts, Lucide Icons, Axios.
- **Backend Server**: Node.js, Express, JWT, Mongoose, Multer, PDFKit.
- **Machine Learning**: Python 3.13, FastAPI, Uvicorn, Pandas, NumPy, Scikit-learn, XGBoost, Statsmodels, Matplotlib, Seaborn.
- **Database**: MongoDB (with fallback file-store).
- **Deployment**: Docker, Nginx (React Router fallback handler).

---

## Directory Structure

```
ai-business-advisor/
├── client/                 # React (Vite) + Tailwind CSS Frontend
├── server/                 # Node.js + Express Backend
├── ml-service/             # Python (FastAPI) Machine Learning Service
├── models/                 # Shared directory storing serialized ML models (.joblib)
├── datasets/               # Shared directory storing uploaded CSV/Excel files
├── reports/                # Shared directory storing temp report charts & PDFs
├── docker-compose.yml      # Docker Multi-Container Configuration
└── README.md               # Setup Guide
```

---

## Setup & Running Instructions

### Option 1: Running Locally (Recommended for Quick Testing)

Ensure Node.js and Python (with venv) are installed on your host system.

#### 1. Setup the Python ML Service
```bash
cd ml-service
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\pip.exe install -r requirements.txt
.\venv\Scripts\uvicorn main:app --reload --port 8000
# On Linux/macOS:
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### 2. Setup the Express Server
```bash
cd server
npm install
npm start
```
*Note: If local MongoDB is not running, the server prints a warning and boots in **Local File Fallback Database** mode automatically, reading/writing to `server/data/db.json`.*

#### 3. Setup the React Client
```bash
cd client
npm install --legacy-peer-deps
npm run dev
```
Open `http://localhost:5173` in your browser. Use the registration tab to create a new user profile!

---

### Option 2: Running with Docker Compose (Production Environment)

With Docker Desktop installed and running, run the following command in the root folder:

```bash
docker-compose up --build
```
This builds and launches four containers:
- **Client (Web)**: Exposed at `http://localhost:3000` (served by Nginx).
- **Server (API)**: Exposed at `http://localhost:5000`.
- **ML Service**: Running on port `8000`.
- **Database**: MongoDB running on port `27017`.

---

## Configuration & Environment Variables

You can customize LLM keys inside `.env` configurations:

- **Express Server (`server/.env`)**:
  - `PORT=5000`
  - `MONGODB_URI=mongodb://localhost:27017/ai_advisor`
  - `ML_SERVICE_URL=http://localhost:8000`
  - `JWT_SECRET=session_signature_secret_key`
  - `GEMINI_API_KEY=` *(Optional: Input Google Gemini API Key)*
  - `OPENAI_API_KEY=` *(Optional: Input OpenAI API Key)*

- **React Client (`client/.env`)**:
  - `VITE_API_URL=http://localhost:5000/api`

---

## Sample Testing Scenario

1. Log in or create a user profile.
2. Navigate to the **Dataset Workspace** tab.
3. Click the drag-and-drop zone and upload the prepared sample dataset file: `datasets/sample_sales.csv`.
4. Navigate to the **Dashboard** to see the interactive correlation matrices, outlier metrics, and bar aggregations.
5. In **Model Studio**, select `Sales` (target) and select other variables as features. Click **Train Model**. Observe accuracy metrics, horizontal feature importances, and try keying in customized attributes to run live inferences.
6. Open **AI Chat Advisor** and enter: *"Which category generated the highest sales?"* or *"Show monthly sales trend."*
7. Open **Report Center** and click **Download Executive Report** to fetch the compiled PDF.
