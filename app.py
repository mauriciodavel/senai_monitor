from flask import Flask, render_template, request, jsonify
import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.io as pio
import datetime

app = Flask(__name__)

# Função para conectar ao banco de dados MySQL
def connect_db():
    return mysql.connector.connect(
        host="10.145.41.252",  # Substitua pelo endereço do seu servidor MySQL
        user="mdavel",       # Nome de usuário de conexão
        password="7820@Mdavel",   # Senha de conexão
        database="cib01"   # Nome do banco de dados
    )

# Função para buscar hostnames únicos
def get_hostnames():
    db_connection = connect_db()
    query = "SELECT DISTINCT hostname FROM monitoramento"
    df = pd.read_sql(query, db_connection)
    db_connection.close()
    return df['hostname'].tolist()

# Função para buscar dados filtrados
def get_filtered_data(hostname, start_date, end_date):
    db_connection = connect_db()
    
    start_date = start_date + " 00:00:00"
    end_date = end_date + " 23:59:59"
    
    query = f"""
        SELECT * FROM monitoramento
        WHERE hostname = '{hostname}' AND
              timestamp BETWEEN '{start_date}' AND '{end_date}'
    """
    df = pd.read_sql(query, db_connection)
    db_connection.close()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# Rota para a página inicial
@app.route('/')
def index():
    hostnames = get_hostnames()
    return render_template('index.html', hostnames=hostnames)

# Rota para atualizar os gráficos
@app.route('/update_graphs', methods=['POST'])
def update_graphs():
    hostname = request.form['hostname']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    df = get_filtered_data(hostname, start_date, end_date)

    # Criar gráficos com Plotly
    fig_cpu = px.line(df, x='timestamp', y='cpu_usage', title='Uso de CPU (%)')
    fig_memory = px.line(df, x='timestamp', y='memory_usage', title='Uso de Memória (%)')
    fig_network = px.line(df, x='timestamp', y=['kb_sent_per_sec', 'kb_recv_per_sec'], title='Tráfego de Rede (KB/s)')

    # Converter gráficos para JSON
    graph_cpu = pio.to_json(fig_cpu)
    graph_memory = pio.to_json(fig_memory)
    graph_network = pio.to_json(fig_network)

    return jsonify({
        'graph_cpu': graph_cpu,
        'graph_memory': graph_memory,
        'graph_network': graph_network
    })

if __name__ == '__main__':
    app.run(debug=True)
