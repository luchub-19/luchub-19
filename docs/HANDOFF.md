# HANDOFF — README profile GTA VI (đọc file này trước khi sửa)

Repo: `luchub-19/luchub-19` (công khai). Thư mục máy: `~/luchub-19-profile`. Cập nhật lần cuối: 2026-11-27.
File này là nguồn sự thật cho các session sau. Đọc xong là biết: mục tiêu, đã quyết gì, đã làm gì, sai ở đâu, làm gì tiếp.

## 1. Mục tiêu và ràng buộc của chủ repo
- Profile GitHub "đẹp, thú vị, ấn tượng, sinh động" theo chất **GTA VI** (không phải GTA IV — chủ repo đã sửa).
  GTA VI đã phát hành **19/11/2026** (PS5, Xbox Series X|S; chưa thấy nguồn về PC).
- Chủ repo là người Việt, yêu cầu **trả lời bằng tiếng Việt**; README viết **tiếng Anh**.
- Muốn được **hỏi nhiều câu ở nhiều giai đoạn** để xác nhận ngữ cảnh, và muốn tham khảo nhiều nguồn uy tín.
- **Luật cứng:** không thêm Claude làm co-author (không `Co-Authored-By`, không "Generated with Claude Code").
  Commit dùng email noreply: `237688683+luchub-19@users.noreply.github.com` (cấu hình riêng cho repo này, không dùng email git global).
- **Không link hay nhắc tên repo riêng tư** trên README công khai (xem danh sách repo riêng tư trong memory cục bộ của Claude, không ghi ở đây).
  Kiểm tra bằng `gh repo view <repo> --json isPrivate` trước khi link bất kỳ repo nào.
- Liên hệ công khai: chỉ GitHub (không email, không mạng xã hội).

## 2. Quyết định đã xác nhận với chủ repo
| Mục | Chọn |
|---|---|
| Mục đích | Khoe cá tính, làm cho vui |
| Ngôn ngữ README | Tiếng Anh |
| Phong cách | Hoàng hôn trailer (hồng, cam, tím, cyan) |
| Nội dung | Giới thiệu, tech stack, dự án nổi bật, thống kê GitHub |
| Khung ý tưởng | Poster + logo, điện thoại trong game, chỉ số nhân vật (HUD), chọn nhiệm vụ |
| Hoạt ảnh | Vừa phải |
| Widget | Tự sinh bằng GitHub Actions (không phụ thuộc dịch vụ ngoài) |
| Món phụ | Radio, rắn ăn contribution, bộ đếm lượt xem (**bộ đếm chưa làm**: cần dịch vụ ngoài) |
| Tên trên logo | `luchub-19` |
| Giọng văn | Ngầu, ngắn gọn |
| Tech stack | C/C++, Python, TypeScript, Linux |
| Sao truy nã | Theo số commit 30 ngày (1/10/30/60/100/200 commit → 1..6 sao) |
| Radio | Tĩnh, tự chọn bài (**chưa có bài nào, đang là chỗ trống**) |

### Quyết định đợt 5 (sau phản hồi v1)
- Bố cục các mục dưới banner/HUD: **áp phích nhân vật kiểu Rockstar `Only in Leonida`** (ảnh nền + hình cắt tiền cảnh + hook + tiểu sử ngôi thứ ba + câu thoại), dùng cho chủ repo và từng dự án.
- Nội dung giới thiệu: **chỉ dùng dữ liệu repo công khai, đánh dấu chỗ cần chủ repo xác nhận** (không bịa thông tin cá nhân). Chủ repo sẽ duyệt.
- Ảnh thật: **Claude tự chụp vibeKing đang chạy**. Đã build trong thư mục tạm của session (raylib 5.5 + CMake, không cài vào hệ thống);
  cần `xvfb` + `xdotool` (apt, chủ repo chạy sudo) để chạy ở màn hình ảo, tránh đụng desktop thật. Sprite `atlas.png` của game là Kenney CC0 (khử màu), dùng làm hình cắt được.
- Thẻ CLASSIFIED: **giữ nhưng làm đẹp hơn** (hồ sơ mật có chủ đích, không lộ tên dự án riêng tư).

## 3. Phản hồi của chủ repo về bản v1 (QUAN TRỌNG)
> "nhìn nó bị AI và không có chiều sâu gì cả. chưa được đầu tư gì, như kiểu làm qua loa."

Chẩn đoán của Claude (đồng ý với phản hồi):
1. **Bố cục là chồng thẻ giống nhau**: mọi mục là một hộp tối bo góc + viền hồng + tiêu đề số. Đúng kiểu template.
2. **Phẳng, không có lớp**: không tiền cảnh/hậu cảnh, không ánh sáng, không hạt phim, không texture.
3. **Nội dung là chữ chung chung Claude tự viết**, không có chi tiết thật của chủ repo (không câu chuyện, không sở thích thật, không ảnh/clip dự án thật).
4. **Còn chỗ trống chưa điền** (3 bài radio), thẻ CLASSIFIED là chỗ độn.
5. Chữ HUD/UX đặt ngẫu hứng, không bám sát UI game thật.
6. Biểu tượng tech stack chỉ là chữ cái trong vòng tròn.

## 4. Nghiên cứu đã làm (kèm độ tin cậy)
**Xác minh được:**
- Rockstar giữ lại font **Pricedown**, minimap, sao truy nã, màn hình Wasted; có nút D-pad ẩn/hiện HUD
  (Stuart Petri qua TechRadar, được Leonida Bay trích lại — thứ cấp). https://leonidabay.com/en/blog/gta-6-hud-map
- Hội thoại điện thoại là **thẻ tin nhắn nổi** trên cảnh game, không phải màn hình điện thoại toàn khung.
  Đây là cách người viết SixCentral đọc video Extended Look, không phải Rockstar nói. https://sixcentral.co.uk/news/gta-6-hud-interface-explained
- Thanh trạng thái màu hồng/cyan/tím kèm biểu tượng; hai số tiền xếp chồng góc trên phải; menu đồ có ô tròn
  (nguồn: cùng bài SixCentral, cách đọc của tác giả). Nhãn UI viết hoa, ngắn, thực dụng.
- Trang Rockstar `/VI/only-in-leonida`: mỗi nhân vật là một khối **ảnh nền + ảnh cắt tiền cảnh** (tên file `Hero_BG`/`Hero_FG`),
  một câu hook, đoạn tiểu sử ngôi thứ ba, vài **câu thoại trích dẫn**. Giọng khô, noir, ngắn.
  Ví dụ (công khai trên trang): "Another day in paradise, right?", "Viral videos. Viral hooks.", "Experience counts."
  Các URL `/cal`, `/boobie`, `/vice-city` trả cùng một tài liệu khi fetch (có thể do JS) — chưa chắc là trang riêng.
- Sao truy nã tối đa 6 sao (hướng dẫn bên thứ ba, chưa chắc).
- Màu trailer: hồng, cam, lavender, cyan; trailer 2 thêm xanh lá; kiến trúc Art Deco gắn với hồng (bài phân tích bên thứ ba).

**KHÔNG xác minh được (đừng khẳng định):** mã màu hex chính xác, hình học HUD (vị trí/độ mờ/viền), animation sao nhấp nháy,
tên đài radio trong game, app trên điện thoại, font logo. Bản v1 dùng màu và font tự chọn (xem mục 6).

**Kỹ thuật README (suy luận, cần test trên repo thử):**
- `<picture>` với `prefers-color-scheme` để có bản sáng/tối. Chưa test.
- SVG qua `<img>` không chạy script, không tải font ngoài → chữ phải thành path (đang làm vậy). SMIL: đã thấy chạy OK trên Chrome khi xem file
  trực tiếp; **chưa xác nhận trên trang GitHub thật** — chủ repo cần kiểm tra bằng mắt.
- camo cache theo URL: sửa SVG xong mà ảnh cũ không đổi thì thêm `?v=2` vào URL trong README.
- Không có link bấm được bên trong SVG; link phải bọc `<a><img></a>` ở README. Vùng bấm riêng lẻ trong một ảnh là chưa hỗ trợ (chưa test image-map).
- Ý tưởng nổi bật trong cộng đồng: GIF/pixel pet phản ứng theo commit, rắn ăn contribution (đang có), ảnh dither động,
  đài nhạc Spotify tự commit, bài blog qua RSS. Mẫu "typing + capsule + stats + badge" xếp chồng = bị coi là template.

## 5. Kiến trúc hiện tại
```
README.md                 HTML thuần (div/img/table), ảnh tương đối assets/*.svg + ảnh rắn từ nhánh output
assets/*.svg              SINH RA TỰ ĐỘNG — đừng sửa tay
tools/build_assets.py     Sinh tất cả SVG. Chữ → path bằng fontTools. Bảng màu ở đầu file.
tools/fetch_stats.py      GraphQL → data/stats.json (commit 30 ngày, ngày hoạt động, đóng góp năm)
tools/preview.py          Xem thử cục bộ bằng Chrome headless (đặt mốc thời gian SMIL)
tools/fonts/              Anton (tiêu đề), Barlow Regular/SemiBold/Bold (chữ nhỏ). Giấy phép OFL kèm theo.
data/stats.json           Số liệu (Actions ghi đè mỗi ngày)
data/radio.json           Danh sách bài radio (đang là placeholder)
.github/workflows/update.yml   Cron 03:17 UTC: fetch + build + commit; job snake → nhánh `output`
CLAUDE.md                 Luật cho AI trong repo này
```
Chạy cục bộ (máy không có fontTools sẵn):
```
python3 -m venv /tmp/v && /tmp/v/bin/pip install fonttools
cd ~/luchub-19-profile
python3 tools/fetch_stats.py luchub-19          # dùng `gh auth token`
/tmp/v/bin/python tools/build_assets.py
python3 tools/preview.py 6 /tmp/preview.png     # xem ảnh bằng Read
```
Lưu ý khi chạy Actions: số liệu Actions (GITHUB_TOKEN) có thể lệch số cục bộ vì quyền xem đóng góp riêng tư khác nhau;
sau mỗi lần push, Actions sẽ ghi đè `assets/hud.svg` — luôn `git pull --rebase` trước khi push.
Workflow có `concurrency` để hai lượt chạy không tranh nhánh `output`/`main`.

## 6. Hiện trạng và điểm yếu cụ thể
**v2 một phần (2026-11-27):** `banner.svg` và `hud.svg` đã dựng lại nhiều lớp (trời/mây/mặt trời/skyline xa mờ → biển → logo có quang sai màu →
đường, đèn đường có quầng sáng, xe chạy, đàn chim → cọ tiền cảnh che một phần chữ → vignette + hạt phim). HUD đặt trên cảnh phố, bố cục theo mục 4
(thanh hồng/cyan/tím kèm biểu tượng, tiền xếp chồng, sao truy nã, minimap, dòng mục tiêu tính từ số commit còn thiếu).
**Áp phích nhiệm vụ (xong lần 1):** `poster-vibeking.svg` (nền = cảnh combat thật của vibeKing làm mờ + phủ màu, hình cắt = boss Sentinel trong khung lục giác nổi)
và `poster-classified.svg` (hồ sơ mật: thanh đen che chữ, ổ khóa, con dấu CLASSIFIED, không lộ tên dự án riêng tư). Hàm `poster()` trong `build_assets.py`.
Ảnh chụp game nằm ở `tools/shots/*.jpg` (nhúng base64 vào SVG vì SVG qua `<img>` không tải được file ngoài). Cách chụp lại (không đụng desktop):
`HOME=<thư mục tạm> xvfb-run -a -s "-screen 0 1280x720x24" space_invaders --scene=combat|boss|menu --capture=out.png --capture-frame=240 --lang=en --quality=high`
(game build từ repo vibeKing với raylib 5.5 build bằng CMake trong thư mục tạm). Đây là cảnh trình diễn dựng sẵn của game, không phải ván chơi thật — README đã ghi chú.
**Chữ chưa được chủ repo duyệt (Claude tự viết):** hook hồ sơ "Wants clean code. The bugs have other plans.", câu thoại "Works on my machine." / "One more commit.", thẻ tin nhắn "Find me on GitHub. Messages answered at the speed of a compile.", "SELECT YOUR WEAPON", cùng các chữ bên dưới.
Chữ trong áp phích (hook "Hold the last line" lấy từ menu game; bio và câu thoại "Kill the medic first." / "Insert coin." / "Some missions never make the credits." do Claude viết từ README và game) **chưa được chủ repo duyệt**.
**Làm xong lần 2 (cùng ngày):** toàn bộ README đã theo kiểu áp phích/cảnh: `poster-profile.svg` (hồ sơ nhân vật: bóng người đội mũ trùm trong khung lục giác + thẻ tin nhắn nổi — thay mục Phone cũ),
`loadout.svg` (4 tấm xiên, chữ lớn tràn khung — thay Inventory cũ), 4 dải tiêu đề chương `h-*.svg` (hàm `chapter()`: gradient riêng từng chương, skyline, tiêu đề lệch trái/phải xen kẽ).
**Radio đã gỡ khỏi README** vì chưa có bài thật (không để placeholder công khai). `radio()` vẫn còn trong code, tự dựng lại khi `data/radio.json` có bài thật (tiêu đề không bắt đầu bằng "Your track") — nhớ thêm lại mục vào README.
**Sửa nội dung không có căn cứ công khai:** bỏ "Rust" khỏi tagline/hồ sơ (chỉ suy ra từ repo riêng tư, chủ repo không chọn); chú thích Python đổi thành "Scripts and automation" (bản cũ "Bots, sockets" ám chỉ repo riêng tư).
Bio hồ sơ chỉ dựa trên repo công khai: vibeKing (raylib), didau (Hangout Planner, TypeScript), sway-ultricing (SwayFX rice, shell tự viết), dsa-web1.0 (StudyOS).
Đã thử và bỏ: biển neon "LUCHUB" trên mái nhà (bị chữ logo và cọ che hết, không đọc được).
Bảng màu tự chọn (chưa phải màu chính thức của game): PINK #FF3E8A, HOT #FF5C7A, ORANGE #FF9A3C, GOLD #FFD35A, PURPLE #7B3FE4, CYAN #35E6D8, nền #140729 / #0B0320.
Điểm yếu cần sửa (xếp theo tác động):
Bảng màu tự chọn: PINK #FF3E8A, HOT #FF5C7A, ORANGE #FF9A3C, GOLD #FFD35A, PURPLE #7B3FE4, CYAN #35E6D8, nền #140729 / #0B0320.
Các SVG: banner (1200×440), 5 tiêu đề mục, phone, hud, mission-1, mission-2 (CLASSIFIED), inventory, radio.
Điểm yếu cần sửa (xếp theo tác động):
1. Thiếu nội dung thật của chủ repo (xem mục 7 — phải HỎI, không được bịa).
2. Các mục dưới banner/HUD vẫn là hộp giống nhau → cần phá nhịp: các khối khác kích thước, chồng lấp, không phải hộp nào cũng viền hồng.
3. Thiếu chiều sâu: tách lớp BG/FG (logo nằm *giữa* các lớp, cọ/tiền cảnh che một phần chữ), khí quyển (xa mờ, gần đậm), hạt phim, flare, quang sai màu.
4. HUD chưa giống game: bám theo mục 4 (thanh hồng/cyan/tím kèm biểu tượng, tiền xếp chồng, nhãn ngắn viết hoa, thẻ tin nhắn nổi).
5. Chưa có ảnh chụp/clip thật của dự án (Space Invaders chạy thật…).
6. Chưa kiểm tra trên GitHub thật (nền sáng/tối, di động).
7. Chưa làm bộ đếm lượt xem; radio chưa có bài.

**Chương 05 Safehouse (desktop rice thật):** `poster-safehouse.svg`. Chụp bằng `gnome-screenshot` sau `wmctrl -k on` (thu nhỏ hết cửa sổ), mở một kitty chạy `fastfetch --structure ...` (bỏ LocalIp/Host/Terminal), rồi `wmctrl -k off`.
Làm sạch bằng `ffmpeg delogo` (tên thành phố của widget thời tiết, số tin chưa đọc trên icon Discord). Ảnh đầy đủ **không** đưa vào repo (có `user@hostname`, phần cứng); chỉ `tools/shots/rice-desktop-bg.jpg` (640px, làm mờ khi vẽ) và `rice-desktop-fg.jpg` (cắt logo Mint).
Lần chụp đầu để lộ Discord, Firefox và cửa sổ làm việc nên đã xóa; **luôn làm sạch và xem lại ảnh trước khi commit**. Cửa sổ Cloudflare One Client tự ẩn khi mất focus (không phải lỗi). Máy: X11, Linux Mint 22.3, Cinnamon 6.6.9, MacTahoe theme, Plank, kitty.
Repo `rice` là riêng tư nên áp phích không có liên kết.

## 7. Câu hỏi MỞ cho chủ repo (cần trả lời để có chiều sâu thật)
- Bạn là ai / đang học-làm gì (ví dụ trường, năm học)? Có muốn nhắc tới không?
- 3 điều thật về bạn mà người lạ không đoán ra (sở thích, thói quen code, sản phẩm tự hào nhất).
- Câu thoại/slogan kiểu nhân vật của bạn (ví dụ "Another day in paradise, right?" phiên bản của bạn).
- Ảnh/GIF thật của dự án công khai (vibeKing: chụp màn hình/GIF chơi game), ảnh desktop rice (nếu muốn khoe).
- 3+ bài radio và tên đài (hiện là "LUCHUB FM 19.11", tên do Claude đặt, chưa được duyệt). Mục Radio đang gỡ khỏi README cho tới khi có bài.
- Bộ đếm lượt xem: có chấp nhận một dịch vụ ngoài không?
- Màu/cỡ logo/tagline: hiện là "C++ • RUST • PYTHON", "GAMES • TOOLS • LINUX RICE", "COMMITS NEVER SLEEP" (Claude tự đặt).

## 8. Việc còn lại / hướng tiếp
- Chủ repo kiểm tra trên GitHub thật (nền sáng/tối, di động, SMIL có chạy không) và duyệt các chữ ở mục 6.
- Thêm radio khi có bài. Cân nhắc: bộ đếm lượt xem (dịch vụ ngoài), ảnh desktop rice thật (cần chủ repo cung cấp/đồng ý).
- Chỗ có thể sâu hơn: poster riêng cho `sway-ultricing` / `didau` nếu muốn thêm nhiệm vụ; ảnh chụp thật của chúng.
- Lưu ý khi viết script patch: `sed s#SCR#...#` từng làm hỏng chữ `TYPESCRIPT` — dùng placeholder không trùng chữ trong nội dung.

## 9. Hướng v2 ban đầu (tham khảo)
- Dựng cảnh nhiều lớp: BG (trời, mặt trời, skyline xa mờ) → logo → FG (cọ, lan can, xe chạy, đàn chim bay chữ V). Hạt phim và flare nhẹ.
- Bỏ khuôn "tiêu đề số + hộp"; mỗi mục một bố cục riêng, có phần lệch/chồng.
- HUD dựng lại theo mục 4. Điện thoại dựng theo thẻ tin nhắn nổi trên một khung cảnh, không phải ảnh điện thoại cố định.
- Mỗi nhân vật/dự án một khối kiểu Rockstar: ảnh nền + hình cắt + hook + đoạn tiểu sử ngôi thứ ba + 1–3 câu thoại — nhưng **nội dung phải do chủ repo cung cấp**.
- Kiểm tra: preview ở các mốc 0/2.4/6/12 giây, thu nhỏ độ rộng 400px (di động), nền sáng, rồi hỏi chủ repo xác nhận trên GitHub thật.
