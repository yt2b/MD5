#!/usr/bin/env python
import sys
import math
import copy
from typing import Callable


MAX_INT32 = 0xffffffff
T = [int(2 ** 32 * abs(math.sin(i))) for i in range(1, 65)]
S = sum([a * 4 for a in [[7, 12, 17, 22], [5, 9, 14, 20], [4, 11, 16, 23], [6, 10, 15, 21]]], [])
IDX_FUNCS = [lambda i: i, lambda i: (5 * i + 1) % 16, lambda i: (3 * i + 5) % 16, lambda i: (7 * i) % 16]


def convert_to_bytes(x: int, n: int) -> bytes:
    """整数をnバイトのバイト配列(リトルエンディアン)に変換する"""
    return (x).to_bytes(n, "little")


def get_padding_len(len_input: int) -> int:
    """
    パディングの長さ(バイト数)を返す
    「インプット+パディング」の長さが「64の倍数 - 8」になるように計算する
    """
    return 64 - (len_input + 8) % 64


def get_padding_bytes(len_input: int) -> bytes:
    """
    パディングのバイト配列を返す
    先頭1バイトのみ0x80で後は0x00で埋める
    """
    len_padding = get_padding_len(len_input)
    return convert_to_bytes(0x80, len_padding)


def split_bytes(ary: bytes, length: int) -> list[bytes]:
    """バイト配列をlengthごとに区切る"""
    return [ary[i: i + length] for i in range(0, len(ary), length)]


def convert_to_ints(ary: bytes) -> list[int]:
    """バイト配列を4バイトごとに整数に変換する"""
    return [int.from_bytes(ary[i:i+4], "little") for i in range(0, len(ary), 4)]


def rotate_left_bit(x: int, n: int) -> int:
    """nビット左にシフトする"""
    return ((x << n) | (x >> (32 - n))) & MAX_INT32


def F(x: int, y: int, z: int) -> int:
    """1ラウンド目に行う演算処理"""
    return (x & y) | (~x & z)


def G(x: int, y: int, z: int) -> int:
    """2ラウンド目に行う演算処理"""
    return (x & z) | (y & ~z)


def H(x: int, y: int, z: int) -> int:
    """3ラウンド目に行う演算処理"""
    return x ^ y ^ z


def I(x: int, y: int, z: int) -> int:
    """4ラウンド目に行う演算処理"""
    return y ^ (x | ~z)


def calculate(func: Callable[[int, int, int], int], a: int, b: int, c: int, d: int, x: int, t: int, s: int) -> int:
    """メインの演算処理"""
    a = (a + func(b, c, d) + x + t) & MAX_INT32
    return (rotate_left_bit(a, s) + b) & MAX_INT32


def move_right(l: list) -> list:
    """リストの各要素を1つ右に移動させる"""
    return [l[len(l) - 1]] + l[:len(l) - 1]


def get_joined_hex(results: list[int]) -> str:
    """配列内の数値を16進数に変換して結合させる"""
    return "".join([convert_to_bytes(r, 4).hex() for r in results])


def md5(input_bytes: bytes) -> str:
    """MD5のハッシュを返す"""
    len_input = len(input_bytes)
    padding_bytes = get_padding_bytes(len_input)
    tail_bytes = convert_to_bytes(len_input * 8, 8)
    message = input_bytes + padding_bytes + tail_bytes  # 長さは必ず64の倍数になる
    results = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476]  # 演算結果の初期値
    # メッセージを64バイトのブロックに分割し、各ブロックに対して演算処理を行う
    for block in split_bytes(message, 64):
        ints = convert_to_ints(block)
        buf = copy.copy(results)
        idx = 0
        # 演算処理を16回=1ラウンドとして4ラウンド行う
        # 各ラウンド毎にfunc, idx_funcは変わる
        for func, idx_func in zip([F, G, H, I], IDX_FUNCS):
            for i in range(16):
                (a, b, c, d), x, t, s = buf, ints[idx_func(i)], T[idx], S[idx]
                buf[0] = calculate(func, a, b, c, d, x, t, s)
                buf = move_right(buf)
                idx += 1
        # 演算結果をresultsに加算する
        for i, x in enumerate(buf):
            results[i] = (results[i] + x) & MAX_INT32
    # 演算結果を16進数文字列に変換して結合させる
    return get_joined_hex(results)


def main():
    if len(sys.argv) == 1:
        print("文字列を指定してください")
        sys.exit(1)
    print(md5(sys.argv[1].encode("utf-8")))


if __name__ == "__main__":
    main()
