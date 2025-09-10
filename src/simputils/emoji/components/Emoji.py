import re
import unicodedata
from collections.abc import Callable
from copy import copy

from simputils.emoji.abstract.AbstractEmojiObject import AbstractEmojiObject
from simputils.emoji.exceptions.WrongEmojiHexValue import WrongEmojiHexValue

_non_code_pattern = re.compile(r"[^0-9a-fA-F]+", re.MULTILINE)
_space_optimizer_pattern = re.compile(r"\s+")


class Emoji(AbstractEmojiObject):

	_data: list[str] = None
	_filtered: list[str] | Callable = None
	_replaced: dict[str, str] | Callable = None

	def __init__(
		self,
		*values: "str | Emoji",
		filtered: list[str] | Callable = None,
		replaced: dict[str, str] | Callable = None
	):
		data = []
		for value in values:
			sub_data = self._prepare_data(value)
			if sub_data:
				data.extend(sub_data)

		self._data = data

		self._filtered = list()
		self._replaced = {}

		if filtered:
			if callable(filtered):
				self._filtered = filtered
			else:
				sub = []
				for value in filtered:
					sub.extend(self._prepare_data(value))
				self._filtered = sub

		if replaced:
			if callable(replaced):
				self._replaced = replaced
			else:
				sub = {}
				for x, y in replaced.items():
					target = "".join(self._prepare_data(x))
					substitution = "".join(self._prepare_data(y))
					sub[target] = substitution
				self._replaced = sub

	@property
	def filtered(self) -> list[str] | Callable:
		return self._filtered

	@property
	def replaced(self) -> dict[str, str] | Callable:
		return self._replaced

	@classmethod
	def _prepare_data(cls, input: "str | Emoji") -> list[str] | None:
		res = []
		# NOTE  Cleaning up and splitting single string by spaces
		values = cls._normalize_values(input)
		for value in values:
			if cls._is_codes(value):
				# NOTE  string represents hex-textual values separated by space
				value = cls._str_code_to_char(value)
			res.append(value)

		return res

	@classmethod
	def _is_codes(cls, val: str):
		res = not _non_code_pattern.findall(val.replace(" ", ""))
		return res

	@classmethod
	def _normalize_values(cls, val: "str | Emoji") -> list[str]:
		if isinstance(val, cls):
			return val.raw_data
		return _space_optimizer_pattern.sub(" ", val).strip(" ").split(" ")

	@classmethod
	def _str_code_to_char(cls, val: str):
		res = None
		try:
			hex_val = int(val, 16)
			res = chr(hex_val)
		except ValueError:
			raise WrongEmojiHexValue(f"\"{val}\" cannot be parsed as unicode hex representation of emoji.")
		return res

	@classmethod
	def _char_to_str_code(cls, val: str):
		return str(hex(ord(val)).replace("0x", "")).upper()

	@property
	def raw_data(self) -> list[str] | None:
		return self._data

	def description(self, is_processed: bool = True) -> tuple[tuple[str, str, str], ...]:
		"""
		Returns description of components of the emoji
		in format `(hex_val, name, category)`
		:return:
		"""
		res = []
		codes = self._processed_data() if is_processed else self._data
		for char in codes:
			hex_val = f"0x{self._char_to_str_code(char)}"
			try:
				row = (hex_val, unicodedata.name(char), unicodedata.category(char))
			except Exception:
				row = (hex_val, None, None)
			res.append(row)

		return tuple(res)

	def explain(self) -> str:
		res = "All codes:\n"
		for hex_val, name, category in self.description(False):
			res = f"{res}\n" if res else res
			res += f"{hex_val} | {name} | {category}"
		if self._filtered:
			res += f"\nFiltered: {self._filtered}"
		if self._replaced:
			res += f"\nReplaced: {self._replaced}"
		return res

	@classmethod
	def lookup(cls, *names: str) -> "Emoji":
		res = []
		for name in names:
			char = unicodedata.lookup(name)
			res.append(cls._char_to_str_code(char))

		em = cls(*res)

		return em

	@classmethod
	def range(cls, from_val: str, to_val: str) -> "Emoji":
		from_val = ord(cls._prepare_data(from_val)[0])
		to_val = ord(cls._prepare_data(to_val)[0])
		context = [chr(i) for i in range(from_val, to_val + 1)]
		res = Emoji(*context)
		return res

	def split(self) -> tuple["Emoji", ...]:
		res = []
		for char in self._data:
			res.append(self.__class__(char))
		return tuple(res)

	def _processed_data(self) -> tuple[str, ...]:
		res = []
		for char in self._data:
			if callable(self._filtered):
				if not self._filtered(self, char, None):
					continue
			elif len(char) == 0 or char in self._filtered:
				continue
			if callable(self._replaced):
				char = self._replaced(self, char)
			elif char in self._replaced:
				char = self._replaced[char]
			if isinstance(char, self.__class__):
				char = char.compact().raw_data[0]
			res.append(char)
		return tuple(res)

	@property
	def is_combined(self) -> bool:
		return len(self) > 1

	def __len__(self) -> int:
		return len(self._processed_data())

	def __str__(self):
		return "".join(self._processed_data())

	def __repr__(self):
		data = self._processed_data()
		return " ".join([self._char_to_str_code(char) for char in data])

	def __add__(self, other: "str | Emoji") -> "Emoji":
		filtered = copy(self._filtered)
		replaced = copy(self._replaced)
		return self.__class__(
			self,
			other,
			replaced=replaced,
			filtered=filtered
		)

	def __sub__(self, other: "str | Emoji") -> "Emoji":
		filtered = copy(self._filtered)
		replaced = copy(self._replaced)
		data = self.raw_data
		if isinstance(filtered, Callable):
			sub_res = []
			for char in data:
				other = Emoji(other)
				if not filtered(self, str(char), other.raw_data):
					continue
				sub_res.append(char)
			data = sub_res
		else:
			filtered.extend(self._prepare_data(other))
		return self.__class__(
			*data,
			replaced=replaced,
			filtered=filtered
		)

	def __mul__(self, other: "str | Emoji") -> "Emoji":
		filtered = copy(self._filtered)
		replaced = copy(self._replaced)
		return self.__class__(
			self,
			"200D",
			other,
			replaced=replaced,
			filtered=filtered
		)

	def compact(self, remove_replaced: bool = True, remove_filtered: bool = True) -> "Emoji":
		"""
		Applying replacements and filtering to raw-data,
		what will filter and replace final values and create a new emoji object.

		Optionally getting rid of modifiers "replaced" and "filtered" (by default True)
		:return:
		"""
		data = self._processed_data()

		filtered = self.filtered if not remove_filtered else None
		replaced = self.replaced if not remove_replaced else None

		res = self.__class__(*data, filtered=filtered, replaced=replaced)

		return res

	def __eq__(self, other: "str | list | Emoji"):
		left = self
		right = other
		if isinstance(other, list | tuple):
			right = " ".join(other)
		right: str | Emoji
		right: Emoji = self.__class__(right)

		return left.raw_data == right.raw_data
