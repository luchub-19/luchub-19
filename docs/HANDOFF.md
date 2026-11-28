# HANDOFF — README profile GTA VI (đọc file này trước khi sửa)

Repo: `luchub-19/luchub-19` (công khai). Thư mục máy: `~/luchub-19-profile`. Cập nhật lần cuối: 2026-11-28 (T3.6).
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

### Quyết định cho T1.6 (2026-11-28; trả lời câu PLAN mục G cho T1.6/T3.2, chủ repo chốt trước khi vẽ)
- Terminal trên laptop: **`npm run dev` của didau (frontend) + `git log --oneline` của didau**. Chỉ lệnh thật của repo công khai (didau đã kiểm `isPrivate=false`;
  tên/version `didau-frontend@0.1.0`, cổng 5173 lấy từ `frontend/package.json` + README; 5 commit lấy bằng `gh api`, nhánh `main`). Số version Vite chưa chạy thật (xem `laptop.py`).
- Sticker nắp laptop: **câu "Works on my machine." (đã duyệt) + chim cánh cụt tự vẽ (kính hồng, khăn cyan, không chép Tux) + sao truy nã 1–6 sao + mép bong + vết dán đè**.
- Đồ uống: **cà phê đen trong cốc sứ**. Chi tiết thật cá nhân: **không** (chỉ chi tiết trung tính; giấy note dùng câu đã duyệt "One more commit.").

### Quyết định cho T2.1 (2026-11-28) — bố cục banner
- Chủ repo chọn **B · một điểm tụ, nhìn dọc Ocean Drive về bắc** (điểm tụ 58%, khách sạn lùi dần bên trái, cọ + biển bên phải, logo trên trục điểm tụ, tagline dải dưới giữa).
  Bỏ A (sân khấu ngang) và C (góc thấp, xe lớn). Phác thảo: `docs/style/t21-layout.jpg` (+ `-a/-b/-c.jpg`), script `tools/art/sample_t21.py`.
- Việc phải làm thêm trước/khi dựng T2.3: (1) `car.py` thêm góc nhìn sau/3/4 (bản phác chỉ ép ngang hình nhìn ngang để giả);
  (2) `deco.py` thêm chế độ phối cảnh cho dãy lùi (bản phác dùng "tấm phông" chính diện, cửa sổ không hội tụ);
  (3) hoạt ảnh xe đi về điểm tụ = co + dịch (không phải "chạy sang phải" như STYLE 6 ghi) — đã làm ở T2.4 theo cách này, chờ chủ repo xác nhận.

### Quyết định cho T3.1 (2026-11-28; PLAN mục G không có câu cho T3.1, chủ repo chốt trước khi vẽ) — dải tiêu đề chương
- Vật: 01 biển tên đường · 02 bảng neon · 03 biển quảng cáo · 04 tấm vé · **05 đổi khỏi "mặt đài"** (trùng áp phích Radio T3.6 là táp lô nhìn từ ghế lái). Vật 05 cụ thể chưa chốt:
  bản chính A = micro phòng thu + đèn ON AIR; B = băng cassette + J-card; C = loa phóng thanh (chủ repo chọn trên trang mẫu).
- Nền: **mỗi vật một chất liệu nền và một nguồn sáng khác nhau** (vữa + đèn tường · gạch men đen + neon · tranh in + đèn rọi · gỗ + nắng xiên · xốp tiêu âm + đèn ON AIR).
- Chữ: **giữ nguyên chữ hiện có** (`CHAPTER 0N`, tên chương, dòng phụ), đặt ngay trên vật. Chữ mới duy nhất: `OCEAN DR` (tên của vật ở dải 01; xoá được bằng một dòng).
- Động: một chi tiết riêng mỗi dải, lặp chậm (đèn tường hụt sáng · khung neon đèn chạy + chữ giật · đèn rọi thở · góc vé bật lên + dấu đục lỗ · đèn ON AIR thở).

### Quyết định cho T3.2 (2026-11-28; trả lời PLAN mục G cho T1.6/T3.2 + 2 câu bố cục, chủ repo chốt trước khi vẽ) — Player One → Safehouse
- Đồ vật: **giữ như T1.6** (terminal `npm run dev` didau, sticker "Works on my machine." + chim cánh cụt + sao, cà phê đen cốc sứ); **bỏ** `ISSUE CLOSED · WON'T FIX` và giờ `23:19` (chưa duyệt).
- Chi tiết cá nhân: **không**, giữ trung tính.
- Ngoài cửa sổ: **nhìn thẳng ra biển phía đông** (phòng ở khách sạn phía tây; không mặt trời, không dãy khách sạn lùi) để khác banner và HUD.
- Chữ **nằm trên đồ vật**: hook = chữ lớn trên tường, tiểu sử = tờ giấy ghim, thoại = giấy note + sticker trên bàn, thẻ tin nhắn trượt lên từ điện thoại. Không có cột chữ riêng.

### Quyết định cho T3.3 (2026-11-28; PLAN mục G không có câu cho T3.3, chủ repo chốt trước khi vẽ) — HUD
- Góc máy: **ngang, máy ở phía bãi biển nhìn về TÂY, chạy theo xe** (xe nhìn ngang hướng sang phải = về bắc, dãy khách sạn đối diện, khe phố cắt có mặt trời ở giữa khung). Bỏ góc cao 3/4 và góc thấp nhìn ngược xe.
- Kể chuyện: **xe chạy một mình**, không xe cảnh sát; mức truy nã chỉ nằm ở lớp HUD.
- Hàng icon bằng chứng: **mỗi icon một số liệu**: CCTV = ngày hoạt động · mặt = repo đụng tới · quần áo = repo công khai · xe = contribution năm · vũ khí = commit 30 ngày (mờ khi = 0).
- Minimap: **tròn kiểu GPS, nhà 3D** (hình dạng là lựa chọn của mình, REFERENCES H10 không xác minh). Mặc định mình tự đặt (chủ repo chưa phản đối): giữ dòng mục tiêu "Land N more commits to earn star N+1." (sửa số ít `commit`), bỏ chú thích công thức khỏi ảnh (vào alt text), sao kế tiếp nhấp nháy, 6 sao đạt tối đa thì đỏ (W2).

### Quyết định cho T3.4 (2026-11-28; trả lời PLAN mục G cho T3.4 + câu phân khung, chủ repo chốt trước khi vẽ) — Missions
- didau: hook **"Nobody picks. Everybody votes."**; bio **bản A** ("Hangout Planner. A shared room where the group suggests places, votes, and breaks ties in favour of whoever travels farthest. About 70,000 real venues across Ho Chi Minh City and Hanoi. No accounts.");
  hai câu thoại **"Anywhere is fine."** và **"Send the room code."**; ảnh chụp app: **trang chủ, bản đồ 3D TP.HCM** (chụp mới bằng Chrome headless trên dữ liệu sạch, không dùng ảnh có sẵn trong repo didau).
- Phân khung ba áp phích (không trùng nhau, không trùng mục khác): vibeKing = **tủ arcade chính diện, ngước lên**; didau = **bản đồ nhìn từ trên xuống, nắng ấm xiên cuối ngày**;
  Classified = **HẠ THẤP GÓC** (ngang tầm mắt, ngang mép bàn, bìa hồ sơ dựng nghiêng dưới đèn rọi gắt, phòng tối; dấu đóng xuống một lần), đổi khỏi "nhìn từ trên xuống" của STYLE mục 6 để khỏi trùng didau.

### Quyết định cho T3.5 (2026-11-28; trả lời PLAN mục G cho T3.5 + 4 câu khung, chủ repo chốt trước khi vẽ) — Loadout → vòng chọn vũ khí
- Ẩn dụ đồ vật: **C / C++ = cưa máy · PYTHON = dao đa năng kiểu Thụy Sĩ · TYPESCRIPT = súng ngắn có ống ngắm laser + chốt an toàn · LINUX = xà beng**. Giữ nguyên "SELECT YOUR WEAPON" + 4 tên + 4 chú thích đã duyệt.
- Cảnh nền mờ: **sân thượng khách sạn ban đêm** (khác banner/HUD: trên cao, ban đêm; khác Safehouse: ngoài trời). Bố cục: vòng ở giữa, 4 ô ở 4 GÓC vòng (chủ repo nói "4 hướng": mình hiểu là 4 góc để chú thích dồn hai bên; cần xác nhận), chú thích hai bên.
- Thêm hai nhãn tab **`WEAPONS / ITEMS`** (chữ mới, REFERENCES M-a). Hoạt ảnh: ô sáng lần lượt (16 s) + một chi tiết riêng mỗi vật.

### Quyết định cho T3.6 (2026-11-28; PLAN mục G không có câu cho T3.6, chủ repo chốt 4 câu trước khi vẽ) — Radio → mặt đài trong xe
- Góc máy: **ghế lái, nhìn qua kính chắn gió** (đúng STYLE mục 6). Mặt đài: **LCD phân đoạn + 3 nút preset** (không kim analog; "kim dò đài" của PLAN thay bằng vạch dò + con trỏ trong LCD).
- Ngoài kính: **đêm, cầu đắp qua vịnh** (khác banner/HUD chạng vạng, khác sân thượng Loadout). Chữ: **tên đài + 3 bài đều trên LCD, ba bài = ba nút preset** (nút đang phát sáng).
- Chữ MỚI: `P1 P2 P3`, `FM`, `ST` (nhãn máy) và `NOW PLAYING` (hook v2 "Now playing", in hoa trên LCD). `ON AIR` KHÔNG dùng (đã ở dải chương 05). Tên đài + 3 bài đọc thẳng từ `data/radio.json`.
- Mình tự thêm (chủ repo chưa phản đối): decal tên đài Pricedown trên dải che nắng; thông hương hình cọ treo ở gương; kính râm trên táp lô; sọc hồng + cam trên mui xe (xe chữ ký T1.2); xe ngược chiều chạy qua; máy lệch phải khỏi trục vô lăng để mặt đài nằm giữa khung.

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
                          T1.6 thêm: `desk.py` (khung chung: `_D` bộ vẽ cục bộ, `Cam`/`Proj`/`Box` chiếu song song cho vật phẳng 3D; `desk_top()` mặt bàn, `desk_lamp()`, `mug()` (5 biến thể style, khói SMIL, vành khô, vệt chảy, mẻ),
                          `headphones()` (stand/lying/hang), `phone()` (flat/lean/down, màn hình = phép afin) + `message_card()` (thẻ tin nhắn UI phẳng, dùng lại ở T3.2), `plant()` (snake/pothos/jar), `cable()`/`charger()`/`cable_coil()`, `sticky_note()`);
                          `laptop.py` (laptop khối 3D xoay tự do: `laptop(yaw, pitch, open_, screen, art)`, terminal mono thật (Space Mono), bàn phím, 3 bố cục sticker `sticker_*`);
                          `blinds.py` (`window()` cửa sổ Deco + rèm lá sách + phố neon ngoài cửa, `blind_light()` sọc neon/bóng đổ lên vùng bất kỳ, có mặt nạ tắt dần);
                          `sample_t16.py` (sinh `docs/style/t16-safehouse.jpg`, `--anim` ra SVG động: khói + sọc neon thở). Font mới: `tools/fonts/SpaceMono-Regular.ttf` (OFL, từ google/fonts). Tham số `lamp=-1|1` lật hướng đèn bàn cho mọi vật.
                          T2.2 thêm: `logo.py` (`Logo` + `logo(s, cx, top, width)` trả `LogoInfo` có bbox/mặt trời; `Logo.parts` bóc lớp cho trang mẫu), `sample_t22.py` (sinh `docs/style/t22-logo.jpg`).
                          T2.3 thêm: `persp.py` (`Cam` máy quay 1 điểm tụ, `homography`, `Job`/`render_jobs` render song song + tách alpha bằng nền đen/trắng + cache theo nội dung SVG,
                          `warp` bẻ lớp raster theo homography có lọc chống răng cưa theo mức co, `Canvas` ghép premultiplied cả 4 lượt col/sh/em/ln rồi mới hậu kỳ một lần);
                          `car3d.py` (`RearCar` + `rear_car(s, cam, spec)` xe chữ ký nhìn từ sau dựng bằng đa giác 3D chiếu, `beams()`, `far_oncoming()`);
                          `ocean.py` (cảnh banner: `buildings()`, `build()` trả danh sách lớp + thứ tự ghép, `compose()`; toạ độ thế giới mét, xem docstring);
                          `sample_t23.py` (sinh `docs/style/t23-banner.jpg` + `-sheet.jpg`; `--svg out.svg` ra SVG tĩnh nền WebP 1.5× + tagline path; `--keep DIR` giữ cache render).
                          T2.4 thêm: `anim.py` (`Stage` cache lớp theo nội dung SVG + cache lớp bẻ phối cảnh; `diff_rgba` tách sprite alpha từ HIỆU hai khung đã hậu kỳ; `crop`, `encode_rgba`, `image_el`, `frame_png` chụp SVG ở mốc t bằng setCurrentTime),
                          `sample_t24.py` (sinh `docs/style/t24-banner.svg` + `t24-frames.jpg`). Sửa thêm `ocean.build(skip=, sky_key=, sign_state=, win_on=, cloud_only=)` + `build_sky()` và chế độ `Line.mode="off"` trong `neon.py`: chỉ THÊM tham số, đầu ra mặc định giống từng byte bản T2.3 (đã so SVG 17 lớp).
                          T3.1 thêm: `chapters.py` (`Strip`, `STRIPS` 01–05, `ALTS` 05B/05C; mỗi dải = hàm `draw_0N(s)` vẽ vào `Scene(raster_ink=True)` trả `Parts(defs, overlay, ui, odefs, notes)`;
                          `render_plate()` render khung 830×320 rồi cắt 104 (Chrome headless sai khung thấp) + hậu kỳ; `build()` chọn chất lượng WebP để cả SVG ≤ 58 KB),
                          `sample_t31.py` (sinh `docs/style/t31/h-0N.svg` + `docs/style/t31-chapters.jpg`). `render.embed_svg` thêm tham số `grain_size` (mặc định 128, đầu ra cũ không đổi).
                          T3.2 thêm: `safehouse.py` (`sea_view()` cảnh ngoài cửa nhìn ra biển phía đông, `pinned_sheet()`, `sticker_sheet()`, `draw_plate()`, `overlay()` SMIL, `ui()` chữ, `build()`;
                          `Glyphs` dựng chữ Barlow bằng `<use>` mỗi glyph một path, CHỈ cho font OFL, Pricedown vẫn một path mỗi chuỗi), `sample_t32.py` (sinh `docs/style/t32/poster-profile.svg` + `docs/style/t32-safehouse.jpg`).
                          Chỉ THÊM tham số, mặc định giữ đầu ra cũ: `laptop.sticker_label(fine=)`, `laptop.laptop(cursor=, clock=)` (+ `Info.extra` screen_mat/term_origin/cursor), `laptop.terminal(cursor=)` trả toạ độ con trỏ,
                          `desk.phone(clock=)`, `desk.sticky_note(size=)`, `blinds.window(view=callable)`.
                          T3.3 thêm: `hud3.py` (NỀN cảnh phố ngang, `render_plate()` cần Chrome + numpy, chạy ở máy chủ repo; hằng `SUN_X/BASE/CAR_*` ở đầu file) và `hud_layer.py` (lớp HUD vector + `compose(stats, plate_bytes)`;
                          CHỈ cần fontTools + Barlow/Anton, đã kiểm không import numpy/Pillow/Chrome nên GitHub Actions chạy được; có `Glyphs` `<use>` riêng để khỏi kéo `safehouse.py`), `sample_t33.py` (sinh `docs/style/t33/hud.svg`, `hud-plate.webp` + `docs/style/t33-hud.jpg`).
                          T3.4 thêm: `missions.py` (dùng chung: `Cam3` máy quay pinhole thật hướng bất kỳ → ngước lên / nhìn xuống / ngang mép bàn, `affine`/`matrix` đặt khung phẳng lên mặt 3D, `poly`, `kicker`, `chip`; hệ số ma trận dùng `nf` 5 chữ số vì `geom.n` chỉ 1 chữ số thập phân),
                          `arcade.py` (vibeKing: tủ arcade dựng bằng đa giác 3D, màn hình = 3 ảnh chụp luân phiên ở lớp vector), `atlas.py` (didau: bản đồ giấy gấp + ghim/dây/cờ SMIL + ảnh in app), `dossier.py` (Classified: bìa hồ sơ 3D, nón sáng, dấu giáng xuống),
                          `sample_t34.py` (sinh `docs/style/t34/{vibeking,didau,classified}.svg` + `docs/style/t34-missions.jpg`). Ảnh nguồn mới: `tools/shots/didau-room.jpg`. Cả ba chỉ cần fonttools + Barlow/Pricedown ở máy chủ repo (không nối Actions: không có số liệu động).
                          T3.5 thêm: `loadout.py` (nền sân thượng ban đêm mờ + vòng elip 4 ô + 4 đồ vật vẽ bằng khối `solid()` = tô + liềm bóng + liềm viền sáng bằng mask "thân trừ thân dịch về phía nguồn sáng" + nét mực;
                          overlay SMIL: ô sáng, kim lõi, xích cưa, lưỡi dao bật, tia laser, ánh kim xà beng, biển hiệu chập chờn), `sample_t35.py` (sinh `docs/style/t35/loadout.svg` + `docs/style/t35-loadout.jpg`). Chỉ cần fonttools + Barlow/Pricedown ở máy chủ repo (không nối Actions: không có số liệu động).
                          T3.6 thêm: `radio.py` (cảnh ghế lái ban đêm: ngoài kính = trời + vịnh + nhà cao xa + cầu đắp bokeh (hàm `prj` chiếu camera cao 1 m, f = 495), mưa trên kính, mui xe + đèn pha lật + sọc, dải che nắng, gương + thông hương, cột A, táp lô, cụm đồng hồ, vô lăng, mặt đài, kính râm;
                          overlay SMIL: LCD (chữ chạy, đổi bài, EQ, vạch dò + con trỏ), nút preset sáng, trục cuốn băng, kim đồng hồ, đèn check chập chờn, thông hương lắc, xe ngược chiều qua `<mask>` kính; chu kỳ = 6 s × số bài; chữ LCD + nhãn Barlow qua `Glyphs`, decal Pricedown một path),
                          `sample_t36.py` (sinh `docs/style/t36/radio.svg` + `docs/style/t36-radio.jpg`). Chỉ cần fonttools + pillow + numpy + Chrome ở máy chủ repo (đọc `data/radio.json`; chưa nối Actions vì Pricedown không chạy ở CI: nếu muốn bài tự cập nhật theo json phải bỏ decal Pricedown hoặc dựng lại ở máy chủ repo).
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
  T1.6 **xong code + trang mẫu, ĐÃ DUYỆT ("duyệt hết", 28/11; câu hỏi mốc không trả lời riêng → theo phương án mặc định trong trang duyệt)** (28/11, chưa commit), trang mẫu `docs/style/t16-safehouse.jpg` (11 phần: cảnh bàn làm việc 12 chi tiết đánh số, laptop 6 góc, sticker cận cảnh, cốc ×4, tai nghe ×4, điện thoại ×4,
  rèm ×4, cây + đèn, dây/note/thẻ, 4 mức chi tiết, 3 ánh sáng). Chạy lại: `CHROME=google-chrome-stable <venv>/bin/python tools/art/sample_t16.py [--anim out.svg] [--only 1,3]`.
  Ghi chú T1.6: (1) Máy này không có Pricedown → tiêu đề trang mẫu dùng Anton (các trang T1.1–T1.5 dùng Pricedown); chạy lại ở máy chủ repo sẽ ra Pricedown. (2) Sticker nhãn có dòng chữ nhỏ `ISSUE CLOSED · WON'T FIX` (3 px, do mình thêm,
  KHÔNG nằm trong danh sách chữ đã duyệt) và màn khoá điện thoại hiện `23:19`: chủ repo cần xác nhận giữ hay bỏ. (3) Mặt trong màn terminal là nội dung thật nhưng chữ ở cỡ k = 1.5 chỉ đọc được ở trang mẫu, ở README sẽ là kết cấu. (4) Chưa kiểm khổ 390 px
  và nền trắng (mục checklist kỹ thuật): làm khi dựng asset thật ở T3.2. (5) SVG động thử 169 KB (nền WebP 95 KB + vector 16 KB); con trỏ terminal nhấp nháy có SMIL (`anim=True`) nhưng chưa đưa vào bản thử vì terminal nằm trong nền raster.
  (6) Lớp SMIL luôn nằm trên nền raster (như ghi chú T1.5): khói và sọc neon ở trên cùng, che vật đứng trước chúng nếu có. (7) Chưa làm: tay cầm/gamepad, sách, ảnh nền tường; cảnh chính chưa có lớp L3 sát khung (T3.2 quyết).
  T2.2 + T2.3 **xong code + trang mẫu, ĐÃ DUYỆT ("duyệt hết", 28/11; câu hỏi mốc không trả lời riêng → theo phương án mặc định trong trang duyệt)** (28/11, chưa commit). `assets/` và README CHƯA đổi (banner cũ vẫn chạy).
  Chạy lại: `CHROME=google-chrome-stable <venv>/bin/python tools/art/sample_t23.py [--svg out.svg] [--keep DIR]` rồi `.../sample_t22.py` (trang logo cắt ảnh banner T2.3).
  Ghi chú T2.2: (1) Logo = LUCHUB (ruột trời hoàng hôn + tháp xa + 3 cọ) / 19 to 1.32× lệch phải, **đỉnh số 19 là chân trời chung**, mặt trời retro lặn vào đó, cột phản chiếu trong ruột 19.
  Viền: khối đùn chàm · mực · hồng/cyan · mực · chỉ kem · bóng loáng. Quang sai do post (Region ca). (2) Máy này đã tải lại Pricedown vào `tools/fonts/local/` (gitignore, theo STYLE 5.4).
  (3) Ở 110 px chữ LUCHUB còn đọc được nhờ viền hồng, chi tiết ruột thành kết cấu.
  Ghi chú T2.3: (1) **Phối cảnh thật** thay "tấm phông" của bản phác: mặt tiền render phẳng rồi bẻ homography (persp.py); biển neon blade vẽ CHÍNH DIỆN (biển thật nhô vuông góc tường nên quay về máy quay),
  vì vậy biển `LUCHUB` đặt thành blade dọc ở toà HERO thay vì chạy dọc thân tháp (thân tháp nằm trong mặt tiền bị co, không đọc được) — cần chủ repo xác nhận.
  (2) 1 đv deco = 0.06 m (khách sạn nhỏ hơn thật ~15% để mái dãy xa lọt khung). Mắt 2 m, tiêu cự 600, điểm tụ (696, 238).
  (3) Xe chữ ký nhìn từ sau (car3d.py, không đụng car.py đã duyệt): dải đèn hậu liền có lá chắn, kính sau lá chắn, cánh gió, nóc targa, hông trái nhận nắng ấm; ánh đèn pha trên đường phía trước = xe chạy về điểm tụ.
  (4) Thêm ngoài danh sách: bàn ô dù quán cà phê vỉa hè trái, vạch qua đường tiền cảnh + ở phố ngang, xe ngược chiều tít xa, dấu chân + dép trên cát, vệt dầu (bất toàn), 1 cột đèn xa tắt.
  Neon trong cảnh: hồng + cyan chính, vàng điểm (LUNA); SEAGLASS đổi cobalt → cyan, SOLANA mái che cobalt → cyan để đúng luật ≤ 2 màu + 1 điểm.
  (5) Dung lượng: SVG tĩnh 462 KB (nền WebP 1.5× giới hạn 330 KB, chừa ~550 KB cho SMIL của T2.4); JPEG xem nhanh 230 KB. budget.py đạt (assets chưa đổi).
  (6) Chưa làm (T2.4): mặt trời của logo chìm dần, xe đi về điểm tụ (co + dịch), neon nhấp nháy, cọ đung đưa, tagline tự gõ. Lớp vector động sẽ nằm TRÊN nền raster nên vật động phải là vật đứng trước (biển, xe, cọ gần) hoặc tách nền làm hai lớp như ghi chú T1.5.
  (7) Điểm yếu đã biết: khách sạn gần nhất bị phóng ~3× từ khung cục bộ nên nét hơi mềm; tháp ống khói của HERO bị khung cắt; biển chỉ là nêm hẹp ở mép phải (đúng phối cảnh nhìn bắc).
  T2.4 **xong code + trang mẫu, ĐÃ DUYỆT ("duyệt hết", 28/11; câu hỏi mốc không trả lời riêng → theo phương án mặc định trong trang duyệt)** (28/11, chưa commit). `docs/style/t24-banner.svg` (918 KB, ngân sách 1 MiB: đạt, còn ~100 KB) + `docs/style/t24-frames.jpg` (6 mốc). `assets/` và README CHƯA đổi.
  Chạy lại: `CHROME=google-chrome-stable <venv>/bin/python tools/art/sample_t24.py [--out f.svg] [--work DIR] [--sheet f.jpg] [--frames 5.5,9.5]` (lần đầu ~6 phút vì dựng ~25 biến thể; có cache ở `--work`, mặc định /tmp/t24-work; `--fresh` xoá cache).
  Cách làm: cả cảnh là MỘT ảnh raster nên mỗi vật động được tách bằng hiệu hai khung (dựng cảnh bỏ/đổi một vật → cùng hậu kỳ → sprite WebP có alpha; xem `anim.py`). Plate (cảnh không có vật động, WebP 252 KB) + 26 sprite (≈365 KB). Khung t = 0 ghép lại ≈ ảnh tĩnh T2.3: sai số TB 4.9/255 so với 3.8/255 của riêng nén plate (đo ngoài dải tagline).
  Chuyển động (chu kỳ chính 24 s; các vật khác lặp theo chu kỳ riêng): (1) xe co đều quanh điểm tụ (đúng phối cảnh: z tăng 1 m/s từ 8 m), mờ dần 13–17 s, chiếc kế tiếp vào từ phía sau máy quay 23.0–23.5 s; (2) 4 đám mây tích trôi ngang qua lại 8–16 px (chu kỳ 44–72 s), vật che mây (đèn, toà, logo) là một sprite "mặt nạ" nằm TRÊN mây;
  (3) 3 cọ xa + cọ sát khung đung đưa quanh gốc (0.8–2°, chu kỳ 6.4–9 s; cả cây, không tách tán); (4) biển neon = mảnh vá "tắt" bật/tắt: LUCHUB sập nguồn rồi bật lại từng chữ (timeline `tl_startup` thật của neon.py, chu kỳ 14 s), CORAL chữ R hỏng (timeline `broken`), SEAGLASS/LUNA/PALMETTO/SOLANA mỗi biển giật một lần;
  (5) 6 ô cửa sổ bật đèn rồi tắt (2 ô lớn ở SEAGLASS, các ô còn lại ở toà xa chỉ là khe hẹp nên khó thấy); (6) tagline: 3 câu ĐÃ DUYỆT (đọc thẳng từ `TAGLINES` trong build_assets.py) tự gõ/xoá lần lượt, câu 1 hiện đủ ở t = 0.
  Cần chủ repo xác nhận: (a) **xe "co + dịch" về điểm tụ** thay cho "chạy sang phải" ở STYLE 6 (HANDOFF T2.1 việc (3)); chiếc kế tiếp hiện lên từ phía sau máy quay bằng fade 0.5 s; (b) xem trên GitHub thật: `<animate>` con của `<image>` (opacity), `animateTransform` rotate/scale/translate và `calcMode="discrete"` cho clipPath tagline — SMIL của T0.4 mới xác nhận với vật vector, chưa với sprite WebP; (c) tốc độ/biên độ có "vừa phải" chưa.
  Điểm yếu đã biết: (1) sprite xe/cọ ở 1.5× phóng tới 1.14× khi xe vào lại nên hơi mềm; (2) sprite nằm trên plate nên vật ở giữa hai sprite chỉ đúng thứ tự cố định (mây < mặt nạ < cọ xa < xe < cọ gần), cọ xa chồng nhau dùng chuỗi cộng dồn nên cây sau không thấy phần bị cây trước che khi đung đưa; (3) quầng sáng (bloom) của đèn đường trên đám mây bị giảm nhẹ khi mây đã trôi đi (bloom nằm trong plate);
  (4) biển tắt không tắt phản chiếu trên đường (giữ nguyên) và quầng tường tắt cùng biển; (5) chưa làm: mặt trời trong logo chìm dần, mòng biển/bồ nông, xe ngược chiều ở xa, đèn hậu nhấp nháy; (6) chưa kiểm khổ 390 px, nền sáng và app mobile; (7) `car3d` sinh id gradient có `id()` của đối tượng nên SVG xe khác nhau mỗi lần chạy (vô hại; `Stage.key` đã chuẩn hoá).
  T3.1 **xong code + trang mẫu, ĐÃ DUYỆT ("duyệt hết", 28/11; câu hỏi mốc không trả lời riêng → theo phương án mặc định trong trang duyệt)** (28/11, chưa commit). 5 SVG ở `docs/style/t31/h-01..05.svg` (+ `h-05b/05c` bản thay thế, không SMIL), trang duyệt `docs/style/t31-chapters.jpg`. `assets/` và README CHƯA đổi (dải v2 `h-*.svg` vẫn chạy).
  Chạy lại: `CHROME=google-chrome-stable <venv>/bin/python tools/art/sample_t31.py [--work DIR] [--no-frames]` (~1 phút; venv cần fonttools + pillow + numpy). Pricedown ở `tools/fonts/local/` (thiếu thì Anton).
  Dung lượng: mỗi SVG 55–57 KB (≤ 60 KB), 5 dải ≈ 281 KB (5 dải v2: 112 KB). Chữ là path (Pricedown, Barlow); dải 02 tách từng chữ tiêu đề thành path riêng để chữ U chập chờn, dải 05 chữ ON AIR là path.
  Ghi chú T3.1: (1) Nền raster ở 1.25× WebP (không 1.5× như banner) vì ngân sách; chữ là vector nên vẫn sắc. (2) SMIL mới so với T0.4/T2.4: `<animate attributeName="points">` (góc vé dải 04), `opacity` có `keyTimes` nhiều mốc, `filter` blur trên `<use>` (chữ neon dải 02, 05), `calcMode="spline"`. **Cần chủ repo xem trên GitHub thật** (desktop + app mobile). Bài học: SMIL `values`/`keyTimes` phải có mốc đầu 0 và cuối 1, sai thì trình duyệt bỏ cả animation (đã gặp ở dải 04).
  (3) Neon ở dải 02: `neon.frame(..., anim=True)` làm khung bậc cyan đèn chạy; đã gỡ ellipse `nn-spill-*` của nó (quầng cyan nuốt quầng hồng của chữ). Biển `neon.sign` ở cỡ k ≈ 0.5 bị che chữ bởi raceway nên **không dùng** cho dòng phụ; dòng phụ dải 02 là chữ hộp đèn Barlow Bold.
  (4) Dải 05: tường xốp tô theo hướng mỗi mặt tới hai nguồn sáng (đèn ON AIR hồng-đỏ + mixer cyan), nên sáng/tối của hình chóp không tự đặt tay. Bản B/C kém chi tiết hơn A (không SMIL); nếu chọn thì dựng thêm.
  (5) Điểm yếu đã biết: dải 03 giống ô cửa sổ nhìn ra trời hơn là tranh in nếu dải benday quá mờ; dải 04 còn khoảng trống giữa vòng chọn và tiêu đề; dải 01 nét hơi tối/đục (halftone phủ cả tường); hoạt ảnh dải 03 (đèn rọi thở) và 05 khá nhẹ, chủ repo cho biết có "vừa phải" chưa;
  khổ 390 px: dòng phụ còn ~6 px (thành kết cấu), nhãn `OCEAN DR`/`CHAPTER 0N` ~5 px; chưa kiểm thật trên app mobile.
  Tiếp theo: chủ repo duyệt T1.6, T2.2, T2.3, T2.4, T3.1 → T2.5 (thay `assets/banner.svg` + README) và T3.x theo `docs/PLAN-v3.md`. T0.3 nhớ: build_assets dùng Anton thay khi thiếu Pricedown; Actions không dùng Pricedown. `style_sample.py` là nguyên mẫu của `palette.py` + `post.py`.
  T3.2 **xong code + trang duyệt, ĐÃ DUYỆT ("duyệt hết", 28/11; câu hỏi mốc không trả lời riêng → theo phương án mặc định trong trang duyệt)** (28/11, chưa commit). `docs/style/t32/poster-profile.svg` (379 KB: nền WebP 1.5× 213 KB + vector/chữ/grain ~94 KB; ngân sách ~400 KB) + `docs/style/t32-safehouse.jpg`.
  `assets/` và README CHƯA đổi (áp phích v2 vẫn chạy). Chạy lại: `CHROME=google-chrome-stable <venv>/bin/python tools/art/sample_t32.py [--work DIR]` (~10 s có cache).
  Bố cục 830 × 420: hook Pricedown 2 dòng (kem/vàng) góc trên trái · tờ tiểu sử ghim tường (dải PLAYER 01 · LUCHUB-19) · đèn bàn Deco giữa (nguồn chính) · cửa sổ phải, rèm kéo nửa, ngoài là biển phía đông
  (biển dọc hồng của chính khách sạn ở mép trái kính + ống cyan mái che mép dưới = nguồn hai màu sọc neon) · thẻ tin nhắn UI góc trên phải · bàn: tai nghe, củ sạc + dây, laptop terminal, cốc, điện thoại · L3: giấy note + tờ sticker.
  Hoạt ảnh: sọc neon thở 2.6 s + chớp mỗi 11 s, khói cốc, con trỏ terminal (overlay đúng ma trận màn), bồ nông bay qua khoảng kính dưới rèm 24 s, thẻ tin nhắn hiện ở t = 0 rồi mỗi 16 s tắt/trượt lên từ điện thoại (màn điện thoại loé).
  Cần chủ repo trả lời (cuối trang duyệt): (1) hook hai màu hay một; (2) giữ dải PLAYER 01 · LUCHUB-19 trên tờ giấy; (3) thẻ lặp 16 s hay trượt vào một lần; (4) sticker trên tờ đế không bong (góc bong che "E."); (5) chữ note 7.4 → 6.3; (6) mức chuyển động.
  Điểm yếu đã biết: thân laptop khá nhạt khi sọc neon đi qua; terminal ở 390 px thành kết cấu; nửa phải bàn chật (điện thoại sát mép khung); chưa xem trên GitHub thật/app mobile; chữ Barlow `<use>` là kỹ thuật mới trong repo (cần xem GitHub render đúng).
  T3.3 **xong code + trang duyệt, ĐÃ DUYỆT ("duyệt hết", 28/11; câu hỏi mốc không trả lời riêng → theo phương án mặc định trong trang duyệt)** (28/11, chưa commit). `docs/style/t33/hud.svg` (333 KB: nền WebP 1.5× 211 KB + lớp HUD ~51 KB; ngân sách ~350 KB), `docs/style/t33/hud-plate.webp` (nền, file Actions sẽ nhúng), trang duyệt `docs/style/t33-hud.jpg`.
  `assets/hud.svg`, `build_assets.py`, workflow và README CHƯA đổi (HUD v2 vẫn chạy). Chạy lại: `CHROME=google-chrome-stable <venv>/bin/python tools/art/sample_t33.py [--work DIR]` (~10 s).
  Bố cục 830 × 340: nền = Ocean Drive chạng vạng nhìn ngang (khách sạn SEAGLASS/CORAL/LUNA/HERO/SOLANA, khe phố cắt + mặt trời dẹt ở x ≈ 481, xe chữ ký chạy làn gần, cột đèn L3 sát khung) · trên trái 3 thanh (HEALTH/ENERGY/FOCUS, giữ phép tính v2) ·
  trên phải: ngân hàng tím + tiền mặt xanh lá, 6 sao, 5 icon bằng chứng + số + nhãn · dưới trái minimap tròn (vùng tìm kiếm đỏ khi có sao, không cảnh sát) · dưới phải dòng mục tiêu.
  Ghi chú T3.3: (1) **Kiến trúc Actions (chưa nối)**: Actions chỉ cần gọi `hud_layer.compose(stats, plate)` với `plate` = bytes `hud-plate.webp` commit trong repo (đề xuất `data/hud-plate.webp`); nền không đổi theo số liệu. Khi duyệt xong mới sửa `build_assets.hud()` + workflow để gọi hàm này thay cho `hud()` v2 (v2 dùng Anton, Barlow, không Pricedown: vẫn đúng STYLE 5.4).
  (2) Nền đứng yên (xe không chạy); muốn xe/neon động phải tách sprite như T2.4 (+~250 KB, Actions phải giữ sprite). Chờ chủ repo chọn. (3) Mặt tiền dùng lại bộ T1.1 (khác tổ hợp, `side=None` vì nhìn chính diện); biển CORAL đọc được; chữ `LUCHUB` dọc trên tháp HERO rất mờ ở k = .56 và nằm ngay dưới hàng sao (chưa xem kỹ ở khổ thật, có thể không đọc được).
  (4) Scrim (ellipse tối) ở 4 góc nướng sẵn trong nền để HUD đọc được; không có HUD thì nền vẫn tự nhiên. (5) Khổ 390 px: số tiền (Anton 34/24) đọc được, nhãn thanh/số dưới icon thành kết cấu; alt text có đủ số liệu và nghĩa icon. (6) Chưa xem trên GitHub thật/app mobile.
  Điểm yếu đã biết: xe nhỏ hơn mong đợi ở khổ 830 (200 px); vệt dầu chỉ là một vệt tối nhạt; cột đèn L3 và dòng mục tiêu gần nhau (cột nằm ngay mép trái ô mục tiêu); icon bằng chứng nằm trên mặt tiền HERO nên nền khá bận (nhờ viền mực INK mới đọc được).
  T3.4 **xong code + trang duyệt, ĐÃ DUYỆT ("duyệt hết", 28/11; câu hỏi mốc không trả lời riêng → theo phương án mặc định trong trang duyệt)** (28/11, chưa commit). Ba SVG ở `docs/style/t34/` (vibeking 420 KB, didau 388 KB, classified 285 KB; ngân sách 450/400/300) + trang duyệt `docs/style/t34-missions.jpg`.
  `assets/`, `build_assets.py` và README CHƯA đổi (áp phích v2 vẫn chạy). Chạy lại: `CHROME=google-chrome-stable <venv>/bin/python tools/art/sample_t34.py [--work DIR] [--only vibeking,didau,classified]` (~25 s).
  Khung (đã chốt, không trùng nhau/mục khác): vibeKing = tủ arcade chính diện ngước lên ~5° (lệch trái 0.55 m thấy hông tủ), hook = chữ sơn tường, bio + 2 thoại + chip + MISSION 01 = bảng chữ A đứng sàn, màn hình = ảnh chụp thật luân phiên combat/boss/attract "INSERT COIN." 24 s.
  didau = bản đồ nhìn từ trên xuống, nắng xiên + bóng lá cọ; hook trên dải tiêu đề dán bản đồ, bio bản A trên thẻ ghi chú kẻ dòng (MISSION 02), 2 thoại trên cờ giấy cắm ghim, ghim rơi + dây tự vẽ chu kỳ 16 s (t = 0 là trạng thái đủ).
  Classified = hạ thấp góc ngang mép bàn, một đèn treo rọi nón sáng gắt; hook = biển hiệu hazard tường, TOP SECRET + dấu CLASSIFIED + ACCESS DENIED trên bìa (giữ từ v2), thoại + MISSION 03 trên thẻ giấy dựng, hai thẻ chứng cứ "???", dấu giáng xuống một lần mỗi 14 s.
  **Chưa chắc / cần chủ repo trả lời (cuối trang duyệt):** (1) ĐỔI SỐ MISSION: vibeKing 01 · didau 02 · Classified 03 (v2: Classified là 02); (2) **trang chủ didau thật hiện KHÔNG có bản đồ 3D** (có thể README chụp bản cũ; trang hiện tại là landing có thẻ phòng mẫu, và ô bản đồ lúc chụp headless chỉ còn nền trơn vì ô gạch không tải) → ảnh in là thẻ phòng mẫu (bản đồ + thẻ hoà phiếu), chủ repo từng chọn "bản đồ 3D";
  (3) chip "TYPESCRIPT · REALTIME" dưới ảnh in didau là chữ mới; (4) "Insert coin." xuất hiện hai nơi (bảng + màn attract); (5) biển hook "CLEARANCE REQUIRED" là hình thức mới của hook; (6) bản đồ didau là tranh tự vẽ, không phải TP.HCM thật; (7) mức chuyển động; (8) marquee vibeKing chỉ ≈ 12 px ở khổ thật.
  Ghi chú kỹ thuật: (a) SMIL mới so với T3.1–T3.3: `stroke-dashoffset` với `pathLength="1"` (dây vẽ), `animateTransform scale` cho dấu, `feDisplacementMap` (mép dấu lem), `feColorMatrix+feBlend` (quang sai CRT), ảnh WebP làm `<image>` nằm trong overlay — **cần xem trên GitHub thật + app mobile**.
  (b) `Cam3` cần điểm có độ sâu dương: lần đầu thảm confetti có z lớn hơn máy quay → hình bị lật khổng lồ (đã giới hạn z ≤ 1.95); đừng đặt vật sau máy quay. (c) Ảnh chụp didau lấy bằng Chrome headless swiftshader (env EGL mesa, không đụng dGPU) từ https://didau-omega.vercel.app; ảnh in chỉ cắt thẻ phòng mẫu (có avatar tròn nhỏ), KHÔNG lấy dải scooter dưới chân trang vì ở đó app gắn tên nhân vật Nobita/Doraemon/Xuka/Xeko (tên của bên thứ ba): chủ repo tự cân nhắc nếu dùng ảnh đó.
  Điểm yếu đã biết: nền vibeKing khá tối, thảm sàn mờ; bảng chữ A hơi nghiêng chữ (nghiêng đứng ~5° do ngước lên); marquee nhỏ; didau: bản đồ nhiều chi tiết nên ở 390 px thành kết cấu, thẻ ghi chú 6 dòng sát mép dưới; Classified: nón sáng ít rõ, nửa trái tối, tag "???" chồng lên nhau một phần; chưa kiểm trên GitHub thật.
  T3.5 **xong code + trang duyệt, ĐÃ DUYỆT ("duyệt hết", 28/11; câu hỏi mốc không trả lời riêng → theo phương án mặc định trong trang duyệt)** (28/11, chưa commit). `docs/style/t35/loadout.svg` (271 KB: nền WebP 1.5× 156 KB + vector/chữ/grain 64 KB; ngân sách ~300 KB) + trang duyệt `docs/style/t35-loadout.jpg`.
  `assets/loadout.svg`, `build_assets.py` và README CHƯA đổi (Loadout v2 vẫn chạy). Chạy lại: `CHROME=google-chrome-stable <venv>/bin/python tools/art/sample_t35.py [--work DIR]` (~15 s).
  Bố cục 830 × 352: tiêu đề + tab trên cùng · vòng elip + lõi tròn có kim chỉ · 4 ô theo chiều kim đồng hồ (C/C++ trên-trái, PYTHON trên-phải, TYPESCRIPT dưới-phải, LINUX dưới-trái) · tên Pricedown + chú thích Barlow hai bên · nền: dây đèn ấm (nguồn chính, góc trên-trái, ngoài khung), trăng lọt giữa hai ô trên, biển, hai tháp bên (biển hiệu hồng chập chờn), hồ bơi ngọc lam, lan can Deco.
  Hoạt ảnh (chu kỳ 16 s, t = 0 là C/C++ sáng): ô sáng + tên/chú thích sáng lần lượt (ô khác mờ 62%), kim lõi quay; cưa: xích chạy · dao: lưỡi chính bật mở lúc tới lượt (đóng lúc 2.5–2.9 s) · súng: tia laser cyan quét · xà beng: ánh kim quét; biển hiệu hồng giật mỗi 9 s.
  **Cần chủ repo trả lời (cuối trang duyệt):** (1) thứ tự ô; (2) "4 hướng" = 4 góc hay N/E/S/W; (3) giữ tab WEAPONS / ITEMS (ITEMS chỉ trang trí); (4) đồ vật tràn khung một chút; (5) trăng giữa hai ô trên; (6) mức chuyển động; (7) dáng cưa máy (vật khó nhận ra nhất ở khổ nhỏ); (8) chú thích Barlow ở 390 px chỉ ≈ 7 px.
  Ghi chú kỹ thuật: (a) `solid()` cần biết góc xoay nhóm (`_rot`) để viền sáng/bóng luôn từ trên-trái; mask dùng `maskUnits=userSpaceOnUse` cục bộ. (b) Nét tối trong `Scene(raster_ink=True)` KHÔNG vào lớp màu: ống/tay cầm phải dùng màu sáng hơn lum .25 (vd. #6A58B8), nếu không biến mất. (c) Nét mực làm đặc mọi vòng nhỏ (bóng đèn r < 5): dùng r ≥ 5; song lan can nét mảnh thành vệt lem nên đã bỏ.
  (d) SMIL mới so với các mục trước: `animateTransform rotate` nhiều đoạn có keySplines xen kẽ giữ/chạy cho kim, `stroke-dashoffset` trên đường dasharray cho xích, lưỡi dao xoay quanh trục với overshoot, `filter` blur trên tia laser — **cần xem trên GitHub thật + app mobile**.
  Điểm yếu đã biết: cưa máy là vật yếu nhất (thân nhỏ, tay cầm lớn); súng khá trơn; nền khá tối ở vùng dưới nên sân thượng/biển chỉ lờ mờ; trăng hơi phẳng; chú thích ô mờ (62%) khó đọc hơn trên bokeh; chưa xem trên GitHub thật/app mobile.
  T3.6 **xong code + trang duyệt, ĐÃ DUYỆT ("duyệt hết", 28/11; câu hỏi mốc không trả lời riêng → theo phương án mặc định trong trang duyệt)** (28/11, chưa commit). `docs/style/t36/radio.svg` (280 KB: nền WebP 1.5× 157 KB + vector/chữ/grain 70 KB; ngân sách ~250–300 KB) + trang duyệt `docs/style/t36-radio.jpg`.
  `assets/poster-radio.svg`, `build_assets.py` và README CHƯA đổi (Radio v2 vẫn chạy). Chạy lại: `CHROME=google-chrome-stable <venv>/bin/python tools/art/sample_t36.py [--work DIR]` (~20 s).
  Bố cục 830 × 350: nền ngoài kính (cầu đắp qua vịnh đêm, bokeh; dãy nhà cao xa có neon hồng bên trái, neon cyan bên phải bị cột A che) · mui xe trắng + 2 đèn pha lật bật + sọc hồng/cam · táp lô (đồng hồ tốc độ/vòng tua/nhỏ, vô lăng bên trái, cửa gió phải) ·
  mặt đài giữa-phải (2 núm, LCD hổ phách, P1–P3, khe băng + nút đẩy) · trên cùng: dải che nắng với decal "LUCHUB FM 19.11" (Pricedown), gương + thông hương cọ, kính râm trên táp lô.
  Hoạt ảnh (chu kỳ 18 s; t = 0 là P1 HUMBLE.): LCD đổi bài mỗi 6 s (tắt 0.3 s giữa hai bài), nút preset sáng theo bài, con trỏ vạch dò quét sang mốc mới, chữ chạy tên đài · NOW PLAYING, EQ 8 cột, trục cuốn băng, kim đồng hồ, thông hương lắc, xe ngược chiều (4–7 s trong chu kỳ 12 s), đèn check chập chờn.
  **Cần chủ repo trả lời (cuối trang duyệt):** (1) máy lệch phải khỏi trục vô lăng: giữ hay đặt đúng trục; (2) decal tên đài trên dải che nắng: giữ hay chỉ để trên LCD; (3) nhãn mới FM/ST/NOW PLAYING; (4) xe chữ ký chỉ lộ qua mui + đèn pha + sọc: có nhận ra không; (5) cảnh ngoài rất mờ: thêm chi tiết nhận ra được hay giữ mờ;
  (6) mức chuyển động; (7) thứ tự bài P1→P2→P3 theo `radio.json`; (8) chữ LCD ở 390 px chỉ ≈ 8 px (tên bài ≈ 9 px), alt text có đủ.
  Ghi chú kỹ thuật: (a) SMIL mới so với các mục trước: `<mask>` bao quanh `<animate cx/cy/r>` (bokeh xe), `animate height + y` (EQ), `clip-path` trên nhóm chạy chữ, `<use>` + filter blur làm quầng chữ LCD, `calcMode="discrete"` cho cửa sổ bài — **cần xem trên GitHub thật + app mobile**.
  (b) Lớp overlay luôn nằm TRÊN nền raster nên mọi vật động phải không bị vật tĩnh che: bokeh xe dùng mask kính trừ mui xe + táp lô; kim đồng hồ đặt cao hơn mép trên vô lăng (tâm y = 262, vành lộ từ y ≈ 275). (c) Không áp quang sai màu ở LCD (STYLE 4.2 cho phép; chữ hổ phách sắc hơn nếu không có). (d) Trục cuốn băng nhỏ ở khổ thật (≈ 14 px), chủ yếu là chi tiết cận cảnh.
  Điểm yếu đã biết: cabin tối và đơn sắc tím/hổ phách (cảnh đêm, đúng nguồn sáng nhưng ít pastel hơn banner); cảnh ngoài mờ nên khó đọc là "cầu đắp"; nhãn P1/P2/P3 ≈ 10 px; vô lăng chỉ lộ cung trên; mui xe là một mảng lavender lớn có halftone; chưa xem trên GitHub thật/app mobile.
- REFERENCES còn yếu: chưa có toàn văn review IGN/Eurogamer/GameSpot. Nếu chủ repo dán đoạn về HUD/điện thoại thì nâng độ tin cậy. Chưa xem được nội dung ảnh "Vice City Postcard" (chủ repo mở tay, không tải vào repo).
- Đã xác nhận SMIL chạy trên GitHub thật. Vẫn cần kiểm tra nền sáng và app mobile.
- **Chương Safehouse (rice chính) — CHỜ.** Rice chính nằm ở laptop, nhiều lớp, chưa có repo chính thức; ảnh thật chưa có. Một lần đã đưa áp phích từ PC (Mint LTS, ít tùy biến) lên với câu "rebuilt by hand" → sai, đã gỡ. Đừng đưa lại ảnh PC này.
  Chỉ làm khi có (a) ảnh thật đã làm sạch từ laptop và (b) chủ repo mô tả. Không link `sway-ultricing` như thể nó là toàn bộ rice; không link repo `rice` (riêng tư).
- Nếu GitHub không hiển thị tốt SMIL/mix: phương án dự phòng là xuất GIF hoặc ảnh tĩnh cho phần quan trọng (chưa làm).
- Nếu sửa ảnh mà trang vẫn hiện bản cũ: thêm `?v=N` vào URL ảnh trong README (camo cache).
