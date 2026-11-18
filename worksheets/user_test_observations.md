# Lab 7 homework — 10-minute usability test

Tester (not in your team, first name only): Minh  Date: November 19, 2026
Task you gave them: "Find out if you can register your thesis with 118 credits, and where to replace a lost student card."

Rule: do not help or explain. Watch and write down what happens.

| # | What the tester did or said | What they expected | Why the system/UI caused it | Fix idea |
|---|---|---|---|---|
| 1 | Typed both questions ("Can I register thesis with 118 credits and where to replace a lost student card?") into a single prompt, then got confused when the assistant ignored the student card question. | The assistant to handle multi-intent queries or clearly guide them on how to ask questions effectively. | The default chat input (`st.chat_input`) used a generic placeholder ("Ask about fees, offices or the handbook…") without advising users to ask one topic at a time. | Update the chat input placeholder to guide users: *"Ask one question at a time (e.g., 'Can I register thesis with 118 credits?')"*. |
| 2 | Looked around the screen for a way to start a fresh conversation or save the current chat history for later reference, then hesitated before refreshing the browser. | Quick session management controls (reset chat, export transcript) directly accessible in the UI without losing state unexpectedly. | The minimalist interface lacked session utility buttons, forcing users to reload the entire page to reset `session_id` and message history. | Add "Clear chat history" (`🗑️ Xóa lịch sử trò chuyện`) and "Download chat history" (`📥 Tải lịch sử chat`) buttons to the sidebar. |
| 3 | Wanted to flag an incomplete answer from the assistant during testing, but saw no way to rate or report response quality on the screen. | Thumbs-up / thumbs-down feedback controls under each assistant message to submit quick quality ratings. | There was no interactive feedback mechanism wired to the backend API (`client.send_feedback`) beneath assistant responses. | Add `👍` and `👎` feedback buttons with unique widget keys and `st.toast` confirmation under each rated assistant message. |

The one change we made (commit link): https://github.com/your-team/study-planner/commit/a1b2c3d4
Before / after screenshot: 
- Before: images/ui_before.png
- After: images/ui_after.png