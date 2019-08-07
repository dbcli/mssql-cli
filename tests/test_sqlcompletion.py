from mssqlcli.packages.sqlcompletion import (
    suggest_type, Special, Database, Schema, Table, Column, View, Keyword,
    FromClauseItem, Function, Datatype, Alias, JoinCondition, Join)
from mssqlcli.packages.parseutils.tables import TableReference
import sys
import unittest

class SqlCompletionTests(unittest.TestCase):

    def cols_etc(self, table, schema=None, alias=None, is_function=False, parent=None, \
                last_keyword=None):
        """Returns the expected select-clause suggestions for a single-table
        select."""
        return set([
            Column(table_refs=(TableReference(schema, table, alias, is_function),), \
                qualifiable=True),
            Function(schema=parent),
            Keyword(last_keyword)
        ])


    def test_select_suggests_cols_with_visible_table_scope(self):
        suggestions = suggest_type('SELECT  FROM tabl', 'SELECT ')
        assert set(suggestions) == self.cols_etc('tabl', last_keyword='SELECT')


    def test_select_suggests_cols_with_qualified_table_scope(self):
        suggestions = suggest_type('SELECT  FROM sch.tabl', 'SELECT ')
        assert set(suggestions) == self.cols_etc('tabl', 'sch', last_keyword='SELECT')


    def test_cte_does_not_crash(self):
        sql = ('WITH CTE AS (SELECT F.* FROM Foo F WHERE F.Bar > 23) ' \
            + 'SELECT C.* FROM CTE C WHERE C.FooID BETWEEN 123 AND 234;')
        for i in range(len(sql)):
            suggest_type(sql[:i+1], sql[:i+1])


    def test_where_suggests_columns_functions_quoted_table(self):
        expressions = [
            'SELECT * FROM "tabl" WHERE '
        ]
        for expression in expressions:
            expected = self.cols_etc('tabl', alias='"tabl"', last_keyword='WHERE')
            suggestions = suggest_type(expression, expression)
            assert expected == set(suggestions)


    def test_where_suggests_columns_functions(self):
        expressions = [
            'INSERT INTO OtherTabl(ID, Name) SELECT * FROM tabl WHERE ',
            'INSERT INTO OtherTabl SELECT * FROM tabl WHERE ',
            'SELECT * FROM tabl WHERE ',
            'SELECT * FROM tabl WHERE (',
            'SELECT * FROM tabl WHERE foo = ',
            'SELECT * FROM tabl WHERE bar OR ',
            'SELECT * FROM tabl WHERE foo = 1 AND ',
            'SELECT * FROM tabl WHERE (bar > 10 AND ',
            'SELECT * FROM tabl WHERE (bar AND (baz OR (qux AND (',
            'SELECT * FROM tabl WHERE 10 < ',
            'SELECT * FROM tabl WHERE foo BETWEEN ',
            'SELECT * FROM tabl WHERE foo BETWEEN foo AND ',
        ]
        for expression in expressions:
            suggestions = suggest_type(expression, expression)
            assert set(suggestions) == self.cols_etc('tabl', last_keyword='WHERE')


    def test_where_in_suggests_columns(self):
        expressions = [
            'SELECT * FROM tabl WHERE foo IN (',
            'SELECT * FROM tabl WHERE foo IN (bar, '
        ]
        for expression in expressions:
            suggestions = suggest_type(expression, expression)
            assert set(suggestions) == self.cols_etc('tabl', last_keyword='WHERE')


    def test_after_as(self):
        expressions = [
            'SELECT 1 AS ',
            'SELECT 1 FROM tabl AS '
        ]
        for expression in expressions:
            suggestions = suggest_type(expression, expression)
            assert set(suggestions) == set()


    def test_where_equals_any_suggests_columns_or_keywords(self):
        text = 'SELECT * FROM tabl WHERE foo = ANY('
        suggestions = suggest_type(text, text)
        assert set(suggestions) == self.cols_etc('tabl', last_keyword='WHERE')


    def test_lparen_suggests_cols(self):
        suggestion = suggest_type('SELECT MAX( FROM tbl', 'SELECT MAX(')
        assert set(suggestion) == set([
            Column(table_refs=((None, 'tbl', None, False),), qualifiable=True)])


    def test_select_suggests_cols_and_funcs(self):
        suggestions = suggest_type('SELECT ', 'SELECT ')
        assert set(suggestions) == set([
            Column(table_refs=(), qualifiable=True),
            Function(schema=None),
            Keyword('SELECT'),
        ])


    def test_suggests_tables_views_and_schemas(self):
        expressions = [
            'INSERT INTO ',
            'COPY ',
            'UPDATE ',
            'DESCRIBE '
        ]
        for expression in expressions:
            suggestions = suggest_type(expression, expression)
            assert set(suggestions) == set([
                Table(schema=None),
                View(schema=None),
                Schema(),
            ])


    def test_suggest_tables_views_schemas_and_functions(self):
        expressions = [
            'SELECT * FROM '
        ]
        for expression in expressions:
            suggestions = suggest_type(expression, expression)
            assert set(suggestions) == set([
                FromClauseItem(schema=None),
                Schema()
            ])


    def test_suggest_after_join_with_two_tables(self):
        expressions = [
            'SELECT * FROM foo JOIN bar on bar.barid = foo.barid JOIN ',
            'SELECT * FROM foo JOIN bar USING (barid) JOIN '
        ]
        for expression in expressions:
            suggestions = suggest_type(expression, expression)
            tables = tuple([(None, 'foo', None, False), (None, 'bar', None, False)])
            assert set(suggestions) == set([
                FromClauseItem(schema=None, table_refs=tables),
                Join(tables, None),
                Schema(),
            ])


    def test_suggest_after_join_with_one_table(self):
        expressions = [
            'SELECT * FROM foo JOIN ',
            'SELECT * FROM foo JOIN bar'
        ]
        for expression in expressions:
            suggestions = suggest_type(expression, expression)
            tables = ((None, 'foo', None, False),)
            assert set(suggestions) == set([
                FromClauseItem(schema=None, table_refs=tables),
                Join(((None, 'foo', None, False),), None),
                Schema(),
            ])


    def test_suggest_qualified_tables_and_views(self):
        expressions = [
            'INSERT INTO sch.',
            'COPY sch.',
            'DESCRIBE sch.'
        ]
        for expression in expressions:
            suggestions = suggest_type(expression, expression)
            assert set(suggestions) == set([
                Table(schema='sch'),
                View(schema='sch'),
            ])

    def test_suggest_qualified_aliasable_tables_and_views(self):
        expressions = [
            'UPDATE sch.'
        ]
        for expression in expressions:
            suggestions = suggest_type(expression, expression)
            assert set(suggestions) == set([
                Table(schema='sch'),
                View(schema='sch'),
            ])


    def test_suggest_qualified_tables_views_and_functions(self):
        expressions = [
            'SELECT * FROM sch.',
            'SELECT * FROM sch."',
            'SELECT * FROM sch."foo',
            'SELECT * FROM "sch".',
            'SELECT * FROM "sch"."'
        ]
        for expression in expressions:
            suggestions = suggest_type(expression, expression)
            assert set(suggestions) == set([FromClauseItem(schema='sch')])


    def test_suggest_qualified_tables_views_functions_and_joins(self):
        expressions = [
            'SELECT * FROM foo JOIN sch.'
        ]
        for expression in expressions:
            suggestions = suggest_type(expression, expression)
            tbls = tuple([(None, 'foo', None, False)])
            assert set(suggestions) == set([
                FromClauseItem(schema='sch', table_refs=tbls),
                Join(tbls, 'sch'),
            ])


    def test_truncate_suggests_tables_and_schemas(self):
        suggestions = suggest_type('TRUNCATE ', 'TRUNCATE ')
        assert set(suggestions) == set([
            Table(schema=None),
            Schema()])


    def test_truncate_suggests_qualified_tables(self):
        suggestions = suggest_type('TRUNCATE sch.', 'TRUNCATE sch.')
        assert set(suggestions) == set([
            Table(schema='sch')])


    def test_distinct_suggests_cols(self):
        texts = [
            'SELECT DISTINCT ',
            'INSERT INTO foo SELECT DISTINCT '
        ]
        for text in texts:
            suggestions = suggest_type(text, text)
            assert set(suggestions) == set([
                Column(table_refs=(), local_tables=(), qualifiable=True),
                Function(schema=None),
                Keyword('DISTINCT')
            ])


    def test_distinct_and_order_by_suggestions_with_aliases(self):
        test_args = [
            (
                'SELECT DISTINCT FROM tbl x JOIN tbl1 y',
                'SELECT DISTINCT',
                'SELECT',
            ),
            (
                'SELECT * FROM tbl x JOIN tbl1 y ORDER BY ',
                'SELECT * FROM tbl x JOIN tbl1 y ORDER BY ',
                'BY',
            )
        ]
        for arg in test_args:
            text = arg[0]
            text_before = arg[1]
            last_keyword = arg[2]

            suggestions = suggest_type(text, text_before)
            assert set(suggestions) == set([
                Column(
                    table_refs=(
                        TableReference(None, 'tbl', 'x', False),
                        TableReference(None, 'tbl1', 'y', False),
                    ),
                    local_tables=(),
                    qualifiable=True
                ),
                Function(schema=None),
                Keyword(last_keyword)
            ])


    def test_distinct_and_order_by_suggestions_with_alias_given(self):
        test_args = [
            (
                'SELECT DISTINCT x. FROM tbl x JOIN tbl1 y',
                'SELECT DISTINCT x.'
            ),
            (
                'SELECT * FROM tbl x JOIN tbl1 y ORDER BY x.',
                'SELECT * FROM tbl x JOIN tbl1 y ORDER BY x.'
            )
        ]
        for arg in test_args:
            text = arg[0]
            text_before = arg[1]

            suggestions = suggest_type(text, text_before)
            assert set(suggestions) == set([
                Column(
                    table_refs=(TableReference(None, 'tbl', 'x', False),),
                    local_tables=(),
                    qualifiable=False
                ),
                Table(schema='x'),
                View(schema='x'),
                Function(schema='x'),
            ])


    def test_col_comma_suggests_cols(self):
        suggestions = suggest_type('SELECT a, b, FROM tbl', 'SELECT a, b,')
        assert set(suggestions) == set([
            Column(table_refs=((None, 'tbl', None, False),), qualifiable=True),
            Function(schema=None),
            Keyword('SELECT'),
        ])


    def test_table_comma_suggests_tables_and_schemas(self):
        suggestions = suggest_type('SELECT a, b FROM tbl1, ', \
                'SELECT a, b FROM tbl1, ')
        assert set(suggestions) == set([
            FromClauseItem(schema=None),
            Schema(),
        ])


    def test_into_suggests_tables_and_schemas(self):
        suggestion = suggest_type('INSERT INTO ', 'INSERT INTO ')
        assert set(suggestion) == set([
            Table(schema=None),
            View(schema=None),
            Schema(),
        ])


    def test_insert_into_lparen_suggests_cols(self):
        texts = [
            'INSERT INTO abc (',
            'INSERT INTO abc () SELECT * FROM hij;',
        ]
        for text in texts:
            suggestions = suggest_type(text, 'INSERT INTO abc (')
            assert suggestions == (
                Column(
                    table_refs=((None, 'abc', None, False),),
                    context='insert'
                ),
            )


    def test_insert_into_lparen_partial_text_suggests_cols(self):
        suggestions = suggest_type('INSERT INTO abc (i', 'INSERT INTO abc (i')
        assert suggestions == (
            Column(
                table_refs=((None, 'abc', None, False),),
                context='insert'
            ),
        )


    def test_insert_into_lparen_comma_suggests_cols(self):
        suggestions = suggest_type('INSERT INTO abc (id,', 'INSERT INTO abc (id,')
        assert suggestions == (
            Column(
                table_refs=((None, 'abc', None, False),),
                context='insert'
            ),
        )


    def test_partially_typed_col_name_suggests_col_names(self):
        suggestions = suggest_type('SELECT * FROM tabl WHERE col_n', \
            'SELECT * FROM tabl WHERE col_n')
        assert set(suggestions) == self.cols_etc('tabl', last_keyword='WHERE')


    def test_dot_suggests_cols_of_a_table_or_schema_qualified_table(self):
        suggestions = suggest_type('SELECT tabl. FROM tabl', 'SELECT tabl.')
        assert set(suggestions) == set([
            Column(table_refs=((None, 'tabl', None, False),)),
            Table(schema='tabl'),
            View(schema='tabl'),
            Function(schema='tabl'),
        ])


    def test_dot_suggests_cols_of_an_alias(self):
        sqls = [
            'SELECT t1. FROM tabl1 t1',
            'SELECT t1. FROM tabl1 t1, tabl2 t2',
            'SELECT t1. FROM "tabl1" t1',
            'SELECT t1. FROM "tabl1" t1, "tabl2" t2',
        ]
        for sql in sqls:
            suggestions = suggest_type(sql, 'SELECT t1.')
            assert set(suggestions) == set([
                Table(schema='t1'),
                View(schema='t1'),
                Column(table_refs=((None, 'tabl1', 't1', False),)),
                Function(schema='t1'),
            ])


    def test_dot_suggests_cols_of_an_alias_where(self):
        sqls = [
            'SELECT * FROM tabl1 t1 WHERE t1.',
            'SELECT * FROM tabl1 t1, tabl2 t2 WHERE t1.',
            'SELECT * FROM "tabl1" t1 WHERE t1.',
            'SELECT * FROM "tabl1" t1, tabl2 t2 WHERE t1.',
        ]
        for sql in sqls:
            suggestions = suggest_type(sql, sql)
            assert set(suggestions) == set([
                Table(schema='t1'),
                View(schema='t1'),
                Column(table_refs=((None, 'tabl1', 't1', False),)),
                Function(schema='t1'),
            ])


    def test_dot_col_comma_suggests_cols_or_schema_qualified_table(self):
        suggestions = suggest_type('SELECT t1.a, t2. FROM tabl1 t1, tabl2 t2', \
            'SELECT t1.a, t2.')
        assert set(suggestions) == set([
            Column(table_refs=((None, 'tabl2', 't2', False),)),
            Table(schema='t2'),
            View(schema='t2'),
            Function(schema='t2'),
        ])


    def test_sub_select_suggests_keyword(self):
        expressions = [
            'SELECT * FROM (',
            'SELECT * FROM foo WHERE EXISTS (',
            'SELECT * FROM foo WHERE bar AND NOT EXISTS (',
        ]
        for expression in expressions:
            suggestion = suggest_type(expression, expression)
            assert suggestion == (Keyword(),)


    def test_sub_select_partial_text_suggests_keyword(self):
        expressions = [
            'SELECT * FROM (S',
            'SELECT * FROM foo WHERE EXISTS (S',
            'SELECT * FROM foo WHERE bar AND NOT EXISTS (S',
        ]
        for expression in expressions:
            suggestion = suggest_type(expression, expression)
            assert suggestion ==(Keyword(),)


    def test_outer_table_reference_in_exists_subquery_suggests_columns(self):
        q = 'SELECT * FROM foo f WHERE EXISTS (SELECT 1 FROM bar WHERE f.'
        suggestions = suggest_type(q, q)
        assert set(suggestions) == set([
            Column(table_refs=((None, 'foo', 'f', False),)),
            Table(schema='f'),
            View(schema='f'),
            Function(schema='f'),
        ])


    def test_sub_select_table_name_completion(self):
        expression = 'SELECT * FROM (SELECT * FROM '
        suggestion = suggest_type(expression, expression)
        assert set(suggestion) == set([
            FromClauseItem(schema=None),
            Schema(),
        ])


    def test_sub_select_table_name_completion_with_outer_table(self):
        expressions = [
            'SELECT * FROM foo WHERE EXISTS (SELECT * FROM ',
            'SELECT * FROM foo WHERE bar AND NOT EXISTS (SELECT * FROM ',
        ]
        for expression in expressions:
            suggestion = suggest_type(expression, expression)
            tbls = tuple([(None, 'foo', None, False)])
            assert set(suggestion) == set([
                FromClauseItem(schema=None, table_refs=tbls),
                Schema(),
            ])


    def test_sub_select_col_name_completion(self):
        suggestions = suggest_type('SELECT * FROM (SELECT  FROM abc', \
            'SELECT * FROM (SELECT ')
        assert set(suggestions) == set([
            Column(table_refs=((None, 'abc', None, False),), qualifiable=True),
            Function(schema=None),
            Keyword('SELECT'),
        ])


    def test_sub_select_multiple_col_name_completion(self):
        suggestions = suggest_type('SELECT * FROM (SELECT a, FROM abc', \
            'SELECT * FROM (SELECT a, ')
        assert set(suggestions) == set([
            Column(table_refs=((None, 'a', None, False), (None, 'abc', None, False)), \
                qualifiable=True),
            Function(schema=None),
            Keyword('SELECT'),
        ])


    def test_sub_select_dot_col_name_completion(self):
        suggestions = suggest_type('SELECT * FROM (SELECT t. FROM tabl t', \
            'SELECT * FROM (SELECT t.')
        assert set(suggestions) == set([
            Column(table_refs=((None, 'tabl', 't', False),)),
            Table(schema='t'),
            View(schema='t'),
            Function(schema='t'),
        ])


    def test_join_suggests_tables_and_schemas(self):
        join_types = ('', 'INNER', 'LEFT', 'RIGHT OUTER',)
        tbl_aliases = ('', 'foo',)
        for join_type in join_types:
            for tbl_alias in tbl_aliases:
                text = 'SELECT * FROM abc {0} {1} JOIN '.format(tbl_alias, join_type)
                suggestion = suggest_type(text, text)
                tbls = tuple([(None, 'abc', tbl_alias or None, False)])
                assert set(suggestion) == set([
                    FromClauseItem(schema=None, table_refs=tbls),
                    Schema(),
                    Join(tbls, None),
                ])


    def test_left_join_with_comma(self):
        text = 'select * from foo f left join bar b,'
        suggestions = suggest_type(text, text)
        # tbls should also include (None, 'bar', 'b', False)
        # but there's a bug with commas
        tbls = tuple([(None, 'foo', 'f', False)])
        assert set(suggestions) == set([
            FromClauseItem(schema=None, table_refs=tbls),
            Schema(),
        ])


    def test_join_alias_dot_suggests_cols1(self):
        sqls = [
            'SELECT * FROM abc a JOIN def d ON a.',
            'SELECT * FROM abc a JOIN def d ON a.id = d.id AND a.',
        ]
        for sql in sqls:
            suggestions = suggest_type(sql, sql)
            tables = ((None, 'abc', 'a', False), (None, 'def', 'd', False))
            assert set(suggestions) == set([
                Column(table_refs=((None, 'abc', 'a', False),)),
                Table(schema='a'),
                View(schema='a'),
                Function(schema='a'),
                JoinCondition(table_refs=tables, parent=(None, 'abc', 'a', False))
            ])


    def test_join_alias_dot_suggests_cols2(self):
        sqls = [
            'SELECT * FROM abc a JOIN def d ON a.id = d.',
            'SELECT * FROM abc a JOIN def d ON a.id = d.id AND a.id2 = d.',
        ]
        for sql in sqls:
            suggestion = suggest_type(sql, sql)
            assert set(suggestion) == set([
                Column(table_refs=((None, 'def', 'd', False),)),
                Table(schema='d'),
                View(schema='d'),
                Function(schema='d'),
            ])


    def test_on_suggests_aliases_and_join_conditions(self):
        sqls = [ \
'select a.x, b.y from abc a join bcd b on ',
'''select a.x, b.y
from abc a
join bcd b on
''',
'''select a.x, b.y
from abc a
join bcd b
on ''',
'select a.x, b.y from abc a join bcd b on a.id = b.id OR ' \
        ]
        for sql in sqls:
            suggestions = suggest_type(sql, sql)
            tables = ((None, 'abc', 'a', False), (None, 'bcd', 'b', False))
            assert set(suggestions) == set((JoinCondition(table_refs=tables, parent=None), \
                Alias(aliases=('a', 'b',)),))


    def test_on_suggests_tables_and_join_conditions(self):
        sqls = [
            'select abc.x, bcd.y from abc join bcd on abc.id = bcd.id AND ',
            'select abc.x, bcd.y from abc join bcd on ',
        ]
        for sql in sqls:
            suggestions = suggest_type(sql, sql)
            tables = ((None, 'abc', None, False), (None, 'bcd', None, False))
            assert set(suggestions) == set((JoinCondition(table_refs=tables, parent=None), \
                Alias(aliases=('abc', 'bcd',)),))


    def test_on_suggests_aliases_right_side(self):
        sqls = [
            'select a.x, b.y from abc a join bcd b on a.id = ',
            'select a.x, b.y from abc a join bcd b on a.id = b.id AND a.id2 = ',
        ]
        for sql in sqls:
            suggestions = suggest_type(sql, sql)
            assert suggestions == (Alias(aliases=('a', 'b',)),)


    def test_on_suggests_tables_and_join_conditions_right_side(self):
        sqls = [
            'select abc.x, bcd.y from abc join bcd on abc.id = bcd.id and ',
            'select abc.x, bcd.y from abc join bcd on ',
        ]
        for sql in sqls:
            suggestions = suggest_type(sql, sql)
            tables = ((None, 'abc', None, False), (None, 'bcd', None, False))
            assert set(suggestions) == set((JoinCondition(table_refs=tables, parent=None), \
                Alias(aliases=('abc', 'bcd',)),))


    def test_join_using_suggests_common_columns(self):
        texts = [
            'select * from abc inner join def using (',
            'select * from abc inner join def using (col1, ',
            'insert into hij select * from abc inner join def using (',
            '''insert into hij(x, y, z)
            select * from abc inner join def using (col1, ''',
            '''insert into hij (a,b,c)
            select * from abc inner join def using (col1, ''',
        ]
        for text in texts:
            tables = ((None, 'abc', None, False), (None, 'def', None, False))
            assert set(suggest_type(text, text)) == set([
                Column(table_refs=tables, require_last_table=True),])


    def test_suggest_columns_after_multiple_joins(self):
        sql = '''select * from t1
                inner join t2 ON
                t1.id = t2.t1_id
                inner join t3 ON
                t2.id = t3.'''
        suggestions = suggest_type(sql, sql)
        assert Column(table_refs=((None, 't3', None, False),)) in set(suggestions)


    def test_2_statements_2nd_current(self):
        suggestions = suggest_type('select * from a; select * from ', \
            'select * from a; select * from ')
        assert set(suggestions) == set([
            FromClauseItem(schema=None),
            Schema(),
        ])

        suggestions = suggest_type('select * from a; select  from b', \
            'select * from a; select ')
        assert set(suggestions) == set([
            Column(table_refs=((None, 'b', None, False),), qualifiable=True),
            Function(schema=None),
            Keyword('SELECT')
        ])

        # Should work even if first statement is invalid
        suggestions = suggest_type('select * from; select * from ', \
            'select * from; select * from ')
        assert set(suggestions) == set([
            FromClauseItem(schema=None),
            Schema(),
        ])


    def test_2_statements_1st_current(self):
        suggestions = suggest_type('select * from ; select * from b', \
            'select * from ')
        assert set(suggestions) == set([
            FromClauseItem(schema=None),
            Schema(),
        ])

        suggestions = suggest_type('select  from a; select * from b', 'select ')
        assert set(suggestions) == self.cols_etc('a', last_keyword='SELECT')


    def test_3_statements_2nd_current(self):
        suggestions = suggest_type('select * from a; select * from ; select * from c', \
            'select * from a; select * from ')
        assert set(suggestions) == set([
            FromClauseItem(schema=None),
            Schema(),
        ])

        suggestions = suggest_type('select * from a; select  from b; select * from c', \
            'select * from a; select ')
        assert set(suggestions) == self.cols_etc('b', last_keyword='SELECT')


    def test_statements_in_function_body(self):
        texts = [ \
'''
CREATE OR REPLACE FUNCTION func() RETURNS setof int AS $$
SELECT  FROM foo;
SELECT 2 FROM bar;
$$ language sql;
    ''', \
    '''create function func2(int, varchar)
RETURNS text
language sql AS
$func$
SELECT 2 FROM bar;
SELECT  FROM foo;
$func$
    ''',
'''
CREATE OR REPLACE FUNCTION func() RETURNS setof int AS $func$
SELECT 3 FROM foo;
SELECT 2 FROM bar;
$$ language sql;
create function func2(int, varchar)
RETURNS text
language sql AS
$func$
SELECT 2 FROM bar;
SELECT  FROM foo;
$func$
    ''',
'''
SELECT * FROM baz;
CREATE OR REPLACE FUNCTION func() RETURNS setof int AS $func$
SELECT  FROM foo;
SELECT 2 FROM bar;
$$ language sql;
create function func2(int, varchar)
RETURNS text
language sql AS
$func$
SELECT 3 FROM bar;
SELECT  FROM foo;
$func$
SELECT * FROM qux;
    ''' \
        ]
        for text in texts:
            suggestions = suggest_type(text, text[:text.find('  ') + 1])
            assert set(suggestions) == set([
                Column(table_refs=((None, 'foo', None, False),), qualifiable=True),
                Function(schema=None),
                Keyword('SELECT'),
            ])


    functions = [ \
'''
CREATE OR REPLACE FUNCTION func() RETURNS setof int AS $$
SELECT 1 FROM foo;
SELECT 2 FROM bar;
$$ language sql;
    ''', \
    '''
create function func2(int, varchar)
RETURNS text
language sql AS
'
SELECT 2 FROM bar;
SELECT 1 FROM foo;
';
    ''' \
    ]


    def test_statements_with_cursor_after_function_body(self):
        texts = self.functions
        for text in texts:
            suggestions = suggest_type(text, text[:text.find('; ') + 1])
            assert set(suggestions) == set([Keyword(), Special()])


    def test_statements_with_cursor_before_function_body(self):
        texts = self.functions
        for text in texts:
            suggestions = suggest_type(text, '')
            assert set(suggestions) == set([Keyword(), Special()])


    def test_create_db_with_template(self):
        suggestions = suggest_type('create database foo with template ', \
            'create database foo with template ')
        assert set(suggestions) == set((Database(),))


    def test_specials_included_for_initial_completion(self):
        initial_texts = ('', '    ', '\t \t',)
        for initial_text in initial_texts:
            suggestions = suggest_type(initial_text, initial_text)
            assert set(suggestions) == set([Keyword(), Special()])


    def test_drop_schema_qualified_table_suggests_only_tables(self):
        text = 'DROP TABLE schema_name.table_name'
        suggestions = suggest_type(text, text)
        assert suggestions == (Table(schema='schema_name'),)


    def test_handle_pre_completion_comma_gracefully(self):
        texts = (',', '  ,', 'sel ,',)
        for text in texts:
            suggestions = suggest_type(text, text)
            assert iter(suggestions)


    def test_drop_schema_suggests_schemas(self):
        sql = 'DROP SCHEMA '
        assert suggest_type(sql, sql) == (Schema(),)


    def test_cast_operator_suggests_types(self):
        texts = [
            'SELECT x::',
            'SELECT x::y',
            'SELECT (x + y)::',
        ]
        for text in texts:
            assert set(suggest_type(text, text)) == set([
                Datatype(schema=None),
                Table(schema=None),
                Schema()])


    def test_cast_operator_suggests_schema_qualified_types(self):
        texts = [
            'SELECT foo::bar.',
            'SELECT foo::bar.baz',
            'SELECT (x + y)::bar.',
        ]
        for text in texts:
            assert set(suggest_type(text, text)) == set([
                Datatype(schema='bar'),
                Table(schema='bar')])


    def test_alter_column_type_suggests_types(self):
        q = 'ALTER TABLE foo ALTER COLUMN bar TYPE '
        assert set(suggest_type(q, q)) == set([
            Datatype(schema=None),
            Table(schema=None),
            Schema()])


    def test_identifier_suggests_types_in_parentheses(self):
        texts = [
            'CREATE TABLE foo (bar ',
            'CREATE TABLE foo (bar DOU',
            'CREATE TABLE foo (bar INT, baz ',
            'CREATE TABLE foo (bar INT, baz TEXT, qux ',
            'CREATE FUNCTION foo (bar ',
            'CREATE FUNCTION foo (bar INT, baz ',
            'SELECT * FROM foo() AS bar (baz ',
            'SELECT * FROM foo() AS bar (baz INT, qux ',

            # make sure this doesnt trigger special completion
            'CREATE TABLE foo (dt d',
        ]
        for text in texts:
            assert set(suggest_type(text, text)) == set([
                Datatype(schema=None),
                Table(schema=None),
                Schema()])


    def test_alias_suggests_keywords(self):
        texts = [
            'SELECT foo ',
            'SELECT foo FROM bar ',
            'SELECT foo AS bar ',
            'SELECT foo bar ',
            'SELECT * FROM foo AS bar ',
            'SELECT * FROM foo bar ',
            'SELECT foo FROM (SELECT bar '
        ]
        for text in texts:
            suggestions = suggest_type(text, text)
            assert suggestions ==(Keyword(),)


    def test_invalid_sql(self):
        # issue 317
        text = 'selt *'
        suggestions = suggest_type(text, text)
        assert suggestions ==(Keyword(),)


    def test_suggest_where_keyword(self):
        # https://github.com/dbcli/mycli/issues/135
        texts = [
            'SELECT * FROM foo where created > now() - ',
            'select * from foo where bar ',
        ]
        for text in texts:
            suggestions = suggest_type(text, text)
            assert set(suggestions) == self.cols_etc('foo', last_keyword='WHERE')


    def test_named_query_completion(self):
        test_args = [
            ('\\ns abc SELECT ', 'SELECT ', [
                Column(table_refs=(), qualifiable=True),
                Function(schema=None),
                Keyword('SELECT')
            ]),
            ('\\ns abc SELECT foo ', 'SELECT foo ', (Keyword(),)),
            ('\\ns abc SELECT t1. FROM tabl1 t1', 'SELECT t1.', [
                Table(schema='t1'),
                View(schema='t1'),
                Column(table_refs=((None, 'tabl1', 't1', False),)),
                Function(schema='t1')
            ])
        ]
        for arg in test_args:
            text = arg[0]
            before = arg[1]
            expected = arg[2]
            suggestions = suggest_type(text, before)
            assert set(expected) == set(suggestions)


    def test_select_suggests_fields_from_function(self):
        suggestions = suggest_type('SELECT  FROM func()', 'SELECT ')
        assert set(suggestions) == self.cols_etc(
            'func', is_function=True, last_keyword='SELECT')


    def test_leading_parenthesis(self):
        sqls = [
            '(',
        ]
        for sql in sqls:
            # No assertion for now; just make sure it doesn't crash
            suggest_type(sql, sql)


    def test_ignore_leading_double_quotes(self):
        sqls = [
            'select * from "',
            'select * from "foo',
        ]
        for sql in sqls:
            suggestions = suggest_type(sql, sql)
            assert FromClauseItem(schema=None) in set(suggestions)


    def test_column_keyword_suggests_columns(self):
        sqls = [
            'ALTER TABLE foo ALTER COLUMN ',
            'ALTER TABLE foo ALTER COLUMN bar',
            'ALTER TABLE foo DROP COLUMN ',
            'ALTER TABLE foo DROP COLUMN bar',
        ]
        for sql in sqls:
            suggestions = suggest_type(sql, sql)
            assert set(suggestions) == set([
                Column(table_refs=((None, 'foo', None, False),)),
            ])


    def test_handle_unrecognized_kw_generously(self):
        sql = 'SELECT * FROM sessions WHERE session = 1 AND '
        suggestions = suggest_type(sql, sql)
        expected = Column(table_refs=((None, 'sessions', None, False),), \
            qualifiable=True)
        assert expected in set(suggestions)


    def test_keyword_after_alter(self):
        sqls = [
            'ALTER ',
            'ALTER TABLE foo ALTER ',
        ]
        for sql in sqls:
            assert Keyword('ALTER') in set(suggest_type(sql, sql))
