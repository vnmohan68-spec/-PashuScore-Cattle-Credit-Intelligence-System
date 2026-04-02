-- ============================================================
-- PashuScore - Full Final SQL
-- Developed by Mohan | NSTI Chennai
-- ============================================================

-- =========================
-- RESET DATABASE
-- =========================
DROP DATABASE IF EXISTS pashuscore;
CREATE DATABASE pashuscore;
USE pashuscore;

-- ============================================================
-- TABLES
-- ============================================================

-- 1. FARMERS TABLE
CREATE TABLE farmers (
    farmer_id   VARCHAR(10) PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    village     VARCHAR(100) NOT NULL,
    state       VARCHAR(50) NOT NULL,
    land_acres  DECIMAL(5,2),
    phone       VARCHAR(15)
);

-- 2. CATTLE TABLE
CREATE TABLE cattle (
    cattle_id      VARCHAR(15) PRIMARY KEY,
    farmer_id      VARCHAR(10) NOT NULL,
    breed          VARCHAR(50) NOT NULL,
    age_years      INT,
    health_status  VARCHAR(20) DEFAULT 'Healthy',
    milk_yield_lpd DECIMAL(5,2),
    ear_tag        VARCHAR(20),
    FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id)
);

-- 3. VACCINATIONS TABLE
CREATE TABLE vaccinations (
    vacc_id    INT AUTO_INCREMENT PRIMARY KEY,
    cattle_id  VARCHAR(15) NOT NULL,
    vaccine    VARCHAR(100),
    given_on   DATE,
    next_due   DATE,
    vet_name   VARCHAR(100),
    FOREIGN KEY (cattle_id) REFERENCES cattle(cattle_id)
);

-- 4. LOAN APPLICATIONS TABLE
CREATE TABLE loan_applications (
    app_id           INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id        VARCHAR(10) NOT NULL,
    credit_score     INT,
    grade            VARCHAR(5),
    amount_eligible  DECIMAL(10,2),
    status           VARCHAR(20) DEFAULT 'Pending',
    applied_on       DATE DEFAULT (CURDATE()),
    FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id)
);

-- ============================================================
-- SAMPLE DATA INSERTION
-- ============================================================

-- FARMERS
INSERT INTO farmers (farmer_id, name, village, state, land_acres, phone) VALUES
('F001', 'Ramaiah Gowda', 'Hosakere', 'Karnataka', 3.50, '9845001234'),
('F002', 'Sunita Devi', 'Barhaj', 'Uttar Pradesh', 1.20, '9012002345'),
('F003', 'Murugesan P.', 'Palani', 'Tamil Nadu', 0.80, '8023003456'),
('F004', 'Harpreet Kaur', 'Barnala', 'Punjab', 6.00, '9779004567');

-- CATTLE
INSERT INTO cattle (cattle_id, farmer_id, breed, age_years, health_status, milk_yield_lpd, ear_tag) VALUES
('C01','F001','Gir',4,'Healthy',12.0,'KA-4821'),
('C02','F001','Sahiwal',6,'Healthy',10.0,'KA-4822'),
('C03','F001','Gir',3,'Healthy',11.0,'KA-4823'),
('C04','F001','HF Cross',5,'Healthy',9.0,'KA-4824'),
('C05','F002','Murrah Buffalo',5,'Healthy',14.0,'UP-2201'),
('C06','F002','Murrah Buffalo',7,'Mild Fever',6.0,'UP-2202'),
('C07','F002','Nondescript',8,'Healthy',4.0,'UP-2203'),
('C08','F003','Nondescript',10,'Limping',2.0,'TN-0901'),
('C09','F003','Nondescript',9,'Healthy',3.0,'TN-0902'),
('C10','F004','Murrah Buffalo',4,'Healthy',16.0,'PB-7731'),
('C11','F004','Murrah Buffalo',5,'Healthy',15.0,'PB-7732'),
('C12','F004','Murrah Buffalo',3,'Healthy',13.0,'PB-7733'),
('C13','F004','Sahiwal',4,'Healthy',10.0,'PB-7734'),
('C14','F004','HF Cross',6,'Healthy',9.0,'PB-7735');

-- VACCINATIONS
INSERT INTO vaccinations (cattle_id, vaccine, given_on, next_due, vet_name) VALUES
('C01','FMD + HS','2024-01-10','2025-01-10','Dr. Nagaraj'),
('C02','FMD + HS','2024-01-10','2025-01-10','Dr. Nagaraj'),
('C03','FMD + HS','2024-01-10','2025-01-10','Dr. Nagaraj'),
('C04','FMD + HS','2024-01-10','2025-01-10','Dr. Nagaraj'),
('C05','FMD + BQ','2024-02-14','2025-02-14','Dr. Mishra'),
('C07','FMD','2023-06-01','2024-06-01','Dr. Mishra'),
('C09','FMD','2022-06-01','2023-06-01','Dr. Arumugam'),
('C10','FMD + HS','2024-03-20','2025-03-20','Dr. Gill'),
('C11','FMD + HS','2024-03-20','2025-03-20','Dr. Gill'),
('C12','FMD + HS','2024-03-20','2025-03-20','Dr. Gill'),
('C13','FMD + HS','2024-03-20','2025-03-20','Dr. Gill'),
('C14','FMD + HS','2024-03-20','2025-03-20','Dr. Gill');

-- OPTIONAL SAMPLE LOAN APPLICATIONS
INSERT INTO loan_applications (farmer_id, credit_score, grade, amount_eligible, status) VALUES
('F004', 88, 'A+', 200000, 'Approved'),
('F001', 76, 'A', 150000, 'Pending');

-- ============================================================
-- BASIC CHECK QUERIES
-- ============================================================

-- 1. View all farmers
SELECT * FROM farmers;

-- 2. View all cattle
SELECT * FROM cattle;

-- 3. View all vaccinations
SELECT * FROM vaccinations;

-- 4. View all loan applications
SELECT * FROM loan_applications;

-- ============================================================
-- USEFUL PROJECT QUERIES
-- ============================================================

-- 5. All cattle with farmer details
SELECT
    f.farmer_id,
    f.name AS farmer_name,
    f.village,
    f.state,
    c.cattle_id,
    c.breed,
    c.age_years,
    c.health_status,
    c.milk_yield_lpd,
    c.ear_tag
FROM farmers f
JOIN cattle c ON f.farmer_id = c.farmer_id
ORDER BY f.name, c.cattle_id;

-- 6. Total cattle count per farmer
SELECT
    f.farmer_id,
    f.name,
    COUNT(c.cattle_id) AS total_cattle
FROM farmers f
LEFT JOIN cattle c ON f.farmer_id = c.farmer_id
GROUP BY f.farmer_id, f.name
ORDER BY total_cattle DESC;

-- 7. Average milk yield per farmer
SELECT
    f.farmer_id,
    f.name,
    ROUND(AVG(c.milk_yield_lpd), 2) AS avg_milk_yield
FROM farmers f
JOIN cattle c ON f.farmer_id = c.farmer_id
GROUP BY f.farmer_id, f.name
ORDER BY avg_milk_yield DESC;

-- 8. Healthy vs unhealthy cattle count per farmer
SELECT
    f.farmer_id,
    f.name,
    SUM(CASE WHEN c.health_status = 'Healthy' THEN 1 ELSE 0 END) AS healthy_count,
    SUM(CASE WHEN c.health_status <> 'Healthy' THEN 1 ELSE 0 END) AS unhealthy_count
FROM farmers f
JOIN cattle c ON f.farmer_id = c.farmer_id
GROUP BY f.farmer_id, f.name;

-- 9. Vaccination overdue list
SELECT
    c.cattle_id,
    c.ear_tag,
    c.breed,
    f.name AS farmer_name,
    f.phone,
    f.village,
    v.vaccine,
    v.given_on,
    v.next_due,
    DATEDIFF(CURDATE(), v.next_due) AS days_overdue
FROM vaccinations v
JOIN cattle c ON v.cattle_id = c.cattle_id
JOIN farmers f ON c.farmer_id = f.farmer_id
WHERE v.next_due < CURDATE()
ORDER BY days_overdue DESC;

-- 10. Cattle not vaccinated (no vaccination record at all)
SELECT
    c.cattle_id,
    c.breed,
    c.health_status,
    f.name AS farmer_name,
    f.village
FROM cattle c
JOIN farmers f ON c.farmer_id = f.farmer_id
LEFT JOIN vaccinations v ON c.cattle_id = v.cattle_id
WHERE v.cattle_id IS NULL
ORDER BY f.name;

-- ============================================================
-- CREDIT SCORE CALCULATION QUERY (MATCHES STREAMLIT LOGIC)
-- ============================================================

-- 11. Farmer credit score leaderboard
SELECT
    f.farmer_id,
    f.name,
    f.village,
    f.state,
    COUNT(c.cattle_id) AS herd_size,

    LEAST(COUNT(c.cattle_id) * 5, 20) AS herd_score,

    ROUND(AVG(
        CASE c.breed
            WHEN 'Gir' THEN 30
            WHEN 'Sahiwal' THEN 28
            WHEN 'Red Sindhi' THEN 26
            WHEN 'Murrah Buffalo' THEN 27
            WHEN 'Surti Buffalo' THEN 24
            WHEN 'HF Cross' THEN 22
            WHEN 'Jersey Cross' THEN 20
            ELSE 10
        END
    )) AS breed_score,

    COUNT(DISTINCT CASE WHEN v.cattle_id IS NOT NULL THEN c.cattle_id END) AS vaccinated_count,

    ROUND(
        COUNT(DISTINCT CASE WHEN v.cattle_id IS NOT NULL THEN c.cattle_id END)
        / COUNT(c.cattle_id) * 25
    ) AS vaccination_score,

    SUM(CASE WHEN c.health_status = 'Healthy' THEN 1 ELSE 0 END) AS healthy_count,

    ROUND(
        SUM(CASE WHEN c.health_status = 'Healthy' THEN 1 ELSE 0 END)
        / COUNT(c.cattle_id) * 15
    ) AS health_score,

    SUM(CASE WHEN c.milk_yield_lpd >= 8 THEN 1 ELSE 0 END) AS high_yield_count,

    ROUND(
        SUM(CASE WHEN c.milk_yield_lpd >= 8 THEN 1 ELSE 0 END)
        / COUNT(c.cattle_id) * 10
    ) AS yield_score,

    (
        LEAST(COUNT(c.cattle_id) * 5, 20)
        + ROUND(AVG(
            CASE c.breed
                WHEN 'Gir' THEN 30
                WHEN 'Sahiwal' THEN 28
                WHEN 'Red Sindhi' THEN 26
                WHEN 'Murrah Buffalo' THEN 27
                WHEN 'Surti Buffalo' THEN 24
                WHEN 'HF Cross' THEN 22
                WHEN 'Jersey Cross' THEN 20
                ELSE 10
            END
        ))
        + ROUND(
            COUNT(DISTINCT CASE WHEN v.cattle_id IS NOT NULL THEN c.cattle_id END)
            / COUNT(c.cattle_id) * 25
        )
        + ROUND(
            SUM(CASE WHEN c.health_status = 'Healthy' THEN 1 ELSE 0 END)
            / COUNT(c.cattle_id) * 15
        )
        + ROUND(
            SUM(CASE WHEN c.milk_yield_lpd >= 8 THEN 1 ELSE 0 END)
            / COUNT(c.cattle_id) * 10
        )
    ) AS credit_score,

    CASE
        WHEN (
            LEAST(COUNT(c.cattle_id) * 5, 20)
            + ROUND(AVG(
                CASE c.breed
                    WHEN 'Gir' THEN 30
                    WHEN 'Sahiwal' THEN 28
                    WHEN 'Red Sindhi' THEN 26
                    WHEN 'Murrah Buffalo' THEN 27
                    WHEN 'Surti Buffalo' THEN 24
                    WHEN 'HF Cross' THEN 22
                    WHEN 'Jersey Cross' THEN 20
                    ELSE 10
                END
            ))
            + ROUND(
                COUNT(DISTINCT CASE WHEN v.cattle_id IS NOT NULL THEN c.cattle_id END)
                / COUNT(c.cattle_id) * 25
            )
            + ROUND(
                SUM(CASE WHEN c.health_status = 'Healthy' THEN 1 ELSE 0 END)
                / COUNT(c.cattle_id) * 15
            )
            + ROUND(
                SUM(CASE WHEN c.milk_yield_lpd >= 8 THEN 1 ELSE 0 END)
                / COUNT(c.cattle_id) * 10
            )
        ) >= 80 THEN 'A+'
        WHEN (
            LEAST(COUNT(c.cattle_id) * 5, 20)
            + ROUND(AVG(
                CASE c.breed
                    WHEN 'Gir' THEN 30
                    WHEN 'Sahiwal' THEN 28
                    WHEN 'Red Sindhi' THEN 26
                    WHEN 'Murrah Buffalo' THEN 27
                    WHEN 'Surti Buffalo' THEN 24
                    WHEN 'HF Cross' THEN 22
                    WHEN 'Jersey Cross' THEN 20
                    ELSE 10
                END
            ))
            + ROUND(
                COUNT(DISTINCT CASE WHEN v.cattle_id IS NOT NULL THEN c.cattle_id END)
                / COUNT(c.cattle_id) * 25
            )
            + ROUND(
                SUM(CASE WHEN c.health_status = 'Healthy' THEN 1 ELSE 0 END)
                / COUNT(c.cattle_id) * 15
            )
            + ROUND(
                SUM(CASE WHEN c.milk_yield_lpd >= 8 THEN 1 ELSE 0 END)
                / COUNT(c.cattle_id) * 10
            )
        ) >= 65 THEN 'A'
        WHEN (
            LEAST(COUNT(c.cattle_id) * 5, 20)
            + ROUND(AVG(
                CASE c.breed
                    WHEN 'Gir' THEN 30
                    WHEN 'Sahiwal' THEN 28
                    WHEN 'Red Sindhi' THEN 26
                    WHEN 'Murrah Buffalo' THEN 27
                    WHEN 'Surti Buffalo' THEN 24
                    WHEN 'HF Cross' THEN 22
                    WHEN 'Jersey Cross' THEN 20
                    ELSE 10
                END
            ))
            + ROUND(
                COUNT(DISTINCT CASE WHEN v.cattle_id IS NOT NULL THEN c.cattle_id END)
                / COUNT(c.cattle_id) * 25
            )
            + ROUND(
                SUM(CASE WHEN c.health_status = 'Healthy' THEN 1 ELSE 0 END)
                / COUNT(c.cattle_id) * 15
            )
            + ROUND(
                SUM(CASE WHEN c.milk_yield_lpd >= 8 THEN 1 ELSE 0 END)
                / COUNT(c.cattle_id) * 10
            )
        ) >= 50 THEN 'B'
        WHEN (
            LEAST(COUNT(c.cattle_id) * 5, 20)
            + ROUND(AVG(
                CASE c.breed
                    WHEN 'Gir' THEN 30
                    WHEN 'Sahiwal' THEN 28
                    WHEN 'Red Sindhi' THEN 26
                    WHEN 'Murrah Buffalo' THEN 27
                    WHEN 'Surti Buffalo' THEN 24
                    WHEN 'HF Cross' THEN 22
                    WHEN 'Jersey Cross' THEN 20
                    ELSE 10
                END
            ))
            + ROUND(
                COUNT(DISTINCT CASE WHEN v.cattle_id IS NOT NULL THEN c.cattle_id END)
                / COUNT(c.cattle_id) * 25
            )
            + ROUND(
                SUM(CASE WHEN c.health_status = 'Healthy' THEN 1 ELSE 0 END)
                / COUNT(c.cattle_id) * 15
            )
            + ROUND(
                SUM(CASE WHEN c.milk_yield_lpd >= 8 THEN 1 ELSE 0 END)
                / COUNT(c.cattle_id) * 10
            )
        ) >= 35 THEN 'C'
        ELSE 'D'
    END AS grade

FROM farmers f
JOIN cattle c ON f.farmer_id = c.farmer_id
LEFT JOIN vaccinations v
    ON c.cattle_id = v.cattle_id
   AND v.next_due >= CURDATE()
WHERE c.health_status <> 'Deceased'
GROUP BY f.farmer_id, f.name, f.village, f.state
ORDER BY credit_score DESC;

-- ============================================================
-- LOAN ELIGIBILITY QUERY
-- ============================================================

-- 12. Loan eligibility based on calculated score
SELECT
    score_table.farmer_id,
    score_table.name,
    score_table.village,
    score_table.state,
    score_table.credit_score,
    CASE
        WHEN score_table.credit_score >= 80 THEN 'A+'
        WHEN score_table.credit_score >= 65 THEN 'A'
        WHEN score_table.credit_score >= 50 THEN 'B'
        WHEN score_table.credit_score >= 35 THEN 'C'
        ELSE 'D'
    END AS grade,
    CASE
        WHEN score_table.credit_score >= 80 THEN 200000
        WHEN score_table.credit_score >= 65 THEN 150000
        WHEN score_table.credit_score >= 50 THEN 75000
        WHEN score_table.credit_score >= 35 THEN 25000
        ELSE 0
    END AS max_loan_eligible
FROM (
    SELECT
        f.farmer_id,
        f.name,
        f.village,
        f.state,
        (
            LEAST(COUNT(c.cattle_id) * 5, 20)
            + ROUND(AVG(
                CASE c.breed
                    WHEN 'Gir' THEN 30
                    WHEN 'Sahiwal' THEN 28
                    WHEN 'Red Sindhi' THEN 26
                    WHEN 'Murrah Buffalo' THEN 27
                    WHEN 'Surti Buffalo' THEN 24
                    WHEN 'HF Cross' THEN 22
                    WHEN 'Jersey Cross' THEN 20
                    ELSE 10
                END
            ))
            + ROUND(
                COUNT(DISTINCT CASE WHEN v.cattle_id IS NOT NULL THEN c.cattle_id END)
                / COUNT(c.cattle_id) * 25
            )
            + ROUND(
                SUM(CASE WHEN c.health_status = 'Healthy' THEN 1 ELSE 0 END)
                / COUNT(c.cattle_id) * 15
            )
            + ROUND(
                SUM(CASE WHEN c.milk_yield_lpd >= 8 THEN 1 ELSE 0 END)
                / COUNT(c.cattle_id) * 10
            )
        ) AS credit_score
    FROM farmers f
    JOIN cattle c ON f.farmer_id = c.farmer_id
    LEFT JOIN vaccinations v
        ON c.cattle_id = v.cattle_id
       AND v.next_due >= CURDATE()
    WHERE c.health_status <> 'Deceased'
    GROUP BY f.farmer_id, f.name, f.village, f.state
) AS score_table
ORDER BY max_loan_eligible DESC, credit_score DESC;

-- ============================================================
-- CRUD / TEST QUERIES
-- ============================================================

-- 13. Add a new farmer
INSERT INTO farmers (farmer_id, name, village, state, land_acres, phone)
VALUES ('F005', 'Mohan', 'Chennai', 'Tamil Nadu', 2.50, '9876543210');

-- 14. Add cattle for Mohan
INSERT INTO cattle (cattle_id, farmer_id, breed, age_years, health_status, milk_yield_lpd, ear_tag)
VALUES ('C15', 'F005', 'Gir', 4, 'Healthy', 11.0, 'TN-5001');

-- 15. Add vaccination for Mohan's cattle
INSERT INTO vaccinations (cattle_id, vaccine, given_on, next_due, vet_name)
VALUES ('C15', 'FMD + HS', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 1 YEAR), 'Dr. Mohan');

-- 16. Submit a loan application manually
INSERT INTO loan_applications (farmer_id, credit_score, grade, amount_eligible, status)
VALUES ('F005', 78, 'A', 150000, 'Pending');

-- 17. Approve a loan application
UPDATE loan_applications
SET status = 'Approved'
WHERE app_id = 1;

-- 18. Reject a loan application
UPDATE loan_applications
SET status = 'Rejected'
WHERE app_id = 2;

-- 19. Mark cattle as deceased
UPDATE cattle
SET health_status = 'Deceased'
WHERE cattle_id = 'C08';

-- 20. View all loan applications with farmer details
SELECT
    la.app_id,
    la.farmer_id,
    f.name AS farmer_name,
    f.village,
    f.state,
    la.credit_score,
    la.grade,
    la.amount_eligible,
    la.status,
    la.applied_on
FROM loan_applications la
JOIN farmers f ON la.farmer_id = f.farmer_id
ORDER BY la.applied_on DESC, la.app_id DESC;

-- ============================================================
-- FINAL QUICK CHECK
-- ============================================================

SELECT 'Farmers Count' AS label, COUNT(*) AS total FROM farmers
UNION ALL
SELECT 'Cattle Count', COUNT(*) FROM cattle
UNION ALL
SELECT 'Vaccination Count', COUNT(*) FROM vaccinations
UNION ALL
SELECT 'Loan Applications Count', COUNT(*) FROM loan_applications;