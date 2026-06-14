-- A Healthy Life Recommendation System Database Schema
-- Run this script in your MySQL environment to set up the database.

CREATE DATABASE IF NOT EXISTS healthy_life_db;
USE healthy_life_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- 2. Health Profile Table
CREATE TABLE IF NOT EXISTS health_profile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    age INT NOT NULL,
    gender VARCHAR(50) NOT NULL,
    height FLOAT NOT NULL, -- height in meters or cm (form inputs in cm, stored as cm or meters, let's store as cm and compute in meters)
    weight FLOAT NOT NULL, -- weight in kg
    activity_level VARCHAR(100) NOT NULL,
    goal VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
