# HANDOFF — README profile GTA VI (đọc file này trước khi sửa)

Repo: `luchub-19/luchub-19` (công khai). Thư mục máy: `~/luchub-19-profile`. Cập nhật lần cuối: 2026-11-28.
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

### Quyết định đợt v3 (2026-11-27, chỉ lập plan, chưa làm) — xem `docs/PLAN-v3.md`
Phản hồi: trang vẫn "bị AI, bóng bẩy bên ngoài nhưng rỗng và sơ sài"; xe và đèn ở banner ngược hướng.
Chốt: làm lại **toàn trang** theo kiểu **tranh minh họa Rockstar** (code thủ tục + hậu kỳ raster, không sinh ảnh AI), định dạng lai raster + SVG/SMIL,
banner **Ocean Drive lúc chạng vạng**, **không có người làm nhân vật chính** (kể chuyện bằng đồ vật; được có bóng người nhỏ ở xa), xe thể thao 80s,
logo xếp tầng có cảnh trong ruột chữ, thêm mission `didau`, hồ sơ = bàn làm việc cạnh cửa sổ, loadout = vòng chọn vũ khí + đồ vật minh họa, cả trang 3–5 MB.
**SMIL chạy tốt trên GitHub thật** (chủ repo xác nhận). Chủ repo không có ảnh game → dùng nguồn công khai.

### Quyết định sau T0.1 (2026-11-27)
- HUD v3: dưới 6 sao có **hàng icon bằng chứng** (kiểu CCTV/mặt/quần áo/xe/vũ khí), map sang số liệu GitHub công khai.
- Tiền trên HUD: **2 số, ngân hàng (tím) = contribution năm × 10, tiền mặt (xanh lá) = commit 30 ngày × 10** (thay cho cash + earned).
- Mặt tiền Art Deco: **giữ pastel**, thêm viền trắng và vài điểm vàng kim.

### Quyết định cho T1.1 (2026-11-27)
- Biển neon trên mặt tiền: **tên khách sạn tự đặt** (CORAL, SEAGLASS, LUNA, PALMETTO, SOLANA; tránh tên khách sạn thật ở Ocean Drive) + **một dấu riêng** `LUCHUB` (chữ dọc trên tháp) và `HOTEL` trên mái che.
- Chóp tháp giữa: **kiểu ống khói tàu neon** (REFERENCES D6), mũ bậc + cột cờ ngắn; không dùng chóp kim (D13 chưa có nguồn).
- Thêm ngoài danh sách bắt buộc: **góc bo Streamline (D7), phù điêu nhiệt đới (D9), sảnh terrazzo (D11)**.

### Quyết định cho T1.2 (2026-11-27)
- Xe chữ ký: **trắng, targa, sọc mảnh 2 màu (hồng + cam)**, trạng thái chính **đèn lật mở + bật, đang chạy**.

### Quyết định cho T1.4 (2026-11-27; PLAN mục G không có câu cho T1.4, chủ repo chốt trước khi vẽ)
- Kiểu biển: **chữ khối Tilt Neon + chữ viết tay một nét (Neonderthaw) + hình ống (icon) + viền khung/đèn chạy**.
- Nhấp nháy: **chữ hỏng chập chờn + khởi động lần lượt + bật/tắt cả biển (đối pha NO/VACANCY) + rung nhẹ độ sáng**.
- Chữ mẫu: tên khách sạn đã chốt + biển phụ chung chung (VACANCY, BAR, OPEN). Phần cứng: **đủ ở gần, giản lược ở xa**.

### Quyết định cho T1.5 (2026-11-28; PLAN mục G không có câu cho T1.5, chủ repo chốt trước khi vẽ)
- Mặt trời dẹt: **lộ qua khe giữa hai khách sạn** (phố cắt thẳng trục mặt trời, tháp xa che nửa dưới); thêm khung phụ chỉ có trời + nước nhìn về phía tây (vịnh Biscayne) để xem hình dẹt, **không dùng cho banner**.
- Mây: **tháp mây tích có khối + nét mực** (đáy phẳng, nắng thấp chiếu từ dưới lên), phía đông thêm mây vệt tầng thấp.
- Chòi cứu hộ: **3 mẫu, mỗi mẫu một dáng** (hộp mái nghiêng, mái chữ A có tia nắng, tháp lục giác), pastel + số hiệu nhỏ (số hiệu là tự đặt, REFERENCES D17).
- Kể chuyện bằng bóng nhỏ: **cặp đôi đi dạo + người trượt patin**, **người câu cá cuối cầu tàu**, **bồ nông lướt thấp trên sóng** (một con đậu cột đèn), **mòng biển nhỏ ở xa**. Đồ vật kể chuyện trên cát: dấu chân từ vỉa hè xuống nước + dép bỏ lại.

### Quyết định cho T0.2 (2026-11-27) — chi tiết ở `docs/STYLE.md`
- Bảng màu **lai: trời trên lạnh, chân trời ấm**; bóng lạnh, nắng ấm.
- Xanh lá **chỉ làm màu phụ** (cọ, nước nông, pastel bạc hà, tiền mặt HUD); không có neon xanh lá.
- Mặt trời **lặn sau dãy khách sạn** (đúng địa lý). Góc máy chuẩn: nhìn về phía bắc, khách sạn bên trái, biển bên phải.
- Font neon: **Tilt Neon** (OFL, `tools/fonts/TiltNeon-Variable.ttf`), chỉ cho biển hiệu trong cảnh.
- **T0.2 được duyệt toàn bộ ("duyệt ổn", 27/11)**: bảng màu, halftone ô 5 px/34%, nét 3/2/1/0 px, góc máy nhìn về bắc, vật cho dải tiêu đề chương, khung bản đồ/bưu thiếp cho didau, kiểu Pricedown viền mực + bóng đổ.
- Chủ repo muốn chữ "đậm chất GTA hơn" → dùng **Pricedown** (Typodermic, tải từ DaFont) cho logo/tiêu đề/hook. Điều này thay luật cũ "giữ Anton" ở REFERENCES H1.
  Theo EULA: font chỉ nằm ở `tools/fonts/local/` (gitignore), **không commit, không dùng trong Actions**, mỗi chuỗi chữ là một path cố định. Chi tiết: STYLE.md mục 5.4.

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
- Thanh trạng thái màu hồng/cyan/tím kèm biểu tượng; menu đồ có ô tròn
  (nguồn: cùng bài SixCentral, cách đọc của tác giả). Nhãn UI viết hoa, ngắn, thực dụng.
  **Đính chính (T0.1):** hai số tiền xếp chồng "15,150 / 700" nằm ở **màn trang bị**, không phải HUD ngoài phố. Xem `docs/REFERENCES.md` M3.

**Nghiên cứu sau phát hành (T0.1, 2026-11-27): xem `docs/REFERENCES.md`**. Mỗi điểm có link và độ tin cậy, kèm danh sách nguồn không đọc được
(IGN/Eurogamer chặn công cụ, GameSpot 403, Newswire chỉ có khung JS). Điểm mới đáng chú ý: lời dev Rockstar Stuart Petri qua TechRadar (Pricedown, minimap, sao, Wasted; HUD động),
6 sao có trạng thái rỗng/trắng/nhấp nháy/đỏ, icon bằng chứng dưới sao, cảnh sát không hiện trên minimap, MiMo không thuộc Ocean Drive, pastel là lớp sơn lại (Horowitz).
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
tools/build_assets.py     Điều phối: ghép cảnh (banner, chapter, hud, poster, loadout) và ghi SVG.
tools/art/                Thư viện vẽ (T0.3, tách nguyên văn từ build_assets): palette, geom, text (fontTools → path), sky, street, palm, car, props.
                          Chưa có deco/neon (thuộc T1.x). Import tương đối; chạy `python3 tools/build_assets.py` như cũ.
                          T0.4 thêm: `scene.py` (Scene 4 lượt col/sh/em/ln), `post.py` (bloom, halftone, viền mực raster, quang sai, LUT 3D, vignette, grain),
                          `render.py` (Chrome 2× song song, xuất WebP/JPEG theo ngân sách, nhúng base64, tile grain), `trial_t04.py` (sinh `lab/t04-pipeline/`).
                          Cần venv có fonttools + pillow + numpy; chưa nối vào build_assets (banner v3 sẽ dùng ở T2.3).
                          T1.1 thêm: `deco.py` (bộ sinh mặt tiền Art Deco, `Deco` + `facade()`, trả `Info` có điểm neo/chữ neon/cửa sổ cho hoạt ảnh),
                          `sample_t11.py` (sinh `docs/style/t11-deco.jpg`).
                          T1.2 thêm vào `car.py` (dưới hàm v2 `wheel`/`car`, giữ nguyên từng byte): `Car` + `sports_car()` trả `CarInfo`
                          (bánh, mắt đèn, đèn hậu, điểm neo), `car.defs()` (tiền tố `cr-`), `wheel_period()`; `sample_t12.py` (sinh `docs/style/t12-car.jpg`, `--anim` ra SVG động). `palette.py` có thêm bảng v3 (STYLE mục 1) + `tones()`, `LAYERS`; DEEP v3 tên là `SH_DEEP`.
                          T1.3 thêm vào `palm.py` (dưới hàm v2 `palm`, giữ nguyên): `Palm` + `palm_tree()` trả `PalmInfo` (3 loài coconut/royal/dwarf, 3 mức chi tiết theo `layer`,
                          viền nắng + viền neon `env`, SMIL 3 tầng cây/tán/tàu lá, `sway_t` dựng khung tĩnh); `sample_t13.py` (sinh `docs/style/t13-palm.jpg`, `--anim` ra SVG động).
                          T1.4 thêm: `neon.py` (`Sign`/`Line` + `sign()`, `icon()`, `frame()`; ống = lõi + thân + 3 quầng, raceway, trụ kẹp, boot điện cực, dây, biến áp, giá blade;
                          timeline nhấp nháy `TL` dùng chung cho khung tĩnh `t=` và SMIL `anim=True`; `glow=` theo ánh sáng nền), `sample_t14.py` (sinh `docs/style/t14-neon.jpg`, `--anim` ra SVG động).
                          Font mới: `tools/fonts/Neonderthaw-Regular.ttf` (OFL). `deco.py` CHƯA gọi `neon.py` (biển tối thiểu của T1.1 giữ nguyên để không đổi ảnh đã duyệt): nối ở T2.3 hoặc khi chủ repo yêu cầu.
                          T1.5 thêm: `sky.py` (dưới hàm v2 `clouds`/`birds`, giữ nguyên từng byte): `dome()` vòm trời lai + tham số `tod` (late/dusk/night, đêm có sao), `sun()` mặt trời dẹt có dải khói + chìm dưới chân trời,
                          `cumulus()` tháp mây (vành sáng dưới-trái, thân tím, halftone, viền mực theo lớp, `drift=` cho SMIL), `streaks()`, `gull()`, `pelican()` (4 tư thế, vỗ cánh SMIL, đậu);
                          `shore.py` (mới): `sea()` (hàng sóng theo phối cảnh + vệt phản chiếu neon, `t=` khung tĩnh hoặc SMIL, `parts=` tách raster/vector), `sand()` (mô cát, dấu chân, dép, cỏ đụn), `lifeguard()` (3 dáng `box|gable|hex`, 3 mức chi tiết), `pier()`, `fisherman()`;
                          `street.py` (dưới hàm v2 `skyline`/`lamp`, giữ nguyên): `ground()` (vỉa hè + bó vỉa + đường), `deco_lamp()` (đèn chập chờn tuỳ chọn, trả điểm đậu), `person()`/`couple()`/`skater()` (bóng đổ toả ra xa đèn), `far_towers()`;
                          `sample_t15.py` (sinh `docs/style/t15-sky-sea-street.jpg`, `--anim` ra SVG động). Palette không đổi (dùng lại v3); `PELICAN` (#2A1E4A) nằm ở `sky.py`.
tools/fetch_stats.py      GraphQL → data/stats.json (commit 30 ngày, ngày hoạt động, đóng góp năm)
tools/preview.py          Bảng ảnh cục bộ bằng Chrome headless: mỗi mốc SMIL một cột khổ 390 px, nền trắng (`--dark` cho nền tối)
tools/budget.py           Kiểm dung lượng: cả trang ≤ 5 MB, banner ≤ 1 MB (thoát mã 1 nếu vượt). Chỉ thư viện chuẩn
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
python3 tools/preview.py 0,2.4,6,12 /tmp/preview.png   # bảng 4 mốc, khổ 390px, nền trắng (xem bằng Read)
python3 tools/budget.py                        # kiểm ngân sách: cả trang ≤ 5 MB, banner ≤ 1 MB
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
- Đã chốt thêm `didau`; chưa làm `sway-ultricing`, `dsa-web1.0`. Các câu hỏi cho từng mốc của v3: xem PLAN-v3 mục G.
- Giới thiệu bản thân sâu hơn (đang học/làm gì, vài điều ít ai đoán ra) — chỉ viết khi chủ repo cung cấp.

## 8. Việc còn lại
- **Làm theo `docs/PLAN-v3.md`** (task + model gợi ý + mốc duyệt). T0.1 xong (`docs/REFERENCES.md`, chưa commit).
  T0.2 **xong, đã duyệt**: `docs/STYLE.md` + trang mẫu `docs/style/style-sample.jpg` (sinh bằng `tools/style_sample.py`, cần venv có fonttools + pillow + numpy;
  Pricedown ở `tools/fonts/local/` không commit; Tilt Neon đã ở `tools/fonts/`).
  T0.0 (hotfix xe) **xong, đã duyệt và commit riêng** (27/11): xe nêm mui trước dài, chùm đèn thấp từ mũi xe, đèn hậu trong thân, bánh trong làn, vạch đường đứng yên.
  T0.3 **xong**: 12 SVG giống hệt từng byte và 48 PNG (12 SVG × mốc 0/2.4/6/12 s) diff = 0 so với trước khi tách.
  T0.4 **xong, chủ repo đã xác nhận trên GitHub (27/11)**: SVG có nền WebP/JPEG nhúng (data URI) + SMIL hiển thị được qua `<img>`. Code ở `tools/art/scene.py`, `post.py`, `render.py`, `trial_t04.py`. Nhánh tạm `lab-t04` và thư mục `lab/` đã xoá; chạy `python tools/art/trial_t04.py` để sinh lại 3 SVG thử.
  T0.5 **xong**: `tools/preview.py` xuất bảng nhiều mốc (cột 390 px, nền trắng, `--dark`); `tools/budget.py` kiểm ngân sách (cả trang ≤ 5 MB, banner ≤ 1 MB, đo byte gốc, 1 MB = 1 MiB). Hiện trang ~0.95 MB, banner 91 KB, đạt. Ảnh rắn từ nhánh `output` không đo được.
  T1.1 **xong, đã duyệt và commit** (27/11), trang mẫu `docs/style/t11-deco.jpg`. Chạy lại: `<venv>/bin/python tools/art/sample_t11.py`.
  Lưu ý kỹ thuật: Chrome headless vẽ sai khi khung thấp (~112 px ra gần đen) → `sample_t11.run()` render khung ≥ 320 px rồi cắt.
  Neon trong `deco.py` là bản tối thiểu, T1.4 thay bằng `neon.py`. Chữ neon dọc ở cỡ nhỏ (k ≈ .5) hơi nhoè.
  T1.2 **xong, đã duyệt và commit** (27/11), trang mẫu `docs/style/t12-car.jpg`. Chạy lại: `<venv>/bin/python tools/art/sample_t12.py [--anim out.svg]`.
  Ghi chú T1.2: toạ độ xe cục bộ dài 200 (k = 1 → 200 px), mặt đường y = 0. Hông xe phản chiếu phía sau người xem (trời đông/biển) nên chỉ đúng
  khi máy quay ở phía biển; banner nhìn về bắc thì xe chạy dọc phố về điểm tụ — T2.1 cần quyết góc xe (ngang hay 3/4), bộ sinh hiện chỉ có nhìn ngang.
  Phản chiếu đường ướt dựng lại thân xe trong một Scene phụ (lượt màu) rồi lật gương. SVG động: xe vẽ bằng nét vector (raster_ink=False), không có halftone/viền mực raster.
  T1.3 **xong, đã duyệt và commit** (27/11), trang mẫu `docs/style/t13-palm.jpg`. Chạy lại: `<venv>/bin/python tools/art/sample_t13.py [--anim out.svg]`.
  Chủ repo chốt trước khi vẽ (27/11; PLAN mục G không có câu cho T1.3): thư viện **cọ dừa + cọ hoàng gia + cọ lùn**; màu lá **theo STYLE (gần INK + viền sáng)**; đung đưa **cả tán + từng tàu lá**.
  Ghi chú T1.3: một cây vector (L2, k ≈ 1) nặng khoảng 50 KB trong SVG động (đã dùng `<use>` cho viền và đường đi tương đối nguyên); 6 cây ≈ 300 KB, cân với ngân sách banner ≤ 1 MB.
  Cọ L0 mờ khí quyển 30% (ngoại lệ đã ghi ở STYLE 1.8). Lá khô rũ và quả dừa vẽ sau cùng nên che gốc tán.
  T1.4 **xong, đã duyệt và commit** (chủ repo "duyệt ổn", 28/11; 5 câu mốc 🔶 theo phương án trong mẫu: giữ 4 màu neon, panel, flamingo, deco.py chưa nối neon.py), trang mẫu `docs/style/t14-neon.jpg`. Chạy lại: `<venv>/bin/python tools/art/sample_t14.py [--anim out.svg]`.
  Ghi chú T1.4: chữ vẽ ở cỡ chuẩn 60 rồi co bằng `transform` (quầng và bộ lọc erode co theo). Biển trên mặt tiền cần **nền tối đỡ phía sau** (panel) mới đọc được trên nền cửa sổ; để biển trần chìm vào tường.
  SVG động thử: 4 biển vector ≈ 260 KB (cả file 359 KB với nền WebP); khi vào banner (≤ 1 MB, còn cọ + xe) nên bớt SMIL: bỏ `hum` ở biển nhỏ, gộp timeline.
  Chữ hỏng/khởi động dựng bằng `<animate opacity>` nhiều keyTimes (bước cứng cách 2 ms), cần xem trên GitHub thật khi vào banner.
  T1.5 **xong, đã duyệt và commit** (chủ repo "duyệt hết", 28/11; 5 câu mốc 🔶 theo phương án trong mẫu: giữ mặt trời dẹt 66%, bồ nông, tháp lục giác, cầu tàu, nét mây L1), trang mẫu `docs/style/t15-sky-sea-street.jpg` (9 phần: cảnh chính có đánh số 10 chi tiết bắt buộc, mặt trời dẹt ba độ cao, cận cảnh, 6 chòi, 4 mức chi tiết, người + chim, theo giờ, sóng 6 khung). Chạy lại: `<venv>/bin/python tools/art/sample_t15.py [--anim out.svg]`.
  Ghi chú T1.5: (1) **Lớp vector SMIL luôn nằm trên nền raster** nên bọt/bồ nông vector che luôn chòi và cọ đứng trước chúng. Khi dựng banner (T2.3/T2.4) cần tách nền raster làm hai lớp
  (sau: trời + biển; trước: vật đứng trên biển, WebP có alpha) rồi kẹp lớp SMIL ở giữa, hoặc chỉ làm bọt tĩnh. SVG động thử 196 KB (nền WebP ~160 KB + vector 17 KB); chưa đưa mây trôi, đung đưa cọ, người đi, cờ, đèn chập chờn vào.
  (2) Cảnh chính theo cách "sân khấu 2.5D" đã duyệt ở STYLE: khách sạn nhìn thẳng, biển bên phải cùng đường chân trời; phố cắt dựng bằng hình thang hội tụ về mặt trời. T2.1 quyết bố cục thật.
  (3) Hình bồ nông ở cỡ nhỏ ổn, ở cỡ lớn (k ≥ 3) còn hơi "vịt" (thân mập); cầu tàu là hình thang phối cảnh, đọc rõ nhất ở cận cảnh có người câu cá.
  (4) Khung phụ mặt trời dẹt dùng nước phía tây (vịnh) nên có cột lấp lánh; ở banner (nhìn bắc) biển phía đông **không** phản chiếu mặt trời (STYLE 1.2).
  Tiếp theo: T1.6 (đồ vật Safehouse; cần hỏi chủ repo các câu ở PLAN mục G), rồi Giai đoạn 2 (banner) theo `docs/PLAN-v3.md`. T0.3 nhớ: build_assets dùng Anton thay khi thiếu Pricedown; Actions không dùng Pricedown. `style_sample.py` là nguyên mẫu của `palette.py` + `post.py`.
- REFERENCES còn yếu: chưa có toàn văn review IGN/Eurogamer/GameSpot. Nếu chủ repo dán đoạn về HUD/điện thoại thì nâng độ tin cậy. Chưa xem được nội dung ảnh "Vice City Postcard" (chủ repo mở tay, không tải vào repo).
- Đã xác nhận SMIL chạy trên GitHub thật. Vẫn cần kiểm tra nền sáng và app mobile.
- **Chương Safehouse (rice chính) — CHỜ.** Rice chính nằm ở laptop, nhiều lớp, chưa có repo chính thức; ảnh thật chưa có. Một lần đã đưa áp phích từ PC (Mint LTS, ít tùy biến) lên với câu "rebuilt by hand" → sai, đã gỡ. Đừng đưa lại ảnh PC này.
  Chỉ làm khi có (a) ảnh thật đã làm sạch từ laptop và (b) chủ repo mô tả. Không link `sway-ultricing` như thể nó là toàn bộ rice; không link repo `rice` (riêng tư).
- Nếu GitHub không hiển thị tốt SMIL/mix: phương án dự phòng là xuất GIF hoặc ảnh tĩnh cho phần quan trọng (chưa làm).
- Nếu sửa ảnh mà trang vẫn hiện bản cũ: thêm `?v=N` vào URL ảnh trong README (camo cache).
