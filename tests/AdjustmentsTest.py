from simputils.emoji.components.Emoji import Emoji
from simputils.emoji.samples.enums.ColourEmojiEnum import ColourEmojiEnum


class AdjustmentsTest:

	def test_simple_filtered(self):
		codes = ["🧑", "200d", "\U0001F9B3"]
		filtered = ["\u200d", "1F9B3"]
		emoji = Emoji(*codes, filtered=filtered)
		assert repr(emoji) == "1F9D1"

	def test_simple_replaced(self):
		codes = ["🧑", "200d", "\U0001F9B3"]
		replaced = {"\u200D": ColourEmojiEnum.LARGE_BLUE_SQUARE, "1F9B3": ColourEmojiEnum.LARGE_YELLOW_SQUARE}
		emoji = Emoji(*codes, replaced=replaced)
		assert f"{emoji}" == "🧑🟦🟨"

	def test_callback_filtered(self):
		def callback(char: str, *args):
			return char == "🧑"

		codes = ["🧑", "200d", "\U0001F9B3"]
		emoji = Emoji(*codes, filtered=callback)
		assert repr(emoji) == "1F9D1"

	def test_callback_replaced(self):
		def callback(char: str, *args):
			return ColourEmojiEnum.LARGE_GREEN_CIRCLE if char != "🧑" else char

		codes = ["🧑", "200d", "\U0001F9B3"]
		emoji = Emoji(*codes, replaced=callback)
		assert str(emoji) == "🧑🟢🟢"

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

