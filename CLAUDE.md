# Luật cho AI khi làm việc trong repo này

- **Không thêm Claude làm co-author.** Không đặt dòng `Co-Authored-By: Claude ...` hay
  `Generated with Claude Code` trong commit message, mô tả PR hoặc bất cứ đâu. Commit chỉ mang tên chủ repo.
- Không link hay nhắc tên repo riêng tư trên README công khai.
- Sửa giao diện: chỉnh `tools/build_assets.py`, chạy `python3 tools/fetch_stats.py luchub-19` rồi
  `python3 tools/build_assets.py` (cần `pip install fonttools`). Không sửa tay file trong `assets/`.
- Trả lời người dùng bằng tiếng Việt, README viết tiếng Anh.
