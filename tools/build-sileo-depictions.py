#!/usr/bin/env python3
"""Sinh depiction gốc của Sileo từ `packages.json`.

Khuôn lấy từ template chính thức `TweakiOS/Sidia`, không tự bịa:

    { "minVersion": "0.1", "tintColor": "...",
      "tabs": [ { "tabname": "Details", "views": [ ... ] } ] }

Ba điểm bản tự viết trước đây làm sai:

* Đặt `"class": "DepictionTabView"` ở cấp cao nhất và `"DepictionStackView"`
  trên từng tab. Khuôn chuẩn **không có** `class` ở cả hai chỗ.
* Dùng `DepictionLabelView` cho đoạn văn. Lớp đó là nhãn MỘT DÒNG: câu dài bị
  cắt cụt bằng ba chấm chứ không xuống dòng. Đo trên máy 24/09.
* Bỏ hẳn đường JSON sau khi đổi sang `DepictionMarkdownView` — nên bản markdown
  chưa từng được chạy thử.

Sinh từ `packages.json` chứ không viết tay: mô tả và nhật ký đã nằm ở đó cho
trang web, và hai bản chép tay là hai bản sẽ nói hai phiên bản khác nhau.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TINT = "#0a84ff"


BASE = "https://pitroytech.github.io/repo/"


def describe(lines):
    """Mô tả thành MỘT khối markdown, cùng quy tắc với package.html.

    Dòng kết thúc bằng ":" là tiêu đề `##`, dòng "- " là ý trong danh sách,
    còn lại là đoạn văn. Một khối duy nhất như depiction của Irisin
    (apt.owngoal.dev): Sileo tự dựng bullet, tự bọc chữ, và khoảng cách giữa
    các phần đều nhau. Nhiều view rời thì khoảng cách doãng ra.
    """
    out = []
    for line in lines:
        if line.startswith("- "):
            if out and not out[-1].startswith("- "):
                out.append("")
            out.append(line)
        else:
            if out:
                out.append("")
            out.append("## " + line.rstrip()[:-1] if line.rstrip().endswith(":") else line)
    return "\n".join(out)


def details_tab(package):
    # Bố cục theo Irisin: tagline in đậm, "Description", thân markdown,
    # rồi bảng "Information". Banner nằm ở `headerImage` của gốc.
    views = [{"class": "DepictionSubheaderView", "title": package["tagline"], "useBoldText": True},
             {"class": "DepictionHeaderView", "title": "Description"},
             {"class": "DepictionSeparatorView"},
             {"class": "DepictionMarkdownView", "markdown": describe(package["description"]),
              "useSpacing": True},
             {"class": "DepictionHeaderView", "title": "Information"},
             {"class": "DepictionSeparatorView"}]
    rows = [("Version", package["version"]), ("Price", package["price"]),
            ("Compatibility", package["compatibility"]), ("Developer", "PitroyTech"),
            ("Identifier", package["id"])]
    if package.get("availability"):
        rows.append(("Availability", package["availability"]))
    if package.get("older"):
        rows.append(("Also on the repo", package["older"]["version"]))
    views += [{"class": "DepictionTableTextView", "title": title, "text": text}
              for title, text in rows]
    for link in package.get("links", []):
        views.append({"class": "DepictionTableButtonView",
                      "title": link["label"], "action": link["url"]})
    return views


def changelog_tab(package):
    # Mỗi bản: tên bản bên trái, ngày bên phải (alignment 2), rồi các ý.
    views = []
    for entry in package.get("changelog", []):
        views.append({"class": "DepictionLayerView", "views": [
            {"class": "DepictionLabelView", "text": f"{package['name']} {entry['version']}",
             "fontWeight": "bold", "fontSize": 16},
            {"class": "DepictionLabelView", "text": entry.get("date", ""),
             "fontWeight": "semibold", "fontSize": 16, "textColor": "#696969", "alignment": 2},
        ]})
        views.append({"class": "DepictionMarkdownView",
                      "markdown": "\n".join("- " + note for note in entry["notes"])})
        views.append({"class": "DepictionSeparatorView"})
    return views or [{"class": "DepictionMarkdownView", "markdown": "No changelog yet."}]


def build(package):
    # Gốc PHẢI có `class`, và mỗi tab cũng vậy.
    #
    # Template Sidia bỏ cả hai, và với khuôn đó Sileo không dựng gì — đo trên
    # máy 24/09, trang gói rơi về `Description:` thô. Template ấy từ 2019.
    #
    # Khuôn dưới đây là khuôn ĐÃ dựng được trên chính máy này ở lần thử đầu;
    # cái sai lần đó chỉ là dùng `DepictionLabelView` cho đoạn văn, vốn là nhãn
    # một dòng nên cắt cụt mọi câu dài. Thân bài nay là markdown.
    return {
        "minVersion": "0.1",
        "class": "DepictionTabView",
        "tintColor": TINT,
        **({"headerImage": BASE + package["banner"]} if package.get("banner") else {}),
        "tabs": [
            {"tabname": "Details", "class": "DepictionStackView",
             "views": details_tab(package)},
            {"tabname": "Changelog", "class": "DepictionStackView",
             "views": changelog_tab(package)},
        ],
    }


def main():
    data = json.loads((ROOT / "packages.json").read_text(encoding="utf-8"))
    out = ROOT / "sileo"
    out.mkdir(exist_ok=True)
    for package in data["packages"]:
        path = out / f"{package['id']}.json"
        path.write_text(json.dumps(build(package), ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
        print(path.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
