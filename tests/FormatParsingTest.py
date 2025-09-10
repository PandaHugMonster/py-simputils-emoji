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

	def test_combining(self):
		emoji = Emoji("1F9D1")
		assert len(emoji) == 1
		assert emoji.is_combined is False
		assert f"{emoji}" == "🧑"
		assert repr(emoji) == "1F9D1"
		assert len(emoji.filtered) == 0

		emoji = emoji * "1F9B3"
		assert len(emoji) == 3
		assert emoji.is_combined is True
		assert f"{emoji}" == "🧑‍🦳"
		assert repr(emoji) == "1F9D1 200D 1F9B3"
		assert len(emoji.filtered) == 0

		emoji = emoji + "1F9B3"
		assert len(emoji) == 4
		assert emoji.is_combined is True
		assert f"{emoji}" == "🧑‍🦳🦳"
		assert repr(emoji) == "1F9D1 200D 1F9B3 1F9B3"
		assert len(emoji.filtered) == 0

		emoji = emoji - "1F9B3" - Emoji("200d")
		assert len(emoji) == 1
		assert emoji.is_combined is False
		assert f"{emoji}" == "🧑"
		assert repr(emoji) == "1F9D1"
		assert len(emoji.filtered) == 2

		emoji = emoji.compact()
		assert len(emoji) == 1
		assert emoji.is_combined is False
		assert f"{emoji}" == "🧑"
		assert repr(emoji) == "1F9D1"
		assert len(emoji.filtered) == 0
