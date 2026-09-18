import os
import sys
import pandas as pd

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.csv_reader import load_csv_data
from utils.excel_reader import load_excel_data
from database.create_database import ingest_dataframe_to_sqlite
from database.sqlite_db import db_manager
from ai.sql_validator import validate_sql_query
from ai.sql_generator import generate_sql_query
from ai.explanation import generate_plain_english_explanation
from sql.executor import execute_sql_query
from visualization.chart_selector import recommend_and_create_chart
from utils.dataframe_converter import convert_df_to_csv, convert_df_to_excel, convert_df_to_pdf

def test_full_pipeline():
    print("=" * 60)
    print("RUNNING COMPREHENSIVE AI SQL ASSISTANT UNIT & INTEGRATION TESTS")
    print("=" * 60)

    # 1. Test CSV Loading & SQLite Ingestion
    sample_csv_path = os.path.join(os.path.dirname(__file__), "uploads", "sample.csv")
    print(f"\n[1/7] Testing CSV Ingestion: {sample_csv_path}")
    df_csv, table_csv = load_csv_data(sample_csv_path)
    assert not df_csv.empty, "DataFrame should not be empty"
    print(f"[OK] Loaded {len(df_csv)} rows, table name: {table_csv}")

    table_name, cols, dtypes = ingest_dataframe_to_sqlite(df_csv, table_name="test_ecommerce")
    print(f"[OK] Ingested to SQLite table '{table_name}' with {len(cols)} columns.")

    # 2. Test SQL Security Validation
    print("\n[2/7] Testing SQL Security Validation (SQLGlot)")
    valid_sql = "SELECT category, SUM(sales) AS total_sales FROM test_ecommerce GROUP BY category"
    malicious_sql = "DROP TABLE test_ecommerce;"
    
    is_valid, msg = validate_sql_query(valid_sql)
    assert is_valid, "Valid SELECT query should pass validation"
    print(f"[OK] Valid SELECT check passed: {msg}")

    is_valid_bad, msg_bad = validate_sql_query(malicious_sql)
    assert not is_valid_bad, "DROP TABLE query should fail validation"
    print(f"[OK] Security check correctly blocked forbidden query: {msg_bad}")

    # 3. Test Text-to-SQL Generator
    print("\n[3/7] Testing Text-to-SQL Generator")
    question = "What are the top 5 products by total sales?"
    sql, meta = generate_sql_query(question, table_name)
    print(f"Question: '{question}'")
    print(f"Generated SQL: {sql}")
    print(f"Metadata: {meta}")

    # 4. Test SQL Execution
    print("\n[4/7] Testing SQL Execution")
    res_df, exec_meta = execute_sql_query(sql)
    print(f"Execution Output (First 3 rows):\n{res_df.head(3)}")
    print(f"Execution Meta: {exec_meta}")

    # 5. Test Plain English Business Explanation
    print("\n[5/7] Testing Plain English Business Explanation")
    explanation = generate_plain_english_explanation(question, sql, res_df)
    print(f"Explanation Output:\n{explanation}")

    # 6. Test Auto Plotly Chart Recommendation
    print("\n[6/7] Testing Auto Plotly Chart Selector")
    fig, chart_type = recommend_and_create_chart(res_df)
    assert fig is not None, "Plotly figure should be generated"
    print(f"[OK] Created visualization: {chart_type}")

    # 7. Test Multi-Format Exporters (CSV, Excel, PDF)
    print("\n[7/7] Testing Multi-Format Exporters")
    csv_bytes = convert_df_to_csv(res_df)
    excel_bytes = convert_df_to_excel(res_df)
    pdf_bytes = convert_df_to_pdf(res_df, query=sql)
    
    assert len(csv_bytes) > 0, "CSV bytes should be non-empty"
    assert len(excel_bytes) > 0, "Excel bytes should be non-empty"
    assert len(pdf_bytes) > 0, "PDF bytes should be non-empty"
    print(f"[OK] Generated CSV ({len(csv_bytes)} bytes), Excel ({len(excel_bytes)} bytes), PDF ({len(pdf_bytes)} bytes).")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_full_pipeline()
