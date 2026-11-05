-- Lab 5 Part F: write your queries for the assistant database here.
-- Q1 requests per intent

-- Q2 average latency per intent

-- Q3 topics with the most thumbs-down (JOIN feedback with interaction)
SELECT
    i.topic,
    COUNT(*) AS thumbs_down
FROM interaction AS i
JOIN feedback AS f
    ON f.request_id = i.request_id
WHERE f.rating = -1
    AND i.topic IS NOT NULL
GROUP BY i.topic
ORDER BY thumbs_down DESC, i.topic ASC;
