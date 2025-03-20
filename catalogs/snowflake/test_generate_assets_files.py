import pytest
from generate_assets_file import add_columns_to_table, fix_columns_comments


@pytest.fixture
def sample_table():
    return {
        "TABLE_NAME": "employees",
        "COLUMNS": []
    }

@pytest.fixture
def sample_columns_data():
    return {
        "column_1": {
            "TABLE_NAME": "employees",
            "COMMENT": "This is column 1\nwith a newline"
        },
        "column_2": {
            "TABLE_NAME": "employees",
            "COMMENT": "This is column 2\nwith a newline"
        },
        "column_3": {
            "TABLE_NAME": "departments",
            "COMMENT": "This column is in departments"
        },
        "column_4": {
            "TABLE_NAME": "employees",
            "COMMENT": "Column 4 without newline"
        }
    }

def test_add_columns_to_table_includes_matching_columns(sample_table, sample_columns_data):
    add_columns_to_table(sample_table, sample_columns_data)
    assert len(list(sample_table["COLUMNS"])) == 3

def test_columns_have_correct_comments_with_newlines(sample_table, sample_columns_data):
    add_columns_to_table(sample_table, sample_columns_data)
    fix_columns_comments(sample_table)
    columns = list(sample_table["COLUMNS"])
    print(columns)
    assert columns[0] == "This is column 1 with a newline"
    assert columns[1] == "This is column 2 with a newline"

def test_columns_for_non_matching_table_are_not_added(sample_table, sample_columns_data):
    sample_table["TABLE_NAME"] = "non_existing_table"
    add_columns_to_table(sample_table, sample_columns_data)
    assert len(list(sample_table["COLUMNS"])) == 0

def test_column_without_comment_is_not_modified(sample_table, sample_columns_data):
    # Ajoute une colonne sans commentaire
    sample_columns_data["column_5"] = {
        "TABLE_NAME": "employees",
        "COMMENT": ""
    }
    add_columns_to_table(sample_table, sample_columns_data)
    columns = list(sample_table["COLUMNS"])
    assert columns[3]["COMMENT"] == "" 

def test_column_with_no_newline_in_comment_is_untouched(sample_table, sample_columns_data):
    add_columns_to_table(sample_table, sample_columns_data)
    columns = list(sample_table["COLUMNS"])
    assert columns[2]["COMMENT"] == "Column 4 without newline"
