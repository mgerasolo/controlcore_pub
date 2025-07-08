import sys
sys.path.append('.')

from gandalf_api.sql_query_handler import build_sql_prompt


def test_build_sql_prompt_includes_example_and_schema():
    schema = '{"table": ["id INT"]}'
    prompt = build_sql_prompt('show data', schema)
    assert '```json' in prompt
    assert schema in prompt
    assert '```sql' in prompt
    assert 'SELECT * FROM table LIMIT 5;' in prompt
    assert 'User question:' in prompt
    assert 'show data' in prompt
    assert 'without prefixing' in prompt
    assert 'postgres' in prompt.lower()
