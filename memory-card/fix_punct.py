# -*- coding: utf-8 -*-
"""Convert half-width punctuation adjacent to CJK chars into full-width.

Rules:
- , : ; ? !  -> full-width when the char immediately before or after is CJK
- ( ) pairs  -> full-width when either side of the pair, or the inner edge, touches CJK
Code-only contexts (CSS values, JS syntax) are untouched because they never
neighbor CJK characters.
"""
import sys

SIMPLE = {',': '，', ':': '：', ';': '；', '?': '？', '!': '！'}


def is_cjk(ch):
    return '一' <= ch <= '鿿'


def convert(text):
    res = list(text)
    n = len(res)
    for i, c in enumerate(res):
        if c in SIMPLE:
            prev = res[i - 1] if i > 0 else ''
            nxt = res[i + 1] if i < n - 1 else ''
            if (prev and is_cjk(prev)) or (nxt and is_cjk(nxt)):
                res[i] = SIMPLE[c]
    opens = []
    for i in range(n):
        ch = res[i]
        if ch == '(':
            opens.append(i)
        elif ch == ')' and opens:
            j = opens.pop()
            before = res[j - 1] if j > 0 else ''
            after = res[i + 1] if i + 1 < n else ''
            inner_l = res[j + 1] if j + 1 < n else ''
            inner_r = res[i - 1] if i > 0 else ''
            if any(c and is_cjk(c) for c in (before, after, inner_l, inner_r)):
                res[j] = '（'
                res[i] = '）'
    return ''.join(res)


for path in sys.argv[1:]:
    with open(path, encoding='utf-8') as f:
        src = f.read()
    dst = convert(src)
    if dst != src:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(dst)
    changed = sum(1 for a, b in zip(src, dst) if a != b)
    print(f'{path}: {changed} chars converted, fullwidth-comma={dst.count(chr(0xff0c))}')
