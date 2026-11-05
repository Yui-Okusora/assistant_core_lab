-- Lab 5 Part F: write your queries for the assistant database here.
-- Q1 requests per intent

-- Q2 average latency per intent
    SELECT 
        intent, 
        ROUND(AVG(latency_ms), 1) AS avg_latency_ms
    FROM interaction
    GROUP BY intent
    ORDER BY avg_latency_ms DESC;
-- Q3 topics with the most thumbs-down (JOIN feedback with interaction)
