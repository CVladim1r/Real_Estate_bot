CREATE DATABASE IF NOT EXISTS real_estate_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE real_estate_db;

CREATE TABLE IF NOT EXISTS houses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    address VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS properties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    house_id INT NOT NULL,
    number INT NOT NULL,
    area FLOAT NOT NULL,
    type ENUM('жилое', 'нежилое') NOT NULL,
    ownership_form VARCHAR(255) NOT NULL,
    cadastral_number VARCHAR(255),
    ownership_doc VARCHAR(255),
    FOREIGN KEY (house_id) REFERENCES houses(id),
    UNIQUE (house_id, number)
);

CREATE TABLE IF NOT EXISTS owners (
    id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT NOT NULL,
    fio VARCHAR(255) NOT NULL,
    birth_date DATE NOT NULL,
    share FLOAT NOT NULL,
    FOREIGN KEY (property_id) REFERENCES properties(id)
);

CREATE TABLE IF NOT EXISTS comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    owner_id INT,
    property_id INT,
    comment TEXT NOT NULL,
    is_general BOOLEAN NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES owners(id),
    FOREIGN KEY (property_id) REFERENCES properties(id)
);

-- Insert sample data for houses
INSERT INTO houses (address) VALUES
('ул. Пронина 27'),
('Рязанский проспект 16');

-- Insert sample data for properties
INSERT INTO properties (house_id, number, area, type, ownership_form, cadastral_number, ownership_doc) VALUES
(1, 1, 159.3, 'жилое', 'Собственная', NULL, 'Соглашение №77-АН №018467 от 19.11.2007г.'),
(1, 2, 112, 'жилое', 'Собственная', NULL, 'Выписка из Единого Государственного Реестра прав на недвижимое имущество №77:04:0005004:6428-77/072/2023-2 от 31.05.2023г.'),
(1, 3, 125.3, 'жилое', 'Собственная', NULL, 'Выписка из Единого Государственного Реестра прав на недвижимое имущество №б/н от 12.10.2021г.'),
(1, 5, 159.3, 'жилое', 'Собственная', '77:04:0005004:6431', 'Договор купли-продажи объекта недвижимости с использованием кредитных средств №77:04:0005004:6431-77/072/2021-3 от 21.12.2021г.'),
(1, 6, 112.5, 'жилое', 'Собственная', NULL, 'Выписка из Единого Государственного Реестра прав на недвижимое имущество №КУВИ-001/2022-148668541 от 29.08.2022г.'),
(1, 7, 126, 'жилое', 'Собственная', NULL, 'Выписка из Единого Государственного Реестра прав на недвижимое имущество №б/н от 15.04.2022г.'),
(1, 8, 70.8, 'жилое', 'Собственная', NULL, 'Договор купли-продажи квартиры с использованием кредитных средств №б/н от 21.12.2021г.'),
(2, 1, 150.0, 'жилое', 'Собственная', NULL, 'Соглашение №88-АН №018467 от 20.11.2008г.'),
(2, 2, 120.0, 'жилое', 'Собственная', NULL, 'Выписка из Единого Государственного Реестра прав на недвижимое имущество №88:04:0005004:6428-88/072/2023-3 от 31.05.2024г.');

-- Insert sample data for owners
INSERT INTO owners (property_id, fio, birth_date, share) VALUES
(1, 'Александрова Любовь Терентьевна', '1950-09-29', 159.3),
(2, 'Червова Татьяна Юрьевна', '1977-12-21', 112),
(3, 'Пушилин Евгений Анатольевич', '1985-12-30', 62.65),
(3, 'Пушилина Виктория Викторовна', '1987-01-27', 62.65),
(4, 'Пшеничников Алексей Викторович', '1970-09-16', 159.3),
(5, 'Акопян Армен Гагикович', '1966-05-29', 112.5),
(6, 'Пеккер Александрина Валентиновна', '1984-12-19', 126),
(7, 'Мазалевская Елена Михайловна', '1980-02-16', 70.8),
(8, 'Иванов Иван Иванович', '1980-01-01', 150.0),
(9, 'Петров Петр Петрович', '1985-02-02', 120.0);
