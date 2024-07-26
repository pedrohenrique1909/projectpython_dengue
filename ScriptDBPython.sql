CREATE SCHEMA dbpython DEFAULT CHARACTER SET utf8mb4;

USE dbpython;

CREATE TABLE paciente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    data_nascimento DATE NOT NULL,
    peso FLOAT NOT NULL,
    cpf VARCHAR(11) NOT NULL UNIQUE,
    regiao VARCHAR(50) NOT NULL
);

CREATE TABLE diagnostico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paciente_id INT NOT NULL,
    sintomas TEXT NOT NULL,
    diagnostico VARCHAR(50) NOT NULL,
    FOREIGN KEY (paciente_id) REFERENCES paciente(id) ON DELETE CASCADE
);