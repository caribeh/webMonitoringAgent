# Agente de Monitoramento Web (webmonitoringagent)

Este projeto implementa uma solução de monitoramento de rede e web, composta por um agente em Python, um banco de dados PostgreSQL e uma plataforma de visualização Grafana, todos orquestrados com Docker Compose.

A solução foi projetada para ser iniciada com um único comando, com provisionamento automático do Data Source e de um Dashboard inicial no Grafana.

## High-Level Design (HLD)

A arquitetura da solução é dividida em três componentes principais que se comunicam através de uma rede Docker dedicada:

1.  **Agente de Monitoramento (`monitoring-agent`)**:
    * Uma aplicação Python containerizada.
    * Responsável por executar testes periódicos de rede contra alvos pré-definidos (`google.com`, `youtube.com`, `rnp.br`, etc.).
    * Testes realizados:
        * **Ping**: Mede a latência média (RTT) e a porcentagem de perda de pacotes.
        * **HTTP GET**: Mede o tempo de carregamento da página e captura o código de status HTTP.
    * Persiste os resultados coletados no banco de dados PostgreSQL.

2.  **Banco de Dados (`postgres-db`)**:
    * Uma instância do PostgreSQL.
    * Armazena os dados históricos das métricas coletadas pelo agente.
    * Serve como fonte de dados (Data Source) para o Grafana.

3.  **Visualização (`grafana`)**:
    * Uma instância do Grafana.
    * É **automaticamente provisionada** ao iniciar para conectar-se ao PostgreSQL e para carregar um dashboard pré-configurado.
    * Exibe as métricas em dashboards visuais e interativos, permitindo a análise histórica do desempenho dos alvos.

### Diagrama da Arquitetura

```
+----------------------+      +----------------------+      +--------------------------+
|      Navegador       |      |                      |      |        Alvos             |
| (Usuário acessando   |----->|       Grafana        |<---->|     - google.com         |
|   o dashboard)       |      | (Visualização)       |      |     - youtube.com        |
+----------------------+      +----------------------+      |     - rnp.br             |
                                                            |     - registro.br        |
                                      ^                     +--------------------------+
                                      | (Consulta SQL)               ^
                                      |                              | (Testes de Rede)
                                      v                              |
+----------------------+      +----------------------+               |
|  Agente de Monitor.  |----->|    PostgreSQL DB     |<--------------+
|      (Python)        |      |    (Armazenamento)   |
+----------------------+      +----------------------+
```

## Como Executar

### Pré-requisitos

* Docker
* Docker Compose

### Passos

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd webmonitoringagent
    ```

2.  **Suba os containers:**
    Execute o seguinte comando na raiz do projeto. Ele irá construir a imagem do agente, baixar as imagens do Postgres e Grafana, e iniciar todos os containers em modo detached (`-d`).
    ```bash
    docker-compose up --build -d
    ```

3.  **Acesse o Grafana:**
    * Abra seu navegador e acesse `http://localhost:3000`.
    * Aguarde alguns instantes para que o agente colete os primeiros dados.
    * **Login:** `admin`
    * **Senha:** `admin`
    * O Grafana pedirá para você alterar a senha no primeiro login.

## Provisionamento Automático do Grafana

**Não é necessário realizar nenhuma configuração manual no Grafana.** Graças ao mecanismo de provisioning:

* **Data Source:** A conexão com o banco de dados `PostgreSQL-Metrics` é criada automaticamente.
* **Dashboard:** Um dashboard chamado **"Web & Network Monitoring"** já estará disponível na página inicial, pronto para uso. Ele contém painéis para latência, perda de pacotes, tempo de carregamento web e um resumo dos status codes HTTP.

## Resolução de Problemas (Troubleshooting)

Caso encontre algum problema, a primeira ação é sempre verificar os logs: `docker-compose logs <nome_do_servico>`.

Para forçar um "reset" completo do ambiente (útil após corrigir algum arquivo de configuração):

1.  **Pare e remova os containers:**
    ```bash
    docker-compose down
    ```
2.  **Remova o volume de dados do Postgres (isso apagará o banco de dados):**
    ```bash
    docker volume rm webmonitoringagent_postgres-data
    ```
3.  **Suba o ambiente novamente:**
    ```bash
    docker-compose up --build -d
    ```