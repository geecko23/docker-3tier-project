-- Seed database for the Docker 3-tier project

CREATE DATABASE IF NOT EXISTS appdb;

USE appdb;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(100) NOT NULL
);

INSERT INTO users (name, role) VALUES
('Abrar', 'DevOps Student'),
('Alice', 'Cloud Engineer'),
('Bob', 'SRE');
