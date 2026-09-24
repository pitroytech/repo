#!/usr/bin/env python3
"""Chèn lại `SileoDepiction:` vào `Packages`.

`dpkg-scanpackages` **vứt trường này**. Nó chỉ chép ra những trường nó biết, và
`SileoDepiction` là phần mở rộng riêng của Sileo — `Depiction`, `Name`,
`Author`, `Icon` qua được, còn nó thì không.

Gói `.deb` vẫn mang trường ấy, nhưng Sileo duyệt kho đọc `Packages` chứ không
mở từng gói, nên depiction gốc không bao giờ tới nơi. Đo trên máy 24/09: Sileo
hiện `Description:` thô và báo "không có nhật ký", trong khi Zebra — vốn dùng
`Depiction:` HTML — hiển thị bình thường.

Lấy tên từ chính `Package:` của mỗi khối, nên giá trị không thể lệch với tên
file trong `sileo/`. Khối nào đã có sẵn trường này thì để yên.
"""
import pathlib
import re
import sys

BASE = "https://pitroytech.github.io/repo/sileo"


def inject(text):
    blocks = []
    for block in text.split("\n\n"):
        if not block.strip():
            continue
        block = block.rstrip("\n")
        name = re.search(r"^Package: (\S+)$", block, re.M)
        if name and not re.search(r"^SileoDepiction:", block, re.M):
            block += f"\nSileoDepiction: {BASE}/{name.group(1)}.json"
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
