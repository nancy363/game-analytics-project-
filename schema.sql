-- Schema for Game Analytics: Unlocking Tennis Data with SportRadar API
CREATE TABLE categories (
    category_id VARCHAR(50) PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);

CREATE TABLE competitions (
    competition_id VARCHAR(50) PRIMARY KEY,
    competition_name VARCHAR(100) NOT NULL,
    parent_id VARCHAR(50) NULL,
    type VARCHAR(20) NOT NULL,
    gender VARCHAR(20) NOT NULL,
    category_id VARCHAR(50),
    level VARCHAR(40) NULL,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE complexes (
    complex_id VARCHAR(50) PRIMARY KEY,
    complex_name VARCHAR(100) NOT NULL
);

CREATE TABLE venues (
    venue_id VARCHAR(50) PRIMARY KEY,
    venue_name VARCHAR(100) NOT NULL,
    city_name VARCHAR(100) NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    country_code CHAR(3) NOT NULL,
    timezone VARCHAR(100) NOT NULL,
    complex_id VARCHAR(50),
    capacity INT NULL,
    FOREIGN KEY (complex_id) REFERENCES complexes(complex_id)
);

CREATE TABLE competitors (
    competitor_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    country_code CHAR(3) NOT NULL,
    abbreviation VARCHAR(10) NOT NULL
);

CREATE TABLE competitor_rankings (
    rank_id INT PRIMARY KEY AUTO_INCREMENT,
    rank INT NOT NULL,
    movement INT NOT NULL,
    points INT NOT NULL,
    competitions_played INT NOT NULL,
    competitor_id VARCHAR(50) NOT NULL,
    tour VARCHAR(20) NOT NULL,
    gender VARCHAR(20) NOT NULL,
    year INT NULL,
    week INT NULL,
    FOREIGN KEY (competitor_id) REFERENCES competitors(competitor_id)
);

CREATE INDEX ix_competitions_category ON competitions(category_id);
CREATE INDEX ix_competitions_type_gender ON competitions(type, gender);
CREATE INDEX ix_venues_country ON venues(country_name);
CREATE INDEX ix_venues_complex ON venues(complex_id);
CREATE INDEX ix_rankings_rank ON competitor_rankings(rank);
CREATE INDEX ix_rankings_points ON competitor_rankings(points);
