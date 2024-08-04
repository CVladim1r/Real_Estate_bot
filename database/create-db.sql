CREATE DATABASE IF NOT EXISTS real_estate_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE real_estate_db;

-- Создание таблицы домов
CREATE TABLE IF NOT EXISTS houses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    address VARCHAR(255) NOT NULL
);

-- Создание таблицы помещений
CREATE TABLE IF NOT EXISTS properties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    house_id INT NOT NULL,
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
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT,
    owner_index INT,
    comment TEXT,
    FOREIGN KEY (property_id) REFERENCES properties(id)
);


CREATE TABLE IF NOT EXISTS user_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(8) NOT NULL,
    expires_at DATETIME NOT NULL,
    UNIQUE (user_id, token)
);


-- Создание таблицы собственников
CREATE TABLE IF NOT EXISTS owners (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT NOT NULL,
    fio VARCHAR(255),
    birth_date DATE,
    share FLOAT,
    comment TEXT,
    FOREIGN KEY (property_id) REFERENCES properties(id)
);

-- Вставка тестовых данных для домов
INSERT INTO houses (address) VALUES
('Волгоградский пр. д.187'),
('Кузнецова генерала ул. д.13 корп.2'),
('Привольная ул. д.19'),
('Привольная ул. д.23 корп.2'),
('Привольная ул. д.23'),
('Привольная ул. д.25'),
('Рязанский пр. д.64 корп.2'),
('Самаркандский бульвар, 134а корп.2')
('Самаркандский_бульвар, 137а корп.9')
('Хлобыстова ул. д.18 корп.1')

