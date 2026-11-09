-- Lab 5: five meaningful queries + the three product questions.

-- Q1. Requests per intent (most common first)
SELECT intent, COUNT(*) AS requests
FROM interaction GROUP BY intent ORDER BY requests DESC;

-- Q2. PRODUCT QUESTION 1 — most failed intent (unresolved or degraded share)
SELECT intent,
       COUNT(*) AS requests,
       SUM(CASE WHEN resolved = 0 OR degraded = 1 THEN 1 ELSE 0 END) AS failed,
       ROUND(100.0 * SUM(CASE WHEN resolved = 0 OR degraded = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS failed_pct
FROM interaction GROUP BY intent ORDER BY failed_pct DESC LIMIT 1;

-- Q3. PRODUCT QUESTION 2 — average response time by intent
SELECT intent, ROUND(AVG(latency_ms), 1) AS avg_ms, MAX(latency_ms) AS max_ms
FROM interaction GROUP BY intent ORDER BY avg_ms DESC;

-- Q4. PRODUCT QUESTION 3 — top topics with negative feedback (join)
SELECT i.topic, COUNT(*) AS thumbs_down
FROM feedback f JOIN interaction i ON i.request_id = f.request_id
WHERE f.rating = -1 AND i.topic IS NOT NULL
GROUP BY i.topic ORDER BY thumbs_down DESC LIMIT 5;

-- Q5. Daily active sessions over the last 7 days
SELECT DATE(created_at) AS day, COUNT(DISTINCT session_id) AS sessions
FROM interaction
WHERE created_at >= DATE('now', '-7 day')
GROUP BY day ORDER BY day;

-- Q6. Satisfaction per intent (feedback coverage and average rating)
SELECT i.intent, COUNT(f.id) AS ratings, ROUND(AVG(f.rating), 2) AS avg_rating
FROM interaction i LEFT JOIN feedback f ON f.request_id = i.request_id
GROUP BY i.intent ORDER BY avg_rating;
