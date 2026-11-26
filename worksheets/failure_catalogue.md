# Lab 8 — Failure catalogue

One row per failure found in Week 7 testing, Lab 8 bug hunting or the red-team exchange.

| # | Failure | Category | Found by | Severity | Mitigation | Regression test |
|---|---|---|---|---|---|---|
| 1 | Incorrect tuition calculation when retakes are written as words (e.g., "two retakes"). | wrong answer | Week 7 testing | Major | Parse number words correctly and include retake fees in the calculation. | `test_bug1_retake_number_as_word` |
| 2 | Feedback buttons remain visible after users submit a rating. | UI | Week 7 testing | Minor | Call `st.rerun()` after submitting feedback to refresh the interface. | `test_bug2_feedback_buttons_trigger_rerun` |
| 3 | Sidebar labels are displayed in Vietnamese instead of English. | UI | Week 7 testing | Minor | Replace Vietnamese sidebar labels with English equivalents. | `test_bug3_sidebar_labels_are_english` |

At least **3 mitigations** must be implemented and tested.