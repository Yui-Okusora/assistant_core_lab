# BUG-1: Fee question with the number written as a word gives a wrong total

**Date:** 2026-11-23   **Severity:** major
**Where:** API / AI (backend `src/assistant_core/tools.py`)

## Steps to reproduce
1. Open the FIT Study AI Assistant UI.
2. Type `tuition for 18 credits and two retakes` in the chat input and submit.

## Expected
`Your tuition is 9,450,000 VND.` (matching `Tuition for 18 credits and 2 retake`).

## Actual (paste the exact output or error)
`Your tuition is 8,100,000 VND.` (the `"two retakes"` part is silently ignored).

## Evidence
Observed in the Streamlit UI when comparing `"tuition for 18 credits and two retakes"` (`8,100,000 VND`) against the sidebar example `"Tuition for 18 credits and 2 retake"` (`9,450,000 VND`).

## Cause (after investigation)
`parse_credits()` in `src/assistant_core/tools.py` only extracts digits using `re.search(r"(\d+)\s*retake", text)` and `re.findall(r"\d+", text)`, so number words like `"two"` are ignored and `retake_n` defaults to `0`.

---

# BUG-2: Feedback buttons (👍 / 👎) do not disappear immediately after clicking

**Date:** 2026-11-23   **Severity:** minor
**Where:** UI (`ui/app.py`)

## Steps to reproduce
1. Open and ask any question (e.g., click `"Where is the library?"` in the sidebar).
2. Click `👍` (or `👎`) under the assistant's response.

## Expected
The feedback toast appears and the `👍` / `👎` buttons immediately disappear so the message cannot be clicked again.

## Actual (paste the exact output or error)
The toast `"Thanks for your feedback!"` appears, but both `👍` and `👎` buttons remain visible and clickable on that message until another action triggers a Streamlit rerun. Clicking `👎` afterwards triggers the rerun that removes both buttons (with no second toast).

## Evidence
Observed in the Streamlit UI across multiple assistant messages.

## Cause (after investigation)
In `ui/app.py`, `st.session_state.rated.add(rid)` and `st.toast(...)` are executed inside the `if c1.button("👍", ...)` / `if c2.button("👎", ...)` blocks without calling `st.rerun()`, so the already-rendered buttons stay visible for the current render pass.

---

# BUG-3: Mixed Vietnamese and English labels in the sidebar UI

**Date:** 2026-11-23   **Severity:** minor
**Where:** UI (`ui/app.py`)

## Steps to reproduce
1. Open.
2. Inspect the left sidebar buttons and compare them with the rest of the application.

## Expected
All UI controls use a consistent language (English, matching the title, welcome message, example questions, responses, toasts, and exported `chat_history.txt`).

## Actual (paste the exact output or error)
Two sidebar buttons are in Vietnamese (`"🗑️ Xóa lịch sử trò chuyện"` and `"📥 Tải lịch sử chat"`), while all other UI text and responses are in English.

## Evidence
Observed in the left sidebar.

## Cause (after investigation)
Hardcoded Vietnamese labels in `ui/app.py` (`st.button("🗑️ Xóa lịch sử trò chuyện", ...)` and `st.download_button(label="📥 Tải lịch sử chat", ...)`).
