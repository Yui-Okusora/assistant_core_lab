-- Lab 5: a BAD first attempt. Find at least 6 problems before reading the tutorial.
CREATE TABLE chats (
    id INTEGER,
    student_name TEXT,          -- real names stored with every message
    student_phone TEXT,
    message TEXT,               -- full raw message, kept forever
    answer TEXT,
    intent TEXT,                -- free text: 'fee', 'Fee', 'FEE', 'tuition'...
    time TEXT,                  -- '5/10/2026 9:03 PM' as text
    feedback TEXT,              -- '1,-1,1' comma-separated list of ratings
    latency TEXT                -- '120ms'
);
