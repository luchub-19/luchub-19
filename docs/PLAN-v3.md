# PLAN v3 — Làm lại toàn trang theo kiểu tranh minh họa Rockstar / Vice City

Soạn 2026-11-27. Session này chỉ lập kế hoạch, chưa sửa gì. Đọc kèm `docs/HANDOFF.md`.
Mỗi task ghi **model gợi ý**: **Opus 5.5** dùng cho chỉ đạo mỹ thuật, bộ sinh hình phức tạp và bố cục; **Sonnet 5.5** dùng khi việc đã có đặc tả rõ;
**Haiku 5.5** dùng cho việc máy móc, kiểm tra và tài liệu.

## A. Chủ repo đã chốt (4 vòng hỏi, 2026-11-27)
| Mục | Chốt |
|---|---|
| Hướng hình ảnh | **Tranh minh họa kiểu Rockstar**: nét mực, đổ bóng nhiều lớp, halftone, chi tiết Art Deco, neon |
| Định dạng | **Lai**: nền chi tiết là raster (WebP/JPEG nhúng base64 trong SVG), chữ, số liệu và hoạt ảnh là SVG/SMIL nằm trên |
| SMIL trên GitHub | **Chủ repo xác nhận chạy tốt** → tiếp tục đầu tư hoạt ảnh |
| Phạm vi | **Làm lại toàn trang** |
| Banner | **Ocean Drive lúc chạng vạng** (dãy khách sạn Art Deco pastel, neon, cọ, biển) |
| Nhân vật | **Không có người làm nhân vật chính; kể chuyện bằng đồ vật.** Được có **bóng người nhỏ ở xa** trên phố |
| Xe chữ ký | **Xe thể thao thập niên 80**: dáng nêm, đèn pha lật. Vẽ dáng chung, không chép mẫu xe thương hiệu |
| Logo | **Chữ xếp tầng, ruột chữ chứa cảnh** hoàng hôn + cọ. Gợi tinh thần logo VI nhưng hình chữ là của riêng mình |
| Pipeline | **Code thủ tục + hậu kỳ raster** (Python → SVG lớp → Chrome render 2x → Pillow hậu kỳ). **Không sinh ảnh bằng AI** |
| Missions | vibeKing + Classified + **thêm `didau`** (công khai, TypeScript, có bản chạy https://didau-omega.vercel.app) |
| Hồ sơ (Player One) | **Bàn làm việc cạnh cửa sổ nhìn ra Ocean Drive** (laptop mở terminal, cà phê, tai nghe, điện thoại có tin nhắn, neon hắt qua rèm) |
| Loadout | **Vòng chọn vũ khí, mỗi ngôn ngữ là một đồ vật minh họa** theo ẩn dụ. Giữ nguyên 4 chú thích đã duyệt |
| Dung lượng | **Cả trang khoảng 3–5 MB** (banner ≤ 1 MB, mỗi áp phích ~300–500 KB) |
| Tham chiếu HUD | Chủ repo không có ảnh game → dùng nguồn công khai, ghi rõ độ chắc chắn |
| Mốc duyệt | Style guide → phác thảo bố cục → từng món trong thư viện → bản hoàn chỉnh từng mục |

Chữ đã duyệt ở HANDOFF mục 6 **giữ nguyên văn**.

## B. Chẩn đoán lỗi xe/đèn ở banner hiện tại (`car()` trong `tools/build_assets.py`)
1. Thân xe gần đối xứng (mui trước và mui sau dài gần bằng nhau), nên mắt không phân biệt được đầu với đuôi. Cộng thêm chùm đèn, người xem thấy xe như đang đi lùi.
2. Chùm đèn pha bắt đầu ở y −16..−30, ngang nóc xe, rồi loe lên trên, trong khi đèn pha thật nằm thấp ở mũi xe. Chùm đèn được vẽ trước thân xe.
3. Đèn hậu đặt ở x = −47, nằm ngoài thân xe (thân kết thúc ở −46), trông như một chấm lơ lửng.
4. Xe đặt ở y = 410, nhưng mép đường ở 404, nên bánh xe nằm trên vạch hồng ở mép biển chứ không nằm trong làn đường.
5. Chuyển động không thống nhất: vạch đường trôi sang trái (như máy quay chạy theo xe) trong khi cọ, cột đèn và xe cùng chạy theo khung hình đứng yên.
   Cần chọn **một** hệ quy chiếu: máy quay đứng yên thì vạch đường đứng yên.
6. Cột đèn đường là ống thẳng + móc tròn, không có chi tiết Art Deco.

## C. Nguyên tắc chống "bị AI / làm qua loa" (checklist cho mọi task)
- Không có hai mục nào dùng chung khung hay chung bố cục. Mỗi mục là một **cảnh** khác nhau: phố, nội thất, HUD, áp phích, vòng chọn vũ khí, đài radio.
- Mỗi cảnh có **ít nhất 3 lớp chiều sâu** (xa / giữa / gần) và **một nguồn sáng chính** có hướng rõ (mặt trời lặn), cộng neon làm nguồn sáng phụ. Bóng đổ và viền sáng phải khớp hướng sáng.
- **Chi tiết đúng chuyện**: đồ vật có lý do tồn tại (terminal hiện lệnh thật của repo công khai, ly cà phê có vết, dây cáp, nhãn dán laptop).
  Không có chi tiết độn vô nghĩa.
- Độ đậm của nét mực giảm theo khoảng cách: gần dày khoảng 3 px, xa không có nét. Halftone chỉ dùng ở vùng bóng.
- Khoảng 5% bất toàn có chủ đích: neon có một chữ chập chờn, sơn tường bạc, cửa sổ tắt đèn không đều.
- Mọi khẳng định về GTA VI phải có nguồn kèm độ tin cậy. Không chép tài sản của Rockstar (logo, ảnh, font logo, nhân vật).

## D. Kiến trúc kỹ thuật đích
```
tools/art/                 Thư viện vẽ (mới)
  palette.py               Bảng màu theo dải (trời, mặt tiền pastel, neon, mực bóng) + quy tắc ánh sáng
  geom.py                  Tiện ích path, phối cảnh 1 điểm, nhiễu có seed
  deco.py                  Bộ sinh mặt tiền Art Deco
  palm.py  car.py  neon.py  street.py  props.py  sky.py
  post.py                  Hậu kỳ Pillow: bloom, halftone, viền mực, quang sai, grain, chỉnh màu (LUT)
  render.py                SVG lớp → PNG 2x (Chrome headless) → hậu kỳ → WebP/JPEG → nhúng base64
tools/build_assets.py      Chỉ điều phối: ghép cảnh, chữ (fontTools), SMIL
tools/preview.py           + bảng ảnh nhiều mốc thời gian, khổ mobile, nền sáng
tools/budget.py            Báo dung lượng từng asset; báo lỗi khi vượt ngân sách
```
Mỗi cảnh = **lớp nền raster tĩnh** (chi tiết, ánh sáng, texture) + **lớp SVG động** (xe, neon nhấp nháy, cọ đung đưa, mây, chữ gõ).
Các vật chuyển động phải vẽ bằng vector để SMIL điều khiển được, và dùng cùng palette/nét với nền để không bị lệch phong cách.
Nếu cần numpy thì cài trong venv, giống fontTools.

## E. Các giai đoạn và task

### Giai đoạn 0 — Nền móng
| ID | Task | Đầu ra / tiêu chí xong | Model |
|---|---|---|---|
| T0.0 | **Hotfix xe ở banner hiện tại** (trong lúc chờ v3): vẽ lại dáng xe có mui trước dài và đuôi cụt, chùm đèn thấp phát ra từ mũi xe theo hướng chạy, đèn hậu nằm trong thân xe, bánh xe nằm trong làn đường, vạch đường đứng yên | Ảnh preview 3 mốc thời gian, người xem nhận ra ngay đâu là đầu xe | Sonnet |
| T0.1 | **Nghiên cứu sau phát hành** (vòng 2): HUD/điện thoại/menu GTA VI từ review sau 19/11 (IGN, Eurogamer, GameSpot, Rockstar Newswire); trang artwork chính thức; kiến trúc Miami Beach (MDPL, miamiandbeaches.com) | `docs/REFERENCES.md`: mỗi điểm có link + độ tin cậy (xác minh / thứ cấp / suy đoán) | Opus |
| T0.2 | **Style guide** `docs/STYLE.md`: dải màu (mở rộng bảng màu hiện có), mô hình ánh sáng, độ dày nét theo khoảng cách, halftone, typography (Anton/Barlow + tìm thêm font OFL cho logo/neon nếu cần), bố cục từng mục, checklist mục C | Trang mẫu ghép màu/nét/texture render được | Opus · **🔶 chủ repo duyệt** |
| T0.3 | **Tách `build_assets.py` thành `tools/art/`**, không đổi hình | Diff ảnh trước/sau = 0 (so sánh PNG render ở cùng mốc thời gian) | Sonnet |
| T0.4 | **Pipeline raster** (`render.py`, `post.py`): render lớp, bloom, halftone, viền mực, grain, LUT, xuất WebP/JPEG, nhúng vào SVG | 1 SVG thử: nền WebP + 1 vật SMIL. Chủ repo xác nhận trên GitHub rằng WebP-trong-SVG hiển thị được (chưa test; nếu không được thì dùng JPEG) | Sonnet (tinh chỉnh hậu kỳ: Opus) |
| T0.5 | **Công cụ QA**: preview nhiều mốc, khổ 390 px (mobile), nền sáng `#ffffff`, `budget.py` | Một lệnh sinh bảng ảnh để duyệt | Haiku |

### Giai đoạn 1 — Thư viện chi tiết (mỗi món có trang mẫu riêng để duyệt)
| ID | Task | Chi tiết bắt buộc | Model |
|---|---|---|---|
| T1.1 | **Mặt tiền Art Deco** (tham số hóa) | Mái bậc thang/ziggurat, mái hiên "eyebrow" trên cửa sổ, sọc dọc, cửa sổ tròn, gạch kính, tháp giữa có chóp, biển neon dọc, mái che vỉa hè, ban công cong; bộ màu pastel; mặt hướng nắng sáng, mặt kia tối; cửa sổ sáng có rèm hoặc bóng nội thất | Opus · 🔶 |
| T1.2 | **Xe thể thao 80s** (nhìn ngang, có tham số hướng) | Dáng nêm, đèn pha lật, đường cửa, la-zăng có nan, phản chiếu trên kính, dải đèn hậu, bóng đổ dưới gầm; chùm đèn thấp phát từ mũi xe; bánh xe quay; bóng phản chiếu trên mặt đường ướt | Opus · 🔶 |
| T1.3 | **Cọ v2** | Tàu lá có lá chét, thân có vòng đốt, chùm dừa; 3 mức chi tiết theo khoảng cách; đung đưa lệch pha | Sonnet · 🔶 |
| T1.4 | **Bộ neon** | Ống neon gồm lõi trắng + 2–3 lớp quầng màu, giá đỡ, dây điện; kiểu nhấp nháy thật (tắt chập chờn ngẫu nhiên, một chữ hỏng); chữ neon từ font | Sonnet · 🔶 |
| T1.5 | **Trời / biển / phố** | Mây tích nhiều lớp đón nắng, mặt trời bị khí quyển làm dẹt, sóng và bọt, cát, vỉa hè, cột đèn Art Deco, chòi cứu hộ pastel, chim bồ nông, bóng người nhỏ ở xa | Sonnet · 🔶 |
| T1.6 | **Đồ vật cho Safehouse** | Laptop (terminal hiện lệnh thật của repo công khai), cà phê, tai nghe, điện thoại có thẻ tin nhắn, rèm lá sách đổ bóng sọc, cây cảnh, dây cáp | Sonnet · 🔶 |

### Giai đoạn 2 — Banner (cảnh chuẩn cho cả trang)
| ID | Task | Đầu ra | Model |
|---|---|---|---|
| T2.1 | **3 phác thảo bố cục** xám trắng cho Ocean Drive: vị trí logo, dãy khách sạn, đường, xe, biển | 3 ảnh thumbnail | Opus · **🔶 chủ repo chọn** |
| T2.2 | **Logo xếp tầng** `LUCHUB` / `19`: ruột chữ chứa cảnh hoàng hôn + cọ, viền nhiều lớp, đổ bóng, quang sai nhẹ | Trang mẫu logo | Opus · 🔶 |
| T2.3 | **Dựng banner** từ thư viện + hậu kỳ raster | Ảnh tĩnh ≤ 1 MB | Opus |
| T2.4 | **Hoạt ảnh vừa phải**: xe chạy đúng hướng, neon nhấp nháy, cọ đung đưa, mây trôi, cửa sổ bật đèn, tagline tự gõ (giữ 3 câu đã duyệt) | Khung đầu (t = 0) phải đẹp như ảnh tĩnh | Sonnet |
| T2.5 | Duyệt bản hoàn chỉnh | | **🔶 chủ repo** |

### Giai đoạn 3 — Các mục còn lại (bắt đầu sau khi banner được duyệt)
| ID | Task | Hướng | Model |
|---|---|---|---|
| T3.1 | **Dải tiêu đề chương** | Bỏ kiểu dải skyline lặp lại. Mỗi chương là một vật thật trên phố: biển tên đường, bảng neon, biển quảng cáo, tấm vé, mặt đài | Sonnet (bố cục: Opus) |
| T3.2 | **Player One → Safehouse** | Cảnh bàn làm việc cạnh cửa sổ nhìn ra Ocean Drive; giữ hook/bio/thoại/thẻ tin nhắn đã duyệt | Opus |
| T3.3 | **HUD** | Cảnh phố từ thư viện; bám HUD thật theo `REFERENCES.md`, phần nào chưa xác minh thì ghi rõ; xe 80s xuất hiện trên đường; số liệu vẫn tự cập nhật | Sonnet (đặc tả: Opus) |
| T3.4 | **Missions** | vibeKing: khung tủ máy arcade minh họa bao quanh ảnh thật. **didau**: chụp app thật (Chrome headless, dữ liệu sạch), áp phích mới, chủ repo duyệt chữ. Classified: làm hồ sơ mật kỹ hơn (giấy, kẹp, dấu, ảnh bị che) | Opus (chụp didau: Sonnet) |
| T3.5 | **Loadout → vòng chọn vũ khí** | 4 ô có đồ vật vẽ tay theo ẩn dụ (cần chủ repo duyệt ẩn dụ cho từng ngôn ngữ), ô đang chọn sáng lên, giữ "SELECT YOUR WEAPON" + 4 chú thích | Opus · 🔶 |
| T3.6 | **Radio** | Mặt đài xe hơi 80s / bộ dàn trong xe chữ ký, màn hình LCD chạy chữ, kim dò đài; dữ liệu từ `data/radio.json` | Sonnet |
| T3.7 | **Chân trang** | Rắn + dòng tuyên bố fan-made, trình bày kiểu danh đề cuối phim | Haiku |

### Giai đoạn 4 — Kiểm tra và bàn giao
| ID | Task | Model |
|---|---|---|
| T4.1 | Kiểm tra ngân sách dung lượng, alt text, preview mobile/nền sáng; thêm `?v=N` vào URL ảnh để vượt cache camo | Haiku |
| T4.2 | Chủ repo xem trên GitHub thật (desktop + app mobile) | 🔶 chủ repo |
| T4.3 | Cập nhật `HANDOFF.md` (mục 6, 7, 8) | Haiku |

Thứ tự phụ thuộc: T0.0 làm độc lập. T0.1 → T0.2 → (T0.3 ∥ T0.4 ∥ T0.5) → Giai đoạn 1 → Giai đoạn 2 → Giai đoạn 3 → Giai đoạn 4.
Trong Giai đoạn 1, các task T1.x chạy song song được sau khi có `palette.py` và `post.py`.

## F. Rủi ro / chưa chắc
- **WebP trong data URI bên trong SVG** hiển thị qua `<img>` trên GitHub: chưa test (T0.4 kiểm tra; dự phòng là JPEG).
- SVG nặng khoảng 1 MB có thể bị GitHub/camo xử lý chậm hoặc giới hạn: chưa có số liệu chính xác, cần đo ở T0.4.
- Thông tin HUD GTA VI phần lớn vẫn từ bài trước phát hành; T0.1 tìm nguồn sau phát hành.
- Vẽ đẹp bằng code thủ tục tốn công. Phần khó nhất là mặt tiền Art Deco và xe, nên hai task này dùng Opus và có vòng duyệt riêng.

## G. Câu hỏi để hỏi ở các mốc sau
- (T0.2) Chọn 1 trong 2–3 bảng màu: hoàng hôn ấm hay chạng vạng tím lạnh. Có thêm xanh lá kiểu trailer 2 không?
- (T1.2) Màu xe chữ ký (trắng / đỏ / đen / hồng)? Mui trần hay targa?
- (T1.6/T3.2) Terminal trên laptop hiện lệnh gì, sticker gì trên laptop, đồ uống gì? Có chi tiết thật nào muốn cài vào không?
- (T3.4) Chữ cho áp phích didau (hook, bio, 2 câu thoại). Ảnh chụp dùng màn hình nào?
- (T3.5) Ẩn dụ đồ vật cho C/C++, Python, TypeScript, Linux.
- Vẫn còn mở từ HANDOFF: bộ đếm lượt xem; rice laptop (Safehouse chờ ảnh thật).
