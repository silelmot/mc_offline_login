CREATE TABLE IF NOT EXISTS users (
    Name char(16) NOT NULL,
    Password text NOT NULL,
    Set_ tinyint(1) NOT NULL DEFAULT 1,
    Email char(124) NOT NULL,
    lastlogin timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
    PRIMARY KEY (Name)
);
