import re
import unicodedata

from simputils.emoji.abstract.AbstractEmojiObject import AbstractEmojiObject
from simputils.emoji.exceptions.WrongEmojiHexValue import WrongEmojiHexValue


class Emoji(AbstractEmojiObject):

	_codes: tuple[str, ...]

	def __init__(self, *codes: str):
		self._codes = self._preprocess_codes(codes)

	def _preprocess_codes(self, codes: tuple[str, ...]):
		res = []
		for code in codes:
			sub = re.sub(r"\s+", " ", code).strip(" ")
			for val in sub.split(" "):
				try:
					hex_val = int(val, 16)
					str_hex_val = chr(hex_val)
					res.append(str_hex_val)
				except ValueError:
					raise WrongEmojiHexValue(f"\"{val}\" cannot be parsed as unicode hex representation of emoji.")
		return tuple(res)

	def data(self) -> tuple[tuple[str, str, str], ...]:
		"""
		Returns description of components of the emoji
		in format `(hex_val, name, category)`
		:return:
		"""
		res = []
		for char in self._codes:
			hex_val = hex(ord(char)).replace("0x", "").upper()
			hex_val = f"0x{hex_val}"
			try:
				row = (hex_val, unicodedata.name(char), unicodedata.category(char))
			except Exception:
				row = (hex_val, None, None)
			res.append(row)

		return tuple(res)

	def explain(self) -> str:
		res = ""
		for hex_val, name, category in self.data():
			res = f"{res}\n" if res else ""
			res += f"{hex_val} | {name} | {category}"
		return res

	def __len__(self) -> int:
		return len(self._codes)

	def __str__(self):
		return "".join(self._codes)

	def __repr__(self):
		return " ".join([hex(ord(c)).replace("0x", "").upper() for c in self._codes])
