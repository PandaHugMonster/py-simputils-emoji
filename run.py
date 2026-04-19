#!/bin/env python3
from simputils.emoji.components.Emoji import Emoji
from simputils.emoji.samples.enums.CommonEmojiEnum import CommonEmojiEnum

if __name__ == "__main__":
    em = Emoji(CommonEmojiEnum.ROCKET)

    print(f"{em} test")
