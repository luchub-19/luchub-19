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
| Radio | Tĩnh, tự chọn bài. Đã có: LUCHUB FM 19.11, HUMBLE. / Wow. / Goodbyes |

### Quyết định đợt 5 (sau phản hồi v1)
- Bố cục các mục dưới banner/HUD: **áp phích nhân vật kiểu Rockstar `Only in Leonida`** (ảnh nền + hình cắt tiền cảnh + hook + tiểu sử ngôi thứ ba + câu thoại), dùng cho chủ repo và từng dự án.
- Nội dung giới thiệu: **chỉ dùng dữ liệu repo công khai** (không bịa thông tin cá nhân). Chủ repo đã duyệt nguyên văn các câu hiện có (xem mục 6).
- Ảnh thật: **Claude tự chụp vibeKing đang chạy**. Đã build trong thư mục tạm của session (raylib 5.5 + CMake, không cài vào hệ thống);
  cần `xvfb` + `xdotool` (apt, chủ repo chạy sudo) để chạy ở màn hình ảo, tránh đụng desktop thật. Sprite `atlas.png` của game là Kenney CC0 (khử màu), dùng làm hình cắt được.
- Thẻ CLASSIFIED: **giữ nhưng làm đẹp hơn** (hồ sơ mật có chủ đích, không lộ tên dự án riêng tư).

## 3. Phản hồi của chủ repo về bản v1 (QUAN TRỌNG)
> "nhìn nó bị AI và không có chiều sâu gì cả. chưa được đầu tư gì, như kiểu làm qua loa."

Chẩn đoán của Claude (đồng ý với phản hồi):
1. **Bố cục là chồng thẻ giống nhau**: mọi mục là một hộp tối bo góc + viền hồng + tiêu đề số. Đúng kiểu template.
2. **Phẳng, không có lớp**: không tiền cảnh/hậu cảnh, không ánh sáng, không hạt phim, không texture.
3. **Nội dung là chữ chung chung Claude tự viết**, không có chi tiết thật của chủ repo (không câu chuyện, không sở thích thật, không ảnh/clip dự án thật).
4. **Còn chỗ trống chưa điền** (radio), thẻ CLASSIFIED là chỗ độn. (Cả hai đã xử lý ở v2, xem mục 6.)
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
tên đài radio trong game, app trên điện thoại, font logo. Dùng màu và font tự chọn (Anton + Barlow, bảng màu ở mục 6).

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
data/radio.json           Danh sách bài radio (bài thật do chủ repo chọn)
tools/shots/*.jpg         Ảnh chụp thật của vibeKing (nhúng base64 vào SVG). KHÔNG đưa ảnh desktop đầy đủ vào đây
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

## 6. Hiện trạng (kết thúc session 2026-11-27)
**Trên profile công khai (README, theo thứ tự):** banner → 01 PLAYER ONE (hồ sơ) → 02 PLAYER STATUS (HUD) → 03 MISSIONS (vibeKing + Classified) → 04 LOADOUT → 05 RADIO → ảnh rắn + dòng "fan-made, không liên kết Rockstar/Take-Two".
Tất cả theo kiểu áp phích/cảnh nhiều lớp (nền + hình cắt tiền cảnh + hook + bio + thoại), không còn hộp thẻ giống nhau.

| File | Nội dung |
|---|---|
| `banner.svg` | Cảnh nhiều lớp: trời/mây/mặt trời, skyline xa mờ, biển, logo `LUCHUB-19` có quang sai màu, đường + đèn đường + xe chạy, đàn chim chữ V, cọ tiền cảnh che một phần chữ, vignette + hạt phim. Tagline tự gõ 3 câu |
| `h-*.svg` | 5 dải tiêu đề chương (`chapter()`), gradient riêng từng chương, tiêu đề lệch trái/phải xen kẽ |
| `poster-profile.svg` | Hồ sơ: bóng người đội mũ trùm trong khung lục giác (`figure_scene()`), thẻ tin nhắn nổi trượt vào sau 1 giây |
| `hud.svg` | HUD đặt trên cảnh phố: thanh hồng/cyan/tím kèm biểu tượng, tiền xếp chồng, 6 sao truy nã nhấp nháy, minimap, dòng mục tiêu tính từ số commit còn thiếu. Tự cập nhật hằng ngày |
| `poster-vibeking.svg` | Nền = cảnh combat thật làm mờ; hình cắt = boss Sentinel trong khung lục giác nổi. Link tới repo vibeKing |
| `poster-classified.svg` | Hồ sơ mật: thanh đen, ổ khóa, con dấu CLASSIFIED. Che dự án riêng tư, không link |
| `loadout.svg` | 4 tấm xiên (C/C++, Python, TypeScript, Linux), chữ lớn tràn khung |
| `poster-radio.svg` | Mặt đài FM (`dial_scene()`) kim chạy + equalizer; bài từ `data/radio.json` |

**Chữ ĐÃ được chủ repo duyệt nguyên văn (2026-11-27) — đừng đổi nếu không được yêu cầu:**
hook hồ sơ "Wants clean code. The bugs have other plans.", thoại "Works on my machine." / "One more commit.", thẻ tin nhắn "Find me on GitHub. Messages answered at the speed of a compile.",
bio hồ sơ, bio vibeKing + thoại "Kill the medic first." / "Insert coin.", Classified ("Clearance required", "Some missions never make the credits."), 3 tagline banner, "SELECT YOUR WEAPON" + 4 chú thích loadout, tên đài "LUCHUB FM 19.11".
Hook "Hold the last line" lấy từ menu game vibeKing.

**Ghi chú kỹ thuật đã rút ra:**
- Ảnh chụp vibeKing: build game (raylib 5.5, CMake) trong thư mục tạm, chạy `HOME=<tạm> xvfb-run -a -s "-screen 0 1280x720x24" space_invaders --scene=combat|boss|menu --capture=out.png --capture-frame=240 --lang=en --quality=high`.
  Đây là cảnh trình diễn dựng sẵn, không phải ván chơi thật (README đã ghi chú). Sprite Kenney CC0. Máy cần `xvfb` (đã cài).
- Kích thước ảnh gốc khai báo trong `SHOT_DIMS` (build_assets.py); thêm ảnh mới phải thêm vào đó. Ảnh nhúng ≈ 50–70KB mỗi cái; tránh nhúng cùng ảnh hai lần ở độ phân giải đầy đủ.
- Bio hồ sơ chỉ dựa trên repo công khai: vibeKing (raylib), didau (Hangout Planner), sway-ultricing (SwayFX rice, shell tự viết), dsa-web1.0 (StudyOS).
- Đã bỏ vì không có căn cứ công khai: "Rust" (suy ra từ repo riêng tư), "Bots, sockets" (ám chỉ repo riêng tư), biển neon trên mái nhà (bị che hết, không đọc được).
- Script patch dùng `sed s#SCR#...#` từng làm hỏng chữ `TYPESCRIPT`; dùng placeholder không trùng chữ trong nội dung.
- Bảng màu tự chọn (không phải màu chính thức của game): PINK #FF3E8A, HOT #FF5C7A, ORANGE #FF9A3C, GOLD #FFD35A, PURPLE #7B3FE4, CYAN #35E6D8, nền #140729 / #0B0320.
- Khi chụp màn hình desktop thật: **luôn làm sạch và xem lại ảnh trước khi commit** (lần chụp đầu để lộ Discord, Firefox, cửa sổ làm việc nên đã xóa). Quy trình dùng được: `wmctrl -k on` → mở kitty sạch chạy `fastfetch --structure ...` (bỏ LocalIp/Host/Terminal)
  → `gnome-screenshot -f` → `wmctrl -k off`; che chi tiết riêng tư bằng `ffmpeg delogo` (tên thành phố của widget thời tiết, số tin chưa đọc Discord). Không đưa ảnh đầy đủ (có `user@hostname`, phần cứng) vào repo. Cửa sổ Cloudflare One Client tự ẩn khi mất focus.

## 7. Câu hỏi MỞ cho chủ repo
- Bộ đếm lượt xem: có chấp nhận một dịch vụ ngoài không? (chưa làm)
- Rice chính ở laptop: mô tả đúng là gì (WM/compositor, shell, điểm đặc biệt)? `sway-ultricing` chỉ là một phần.
- Có muốn thêm poster riêng cho dự án công khai khác (`sway-ultricing`, `didau`, `dsa-web1.0`) làm nhiệm vụ mới không?
- Giới thiệu bản thân sâu hơn (đang học/làm gì, vài điều ít ai đoán ra) — chỉ viết khi chủ repo cung cấp.

## 8. Việc còn lại
- **Chủ repo kiểm tra trên GitHub thật**: nền sáng/tối, điện thoại, và hiệu ứng SMIL có chạy không. Chưa ai xác nhận trên trang thật (mới xem bằng Chrome trong máy). Phản hồi này quyết định sửa gì tiếp.
- **Chương Safehouse (rice chính) — CHỜ.** Rice chính nằm ở laptop, nhiều lớp, chưa có repo chính thức; ảnh thật chưa có. Một lần đã đưa áp phích từ PC (Mint LTS, ít tùy biến) lên với câu "rebuilt by hand" → sai, đã gỡ. Đừng đưa lại ảnh PC này.
  Chỉ làm khi có (a) ảnh thật đã làm sạch từ laptop và (b) chủ repo mô tả. Không link `sway-ultricing` như thể nó là toàn bộ rice; không link repo `rice` (riêng tư).
- Nếu GitHub không hiển thị tốt SMIL/mix: phương án dự phòng là xuất GIF hoặc ảnh tĩnh cho phần quan trọng (chưa làm).
- Nếu sửa ảnh mà trang vẫn hiện bản cũ: thêm `?v=N` vào URL ảnh trong README (camo cache).
