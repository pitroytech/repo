#!/usr/bin/env python3
"""Viết đè `Description:` trong `Packages` bằng nội dung trong `descriptions/`.

Sileo hiện trường `Description:` thô ngay trên trang gói. Trường đó nằm trong
`.deb`, nên sửa nó bình thường là phải build lại tweak rồi chờ mọi người cập
nhật — trong khi thứ cần đổi chỉ là mấy dòng chữ.

Các gói đang phục vụ được đóng từ trước, và mô tả trong đó còn **song ngữ** cùng
một địa chỉ email không muốn công khai nữa. Hai khối ngôn ngữ nối lại thành một
mảng chữ dài trên trang gói của Sileo.

Nên chép đè ở đây: chỉ mục là thứ Sileo đọc, và nó được dựng lại mỗi lần đẩy.
Gói nào không có file mô tả thì giữ nguyên trường cũ.

Định dạng Debian: dòng đầu là tóm tắt, mọi dòng sau phải bắt đầu bằng **một dấu
cách**, và dòng trống được viết là một dấu chấm. File nguồn viết bằng văn xuôi
thường; hàm dưới lo phần thụt lề.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FOLDER = ROOT / "descriptions"


def as_field(text):
    lines = [line.rstrip() for line in text.strip().splitlines()]
    body = "\n".join(" " + (line if line else ".") for line in lines[1:])
    return f"Description: {lines[0]}" + (f"\n{body}" if body else "")


def rewrite(index_text):
    blocks = []
    replaced = 0
    for block in index_text.split("\n\n"):
        if not block.strip():
            continue
        block = block.rstrip("\n")
        name = re.search(r"^Package: (\S+)$", block, re.M)
        source = FOLDER / f"{name.group(1)}.txt" if name else None
        if source and source.is_file():
            # Trường `Description` kéo dài tới dòng tiếp theo KHÔNG bắt đầu bằng
            # dấu cách. Cắt đúng vùng đó rồi thay, để không đụng trường khác.
            new = as_field(source.read_text(encoding="utf-8"))
            block, count = re.subn(r"^Description:.*?(?=^\S|\Z)", new + "\n",
                                   block + "\n", flags=re.S | re.M)
            block = block.rstrip("\n")
            replaced += count
        blocks.append(block)
    return "\n\n".join(blocks) + "\n", replaced


def main(argv):
    path = pathlib.Path(argv[1] if len(argv) > 1 else "Packages")
    result, count = rewrite(path.read_text(encoding="utf-8"))
    path.write_text(result, encoding="utf-8")
    print(f"{count} stanza rewritten")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
