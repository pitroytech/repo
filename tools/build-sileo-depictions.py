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


def markdown(text):
    return {"class": "DepictionMarkdownView", "markdown": text}


def details_tab(package):
    views = [markdown(f"## {package['name']}\n{package['tagline']}"),
             {"class": "DepictionSeparatorView"}]

    # Gom các câu liền nhau thành MỘT khối markdown, tiêu đề thành heading.
    # Mỗi câu một view thì khoảng cách giữa chúng doãng ra rất xa.
    buffer = []
    for line in package["description"]:
        if line.rstrip().endswith(":"):
            if buffer:
                views.append(markdown("\n\n".join(buffer)))
                buffer = []
            views.append({"class": "DepictionHeaderView", "title": line.rstrip(":")})
        else:
            buffer.append(line)
    if buffer:
        views.append(markdown("\n\n".join(buffer)))

    views.append({"class": "DepictionSeparatorView"})
    views.append({"class": "DepictionHeaderView", "title": "Details"})
    for title, text in [("Version", package["version"]),
                        ("Section", package["section"]),
                        ("Price", package["price"]),
                        ("Identifier", package["id"])]:
        views.append({"class": "DepictionTableTextView", "title": title, "text": text})
    views.append({"class": "DepictionTableTextView", "title": "Compatibility",
                  "text": package["compatibility"]})
    if package.get("older"):
        views.append({"class": "DepictionTableTextView", "title": "Also on the repo",
                      "text": package["older"]["version"]})

    for link in package.get("links", []):
        views.append({"class": "DepictionTableButtonView",
                      "title": link["label"], "action": link["url"]})
    return views


def changelog_tab(package):
    views = []
    for entry in package.get("changelog", []):
        heading = f"{entry['version']}  ·  {entry.get('date', '')}".strip(" ·")
        views.append({"class": "DepictionHeaderView", "title": heading})
        # Một khối markdown cho cả danh sách: Sileo tự dựng bullet và tự bọc chữ.
        views.append(markdown("\n".join("- " + note for note in entry["notes"])))
        views.append({"class": "DepictionSeparatorView"})
    return views or [markdown("No changelog yet.")]


def build(package):
    return {
        "minVersion": "0.1",
        "tintColor": TINT,
        "tabs": [
            {"tabname": "Details", "views": details_tab(package)},
            {"tabname": "Changelog", "views": changelog_tab(package)},
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
