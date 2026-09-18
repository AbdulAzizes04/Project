# ⚡ AI SQL Assistant & Analytics Dashboard

Production-ready, modular AI SQL Assistant built using **Streamlit**, **Pandas**, **SQLite**, **SQLGlot**, **LangChain**, **ChromaDB**, and **Plotly**.

---

## 🌟 Key Features

1. **No Authentication Required**: Instantly open the app and analyze data.
2. **Flexible File Upload**: Supports **CSV** and **Excel (.xlsx, .xls)** datasets.
3. **Automated SQLite Conversion**: Automatically cleans schemas, normalizes column identifiers, and builds a temporary SQLite database.
4. **Schema & Metadata Inspection**: Automatically detects table names, column lists, and data types.
5. **AI-Powered Text-to-SQL**: Uses **LangChain** with **Google Gemini 2.5 / OpenAI GPT** (or built-in Rule-Based Fallback Engine).
6. **RAG Vector Search**: **ChromaDB** schema vector database to enrich LLM prompts with semantic column context.
7. **AST SQL Validation**: **SQLGlot** ensures queries are strictly read-only `SELECT` statements (intercepting `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`).
8. **Interactive Visualizations**: **Plotly** auto-recommends optimal charts (Bar, Line, Donut, Scatter, Pie).
9. **Modern KPI Cards**: Auto-calculates totals, averages, maximums, and record counts.
10. **Multi-Format Data Export**: Export results instantly to **CSV**, **Excel**, and styled **PDF reports**.
11. **ChatGPT-Style UI**: Sleek dark-mode interface with conversational history and sample question presets.

---

## 📂 Project Directory Structure

```
AI-SQL-Assistant/
│
├── app.py                 # Main Streamlit App with ChatGPT UI
├── requirements.txt       # Dependencies
├── README.md              # Setup & Documentation
│
├── uploads/               # Sample & uploaded datasets
│   ├── sample.csv         # Sample E-commerce orders dataset
│   └── sales.xlsx         # Sample Regional store sales dataset
│
├── database/              # SQLite connection & table creation
│   ├── sqlite_db.py
│   ├── create_database.py
│   └── dataset.db
│
├── ai/                    # LLM, Prompting, SQL Generator & Validation
│   ├── llm.py
│   ├── prompt.py
│   ├── sql_generator.py
│   ├── sql_validator.py
│   ├── schema_reader.py
│   └── explanation.py
│
├── rag/                   # Schema RAG with ChromaDB
│   ├── chroma_db/
│   ├── embeddings.py
│   └── retriever.py
│
├── visualization/         # Visualizations, KPIs & Dashboard layout
│   ├── charts.py
│   ├── dashboard.py
│   ├── kpi.py
│   └── chart_selector.py
│
├── utils/                 # Readers, Converters & Formatters
│   ├── excel_reader.py
│   ├── csv_reader.py
│   ├── dataframe_converter.py
│   ├── helper.py
│   └── logger.py
│
├── sql/                   # SQL execution, parsing, formatting, optimizer
│   ├── executor.py
│   ├── parser.py
│   ├── formatter.py
│   └── optimizer.py
│
├── assets/                # Styling & CSS
│   └── style.css
│
├── outputs/               # Generated reports & charts
│   ├── charts/
│   ├── reports/
│   └── exports/
│
└── docs/                  # Architecture & Workflow Markdown docs
    ├── architecture.md
    └── workflow.md
```

---

## 🚀 Getting Started

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Launch the Application

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 💡 Input Examples & Output Results Examples

### Example 1: E-Commerce Dataset Analysis

- **Input File**: `uploads/sample.csv` (Columns: `order_id`, `customer_name`, `category`, `product_name`, `sales`, `quantity`, `discount`, `profit`, `order_date`, `region`)
- **User Question**: *"What are the top 5 products by total sales?"*
- **Generated SQL**:
```sql
SELECT product_name, SUM(sales) AS total_sales
FROM sample_ecommerce_orders
GROUP BY product_name
ORDER BY total_sales DESC
LIMIT 5
```
- **Query Results Output**:
| product_name | total_sales |
| :--- | :--- |
| MacBook Pro | 1999.99 |
| Executive Desk | 850.00 |
| Leather Recliner | 650.00 |
| Standing Desk | 550.00 |
| 4K Monitor | 450.00 |

- **Plain English Business Explanation**:
> "This query analyzes data based on your request: 'What are the top 5 products by total sales?'. The top result is MacBook Pro with total_sales of $1,999.99. The dataset displays a total of 5 distinct grouped records."
- **Auto Visualization**: Interactive Bar Chart comparing total sales across the top 5 products.
- **Export Options**: Downloadable CSV, Excel (`.xlsx`), and PDF report (`.pdf`).

---

### Example 2: Store Financial Performance Analysis

- **Input File**: `uploads/sales.xlsx` (Columns: `store_id`, `city`, `state`, `regional_manager`, `q1_sales`, `q2_sales`, `q3_sales`, `q4_sales`, `employee_count`, `satisfaction_score`)
- **User Question**: *"What are the top 5 cities by q4_sales?"*
- **Generated SQL**:
```sql
SELECT city, SUM(q4_sales) AS total_q4_sales
FROM sample_store_sales
GROUP BY city
ORDER BY total_q4_sales DESC
LIMIT 5
```
- **Query Results Output**:
| city | total_q4_sales |
| :--- | :--- |
| Los Angeles | 180,000 |
| New York | 160,000 |
| Houston | 139,000 |
| San Diego | 131,000 |
| Chicago | 128,000 |

---

## 🔒 Security & Guardrails

- **SQLGlot AST Validation**: Blocks all write or destructive actions (`DROP TABLE`, `DELETE FROM`, `UPDATE`, `INSERT INTO`, `ALTER TABLE`).
- **Parameterized & Read-Only Execution**: Uses SQLAlchemy engine connected directly to read-only database cursor mode.
