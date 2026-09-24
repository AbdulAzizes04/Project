# Enhanced TDA-Based Machine Learning Approach for Maritime Loan Default Prediction

An AI-powered maritime financial risk intelligence platform designed for evaluating shipping company loan default risk using Topological Data Analysis (TDA), Graph Neural Networks (GNN), and financial feature modeling.

---

## 🚀 Quick Start Guide (For Evaluators / Reviewers)

### 1. Prerequisites
Make sure you have **Node.js** (v18 or higher) installed on your computer.
- Check with: `node -v`
- Download if needed: [https://nodejs.org/](https://nodejs.org/)

---

### 2. How to Install Dependencies & Run

In modern JavaScript/React web projects, dependencies are managed via **`package.json`** (the Node.js equivalent of Python's `requirements.txt`).

Open your terminal, navigate to the `frontend` folder, and run:

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install all required packages (defined in package.json)
npm install

# 3. Start the local development server
npm run dev
```

Once started, open your browser at:
👉 **`http://localhost:5173`**

---

## 🔑 Demo Login Credentials

The system includes pre-filled demo credentials on the login screen:
* **Email:** `admin@maritimerisks.com`
* **Password:** `maritime2026`

---

## 📊 Will Reviewers See All Data If I Share a Zip?

**YES, 100%!**

* All data (50+ shipping companies, fleet characteristics, loan portfolios, topological persistence diagrams, Betti barcodes, network contagion graphs, and ML model benchmark metrics) is **self-contained** inside `src/services/mock/mockData.ts`.
* The application runs in simulated mock mode (`VITE_USE_MOCK=true`) out of the box.
* **No backend, database, or Python installation is required** for evaluators to test and experience the full application.

---

## 📦 How to Create a Clean Zip File to Share

> ⚠️ **IMPORTANT TIP BEFORE ZIPPING:**
> **Do NOT include the `node_modules` folder** in your zip file!
> 
> * With `node_modules`: ~350 MB (slow to upload/email)
> * Without `node_modules`: **~5 MB** (instant to send)
>
> When the receiver unzips the folder, they simply run `npm install` inside the `frontend` folder to automatically download all dependencies.

---

## 🛠 Technology Stack

* **Frontend Framework:** React 18 with TypeScript
* **Build System:** Vite
* **Styling:** Tailwind CSS (Custom Maritime Enterprise Design System)
* **Visualizations:** Recharts & Interactive SVG (Contagion Graph, Persistence Homology)
* **Form & Validation:** React Hook Form + Zod
* **Icons & Animation:** Lucide React & Framer Motion
