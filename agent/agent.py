import os
import time
import requests
import psycopg2
import subprocess
import re

# --- Configurações ---
TARGETS = ["google.com", "youtube.com", "rnp.br", "registro.br", "brunocaribe.com.br"]
INTERVALO_SEGUNDOS = 60

# Configs do DB vindas do ambiente Docker
DB_HOST = os.getenv("DB_HOST", "postgres-db")
DB_NAME = os.getenv("DB_NAME", "monitoring_db")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

# Cabeçalho para simular um navegador real
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_db_connection():
    """Tenta conectar ao banco de dados até conseguir."""
    conn = None
    while not conn:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            print("Conexão com o PostgreSQL estabelecida.")
        except psycopg2.OperationalError as e:
            print(f"Aguardando o banco de dados ficar disponível... ({e})")
            time.sleep(5)
    return conn

def measure_ping(host):
    """
    Chama o comando ping do sistema e parseia o resultado.
    Retorna uma tupla com (latencia_media, perda_pacotes).
    """
    try:
        command = ["ping", "-c", "5", host]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode != 0:
            print(f"Ping para {host} falhou. stderr: {result.stderr}")
            return None, None

        output = result.stdout
        rtt_line = re.search(r"rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms", output)
        packet_loss_line = re.search(r"(\d+)% packet loss", output)

        rtt_avg = float(rtt_line.group(2)) if rtt_line else None
        packet_loss = float(packet_loss_line.group(1)) if packet_loss_line else None

        return rtt_avg, packet_loss

    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"Erro ao executar ping para {host}: {e}")
        return None, None

def measure_website_load(url):
    """Mede o tempo de carregamento de uma URL e pega o status code."""
    full_url = f"https://{url}"
    try:
        response = requests.get(full_url, headers=HTTP_HEADERS, timeout=10)
        return response.elapsed.total_seconds() * 1000, response.status_code
    except requests.RequestException as e:
        print(f"Erro ao acessar {full_url}: {e}")
        return None, None

def salvar_metricas(db_conn, target, ping_data, web_data):
    """
    Salva os resultados dos testes de ping e web no banco de dados.
    Retorna True em caso de sucesso, False em caso de falha.
    """
    latency, packet_loss = ping_data
    load_time, status_code = web_data

    try:
        # Usar 'with' garante que o cursor seja fechado automaticamente
        with db_conn.cursor() as cursor:
            if latency is not None:
                cursor.execute(
                    "INSERT INTO ping_metrics (target, rtt_avg_ms, packet_loss_percent) VALUES (%s, %s, %s)",
                    (target, latency, packet_loss)
                )
            if load_time is not None:
                cursor.execute(
                    "INSERT INTO web_metrics (url, load_time_ms, status_code) VALUES (%s, %s, %s)",
                    (f"https://{target}", load_time, status_code)
                )
        db_conn.commit()
        print("  -> Dados salvos no banco.")
        return True
    except (Exception, psycopg2.Error) as error:
        print(f"!! Erro ao salvar no banco de dados: {error}")
        # Desfaz a transação em caso de erro
        db_conn.rollback()
        return False

def main():
    """Lógica principal do agente de monitoramento."""
    print("Iniciando o agente de monitoramento...")
    db_conn = get_db_connection()

    while True:
        print(f"\n--- {time.ctime()} ---")
        for target in TARGETS:
            print(f"Testando alvo: {target}")

            # 1. Coleta as métricas
            ping_results = measure_ping(target)
            web_results = measure_website_load(target)
            
            # Imprime os resultados no console
            if ping_results[0] is not None:
                print(f"  -> Ping: Latência={ping_results[0]:.2f}ms, Perda={ping_results[1]}%")
            else:
                print("  -> Ping: Falhou")
            
            if web_results[0] is not None:
                print(f"  -> Web: Tempo={web_results[0]:.2f}ms, Status={web_results[1]}")
            else:
                print("  -> Web: Falhou")

            # 2. Salva as métricas no banco de dados
            if not salvar_metricas(db_conn, target, ping_results, web_results):
                # Se a escrita falhar, a conexão pode ter caído. Tenta reconectar.
                print("Tentando reconectar ao banco de dados...")
                if db_conn:
                    db_conn.close()
                db_conn = get_db_connection()

        time.sleep(INTERVALO_SEGUNDOS)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAgente finalizado pelo usuário.")