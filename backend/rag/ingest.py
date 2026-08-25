"""
Data Dictionary Ingestion Module for ChromaDB Vector Store.
Splits data_dictionary.md into logical chunks and indexes them in ChromaDB.
"""

import os
import sys
import re

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import chromadb
from backend.core.config import settings

CHROMA_DB_DIR = os.path.join(settings.BASE_DIR, "rag", "chroma_db")
DATA_DICT_PATH = os.path.join(settings.BASE_DIR, "rag", "data_dictionary.md")
COLLECTION_NAME = "workday_schema_docs"


def parse_data_dictionary_chunks(markdown_content: str):
    """
    Parse data_dictionary.md into 12 distinct, logical chunks with rich metadata.
    """
    chunks = []

    # 1. Regions Table Schema
    regions_match = re.search(r"### 2.1 Table: `regions`[\s\S]*?(?=### 2.2 Table: `departments`)", markdown_content)
    if regions_match:
        chunks.append({
            "id": "chunk_table_regions",
            "content": regions_match.group(0).strip(),
            "metadata": {"section": "regions", "type": "table_schema", "table": "regions"}
        })

    # 2. Departments Table Schema
    depts_match = re.search(r"### 2.2 Table: `departments`[\s\S]*?(?=### 2.3 Table: `employees`)", markdown_content)
    if depts_match:
        chunks.append({
            "id": "chunk_table_departments",
            "content": depts_match.group(0).strip(),
            "metadata": {"section": "departments", "type": "table_schema", "table": "departments"}
        })

    # 3. Employees Table Schema
    emp_match = re.search(r"### 2.3 Table: `employees`[\s\S]*?(?=### 2.4 Table: `leave_records`)", markdown_content)
    if emp_match:
        chunks.append({
            "id": "chunk_table_employees",
            "content": emp_match.group(0).strip(),
            "metadata": {"section": "employees", "type": "table_schema", "table": "employees"}
        })

    # 4. Leave Records Table Schema
    leave_match = re.search(r"### 2.4 Table: `leave_records`[\s\S]*?(?=### 2.5 Table: `job_openings`)", markdown_content)
    if leave_match:
        chunks.append({
            "id": "chunk_table_leave_records",
            "content": leave_match.group(0).strip(),
            "metadata": {"section": "leave_records", "type": "table_schema", "table": "leave_records"}
        })

    # 5. Job Openings Table Schema
    job_match = re.search(r"### 2.5 Table: `job_openings`[\s\S]*?(?=## 3. Entity Relationships Summary)", markdown_content)
    if job_match:
        chunks.append({
            "id": "chunk_table_job_openings",
            "content": job_match.group(0).strip(),
            "metadata": {"section": "job_openings", "type": "table_schema", "table": "job_openings"}
        })

    # 6. Business Query Guide: Headcount
    headcount_match = re.search(r"### 4.1 Employee Headcount Analytics[\s\S]*?(?=### 4.2 Employees Currently on Leave)", markdown_content)
    if headcount_match:
        chunks.append({
            "id": "chunk_guide_headcount",
            "content": headcount_match.group(0).strip(),
            "metadata": {"section": "employee_headcount", "type": "business_rule"}
        })

    # 7. Business Query Guide: Employees on Leave
    on_leave_match = re.search(r"### 4.2 Employees Currently on Leave[\s\S]*?(?=### 4.3 Leave Analytics)", markdown_content)
    if on_leave_match:
        chunks.append({
            "id": "chunk_guide_employees_on_leave",
            "content": on_leave_match.group(0).strip(),
            "metadata": {"section": "employees_on_leave", "type": "business_rule"}
        })

    # 8. Business Query Guide: Leave Analytics
    leave_analytics_match = re.search(r"### 4.3 Leave Analytics & Time-Off Breakdown[\s\S]*?(?=### 4.4 Job Openings & Recruiting Analytics)", markdown_content)
    if leave_analytics_match:
        chunks.append({
            "id": "chunk_guide_leave_analytics",
            "content": leave_analytics_match.group(0).strip(),
            "metadata": {"section": "leave_analytics", "type": "business_rule"}
        })

    # 9. Business Query Guide: Job Openings & Time to Fill
    job_analytics_match = re.search(r"### 4.4 Job Openings & Recruiting Analytics[\s\S]*?(?=### 4.5 Compensation & Salary Analytics)", markdown_content)
    if job_analytics_match:
        chunks.append({
            "id": "chunk_guide_job_openings",
            "content": job_analytics_match.group(0).strip(),
            "metadata": {"section": "job_openings_analytics", "type": "business_rule"}
        })

    # 10. Business Query Guide: Salary Analytics
    salary_match = re.search(r"### 4.5 Compensation & Salary Analytics[\s\S]*?(?=## 5. SQL Generation Rules for This Schema)", markdown_content)
    if salary_match:
        chunks.append({
            "id": "chunk_guide_salary",
            "content": salary_match.group(0).strip(),
            "metadata": {"section": "salary_analytics", "type": "business_rule"}
        })

    # 11. SQL Generation Rules
    rules_match = re.search(r"## 5. SQL Generation Rules for This Schema[\s\S]*?(?=## 6. Common Mistakes to Avoid)", markdown_content)
    if rules_match:
        chunks.append({
            "id": "chunk_sql_rules",
            "content": rules_match.group(0).strip(),
            "metadata": {"section": "sql_generation_rules", "type": "sql_guidance"}
        })

    # 12. Common SQL Mistakes (Anti-Patterns)
    mistakes_match = re.search(r"## 6. Common Mistakes to Avoid[\s\S]*$", markdown_content)
    if mistakes_match:
        chunks.append({
            "id": "chunk_sql_anti_patterns",
            "content": mistakes_match.group(0).strip(),
            "metadata": {"section": "common_sql_mistakes", "type": "sql_guidance"}
        })

    return chunks


def ingest_data_dictionary(db_dir: str = CHROMA_DB_DIR, doc_path: str = DATA_DICT_PATH):
    """
    Reads data_dictionary.md, splits into chunks, and upserts them into persistent ChromaDB.
    """
    if not os.path.exists(doc_path):
        raise FileNotFoundError(f"Data dictionary not found at {doc_path}")

    os.makedirs(db_dir, exist_ok=True)

    with open(doc_path, "r", encoding="utf-8") as f:
        markdown_text = f.read()

    chunks = parse_data_dictionary_chunks(markdown_text)
    if not chunks:
        raise ValueError("Failed to extract chunks from data_dictionary.md")

    # Initialize ChromaDB persistent client
    client = chromadb.PersistentClient(path=db_dir)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    ids = [chunk["id"] for chunk in chunks]
    documents = [chunk["content"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    # Use upsert to guarantee determinism without duplicate growth
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(f"Successfully ingested {len(chunks)} chunks into ChromaDB collection '{COLLECTION_NAME}' at {db_dir}.")
    return len(chunks)


if __name__ == "__main__":
    ingest_data_dictionary()
