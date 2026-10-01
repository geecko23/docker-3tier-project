#!/bin/bash

mysql -u root -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" <<'EOF'
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(100) NOT NULL
);

INSERT INTO users (name, role) VALUES
('Abrar', 'DevOps Student'),
('Alice', 'Cloud Engineer'),
('Bob', 'SRE');
EOF
