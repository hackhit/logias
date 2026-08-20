-- Habilitar la extensión pgvector si no existe
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabla de Miembros
CREATE TABLE IF NOT EXISTS miembros (
    cedula VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'miembro' CHECK (rol IN ('publico', 'miembro', 'admin')),
    fecha_ingreso DATE NOT NULL,
    logia VARCHAR(150),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Pagos
CREATE TABLE IF NOT EXISTS pagos (
    id SERIAL PRIMARY KEY,
    miembro_cedula VARCHAR(20) NOT NULL REFERENCES miembros(cedula) ON DELETE CASCADE,
    fecha_pago DATE NOT NULL,
    monto DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_miembro_pago_fecha UNIQUE (miembro_cedula, fecha_pago)
);

-- Tabla de Documentos Vectoriales para RAG
CREATE TABLE IF NOT EXISTS documentos_vectoriales (
    id SERIAL PRIMARY KEY,
    chunk_hash VARCHAR(64) UNIQUE NOT NULL,
    texto TEXT NOT NULL,
    embedding vector(384) NOT NULL,
    nivel_acceso VARCHAR(20) NOT NULL DEFAULT 'publico' CHECK (nivel_acceso IN ('publico', 'miembro', 'admin')),
    documento_origen VARCHAR(255) NOT NULL,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Auditoría
CREATE TABLE IF NOT EXISTS auditoria (
    id SERIAL PRIMARY KEY,
    usuario_id VARCHAR(50), -- Cédula o 'anonimo'
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tipo_consulta VARCHAR(50) NOT NULL,
    resultado TEXT NOT NULL
);

-- Triggers para hacer la tabla de auditoría INMUTABLE
CREATE OR REPLACE FUNCTION prevent_update_or_delete_audit()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'La tabla de auditoría es inmutable. No se permiten actualizaciones o borrados.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_prevent_update_delete
BEFORE UPDATE OR DELETE ON auditoria
FOR EACH ROW
EXECUTE FUNCTION prevent_update_or_delete_audit();


-- Configuración de la Regla de Mora (3 meses / 90 días)
-- Función para calcular el estado_membresia de un miembro
-- Soporta el uso de la variable de configuración 'app.fecha_referencia_mora' si se define.
-- Marcada como STABLE para optimización de rendimiento según Prioridad 2.1
CREATE OR REPLACE FUNCTION calcular_estado_membresia(p_cedula VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    v_fecha_referencia DATE;
    v_ultimo_pago DATE;
    v_dias_mora INT;
BEGIN
    -- Intentar obtener la variable de sesión 'app.fecha_referencia_mora'
    -- Si no está definida o está vacía, se usa CURRENT_DATE
    BEGIN
        v_fecha_referencia := NULLIF(current_setting('app.fecha_referencia_mora', true), '')::DATE;
    EXCEPTION WHEN OTHERS THEN
        v_fecha_referencia := NULL;
    END;

    IF v_fecha_referencia IS NULL THEN
        v_fecha_referencia := CURRENT_DATE;
    END IF;

    -- Obtener la fecha del último pago del miembro
    SELECT MAX(fecha_pago) INTO v_ultimo_pago FROM pagos WHERE miembro_cedula = p_cedula;

    -- Si nunca ha pagado, se calcula desde la fecha de ingreso
    IF v_ultimo_pago IS NULL THEN
        SELECT fecha_ingreso INTO v_ultimo_pago FROM miembros WHERE cedula = p_cedula;
    END IF;

    -- Calcular días de mora
    v_dias_mora := v_fecha_referencia - v_ultimo_pago;

    IF v_dias_mora > 90 THEN
        RETURN 'entredicho';
    ELSE
        RETURN 'activo';
    END IF;
END;
$$ LANGUAGE plpgsql STABLE;


-- Vista de Miembros con su estado recalculado en tiempo real
CREATE OR REPLACE VIEW vista_miembros AS
SELECT
    m.cedula,
    m.nombre,
    m.email,
    m.rol,
    m.fecha_ingreso,
    m.logia,
    calcular_estado_membresia(m.cedula) AS estado_membresia
FROM miembros m;


-- HABILITAR ROW LEVEL SECURITY (RLS) Y FORZAR RLS (FORCE RLS) OBLIGATORIAMENTE PARA SEGURIDAD DEL OWNER
ALTER TABLE miembros ENABLE ROW LEVEL SECURITY;
ALTER TABLE miembros FORCE ROW LEVEL SECURITY;

ALTER TABLE pagos ENABLE ROW LEVEL SECURITY;
ALTER TABLE pagos FORCE ROW LEVEL SECURITY;

ALTER TABLE documentos_vectoriales ENABLE ROW LEVEL SECURITY;
ALTER TABLE documentos_vectoriales FORCE ROW LEVEL SECURITY;

-- Política de RLS para 'documentos_vectoriales'
CREATE POLICY rls_documentos_policy ON documentos_vectoriales
FOR SELECT
USING (
    CASE
        -- Si es admin, puede ver todo
        WHEN COALESCE(current_setting('app.current_user_role', true), 'publico') = 'admin' THEN TRUE

        -- Si es miembro
        WHEN COALESCE(current_setting('app.current_user_role', true), 'publico') = 'miembro' THEN (
            CASE
                -- Verificar si el miembro está activo o en entredicho (mora)
                WHEN calcular_estado_membresia(current_setting('app.current_user_id', true)) = 'activo'
                    THEN nivel_acceso IN ('publico', 'miembro')
                ELSE nivel_acceso = 'publico' -- Degradado a público por mora
            END
        )

        -- Por defecto / público
        ELSE nivel_acceso = 'publico'
    END
);

-- Política de RLS para 'miembros' (un miembro solo puede ver su propio perfil, admin ve todos)
CREATE POLICY rls_miembros_policy ON miembros
FOR ALL
USING (
    COALESCE(current_setting('app.current_user_role', true), 'publico') = 'admin'
    OR cedula = COALESCE(current_setting('app.current_user_id', true), '')
);

-- Política de RLS para 'pagos' (un miembro solo puede ver sus propios pagos, admin ve todos)
CREATE POLICY rls_pagos_policy ON pagos
FOR ALL
USING (
    COALESCE(current_setting('app.current_user_role', true), 'publico') = 'admin'
    OR miembro_cedula = COALESCE(current_setting('app.current_user_id', true), '')
);


-- SEPARACIÓN DE ROLES DE BASE DE DATOS (Prioridad 0.2)
-- Creamos el rol 'app_runtime' para uso en producción de la app (no es owner de las tablas)
-- Nota: DO block para evitar fallos si el rol ya existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'app_runtime') THEN
        CREATE ROLE app_runtime WITH LOGIN PASSWORD 'app_runtime_secure_pass_2026';
    END IF;
END
$$;

-- Otorgar privilegios estrictos al rol de ejecución
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE miembros TO app_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE pagos TO app_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE documentos_vectoriales TO app_runtime;
GRANT SELECT, INSERT ON TABLE auditoria TO app_runtime;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_runtime;
GRANT SELECT ON vista_miembros TO app_runtime;
