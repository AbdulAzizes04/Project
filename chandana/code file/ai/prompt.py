from langchain.prompts import PromptTemplate

SQL_GENERATION_PROMPT_TEMPLATE = """
You are an expert Senior Database & SQL Developer.
Your job is to translate a user's Natural Language question into a valid, efficient SQLite SQL query.

### Database Schema Information:
{schema_context}

### Relevant Context / Metadata:
{rag_context}

### CRITICAL RULES & CONSTRAINTS:
1. ONLY return valid SQLite executable SELECT queries.
2. DO NOT use markdown code block backticks (e.g. DO NOT use ```sql ... ```). Return ONLY raw executable SQL text.
3. DO NOT generate any data-modifying queries (NO INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, EXEC).
4. Use double quotes or backticks for column names if they contain special characters or SQL keywords.
5. Apply appropriate aggregate functions (SUM, AVG, COUNT, MIN, MAX) and GROUP BY clauses when answering summary questions.
6. IF THE USER ASKS A SINGULAR QUESTION FOR THE TOP/HIGHEST/BEST ITEM (e.g. "which store...", "what product...", "who has highest...", "which manager..."), ALWAYS USE `LIMIT 1` to return ONLY that single store/product/item.
7. Only use a larger limit (e.g., `LIMIT 5`) if the user explicitly requested multiple items (e.g., "top 5 stores").
8. Carefully match user terms to exact column names in the schema (e.g. 'store' -> `store_id`, 'sales' -> `q1_sales` or `sales`).

User Question: {question}

SQL Query:
"""


SQL_EXPLANATION_PROMPT_TEMPLATE = """
You are an expert Data Analyst presenting insights to business stakeholders.

### Natural Language Question:
{question}

### Executed SQL Query:
{sql_query}

### Query Result Summary (First few rows / aggregated summary):
{result_summary}

Provide a concise 2-3 sentence explanation in Plain English.
1. Explain what business metric or pattern this SQL query computes.
2. Highlight key numerical findings or top results from the query data.
3. Keep the tone professional, clear, and actionable.

Explanation:
"""

sql_gen_prompt = PromptTemplate(
    input_variables=["schema_context", "rag_context", "question"],
    template=SQL_GENERATION_PROMPT_TEMPLATE
)

sql_explain_prompt = PromptTemplate(
    input_variables=["question", "sql_query", "result_summary"],
    template=SQL_EXPLANATION_PROMPT_TEMPLATE
)
