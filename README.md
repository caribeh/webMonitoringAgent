# Prova Prática - Agente de Monitoramento Web

Este projeto implementa uma solução de monitoramento de rede e web, composta por um agente em Python, um banco de dados PostgreSQL e uma plataforma de visualização Grafana, todos orquestrados com Docker Compose.

## High-Level Design (HLD)

A arquitetura da solução é dividida em três componentes principais que se comunicam através de uma rede Docker dedicada:

1.  **Agente de Monitoramento (`monitoring-agent`)**:
    * Uma aplicação Python containerizada.
    * Responsável por executar testes periódicos de rede contra alvos pré-definidos.
    * Testes realizados:
        * **Ping**: Mede a latência média (RTT) e a porcentagem de perda de pacotes.
        * **HTTP GET**: Mede o tempo de carregamento da página e captura o código de status HTTP.
    * Persiste os resultados coletados no banco de dados PostgreSQL.

2.  **Banco de Dados (`postgres-db`)**:
    * Uma instância do PostgreSQL.
    * Armazena os dados históricos das métricas coletadas pelo agente.
    * Possui duas tabelas principais: `ping_metrics` e `web_metrics`.
    * Serve como fonte de dados (Data Source) para o Grafana.

3.  **Visualização (`grafana`)**:
    * Uma instância do Grafana.
    * Conecta-se ao PostgreSQL para consultar os dados de monitoramento.
    * Exibe as métricas em dashboards visuais e interativos, permitindo a análise histórica do desempenho dos alvos.

### Diagrama da Arquitetura

```
+----------------------+      +----------------------+      +--------------------------+
|      Navegador       |      |                      |      |        Alvos             |
| (Usuário acessando   |----->|       Grafana        |<---->|     - google.com         |
|   o dashboard)       |      | (Visualização)       |      |     - youtube.com        |
+----------------------+      +----------------------+      |     - rnp.br             |
                                                            |     - registro.br        |
                                                            |     - brunocaribe.com.br |
                                      ^                     +--------------------------+
                                      | (Consulta SQL)               ^
                                      |                              | (Testes de Rede)
                                      v                              |
+----------------------+      +----------------------+               |
|  Agente de Monitor.  |----->|    PostgreSQL DB     |<--------------+
|      (Python)        |      |    (Armazenamento)   |
+----------------------+      +----------------------+
```

## Estrutura do Projeto

```
/
├── agent/              # Contém o código e Dockerfile do agente
│   ├── Dockerfile
│   ├── agent.py
│   └── requirements.txt
├── postgres/           # Contém o script de inicialização do banco
│   └── init.sql
├── docker-compose.yml  # Orquestra todos os serviços
└── README.md           # Esta documentação
```

## Como Executar

### Pré-requisitos

* Docker
* Docker Compose

### Passos

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd devops-monitoring-challenge
    ```

2.  **Suba os containers:**
    Execute o seguinte comando na raiz do projeto. Ele irá construir a imagem do agente, baixar as imagens do Postgres e Grafana, e iniciar todos os containers em modo detached (`-d`).
    ```bash
    docker-compose up --build -d
    ```

3.  **Verifique se os serviços estão rodando:**
    ```bash
    docker-compose ps
    ```
    Você deve ver os três containers (`monitoring-agent`, `postgres-db`, `grafana`) com o status `Up`.

4.  **Acesse o Grafana:**
    Abra seu navegador e acesse `http://localhost:3000`.
    * **Login:** `admin`
    * **Senha:** `admin`
    (O Grafana pedirá para você alterar a senha no primeiro login).

## Configurando o Grafana

Siga os passos abaixo para criar seu dashboard.

### 1. Adicionar o PostgreSQL como Data Source

* No menu lateral esquerdo, vá em **Configuration (engrenagem) > Data Sources**.
* Clique em **"Add data source"**.
* Selecione **"PostgreSQL"**.
* Preencha os detalhes da conexão:
    * **Host**: `postgres-db:5432`
    * **Database**: `monitoring_db`
    * **User**: `user`
    * **Password**: `password`
    * **SSL Mode**: `disable`
* Clique em **"Save & test"**. Você deve ver uma mensagem de sucesso.

### 2. Criar o Dashboard

* No menu lateral, vá em **Dashboards (ícone de quatro quadrados) > New > New Dashboard**.
* Clique em **"Add visualization"**.

#### Exemplo de Painel: Latência Média (Ping)

* **Data source**: Selecione o `PostgreSQL` que você acabou de configurar.
* No editor de query, mude para o modo **"Code"** e insira a seguinte query SQL:
    ```sql
    SELECT
      timestamp AS "time",
      rtt_avg_ms,
      target
    FROM
      ping_metrics
    ORDER BY
      timestamp
    ```
* No painel à direita, em **"Visualization"**, escolha **"Time series"**.
* Em **"Panel title"**, coloque "Latência Média (RTT - ms)".
* Clique em **"Apply"** no canto superior direito para salvar o painel.

#### Exemplo de Painel: Tempo de Carregamento (Web)

* Adicione um novo painel.
* Use a seguinte query:
    ```sql
    SELECT
      timestamp AS "time",
      load_time_ms,
      url
    FROM
      web_metrics
    ORDER BY
      timestamp
    ```
* Configure a visualização como **"Time series"** e dê um título como "Tempo de Carregamento Web (ms)".
* Clique em **"Apply"**.

**Continue adicionando painéis para as outras métricas (perda de pacotes, status code) da mesma forma!**

### 5. Parando a Aplicação

Para parar todos os containers, execute:
```bash
docker-compose down
```
Para remover também os volumes (perdendo todos os dados), execute:
```bash
docker-compose down -v
```