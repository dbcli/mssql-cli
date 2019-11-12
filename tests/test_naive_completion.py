from __future__ import unicode_literals
import unittest
from prompt_toolkit.completion import Completion
from prompt_toolkit.document import Document
from mock import Mock
import mssqlcli.mssqlcompleter as mssqlcompleter

class NaiveCompletionTests(unittest.TestCase):

    def test_empty_string_completion(self):
        completer = self.get_completer()
        complete_event = self.get_complete_event()
        text = ''
        position = 0
        actual = list(
            completer.get_completions(
                Document(text=text, cursor_position=position),
                complete_event
            )
        )
        actual = list(filter(lambda e: e.display_meta_text == 'keyword', actual))
        actual = set(map(lambda e: e.text, actual))
        expected = set(completer.keywords_tree.keys())
        assert actual == expected

    def test_select_keyword_completion(self):
        completer = self.get_completer()
        complete_event = self.get_complete_event()
        text = 'SEL'
        position = len('SEL')
        actual = list(
            completer.get_completions(
                Document(text=text, cursor_position=position),
                complete_event,
            )
        )
        expected = [Completion(text='SELECT', start_position=-3, display_meta="keyword")]
        assert self.equals(actual, expected)

    def test_function_name_completion(self):
        completer = self.get_completer()
        complete_event = self.get_complete_event()
        text = 'SELECT MA'
        position = len('SELECT MA')
        actual = list(
            completer.get_completions(
                Document(text=text, cursor_position=position),
                complete_event
            )
        )
        expected = [Completion(text='MAX', start_position=-2, display_meta="function")]
        assert self.equals(actual, expected)

    def test_column_name_completion(self):
        completer = self.get_completer()
        complete_event = self.get_complete_event()
        text = 'SELECT  FROM users'
        position = len('SELECT ')
        actual = list(
            completer.get_completions(
                Document(text=text, cursor_position=position),
                complete_event
            )
        )
        actual = set(map(lambda e: e.text, actual))
        expected = set(completer.keywords_tree.keys())
        expected.update(completer.functions)
        assert actual == expected

    def test_paths_completion(self):
        completer = self.get_completer()
        complete_event = self.get_complete_event()
        text = r'\i '
        position = len(text)
        actual = list(
            completer.get_completions(
                Document(text=text, cursor_position=position),
                complete_event
            )
        )
        expected = [Completion(text="setup.py", start_position=0, display_meta="")]
        assert self.contains(actual, expected)

    def test_alter_well_known_keywords_completion(self):
        completer = self.get_completer()
        complete_event = self.get_complete_event()
        text = 'ALTER '
        position = len(text)
        actual = list(
            completer.get_completions(
                Document(text=text, cursor_position=position),
                complete_event
            )
        )
        expected = [
            Completion(text="DATABASE", display_meta='keyword'),
            Completion(text="TABLE", display_meta='keyword')
        ]
        assert self.contains(actual, expected)
        not_expected = [Completion(text="CREATE", display_meta="keyword")]
        assert not self.contains(actual, not_expected)

    @staticmethod
    def get_completer():
        return mssqlcompleter.MssqlCompleter(smart_completion=True)

    @staticmethod
    def get_complete_event():
        return Mock()

    @staticmethod
    def equals(completion_list1, completion_list2):
        if len(completion_list1) != len(completion_list2):
            return False
        for e1 in completion_list1:
            theSame = None
            for e2 in completion_list2:
                if (e1.text == e2.text
                        and e1.start_position == e2.start_position
                        and e1.display_meta_text == e2.display_meta_text):
                    theSame = e2
                    break
            if theSame is None:
                return False
        return True

    @staticmethod
    def contains(completion_list1, completion_list2):
        for e2 in completion_list2:
            theSame = None
            for e1 in completion_list1:
                if (e2.text == e1.text
                        and e2.start_position == e1.start_position
                        and e2.display_meta_text == e1.display_meta_text):
                    theSame = e1
                    break
            if theSame is None:
                return False
        return True
