#!/usr/bin/env python3
"""Sinh depiction gốc của Sileo từ `packages.json`.

Sileo đọc `SileoDepiction:` như **JSON**, không phải HTML. Trỏ nó vào
`package.html` thì Sileo không dựng được gì — đó là lỗi có thật trong control
trước 1.16.2, và triệu chứng là trang gói trống trơn trong Sileo mà không báo
lỗi gì.

Sinh từ `packages.json` chứ không viết tay: mô tả và nhật ký đã nằm ở đó cho
trang web, và hai bản chép tay là hai bản sẽ nói hai phiên bản khác nhau.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LANGS = ("en", "vi")


def heading(text):
    """Tiêu đề một dòng. `DepictionLabelView` vừa đúng việc này."""
    return {"class": "DepictionLabelView", "text": text,
            "fontWeight": "bold", "usePadding": True}


def paragraph(lines):
    """Đoạn văn nhiều dòng.

    **Không dùng `DepictionLabelView`.** Lớp đó là nhãn MỘT DÒNG: gặp câu dài
    nó cắt cụt bằng dấu ba chấm thay vì xuống dòng. Đo trên máy 24/09 — mọi câu
    mô tả trong Sileo đều đứt giữa chừng. `DepictionMarkdownView` mới bọc chữ
    theo bề ngang màn hình.
    """
    return {"class": "DepictionMarkdownView",
            "markdown": "\n\n".join(lines),
            "useSpacing": True}


def details_tab(package, lang):
    views = [{"class": "DepictionSubheaderView", "title": package["name"]}]
    # Gom các câu liền nhau thành MỘT khối markdown; tiêu đề tách riêng.
    # Mỗi câu một view thì khoảng cách giữa chúng doãng ra rất xa.
    buffer = []
    for line in package["description"][lang]:
        if line.rstrip().endswith(":"):
            if buffer:
                views.append(paragraph(buffer))
                buffer = []
            views.append(heading(line))
        else:
            buffer.append(line)
    if buffer:
        views.append(paragraph(buffer))
    views.append({"class": "DepictionSeparatorView"})
    views.append({"class": "DepictionTableTextView", "title": "Identifier",
                  "text": package["id"]})
    views.append({"class": "DepictionTableTextView", "title": "Version",
                  "text": package["version"]})
    views.append({"class": "DepictionTableTextView", "title": "Compatibility",
                  "text": package["compatibility"][lang]})
    return views


def changelog_tab(package, lang):
    views = []
    for entry in package.get("changelog", []):
        views.append({"class": "DepictionSubheaderView",
                      "title": f"{entry['version']}  ·  {entry.get('date', '')}".strip(" ·")})
        # Một khối markdown cho cả danh sách: Sileo tự dựng bullet và tự bọc chữ.
        views.append({"class": "DepictionMarkdownView",
                      "markdown": "\n".join("- " + note for note in entry["notes"][lang]),
                      "useSpacing": True})
        views.append({"class": "DepictionSeparatorView"})
    return views or [heading("—")]


def build(package, lang):
    return {
        "minVersion": "0.1",
        "class": "DepictionTabView",
        "tabs": [
            {"tabname": "Details" if lang == "en" else "Chi tiết",
             "class": "DepictionStackView", "views": details_tab(package, lang)},
            {"tabname": "Changelog" if lang == "en" else "Nhật ký",
             "class": "DepictionStackView", "views": changelog_tab(package, lang)},
        ],
    }


def main():
    data = json.loads((ROOT / "packages.json").read_text(encoding="utf-8"))
    out = ROOT / "sileo"
    out.mkdir(exist_ok=True)
    written = []
    for package in data["packages"]:
        for lang in LANGS:
            name = f"{package['id']}.{lang}.json" if lang != "en" else f"{package['id']}.json"
            path = out / name
            path.write_text(json.dumps(build(package, lang), ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
            written.append(name)
    print("\n".join(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
