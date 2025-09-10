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
    FOREIGN KEY(user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- Table: Games
CREATE TABLE Games (
    id INT AUTO_INCREMENT PRIMARY KEY,
    game_date DATE NOT NULL DEFAULT CURRENT_DATE,
    is_terminated BOOLEAN DEFAULT FALSE
);

-- Table: UserGames
CREATE TABLE UserGames(
    game_id INT NOT NULL,
    player_id INT NOT NULL,
    player_role VARCHAR(15) NOT NULL,
    is_won BOOLEAN DEFAULT NULL,
    points int DEFAULT 0,
    PRIMARY KEY (game_id, player_role),
    UNIQUE (game_id, player_ id),
    CHECK (player_role IN ('judge', 'participant')),
    FOREIGN KEY(game_id) REFERENCES Games(id) ON DELETE CASCADE,
    FOREIGN KEY(player_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- Table: Q_A
CREATE TABLE Q_A (
    game_id INT NOT NULL,
    question_id INT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    ai_question BOOLEAN DEFAULT FALSE,
    ai_answer BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (game_id, question_id),
    FOREIGN KEY(game_id) REFERENCES Games(id) ON DELETE CASCADE
);


INSERT INTO Users(id, user_name, email, hashed_password) VALUES (1, "AI", "--", "--");
INSERT INTO Stats(user_id) VALUES (1);


-- Trigger per update
DELIMITER $$

CREATE TRIGGER prevent_negative_scores
BEFORE UPDATE ON Stats
FOR EACH ROW
BEGIN
    IF NEW.score_part < 0 THEN
        SET NEW.score_part = 0;
    END IF;

    IF NEW.score_judge < 0 THEN
        SET NEW.score_judge = 0;
    END IF;
END$$

DELIMITER ;

-- Trigger per insert
DELIMITER $$

CREATE TRIGGER prevent_negative_scores_insert
BEFORE INSERT ON Stats
FOR EACH ROW
BEGIN
    IF NEW.score_part < 0 THEN
        SET NEW.score_part = 0;
    END IF;

    IF NEW.score_judge < 0 THEN
        SET NEW.score_judge = 0;
    END IF;
END$$

DELIMITER ;
