-- ==========================================================
--  MARINE SPECIES MONITORING & CONSERVATION DATABASE
--  DBMS Mini Project (Full SQL File)
-- ==========================================================
--  Team :
--  K L Sonika - PES2UG23CS247
--  J Sai Vihitha - PES2UG23CS234
--  Date: 23 October 2025
-- ==========================================================

-- -------------------------------
-- STEP 1: DATABASE CREATION
-- -------------------------------
DROP DATABASE IF EXISTS marine_db;
CREATE DATABASE marine_db;
USE marine_db;

-- -------------------------------
-- STEP 2: TABLE CREATION (DDL)
-- -------------------------------

CREATE TABLE Species (
    species_id INT AUTO_INCREMENT PRIMARY KEY,
    common_name VARCHAR(100) NOT NULL,
    scientific_name VARCHAR(150),
    conservation_status VARCHAR(50)
);

CREATE TABLE Location (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    location_name VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    water_type ENUM('Ocean', 'Sea', 'Lake', 'River')
);

CREATE TABLE Observer (
    observer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    organization VARCHAR(100),
    contact VARCHAR(50)
);

CREATE TABLE Water_Quality (
    quality_id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT,
    temperature DECIMAL(5,2),
    pH DECIMAL(4,2),
    salinity DECIMAL(6,2),
    pollution_index DECIMAL(5,2),
    FOREIGN KEY (location_id) REFERENCES Location(location_id)
);

CREATE TABLE Observation (
    obs_id INT AUTO_INCREMENT PRIMARY KEY,
    species_id INT,
    location_id INT,
    observer_id INT,
    quality_id INT,
    obs_date DATETIME,
    count_observed INT,
    remarks VARCHAR(255),
    FOREIGN KEY (species_id) REFERENCES Species(species_id),
    FOREIGN KEY (location_id) REFERENCES Location(location_id),
    FOREIGN KEY (observer_id) REFERENCES Observer(observer_id),
    FOREIGN KEY (quality_id) REFERENCES Water_Quality(quality_id)
);

CREATE TABLE Conservation_Action (
    action_id INT AUTO_INCREMENT PRIMARY KEY,
    species_id INT,
    action_type VARCHAR(100),
    description VARCHAR(255),
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (species_id) REFERENCES Species(species_id)
);

CREATE TABLE Species_Threat (
    threat_id INT AUTO_INCREMENT PRIMARY KEY,
    species_id INT,
    threat_type VARCHAR(100),
    severity ENUM('Low', 'Moderate', 'High'),
    FOREIGN KEY (species_id) REFERENCES Species(species_id)
);

CREATE TABLE Equipment (
    equipment_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    type VARCHAR(100),
    availability ENUM('Available', 'In Maintenance')
);

CREATE TABLE Action_Equipment (
    action_id INT,
    equipment_id INT,
    PRIMARY KEY (action_id, equipment_id),
    FOREIGN KEY (action_id) REFERENCES Conservation_Action(action_id),
    FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id)
);

CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL,
    role ENUM('Admin', 'Researcher', 'Viewer') DEFAULT 'Viewer'
);

CREATE TABLE Action_Log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    action_id INT,
    action_type VARCHAR(100),
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -------------------------------
-- STEP 3: SAMPLE DATA INSERTS (DML)
-- -------------------------------

-- Species
INSERT INTO Species (common_name, scientific_name, conservation_status) VALUES
('Blue Whale', 'Balaenoptera musculus', 'Endangered'),
('Clownfish', 'Amphiprioninae', 'Least Concern'),
('Great White Shark', 'Carcharodon carcharias', 'Vulnerable'),
('Green Turtle', 'Chelonia mydas', 'Endangered'),
('Dolphin', 'Delphinidae', 'Least Concern');

-- Location
INSERT INTO Location (location_name, region, water_type) VALUES
('Great Barrier Reef', 'Australia', 'Ocean'),
('Monterey Bay', 'USA', 'Sea'),
('Bali Coast', 'Indonesia', 'Ocean'),
('Andaman Sea', 'India', 'Sea'),
('Lake Victoria', 'Africa', 'Lake');

-- Observer
INSERT INTO Observer (name, organization, contact) VALUES
('Dr. Emily Clark', 'MarineLife Org', 'emily@marine.org'),
('John Doe', 'OceanWatch', 'john@oceanwatch.com'),
('Sophia Lee', 'AquaSave', 'sophia@aquasave.org'),
('Arun Kumar', 'BluePlanet', 'arun@blueplanet.org'),
('Isabella Gomez', 'WildSea', 'isabella@wildsea.com');

-- Water Quality
INSERT INTO Water_Quality (location_id, temperature, pH, salinity, pollution_index) VALUES
(1, 27.5, 8.1, 35.2, 12.4),
(2, 18.2, 7.8, 33.5, 24.0),
(3, 25.8, 8.3, 36.1, 10.2),
(4, 29.4, 7.5, 34.8, 28.9),
(5, 22.0, 7.6, 0.5, 18.3);

-- Observation
INSERT INTO Observation (species_id, location_id, observer_id, quality_id, obs_date, count_observed, remarks) VALUES
(1, 1, 1, 1, '2025-05-10 09:00:00', 4, 'Observed near coral zone'),
(2, 3, 2, 3, '2025-06-14 10:30:00', 25, 'Small group'),
(3, 2, 3, 2, '2025-04-09 15:10:00', 2, 'One large adult seen'),
(4, 4, 4, 4, '2025-07-22 08:45:00', 7, 'Near shallow area'),
(5, 5, 5, 5, '2025-08-11 17:00:00', 12, 'Playing in pods');

-- Conservation Action
INSERT INTO Conservation_Action (species_id, action_type, description, start_date, end_date) VALUES
(1, 'Habitat Protection', 'Establish marine sanctuary', '2025-03-01', '2026-03-01'),
(3, 'Anti-Poaching Patrol', 'Deploy drones for shark protection', '2025-04-15', '2025-12-15'),
(4, 'Beach Clean-up', 'Volunteer turtle-safe zones', '2025-01-10', '2025-09-10'),
(5, 'Awareness Campaign', 'Promote dolphin conservation', '2025-02-05', '2025-11-05'),
(2, 'Coral Health Monitoring', 'Protect clownfish habitat', '2025-05-01', '2026-05-01');

-- Species Threat
INSERT INTO Species_Threat (species_id, threat_type, severity) VALUES
(1, 'Ship Strikes', 'High'),
(2, 'Coral Bleaching', 'Moderate'),
(3, 'Overfishing', 'High'),
(4, 'Plastic Pollution', 'High'),
(5, 'Noise Pollution', 'Moderate');

-- Equipment
INSERT INTO Equipment (name, type, availability) VALUES
('Underwater Drone', 'Monitoring', 'Available'),
('Boat', 'Patrol', 'Available'),
('Water Sampler', 'Research', 'In Maintenance'),
('Camera Trap', 'Monitoring', 'Available'),
('GPS Tracker', 'Tracking', 'Available');

-- Action Equipment Mapping
INSERT INTO Action_Equipment VALUES
(1,1), (1,5), (2,2), (3,3), (4,4);

-- Users
INSERT INTO Users (username, password, role) VALUES
('admin', 'admin123', 'Admin'),
('researcher', 'res123', 'Researcher'),
('guest', 'guest123', 'Viewer');

-- -------------------------------
-- STEP 4: TRIGGERS, PROCEDURES, FUNCTIONS
-- -------------------------------

-- Trigger: Log each new conservation action
DELIMITER //
CREATE TRIGGER After_Action_Insert
AFTER INSERT ON Conservation_Action
FOR EACH ROW
BEGIN
    INSERT INTO Action_Log (action_id, action_type)
    VALUES (NEW.action_id, NEW.action_type);
END //
DELIMITER ;

-- Stored Procedure: Get all actions related to a given species name
DELIMITER //
CREATE PROCEDURE GetConservationActionsBySpecies(IN sp_name VARCHAR(100))
BEGIN
    SELECT s.common_name, ca.action_type, ca.description, ca.start_date, ca.end_date
    FROM Conservation_Action ca
    JOIN Species s ON ca.species_id = s.species_id
    WHERE s.common_name = sp_name;
END //
DELIMITER ;

-- Function: Compute average pollution index for a given location
DELIMITER //
CREATE FUNCTION AvgPollution(locName VARCHAR(100)) RETURNS DECIMAL(5,2)
DETERMINISTIC
BEGIN
    DECLARE avgPoll DECIMAL(5,2);
    SELECT AVG(pollution_index) INTO avgPoll
    FROM Water_Quality wq
    JOIN Location l ON wq.location_id = l.location_id
    WHERE l.location_name = locName;
    RETURN avgPoll;
END //
DELIMITER ;

-- -------------------------------
-- STEP 5: VIEW CREATION
-- -------------------------------

CREATE VIEW Species_Observation_View AS
SELECT s.common_name, l.location_name, o.obs_date, o.count_observed
FROM Observation o
JOIN Species s ON o.species_id = s.species_id
JOIN Location l ON o.location_id = l.location_id;

-- -------------------------------
-- STEP 6: EXAMPLE QUERIES
-- -------------------------------

-- 1️⃣ Nested Query: species found in areas with above-average pollution
SELECT DISTINCT s.common_name
FROM Species s
JOIN Observation o ON s.species_id = o.species_id
JOIN Water_Quality wq ON o.quality_id = wq.quality_id
WHERE wq.pollution_index > (SELECT AVG(pollution_index) FROM Water_Quality);

-- Find all locations where average water temperature is higher than the overall average.

SELECT l.region, AVG(wq.temperature) AS avg_temp
FROM Location l
JOIN Water_Quality wq ON l.location_id = wq.location_id
GROUP BY l.region
HAVING AVG(wq.temperature) > (
    SELECT AVG(temperature) FROM Water_Quality
);

-- 2️⃣ Join Query: actions and equipment used
SELECT ca.action_id, s.common_name, e.name AS equipment_used
FROM Conservation_Action ca
JOIN Species s ON ca.species_id = s.species_id
JOIN Action_Equipment ae ON ca.action_id = ae.action_id
JOIN Equipment e ON ae.equipment_id = e.equipment_id;

-- 3️⃣ Aggregate Query: average water temperature per region
SELECT l.region, AVG(wq.temperature) AS avg_temp
FROM Location l JOIN Water_Quality wq ON l.location_id = wq.location_id
GROUP BY l.region;

-- 4️⃣ Procedure Call Example:
CALL GetConservationActionsBySpecies('Blue Whale');

-- 5️⃣ Function Example:
SELECT AvgPollution('Great Barrier Reef') AS AvgPollutionIndex;

-- 6️⃣ Trigger Check:
INSERT INTO Conservation_Action (species_id, action_type, description, start_date, end_date)
VALUES (3, 'Shark Awareness', 'Promote safe fishing zones', '2025-10-01', '2026-03-01');
SELECT * FROM Action_Log;

-- AUTOINCREMENT

ALTER TABLE Species 
MODIFY species_id INT AUTO_INCREMENT PRIMARY KEY;
ALTER TABLE Location MODIFY location_id INT AUTO_INCREMENT PRIMARY KEY;
ALTER TABLE Observer MODIFY observer_id INT AUTO_INCREMENT PRIMARY KEY;
ALTER TABLE Water_Quality MODIFY quality_id INT AUTO_INCREMENT PRIMARY KEY;
ALTER TABLE Observation MODIFY obs_id INT AUTO_INCREMENT PRIMARY KEY;
ALTER TABLE Conservation_Action MODIFY action_id INT AUTO_INCREMENT PRIMARY KEY;
ALTER TABLE Species_Threat MODIFY threat_id INT AUTO_INCREMENT PRIMARY KEY;
ALTER TABLE Equipment MODIFY equipment_id INT AUTO_INCREMENT PRIMARY KEY;
-- ALTER TABLE Action_Equipment MODIFY mapping_id INT AUTO_INCREMENT PRIMARY KEY;




-- ==========================================================
-- END OF FILE
-- ==========================================================
