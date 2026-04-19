import pytest

from fixtures import test_data_value_formats
from simputils.emoji.components.Emoji import Emoji


class FormatParsingTest:

	@pytest.mark.parametrize(
		"format,expected_code,expected_data,expected_len",
		test_data_value_formats.data
	)
	def test_value_formats(
		self,
		format,
		expected_code,
		expected_data,
		expected_len
	):
		emoji = Emoji(format)
		assert expected_code == repr(emoji)
		assert expected_data == str(emoji)
		assert expected_len == len(emoji)
