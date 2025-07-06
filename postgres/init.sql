-- Cria a tabela para as métricas de ping
CREATE TABLE ping_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    target VARCHAR(255) NOT NULL,
    rtt_avg_ms FLOAT,
    packet_loss_percent FLOAT
);

-- Cria a tabela para as métricas de website
CREATE TABLE web_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    url VARCHAR(255) NOT NULL,
    load_time_ms FLOAT,
    status_code INT
);