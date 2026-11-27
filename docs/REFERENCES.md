# REFERENCES — Nguồn tham chiếu cho v3 (task T0.1)

Soạn 2026-11-27 (8 ngày sau khi GTA VI phát hành 19/11/2026). Đọc kèm `docs/HANDOFF.md`, `docs/PLAN-v3.md`.
**Không tải ảnh của Rockstar vào repo.** File này chỉ ghi link và mô tả bằng chữ.

## Cách đọc độ tin cậy
| Nhãn | Nghĩa |
|---|---|
| **Xác minh** | Đọc trực tiếp từ nguồn chính thức (Rockstar, MDPL, thành phố Miami Beach), hoặc lời dev Rockstar được báo uy tín trích nguyên văn, hoặc ≥ 2 nguồn độc lập sau phát hành nói giống nhau |
| **Thứ cấp** | Một trang hướng dẫn hay bài tổng hợp bên thứ ba; hoặc đoạn trích từ máy tìm kiếm mà chưa đọc được toàn văn |
| **Suy đoán** | Cách người viết đọc video trước phát hành, các nguồn mâu thuẫn nhau, hoặc chỉ có một nguồn viết trước 19/11 |

Lưu ý chung: **chưa trang hướng dẫn nào nói tác giả đã tự chơi bản phát hành.** Phần lớn dựa trên video *An Extended Look*
(Rockstar, 27/8/2026, quay trên PS5) cộng với phỏng vấn. Vì vậy hầu hết chi tiết HUD dưới đây chỉ ở mức **thứ cấp**.

## Nguồn không đọc được (đừng thử lại cùng cách)
| Nguồn | URL | Kết quả |
|---|---|---|
| IGN review (Luke Reilly, 10/10) | https://www.ign.com/articles/grand-theft-auto-vi-review | Công cụ fetch và tìm kiếm bị chặn |
| Eurogamer review (Chris Tapsell, 5/5) | https://www.eurogamer.net/grand-theft-auto-6-review | Bị chặn |
| GameSpot review (Tamoor Hussain, 10/10) | https://www.gamespot.com/reviews/grand-theft-auto-6-review/ | HTTP 403 (chỉ có đoạn trích từ máy tìm kiếm) |
| Rockstar Newswire "GTA VI Now Available" | https://www.rockstargames.com/newswire/article/39akk424a9oo53/grand-theft-auto-vi-now-available | Chỉ trả về khung JS |
| Rockstar Newswire "Launch Gallery" | https://www.rockstargames.com/newswire/article/39ak81277255o9/explore-the-grand-theft-auto-vi-launch-gallery | Chỉ trả về khung JS |
| Thông cáo Take-Two | https://taketwointeractivesoftwareinc.gcs-web.com/news-releases/news-release-details/rockstar-games-announces-grand-theft-auto-vi-now-available | HTTP 403 |
| GamesRadar (review, hướng dẫn Heat, bài 6 sao) | xem mục 1.3 | Chỉ lấy được tiêu đề trang |
| miamiandbeaches.com (2 trang kiến trúc) | xem mục 3 | HTTP 403 |

Tên tác giả và điểm số ở trên lấy từ OpenCritic (https://opencritic.com/game/15398/grand-theft-auto-vi; top critic average 99). Chủ repo có thể mở các bài này
bằng trình duyệt rồi dán đoạn về HUD/điện thoại vào để nâng độ tin cậy.

---

## 1. GTA VI — HUD, minimap, sao truy nã

### 1.1 Nguyên tắc thiết kế (từ Rockstar)
| # | Điểm | Nguồn | Độ tin cậy |
|---|---|---|---|
| H1 | Rockstar giữ các "chữ ký" cũ: **font Pricedown, mini-map, sao truy nã, màn hình Wasted**. Nguyên văn: "From the iconic Pricedown font to the familiar mini-map to the wanted stars and the unmistakable Wasted screen" | Stuart Petri (VP of Art: 2D/UI Design, Rockstar), qua TechRadar, Rob Dwiar, 24/11/2026: https://www.techradar.com/gaming/gta-6-dev-says-rockstar-evolved-the-hud-by-pushing-the-design-language-forward-keeping-the-player-immersed-while-keeping-the-heritage-of-gta-the-game-is-what-matters-most-and-the-ui-is-there-to-serve-that-experience | **Xác minh** (lời dev). Trước đây HANDOFF xếp điểm này là thứ cấp qua Leonida Bay, nay đã đọc được bài gốc |
| H2 | HUD phải kín đáo: "It should be there when you need it, but at the same time is not distracting." / "We aim to keep the players immersed in the world as much as possible" | Như H1 | **Xác minh** |
| H3 | **HUD động**: bấm một nút D-pad để thu gọn UI hoặc hiện đủ bộ (bản đồ, ví tiền, thanh trạng thái, buff) | TechRadar (lời phóng viên tóm tắt ghi chú của dev; không nói nút hướng nào) | **Xác minh** cho việc có ẩn/hiện. Hướng nút: xem H4 |
| H4 | Mặc định HUD ẩn bớt; **bấm D-pad xuống** để hiện minimap và các phần chính; tắt/bật từng phần trong Settings | GamesRadar (đoạn trích máy tìm kiếm: "you need to press down on the D-pad to bring up key elements such as the minimap"; không rõ là trang hướng dẫn nào của GamesRadar, có thể là https://www.gamesradar.com/games/grand-theft-auto/gta-6-classic-controls/) | **Thứ cấp** |

**Dùng cho v3:** HUD trong README nên ít chữ, để cảnh phố là chính. ~~Có thể dùng chữ kiểu Pricedown? Không.~~ **Cập nhật 27/11:** chủ repo muốn chữ đậm chất GTA hơn. Pricedown là font của Typodermic (không phải của Rockstar), miễn phí theo Desktop EULA, nên được dùng cho logo và tiêu đề với điều kiện ở STYLE.md mục 5.4.

### 1.2 Bố cục màn hình
| # | Điểm | Nguồn | Độ tin cậy |
|---|---|---|---|
| H5 | **Góc trên trái**: các thanh chỉ số (máu = tim, thể lực = tia sét, Focus = mắt, O2 khi lặn) | games.gg (cập nhật 23/11/2026): https://games.gg/grand-theft-auto-vi/guides/gta-6-hud-and-ui-icons-explained/ · technerdiness (4/10/2026, trước phát hành): https://www.technerdiness.com/gta/gta-6-hud-icons-explained/ · gtamap.io: https://gtamap.io/gta-6-gameplay/ | **Thứ cấp** (3 nguồn đồng ý nhưng đều dựa trên footage/guide) |
| H6 | Màu thanh: máu **hồng**, thể lực **cyan**, Focus **tím**, O2 **xanh lá** | technerdiness (cách tác giả đọc footage) · SixCentral (hồng/cyan/tím ở màn trang bị): https://sixcentral.co.uk/news/gta-6-hud-interface-explained | **Suy đoán** (không có mã màu; chỉ là cách đọc video) |
| H7 | **Góc trên phải**: vũ khí + đạn, sao truy nã, dãy icon bên dưới sao, tiền | games.gg · technerdiness | **Thứ cấp** |
| H8 | Tiền: số dư **BuckMe (ngân hàng) màu tím** và **tiền mặt màu xanh lá**; ví tiền mặt tối đa $20,000 | games.gg | **Thứ cấp** (chỉ một nguồn ghi màu) |
| H9 | Hai số tiền xếp chồng "15,150" và "700" nằm ở **màn trang bị/vòng vũ khí**, không phải HUD lúc chạy ngoài phố; chưa rõ số nào là gì | SixCentral (cập nhật 21/11/2026) · technerdiness đoán là ngân hàng + tiền mặt | **Suy đoán**. ⚠ HANDOFF mục 4 ghi "hai số tiền xếp chồng góc trên phải" mà không nói đó là màn trang bị |
| H10 | **Minimap góc dưới trái**, vẽ như GPS thật, có **nhà 3D** | technerdiness · gtamap.io ("a minimap rendering 3D buildings") · games.gg | **Thứ cấp**. **Hình dạng (tròn hay vuông) chưa nguồn nào nói rõ** |
| H11 | **Cảnh sát không hiện trên minimap**; phải tìm bằng mắt, Focus hoặc máy nghe lén radio cảnh sát | technerdiness · nhiều trang guide | **Thứ cấp** |
| H12 | Khi bị truy nã, **vùng tìm kiếm tô đỏ/hồng** trên minimap; ở mức sao cao, minimap bị **đèn đỏ–xanh nhấp nháy** che bớt | allthings.how (30/8/2026, trước phát hành): https://allthings.how/gta-6-wanted-system-explained-how-heat-builds-and-how-you-lose-it/ · GamesRadar (đoạn trích tìm kiếm, dùng chữ "looks like"): https://www.gamesradar.com/games/grand-theft-auto/gta-6-wanted-levels-heat/ | **Thứ cấp** (vùng đỏ) / **Suy đoán** (đèn che minimap) |

### 1.3 Sao truy nã và Heat
| # | Điểm | Nguồn | Độ tin cậy |
|---|---|---|---|
| W1 | Tối đa **6 sao** | GameSpot review (đoạn trích: "extreme six-star wanted-level situations") · tiêu đề GamesRadar "GTA 6 wanted system goes up to 6 stars…": https://www.gamesradar.com/games/grand-theft-auto/gta-6-wanted-system-goes-up-to-6-stars-and-lets-police-track-your-face-your-clothes-and-your-car/ · GamesRadar review (đoạn trích): https://www.gamesradar.com/games/grand-theft-auto/gta-6-review/ · games.gg | **Xác minh** (≥ 2 nguồn sau phát hành; 1 nguồn trước phát hành nói 5 sao, xem M1) |
| W2 | Sao có **nhiều trạng thái**: rỗng (bị báo, chưa có nhận dạng) · trắng đặc (đang bị truy đuổi, trong tầm nhìn) · trắng nhấp nháy (mất dấu) · đỏ (vùng nóng sau truy đuổi) | games.gg · technerdiness (cùng 4 trạng thái) · GamesRadar (đoạn trích: sao "take on various appearances" theo trạng thái) | Có trạng thái: **xác minh**. Ý nghĩa từng màu: **thứ cấp** (các guide gán nghĩa hơi khác nhau) |
| W3 | Dưới sao có **dãy icon "bằng chứng"**: CCTV, khuôn mặt, quần áo (móc treo), vũ khí, xe, hai người (cặp đôi) | games.gg · technerdiness · gtamap.io · tiêu đề GamesRadar ("track your face, your clothes, and your car") | **Thứ cấp** (xem M2) |
| W4 | **Heat**: cảnh sát nhớ nhận dạng (trang phục, xe, CCTV) sau truy đuổi; đổi xe hoặc đổi đồ để xóa | GamesRadar review (đoạn trích) · allthings.how · trang hướng dẫn sơn xe GamesRadar: https://www.gamesradar.com/games/grand-theft-auto/gta-6-respray-cars-how-to/ | **Thứ cấp** |
| W5 | "Criminal Profile" có bật thông báo trên HUD, tắt được | Tiêu đề bài Eurogamer được gtamap.io trích: "I'm having a much better time in GTA 6 now I've disabled its pesky Criminal Profile pings" (https://gtamap.io/gta-6-reviews/) | **Thứ cấp**. Tên các bậc Profile mâu thuẫn giữa các guide → **đừng dùng** |

**Dùng cho v3 (T3.3):** 6 sao khớp HUD hiện tại. Hiện `hud()` cho sao nhấp nháy đổi màu kem → hồng → cyan; game thật (theo guide) dùng **trắng đặc / trắng nhấp nháy / đỏ / rỗng**.
Có thể ánh xạ sang số liệu commit (ví dụ: sao rỗng là các mốc chưa đạt) mà không bịa thêm.

### 1.4 Điện thoại
| # | Điểm | Nguồn | Độ tin cậy |
|---|---|---|---|
| P1 | Mở bằng **D-pad lên**; nhận cuộc gọi cũng bằng nút lên | Beebom (19/11/2026, ảnh "screenshot by Beebom"): https://beebom.com/gta-6-phone-guide/ · gtaboom: https://www.gtaboom.com/gta-6-phone-apps-fb38 | **Xác minh** (2 nguồn độc lập; Beebom có vẻ chụp từ game) |
| P2 | Điện thoại là **vật thể trong tay**, dùng **không dừng game**; lên xe thì camera chuyển sang góc thứ nhất | gtaboom (ngày ghi 9/10/2026 nhưng nội dung mô tả sau phát hành, ngày không khớp) | **Thứ cấp** |
| P3 | Hội thoại tin nhắn hiện thành **thẻ nổi trên cảnh**, không chiếm toàn màn hình | SixCentral (đọc từng khung video Extended Look) | **Suy đoán** (cách đọc video; khớp với thẻ tin nhắn đang dùng ở `poster-profile.svg`) |
| P4 | Tên app: **WhatUp** (tin nhắn), Contacts, **BuckMe** (ngân hàng), **RydeMe** (gọi xe, kiêm di chuyển nhanh), **WAiNK** (quét xe), **Scooter Bros** (giao xe), **Snapmatic** (mạng xã hội, chỉ xem), Camera, Gallery, Fitness, News, Weather, Settings, Vice City Real Estate | gtaboom (14 app) · Beebom ("more than 12 apps") · games.gg (15 app): https://games.gg/grand-theft-auto-vi/guides/grand-theft-auto-6-phone-apps-every-app-and-what-they/ · gtamap.io | Tên WhatUp, BuckMe, RydeMe, WAiNK, Snapmatic: **xác minh** (nhiều nguồn trùng). Tổng số app: **mâu thuẫn** (12/14/15) |

**Dùng cho v3:** **Không dùng tên app hay logo app của Rockstar** trong ảnh (đó là tài sản của họ). Chỉ mượn *cách trình bày*: thẻ tin nhắn nổi, điện thoại cầm tay trong cảnh (T1.6).

### 1.5 Menu: vòng vũ khí, menu tạm dừng
| # | Điểm | Nguồn | Độ tin cậy |
|---|---|---|---|
| M-a | Vòng chọn đồ có **2 tab WEAPONS / ITEMS**, chuyển tab bằng R1/RB, giữ L1/LB để mở; ô đồ xếp thành **vòng tròn** | SixCentral ("The overlay separates WEAPONS and ITEMS", "a ring of equipment tiles") · 6cheats (cập nhật 21/11/2026): https://www.6cheats.com/en/guides/gta-6-inventory-weapon-wheel-explained | **Thứ cấp** |
| M-b | Chỉ mang được **số vũ khí giới hạn** khi đi bộ (2 súng ngắn, 2 súng dài, cận chiến, chất nổ, thiết bị); phần còn lại cất trong xe | 6cheats · gtamap.io | **Thứ cấp** |
| M-c | Vòng vũ khí có **dừng/làm chậm game** không | 6cheats ghi rõ là chưa xác nhận; một guide khác nói cảnh bị làm mờ chứ không dừng | **Suy đoán** |
| M-d | Menu tạm dừng mở thẳng vào **bản đồ**; danh sách tab | Chỉ có trang guide SEO (beatcopgame, theclick.gg); các guide liệt kê tab khác nhau | **Suy đoán**. Đừng vẽ theo |

**Dùng cho v3 (T3.5):** "vòng chọn vũ khí" ở Loadout khớp với game (dạng vòng, có tab). Có thể thêm 2 nhãn tab kiểu `WEAPONS / ITEMS` mà không chép đồ họa.

### 1.6 Artwork chính thức (chỉ để xem, không tải vào repo)
| # | Điểm | Nguồn | Độ tin cậy |
|---|---|---|---|
| A1 | Trang tải về chính thức: Featured, Videos, Screenshots (138), **Artwork & Wallpapers (28)** | https://www.rockstargames.com/VI/downloads · https://www.rockstargames.com/VI/media/artwork-wallpapers | **Xác minh** (đọc trực tiếp) |
| A2 | 28 artwork gồm: key art Jason & Lucia (Rooftop, Lock and Load, Robbery, Beach, Motel…), cover art, The Album Cover Art, chân dung nhân vật phụ, **6 tấm bưu thiếp địa danh**: **Vice City Postcard**, Leonida Keys, Port Gellhorn, Ambrosia, Grassrivers, Mount Kalaga National Park | Như A1 (chỉ đọc được tên, chưa thấy ảnh) | Tên: **xác minh**. Nội dung tấm Vice City Postcard (có Ocean Drive/Art Deco không): **chưa biết** |
| A3 | Ngày phát hành 19/11/2026, **PS5 và Xbox Series X\|S**, nhãn "Plays Best On PS5". Chưa có bản PC chính thức | https://www.rockstargames.com/VI/out-now · Newswire dời ngày: https://www.rockstargames.com/newswire/article/ak3ak31a49a221/grand-theft-auto-vi-is-now-set-to-launch-november-19-2026 | **Xác minh** |
| A4 | Video chính thức: Trailer 1 (4/12/2023), Trailer 2 (6/5/2025), An Extended Look (27/8/2026), Launch Trailer (15/10/2026) | https://www.rockstargames.com/VI/out-now | **Xác minh** |

**Gợi ý xem tay (chủ repo):** mở **Vice City Postcard** và vài ảnh *Screenshots* tên "Vice City NN" để xem cách Rockstar vẽ dãy khách sạn, neon, bố cục bưu thiếp.
Chỉ dùng để tham khảo bố cục và ánh sáng; không chép hình.

---

## 2. Kiến trúc Art Deco Miami Beach (cho T1.1, T1.5, T2.x)

Ký hiệu nguồn:
- **[mdpl-deco]** https://mdpl.org/design-style/art-deco-design-style/
- **[mdpl-styles]** https://mdpl.org/miami-design-styles/
- **[mdpl-mimo]** https://mdpl.org/design-style/memo-design-style/
- **[city-arch]** https://www.miamibeachfl.gov/architecture
- **[city-deco]** https://www.miamibeachfl.gov/architecture/art-deco/
- **[city-med]** https://www.miamibeachfl.gov/architecture/mediterranean-revival/
- **[city-mimo]** https://www.miamibeachfl.gov/architecture/mimo-miami-modern/
- **[pbs]** https://www.pbs.org/wgbh/americanexperience/features/miami-beach-deco/
- **[wiki]** https://en.wikipedia.org/wiki/Miami_Beach_Architectural_District

MDPL là Miami Design Preservation League (tổ chức bảo tồn). `miamiandbeaches.com` trả 403, chỉ có đoạn trích từ máy tìm kiếm.

### 2.1 Chi tiết hình khối (dùng trực tiếp cho bộ sinh mặt tiền)
| # | Chi tiết | Trích dẫn | Nguồn | Độ tin cậy |
|---|---|---|---|---|
| D1 | **Mái hiên "eyebrow"** trên cửa sổ dải ngang | "eyebrow awnings shading horizontal strip windows" | [mdpl-deco] · [pbs] ("window "eyebrows"") | **Xác minh** |
| D2 | **Mái bậc thang ziggurat** | "ziggurat rooflines stepping upward like stylized pyramids" | [mdpl-deco] · [city-deco] ("step-back designs") | **Xác minh** |
| D3 | **Đường đứng, cảm giác vươn lên**; vây đứng (vertical fin) | "Tall, Vertical Lines" · Colony Hotel có "vertical fin" | [city-deco] · [mdpl-deco] | **Xác minh** |
| D4 | **Cửa sổ tròn kiểu tàu biển** | "round porthole windows borrowed straight from ocean liner design" | [mdpl-deco] · [pbs] (Essex House) | **Xác minh** |
| D5 | **Gạch kính (glass block)** | "glass block catching the light are everywhere" | [mdpl-deco] · [city-deco] | **Xác minh** |
| D6 | **Tháp nhô, tháp neon như ống khói tàu** | "jutting towers" · "smokestack-like neon tower" (Essex House, Henry Hohauser, 1938) | [pbs] | **Xác minh** (1 nguồn chính thống) |
| D7 | **Góc bo tròn** (Streamline Moderne) | "curved corners and edges that seem to slice through the air" | [mdpl-deco] (Carlyle, 1250 Ocean Drive) · [city-deco] | **Xác minh** |
| D8 | **Đối xứng, chi tiết theo bộ ba** | "Symmetry is your anchor." · "Count the details in threes — Art Deco loves a trio." · Carlyle: "three dramatic vertical columns" | [mdpl-deco] · [city-deco] ("symmetrical designs") | Đối xứng: **xác minh**. "Bộ ba": mẹo quan sát của MDPL, không phải luật thiết kế → **thứ cấp** |
| D9 | **Phù điêu nhiệt đới** (cây, chim, sóng, motif tàu biển) đắp lên khối Deco = "Tropical Deco", phong cách riêng của Miami | "whimsical relief ornamentation of flora, fauna, and ocean-liner motifs" | [mdpl-styles] | **Xác minh** |
| D10 | **Neon**: báo hiệu khách sạn ban đêm; ví dụ Breakwater neon **xanh cobalt** | "Neon signs effectively announced a hotel's presence" · "after dark, the neon comes alive" | [pbs] · [mdpl-deco] · [city-deco] | **Xác minh** |
| D11 | Vật liệu: sàn **terrazzo**, gạch kính, neon | "terrazzo floors, neon lighting and glass block windows" | [city-deco] (Streamline) · [city-mimo] | **Xác minh** |
| D12 | **Chòi cứu hộ** kiểu "Nautical Art Deco" (William Lane) | "The lifeguard towers designed by William Lane in Miami Beach" | [city-deco] | **Xác minh** |
| D13 | Chóp nhọn (spire/finial), đá khóa vòm (keystone) | Không trang nào nhắc | — | **Chưa có nguồn**. Dùng hạn chế |

### 2.2 Màu sắc — ⚠ có mâu thuẫn (xem M4)
| # | Điểm | Nguồn | Độ tin cậy |
|---|---|---|---|
| C1 | Màu **pastel "kẹo ngọt"** trên mặt tiền là do **Leonard Horowitz** sơn lại sau này, không phải màu gốc thập niên 1930 | "Leonard Horowitz updated the exteriors… with a confectionary pastel paint scheme" | [pbs] (không ghi năm) | **Xác minh** cho việc ai sơn; năm sơn: chưa có nguồn đã đọc |
| C2 | Màu Deco gốc theo thành phố: **màu rực, tương phản đen–trắng, điểm vàng kim** | "Vibrant, eye-catching colors, often with contrasts like black and white, or gold accents" | [city-deco] | **Xác minh** (nhưng mô tả chung về Art Deco, không riêng Ocean Drive) |
| C3 | Mediterranean Revival: **vữa trắng/sáng màu + mái ngói đỏ/cam**, vòm tròn hoặc nhọn | "White or light-colored stucco… red-tiled roofs" · "Rounded or pointed arches" | [city-med] | **Xác minh** |

### 2.3 Phạm vi và bối cảnh (cho bố cục banner Ocean Drive)
| # | Điểm | Nguồn | Độ tin cậy |
|---|---|---|---|
| L1 | Dãy khách sạn Ocean Drive nổi tiếng nhất nằm **từ đường 5 tới đường 15**, mặt hướng ra biển | [mdpl-deco] ("the most concentrated strip of Art Deco architecture in the world") · [wiki] | **Xác minh** |
| L2 | Công trình Art Deco xây khoảng **1923–1943**, hơn 800 công trình | [city-deco] | **Xác minh** |
| L3 | Quận lịch sử vào National Register ngày **14/5/1979**, là quận lịch sử đô thị thế kỷ 20 đầu tiên của Mỹ | [city-arch] · [wiki] | **Xác minh** |
| L4 | Trung tâm Art Deco Welcome Center ở **1001 Ocean Drive** | miamiandbeaches.com (đoạn trích tìm kiếm; trang trả 403): https://www.miamiandbeaches.com/thing-to-do/attractions/art-deco-historic-district/2116 | **Thứ cấp** |
| L5 | **MiMo** (Miami Modern, sau Thế chiến II) chủ yếu ở **Mid/North Beach**, không phải Ocean Drive: mái bằng, khối bê tông trang trí, bất đối xứng, biển neon lớn | [city-mimo] · [mdpl-mimo] | **Xác minh** → **Không** đưa MiMo vào banner Ocean Drive; có thể dùng ở cảnh khác |
| L6 | Số công trình và diện tích quận khác nhau giữa các nguồn (960 / 800+ / 2.600+; "1 dặm vuông" vs 5.750 mẫu Anh) | [wiki] · [city-deco] · [city-arch] · [pbs] | Khác **phạm vi đo**, không phải mâu thuẫn thật. Không cần dùng số này |

---

## 3. Mâu thuẫn và cách xử lý
| # | Mâu thuẫn | Bên A | Bên B | Xử lý đề xuất |
|---|---|---|---|---|
| M1 | Số sao truy nã | 6 sao (GameSpot, GamesRadar, games.gg; đều sau phát hành) | 5 sao (allthings.how, 30/8/2026, trước phát hành) | Theo **6 sao** (nguồn mới hơn, nhiều hơn). Đã khớp HUD hiện tại |
| M2 | Dãy icon dưới sao | Icon **bằng chứng/nhận dạng** (CCTV, mặt, quần áo, xe, vũ khí, cặp đôi): games.gg, technerdiness, gtamap, tiêu đề GamesRadar | Icon **đơn vị cảnh sát** (người, xe tuần tra, trực thăng): allthings.how (trước phát hành) | **Chủ repo chốt (27/11): icon bằng chứng.** Map sang số liệu GitHub công khai ở T3.3 |
| M3 | Số tiền trên HUD | HANDOFF ghi "hai số tiền xếp chồng góc trên phải" | SixCentral: hai số đó nằm ở **màn trang bị**; games.gg: HUD ngoài phố có BuckMe (tím) + tiền mặt (xanh lá) | Đã sửa HANDOFF mục 4. **Chủ repo chốt (27/11): HUD hiện 2 số, ngân hàng (tím) = contribution năm × 10, tiền mặt (xanh lá) = commit 30 ngày × 10** |
| M4 | Màu mặt tiền | PLAN A chốt "pastel", khớp hình ảnh Ocean Drive ngày nay và Vice City | Màu gốc thập niên 30 là rực/tương phản/vàng kim [city-deco]; pastel là lớp sơn sau này [pbs] | **Chủ repo chốt (27/11): giữ pastel**, thêm viền trắng và vài điểm vàng kim (C2) |
| M5 | Số app điện thoại | 12 (Beebom) / 14 (gtaboom) / 15 (games.gg) | — | Không quan trọng: không dùng tên app trong ảnh |
| M6 | Tên các bậc Criminal Profile | games.gg / technerdiness / gtamap ghi khác nhau | — | Không dùng |

## 4. Điều vẫn KHÔNG xác minh được (đừng khẳng định)
Mã màu hex chính xác của HUD; hình dạng minimap (tròn hay vuông); độ mờ/viền/khoảng cách các phần tử HUD; menu tạm dừng gồm những tab nào;
vòng vũ khí có dừng game không; font dùng cho nhãn HUD ngoài Pricedown; nội dung tấm Vice City Postcard; năm Horowitz sơn pastel.
