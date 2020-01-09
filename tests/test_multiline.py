import pytest
from mssqlcli.mssqlbuffer import _is_complete


class TestMssqlCliMultiline:
    testdata = [
        ('select 1 /* open comment!\ngo', False),
        ('select 1\ngo -- another comment', True),
        ('select 1; select 2, "open quote: go', False),
        ('select 1; go', False),
        ('select 1\n select 2;\ngo', True),
        ('select 1;', False),
        ('select 3 /* another open comment\n*/   go', True)
    ]

    @staticmethod
    @pytest.mark.parametrize("query_str, is_complete", testdata)
    def test_multiline_completeness(query_str, is_complete):
        assert _is_complete(query_str) == is_complete
