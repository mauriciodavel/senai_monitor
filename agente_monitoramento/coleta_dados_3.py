import time
import psutil
import socket
import mysql.connector
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import matplotlib.pyplot as plt

# Função para coletar o hostname
def get_hostname():
    return socket.gethostname()

# Função para coletar o endereço IPv4
def get_ipv4_address():
    hostname = get_hostname()
    return socket.gethostbyname(hostname)

# Função para coletar o uso de CPU
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

# Função para coletar o uso de Memória
def get_memory_usage():
    memory = psutil.virtual_memory()
    return memory.percent

# Função para coletar espaço em disco e uso do disco
def get_disk_usage():
    disk = psutil.disk_usage('/')
    return disk.total, disk.used, disk.free, disk.percent

# Função para coletar o tráfego da interface de rede (KB/s)
def get_network_traffic(prev_data, interval):
    net_io = psutil.net_io_counters()
    bytes_sent_per_sec = (net_io.bytes_sent - prev_data['bytes_sent']) / interval / 1024
    bytes_recv_per_sec = (net_io.bytes_recv - prev_data['bytes_recv']) / interval / 1024
    return bytes_sent_per_sec, bytes_recv_per_sec, net_io.bytes_sent, net_io.bytes_recv

# Função para enviar e-mail
def send_email(subject, body):
    sender_email = "davelmauricio@gmail.com"  # Substitua pelo seu e-mail
    receiver_email = "davelmauricio@gmail.com"
    password = "ujlk zgzi jkpp cdvn"  # Substitua pela sua senha de e-mail

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"E-mail enviado para {receiver_email}")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

# Conectar ao banco de dados MySQL
def connect_db():
    return mysql.connector.connect(
        host="10.145.41.252",  # Substitua pelo endereço do seu servidor MySQL
        user="mdavel",  # Substitua pelo seu usuário do MySQL
        password="7820@Mdavel",  # Substitua pela sua senha do MySQL
        database="cib01"  # Substitua pelo nome do seu banco de dados
    )

# Criar tabela se não existir
def create_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitoramento (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME,
            hostname VARCHAR(255),
            ipv4 VARCHAR(255),
            cpu_usage FLOAT,
            memory_usage FLOAT,
            disk_total FLOAT,
            disk_used FLOAT,
            disk_free FLOAT,
            disk_percent FLOAT,
            kb_sent_per_sec FLOAT,
            kb_recv_per_sec FLOAT
        )
    """)

# Inserir dados no banco de dados
def insert_data(cursor, data):
    cursor.execute("""
        INSERT INTO monitoramento (
            timestamp, hostname, ipv4, cpu_usage, memory_usage, disk_total, disk_used, disk_free, disk_percent, kb_sent_per_sec, kb_recv_per_sec
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, data)

# Intervalo de coleta em segundos
interval = 10

# Coletar dados iniciais de rede
net_io_initial = psutil.net_io_counters()
prev_data = {'bytes_sent': net_io_initial.bytes_sent, 'bytes_recv': net_io_initial.bytes_recv}

# Conectar ao banco de dados
db_connection = connect_db()
db_cursor = db_connection.cursor()
create_table(db_cursor)

# Coletar e inserir dados no banco de dados a cada 10 segundos
try:
    while True:
        timestamp = datetime.now()
        hostname = get_hostname()
        ipv4_address = get_ipv4_address()
        cpu_usage = get_cpu_usage()
        memory_usage = get_memory_usage()
        total_disk, used_disk, free_disk, percent_disk = get_disk_usage()
        kb_sent_per_sec, kb_recv_per_sec, bytes_sent, bytes_recv = get_network_traffic(prev_data, interval)

        data = (timestamp, hostname, ipv4_address, cpu_usage, memory_usage, total_disk, used_disk, free_disk, percent_disk, kb_sent_per_sec, kb_recv_per_sec)
        insert_data(db_cursor, data)
        db_connection.commit()

        # Enviar e-mail se o uso do disco for maior ou igual a 90%
        if percent_disk >= 90:
            subject = "Alerta: Uso do Disco Acima de 90%"
            body = f"O uso do disco no host {hostname} ({ipv4_address}) atingiu {percent_disk}%.\nEspaço Total: {total_disk / (1024 ** 3):.2f} GB\nEspaço Usado: {used_disk / (1024 ** 3):.2f} GB\nEspaço Livre: {free_disk / (1024 ** 3):.2f} GB"
            send_email(subject, body)

        # Atualizar os dados anteriores para a próxima coleta
        prev_data['bytes_sent'] = bytes_sent
        prev_data['bytes_recv'] = bytes_recv

        time.sleep(interval)

except KeyboardInterrupt:
    print("Parando a coleta de dados.")
finally:
    db_cursor.close()
    db_connection.close()
