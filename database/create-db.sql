CREATE DATABASE IF NOT EXISTS real_estate_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE real_estate_db;

CREATE TABLE IF NOT EXISTS houses (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    address VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS properties (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    house_id BIGINT NOT NULL,
    number INT NOT NULL,
    area FLOAT NOT NULL,
    type ENUM('жилое', 'нежилое'),
    ownership_form VARCHAR(255),
    cadastral_number VARCHAR(255),
    ownership_doc VARCHAR(255),
    general_comment TEXT,
    FOREIGN KEY (house_id) REFERENCES houses(id),
    UNIQUE (house_id, number)
);

CREATE TABLE comments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    property_id BIGINT,
    owner_index BIGINT,
    comment TEXT,
    FOREIGN KEY (property_id) REFERENCES properties(id)
);


CREATE TABLE IF NOT EXISTS user_tokens (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    token VARCHAR(32) NOT NULL,
    expires_at DATETIME NOT NULL,
    UNIQUE (user_id, token)
);


CREATE TABLE IF NOT EXISTS owners (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    property_id BIGINT NOT NULL,
    fio VARCHAR(255),
    birth_date DATE,
    share FLOAT,
    comment TEXT,
    FOREIGN KEY (property_id) REFERENCES properties(id)
);

CREATE TABLE active_properties (
    user_id BIGINT PRIMARY KEY,
    property_id BIGINT NOT NULL,
    FOREIGN KEY (property_id) REFERENCES properties(id)
);

CREATE TABLE user_state (
    user_id BIGINT PRIMARY KEY,
    last_house_id BIGINT,
    FOREIGN KEY (last_house_id) REFERENCES houses(id)
);

CREATE TABLE user_last_owner (
    user_id INT PRIMARY KEY,
    last_owner_id INT,
    FOREIGN KEY (last_owner_id) REFERENCES owner_data(owner_id) ON DELETE SET NULL
);


ALTER TABLE user_tokens MODIFY COLUMN expires_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;
