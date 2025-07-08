DROP DATABASE IF EXISTS turingDB;
CREATE DATABASE turingDB;
USE turingDB;

-- Table: Users
CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL
);

-- Table: Stats
CREATE TABLE Stats (
    user_id INT PRIMARY KEY,
    n_games INT DEFAULT 0,
    score_part INT DEFAULT 0,
    score_judge INT DEFAULT 0,
    won_part INT DEFAULT 0,
    won_judge INT DEFAULT 0,
    lost_part INT DEFAULT 0,
    lost_judge INT DEFAULT 0,
    FOREIGN KEY user_id REFERENCES Users(id) ON DELETE CASCADE
);

-- Table: Games
CREATE TABLE Games (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    result VARCHAR(20) DEFAULT NULL,
    terminated BOOLEAN DEFAULT 0,
    CHECK (result IN ('win', 'loss'))
);

CREATE TABLE UserGames(
    game_id INT NOT NULL,
    player_id INT NOT NULL,
    role VARCHAR(15) NOT NULL,
    PRIMARY KEY(game_id, player_id),
    CHECK (role in ('judge', 'participant')),
    FOREIGN KEY game_id REFERENCES Games(id) ON DELETE CASCADE,
    FOREIGN KEY player_id REFERENCES Users(id) ON DELETE CASCADE
)
-- Table: Q_A
CREATE TABLE Q_A (
    id INT AUTO_INCREMENT PRIMARY KEY,
    game_id INT NOT NULL,
    question_id INT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    ai_question BOOLEAN DEFAULT FALSE,
    ai_answer BOOLEAN DEFAULT FALSE,
    FOREIGN KEY game_id REFERENCES Games(id) ON DELETE CASCADE
);
