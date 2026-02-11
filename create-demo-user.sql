-- Script SQL para crear usuario demo en ClientFlow Pro
-- Ejecutar en Railway Dashboard → Query

-- Crear tablas si no existen (simplificado)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(50),
    role VARCHAR(50) DEFAULT 'professional',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar usuario demo (contraseña: demo123)
-- El hash es para "demo123"
INSERT INTO users (email, hashed_password, full_name, phone, role, is_active)
VALUES (
    'demo@clientflow.pro',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/I1K',
    'Dr. Ana García',
    '+5215512345678',
    'professional',
    true
)
ON CONFLICT (email) DO NOTHING;

-- Verificar que se creó
SELECT * FROM users WHERE email = 'demo@clientflow.pro';
