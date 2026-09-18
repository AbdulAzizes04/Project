# Production AI SQL Assistant Architecture

## System Diagram
```
                     +---------------------------------------+
                     |         Streamlit Frontend UI         |
                     |       (ChatGPT-style Interface)       |
                     +-------------------+-------------------+
                                         |
                                 Dataset Upload
                             (CSV / Excel .xlsx)
                                         |
                                         v
                     +-------------------+-------------------+
                     |         Pandas Data Engine            |
                     |     (Clean & Sanitize Schema)         |
                     +-------------------+-------------------+
                                         |
                                         v
                     +-------------------+-------------------+
                     |       Temporary SQLite Storage        |
                     |             (dataset.db)              |
                     +-------------------+-------------------+
                                         |
             +---------------------------+---------------------------+
             |                                                       |
             v                                                       v
+--------------------------+                               +--------------------+
|  ChromaDB RAG Engine     |                               |  Schema Reader     |
| (Column Index & Embeds)  |                               | (Prompt Injector)  |
+------------+-------------+                               +---------+----------+
             |                                                       |
             +---------------------------+---------------------------+
                                         |
                                         v
                     +-------------------+-------------------+
                     |      LLM / Fallback Rule Engine       |
                     |  (Google Gemini / OpenAI / Rule SQL)  |
                     +-------------------+-------------------+
                                         |
                                  SQL Statement
                                         v
                     +-------------------+-------------------+
                     |       SQLGlot Security Validator      |
                     |     (Blocks non-SELECT queries)       |
                     +-------------------+-------------------+
                                         |
                                    Valid SELECT
                                         v
                     +-------------------+-------------------+
                     |        SQLAlchemy SQL Executor        |
                     +-------------------+-------------------+
                                         |
                                 Query Result DF
                                         v
                     +-------------------+-------------------+
                     |     Plotly Visualizer & KPI Cards     |
                     |       + CSV/Excel/PDF Exporter        |
                     +---------------------------------------+
```

## Component Architecture Overview
1. **Frontend (Streamlit)**: ChatGPT-style conversational assistant with active chat memory, sidebar data controls, and dynamic charts.
2. **Database Engine**: SQLAlchemy & SQLite convert uploaded CSV/Excel files into clean relational tables.
3. **AI Pipeline**: LangChain orchestration linking system prompts, schema context, and LLMs (Google Gemini / OpenAI GPT). Includes a fallback rule engine if no API key is specified.
4. **Validation Layer**: SQLGlot parses the AST of generated queries to block data manipulation commands (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`).
5. **Visualization Engine**: Plotly charts, KPI metrics, and export engine supporting CSV, Excel, and PDF formats.
