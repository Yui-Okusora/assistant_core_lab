# Lab 8 — Failure catalogue

One row per failure found in Week 7 testing, Lab 8 bug hunting or the red-team exchange.

| # | Failure | Category | Found by | Severity | Mitigation | Regression test |
|---|---|---|---|---|---|---|
| BUG-7 | Word-form retake count ("two retakes") was ignored, producing an undercalculated fee | Logic / Tool parsing | Major | Detect word numbers (`one`–`ten`) before `retake`/`credit` in `tools.py` and return `"Please write the number of retake credits as digits."` | `test_retake_number_as_word` |
| BUG-8 | Out-of-range credit count (99 credits) still returned a VND fee amount | Input validation | Minor | Enforce `1 <= credits <= 30` range check in `tuition()` | `test_fee_out_of_range_credits_gives_no_amount` |
| BUG-9 | [Mô tả lỗi thứ 3 từ Lab 7 của nhóm bạn] | [Category] | [Severity] | [Mô tả đoạn code đã sửa] | `[test_name_3]` |
