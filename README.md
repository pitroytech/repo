# PitroyTech — kho tweak

Nguồn: `https://pitroytech.github.io/repo/`

Tweak miễn phí. Bản trả phí bán trên Havoc.

## Thêm nguồn

Sileo hoặc Zebra → Nguồn → thêm → dán địa chỉ trên.

## Cấu trúc

    debs/         gói .deb
    Packages      chỉ mục, sinh tự động từ debs/
    Release       mô tả kho
    index.html    trang chủ
    package.html  trang chi tiết, đọc ?id=
    packages.json dữ liệu cho hai trang trên

`Packages` do GitHub Actions sinh lại mỗi khi `debs/` đổi. Đừng sửa tay: nó
phải khớp từng byte với file thật, và một chỉ mục lệch thì Sileo chỉ báo
"package not found" mà không nói lệch ở đâu.
