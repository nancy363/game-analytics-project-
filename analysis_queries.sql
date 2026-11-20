-- A. COMPETITIONS (PDF pages 3-4)
-- 1. List all competitions with category name
SELECT cp.competition_id, cp.competition_name, ca.category_name,
       cp.parent_id, cp.type, cp.gender, cp.level
FROM competitions cp
LEFT JOIN categories ca ON ca.category_id = cp.category_id
ORDER BY ca.category_name, cp.competition_name;

-- 2. Count competitions in each category
SELECT ca.category_name, COUNT(cp.competition_id) AS competition_count
FROM categories ca
LEFT JOIN competitions cp ON cp.category_id = ca.category_id
GROUP BY ca.category_id, ca.category_name
ORDER BY competition_count DESC;

-- 3. Find all competitions of type doubles (also includes mixed_doubles)
SELECT * FROM competitions
WHERE LOWER(type) LIKE '%doubles%';

-- 4. Competitions in a specific category (example: ITF Men)
SELECT cp.*
FROM competitions cp
JOIN categories ca ON ca.category_id = cp.category_id
WHERE ca.category_name = 'ITF Men';

-- 5. Parent competitions and their sub-competitions
SELECT parent.competition_name AS parent_competition,
       child.competition_name AS sub_competition
FROM competitions child
LEFT JOIN competitions parent ON child.parent_id = parent.competition_id
WHERE child.parent_id IS NOT NULL;

-- 6. Distribution of competition types by category
SELECT ca.category_name, cp.type, COUNT(*) AS competition_count
FROM competitions cp
JOIN categories ca ON ca.category_id = cp.category_id
GROUP BY ca.category_name, cp.type
ORDER BY ca.category_name, competition_count DESC;

-- 7. Competitions with no parent
SELECT * FROM competitions
WHERE parent_id IS NULL OR parent_id = '';

-- B. COMPLEXES AND VENUES (PDF pages 4-5)
-- 1. All venues with associated complex name
SELECT v.*, c.complex_name
FROM venues v
LEFT JOIN complexes c ON c.complex_id = v.complex_id;

-- 2. Number of venues in each complex
SELECT c.complex_name, COUNT(v.venue_id) AS venue_count
FROM complexes c
LEFT JOIN venues v ON v.complex_id = c.complex_id
GROUP BY c.complex_id, c.complex_name;

-- 3. Venues in a specific country (example: Chile)
SELECT * FROM venues WHERE country_name = 'Chile';

-- 4. Venues and their timezones
SELECT venue_name, city_name, country_name, timezone FROM venues;

-- 5. Complexes with more than one venue
SELECT c.complex_name, COUNT(v.venue_id) AS venue_count
FROM complexes c
JOIN venues v ON v.complex_id = c.complex_id
GROUP BY c.complex_id, c.complex_name
HAVING COUNT(v.venue_id) > 1;

-- 6. Venues grouped by country
SELECT country_name, COUNT(*) AS venue_count
FROM venues GROUP BY country_name ORDER BY venue_count DESC;

-- 7. Venues for a specific complex (example: Nacional)
SELECT v.*, c.complex_name
FROM venues v
JOIN complexes c ON c.complex_id = v.complex_id
WHERE c.complex_name LIKE '%Nacional%';

-- C. DOUBLES COMPETITOR RANKINGS (PDF pages 6-8)
-- 1. Competitors with rank and points
SELECT c.name, c.country, r.rank, r.points, r.movement, r.competitions_played
FROM competitors c
JOIN competitor_rankings r ON r.competitor_id = c.competitor_id
ORDER BY r.rank;

-- 2. Top 5 competitors
SELECT c.name, c.country, r.rank, r.points
FROM competitors c
JOIN competitor_rankings r ON r.competitor_id = c.competitor_id
ORDER BY r.rank LIMIT 5;

-- 3. Competitors with stable rank
SELECT c.name, c.country, r.rank, r.points
FROM competitors c
JOIN competitor_rankings r ON r.competitor_id = c.competitor_id
WHERE r.movement = 0 ORDER BY r.rank;

-- 4. Total points from a specific country (example: Croatia)
SELECT c.country, SUM(r.points) AS total_points
FROM competitors c
JOIN competitor_rankings r ON r.competitor_id = c.competitor_id
WHERE c.country = 'Croatia'
GROUP BY c.country;

-- 5. Competitor count per country
SELECT country, COUNT(*) AS competitor_count
FROM competitors GROUP BY country ORDER BY competitor_count DESC;

-- 6. Competitors with highest points in the current imported ranking snapshot
SELECT c.name, c.country, r.points, r.rank, r.tour, r.gender, r.year, r.week
FROM competitors c
JOIN competitor_rankings r ON r.competitor_id = c.competitor_id
WHERE r.points = (SELECT MAX(points) FROM competitor_rankings);
