# Production AI SQL Assistant Workflow

## End-to-End Execution Flow

1. **User Connection**:
   - User opens the Streamlit application. No login or authentication is required.

2. **Dataset Upload & Ingestion**:
   - User uploads a `.csv` or `.xlsx` dataset, or selects one of the pre-loaded sample datasets (`sample.csv` or `sales.xlsx`).
   - `utils/csv_reader.py` or `utils/excel_reader.py` parses the file into a Pandas DataFrame and sanitizes table/column names.
   - `database/create_database.py` ingests the DataFrame into a temporary SQLite database (`database/dataset.db`).

3. **Schema Extraction & RAG Indexing**:
   - `ai/schema_reader.py` extracts table columns, data types, and sample data.
   - `rag/retriever.py` indexes column semantics into ChromaDB vectorstore for RAG context retrieval.

4. **Natural Language Question Processing**:
   - User submits a question via the ChatGPT-style prompt input.
   - `ai/sql_generator.py` combines prompt template + database schema + RAG context + LLM (Gemini / OpenAI or Rule Fallback) to translate NL to SQLite query.

5. **SQL Security Validation**:
   - `ai/sql_validator.py` validates the SQL AST via `SQLGlot`.
   - Rejects non-SELECT queries (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `CREATE`).

6. **Execution & Results**:
   - `sql/executor.py` runs the query against SQLite and captures execution timing.
   - `ai/explanation.py` produces a Plain English summary of the results.

7. **Dashboard & Visualization**:
   - `visualization/kpi.py` generates top KPI metric cards.
   - `visualization/chart_selector.py` recommends and creates the optimal interactive Plotly chart.
   - `utils/dataframe_converter.py` provides download buttons for CSV, Excel, and PDF formats.
