#!/usr/bin/env python3
"""Chèn lại `SileoDepiction:` vào `Packages`.

`dpkg-scanpackages` **vứt trường này**. Nó chỉ chép ra những trường nó biết, và
`SileoDepiction` là phần mở rộng riêng của Sileo — `Depiction`, `Name`,
`Author`, `Icon` qua được, còn nó thì không.

Và Sileo **không vẽ từ `Depiction:`** — đó là trường của Cydia với Zebra. Nó chỉ
vẽ từ `SileoDepiction`; khi URL đó trả HTML thì nó dựng webview, vốn tự bọc chữ
theo bề ngang máy. A/B trên cùng một máy 24/09:

    trỏ vào package.html  -> nhúng trang, chữ xuống dòng đủ
    trỏ vào .json         -> depiction gốc, cắt cụt mọi câu dài
    không khai            -> không nhúng gì, chỉ `Description:` thô

Chèn ở đây chứ không chỉ trong `control`: sửa control thì phải build lại gói và
người dùng phải cập nhật mới thấy. Chỉ mục thì chỉ cần làm mới nguồn.

Giá trị lấy từ chính `Package:` của mỗi khối, nên nó không thể lệch với `id`
mà trang đọc.
"""
import pathlib
import re
import sys

PAGE = "https://pitroytech.github.io/repo/package.html?id="


def inject(text):
    blocks = []
    for block in text.split("\n\n"):
        if not block.strip():
            continue
        block = block.rstrip("\n")
        name = re.search(r"^Package: (\S+)$", block, re.M)
        if name and not re.search(r"^SileoDepiction:", block, re.M):
            block += f"\nSileoDepiction: {PAGE}{name.group(1)}"
        blocks.append(block)
    return "\n\n".join(blocks) + "\n"


def main(argv):
    path = pathlib.Path(argv[1] if len(argv) > 1 else "Packages")
    result = inject(path.read_text(encoding="utf-8"))
    path.write_text(result, encoding="utf-8")
    print(f"{result.count('SileoDepiction:')} stanza có SileoDepiction")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
