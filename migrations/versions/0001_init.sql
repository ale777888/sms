-- 初始建表草案（下一阶段将改造为 Alembic 脚本）
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id BIGINT UNIQUE NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin','support','readonly','user')),
    balance NUMERIC NOT NULL DEFAULT 0,
    frozen_balance NUMERIC NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    aliases TEXT,
    enabled INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    country TEXT NOT NULL,
    price NUMERIC NOT NULL,
    currency TEXT NOT NULL,
    user_overrides_json TEXT,
    active_from TIMESTAMP,
    active_to TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    country TEXT NOT NULL,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    phone TEXT,
    pkey TEXT,
    unit_price NUMERIC NOT NULL,
    status TEXT NOT NULL,
    sms_text TEXT,
    fail_code TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    order_id INTEGER REFERENCES orders(id),
    type TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    meta_json TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor INTEGER NOT NULL,
    action TEXT NOT NULL,
    target TEXT,
    diff_json TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT OR IGNORE INTO projects (id, name, aliases) VALUES
    (1001, 'Telegram', 'tg,telegram,飞机'),
    (1007, 'Facebook', 'fb,脸书'),
    (1013, '探探', 'tantan,交友');
