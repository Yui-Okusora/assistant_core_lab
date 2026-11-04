-- Lab 5 Part F: write your queries for the assistant database here.
-- Q1 requests per intent
SELECT intent, COUNT(*) AS requests FROM interaction GROUP BY intent ORDER BY COUNT(*) DESC;
-- Q2 average latency per intent

-- Q3 topics with the most thumbs-down (JOIN feedback with interaction)
