DROP DATABASE IF EXISTS `imgura`;
CREATE DATABASE IF NOT EXISTS `imgura`;
USE `imgura`;

CREATE TABLE IF NOT EXISTS `users` (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    password TEXT,
    admin INTEGER,
    UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS `image` (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER,
    nanoid VARCHAR(10),
    path TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id),
    UNIQUE (nanoid)
);


INSERT INTO users (name, password, admin) VALUES ('admin', '496d6c199f6e0546c8d6549b28632a5b444be2af', 1);
INSERT INTO users (name, password, admin) VALUES ('user', '12dea96fec20593566ab75692c9949596833adc9', 0);

