#!/usr/bin/env python3
"""
Sistema de Monitoramento de Bots
Monitora containers Docker e atualiza status no banco de dados
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, List

import redis
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://botuser:senha@postgres:5432/telegram_bots")

class BotMonitor:
    def __init__(self):
        self.redis_client = redis.from_url(REDIS_URL)
        self.db_connection = None
        self.running = True
        
    def connect_database(self):
        """Conecta ao banco de dados PostgreSQL"""
        try:
            # Parse DATABASE_URL
            db_url = DATABASE_URL.replace("postgresql://", "")
            user_pass, host_port_db = db_url.split("@")
            user, password = user_pass.split(":")
            host_port, database = host_port_db.split("/")
            host, port = host_port.split(":")
            
            self.db_connection = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            logger.info("Conectado ao banco de dados PostgreSQL")
        except Exception as e:
            logger.error(f"Erro ao conectar ao banco de dados: {e}")
            raise
    
    def get_docker_containers(self) -> List[Dict]:
        """Obtém lista de containers Docker relacionados aos bots"""
        try:
            cmd = [
                "docker", "ps", "-a", "--filter", "name=bot-",
                "--format", "{{.Names}}|{{.Status}}|{{.CreatedAt}}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        name = parts[0]
                        status = parts[1]
                        created = parts[2]
                        
                        # Extrair nome do bot (remover prefixo "bot-")
                        bot_name = name.replace("bot-", "")
                        
                        containers.append({
                            "name": bot_name,
                            "container_name": name,
                            "status": "running" if "Up" in status else "stopped",
                            "created": created,
                            "raw_status": status
                        })
            
            return containers
        except Exception as e:
            logger.error(f"Erro ao obter containers Docker: {e}")
            return []
    
    def update_bot_status(self, bot_name: str, status: str, error_message: str = None):
        """Atualiza status do bot no banco de dados"""
        try:
            cursor = self.db_connection.cursor()
            
            # Verificar se bot existe
            cursor.execute("SELECT id FROM bots WHERE name = %s", (bot_name,))
            result = cursor.fetchone()
            
            if result:
                bot_id = result[0]
                
                # Atualizar status
                if error_message:
                    cursor.execute(
                        "UPDATE bots SET status = %s, error_message = %s, last_activity = %s WHERE id = %s",
                        (status, error_message, datetime.utcnow(), bot_id)
                    )
                else:
                    cursor.execute(
                        "UPDATE bots SET status = %s, last_activity = %s WHERE id = %s",
                        (status, datetime.utcnow(), bot_id)
                    )
                
                # Adicionar log
                cursor.execute(
                    "INSERT INTO bot_logs (bot_id, level, message) VALUES (%s, %s, %s)",
                    (bot_id, "info", f"Status alterado para: {status}")
                )
                
                self.db_connection.commit()
                logger.info(f"Status do bot {bot_name} atualizado para: {status}")
            else:
                logger.warning(f"Bot {bot_name} não encontrado no banco de dados")
                
        except Exception as e:
            logger.error(f"Erro ao atualizar status do bot {bot_name}: {e}")
            if self.db_connection:
                self.db_connection.rollback()
        finally:
            if cursor:
                cursor.close()
    
    def check_container_health(self, container_name: str) -> Dict:
        """Verifica saúde de um container específico"""
        try:
            # Verificar se container está rodando
            cmd = ["docker", "inspect", container_name, "--format", "{{.State.Status}}"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {"status": "not_found", "error": "Container não encontrado"}
            
            status = result.stdout.strip()
            
            if status == "running":
                # Verificar logs recentes para erros
                cmd = ["docker", "logs", "--tail", "10", container_name]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                logs = result.stdout
                error_count = logs.lower().count("error")
                warning_count = logs.lower().count("warning")
                
                return {
                    "status": "running",
                    "error_count": error_count,
                    "warning_count": warning_count,
                    "logs": logs
                }
            else:
                return {"status": "stopped", "error": f"Container parado: {status}"}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_container_logs(self, container_name: str, lines: int = 50) -> str:
        """Obtém logs de um container"""
        try:
            cmd = ["docker", "logs", "--tail", str(lines), container_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            logger.error(f"Erro ao obter logs do container {container_name}: {e}")
            return f"Erro ao obter logs: {e}"
    
    def monitor_containers(self):
        """Monitora todos os containers de bots"""
        logger.info("Iniciando monitoramento de containers...")
        
        while self.running:
            try:
                containers = self.get_docker_containers()
                
                for container in containers:
                    bot_name = container["name"]
                    container_name = container["container_name"]
                    
                    # Verificar saúde do container
                    health = self.check_container_health(container_name)
                    
                    if health["status"] == "running":
                        # Container está rodando
                        if health.get("error_count", 0) > 5:
                            # Muitos erros, marcar como erro
                            self.update_bot_status(
                                bot_name, 
                                "error", 
                                f"Muitos erros detectados: {health['error_count']} erros"
                            )
                        else:
                            # Tudo ok
                            self.update_bot_status(bot_name, "running")
                    elif health["status"] == "stopped":
                        # Container parado
                        self.update_bot_status(
                            bot_name, 
                            "stopped", 
                            health.get("error", "Container parado")
                        )
                    else:
                        # Erro ou não encontrado
                        self.update_bot_status(
                            bot_name, 
                            "error", 
                            health.get("error", "Erro desconhecido")
                        )
                
                # Publicar status no Redis para WebSocket
                self.publish_status_update()
                
                # Aguardar antes da próxima verificação
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Erro durante monitoramento: {e}")
                time.sleep(30)  # Aguardar mais tempo em caso de erro
    
    def publish_status_update(self):
        """Publica atualização de status no Redis"""
        try:
            cursor = self.db_connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM bots ORDER BY name")
            bots = cursor.fetchall()
            
            status_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "bots": [
                    {
                        "id": bot["id"],
                        "name": bot["name"],
                        "phone_number": bot["phone_number"],
                        "status": bot["status"],
                        "bot_type": bot["bot_type"],
                        "last_activity": bot["last_activity"].isoformat() if bot["last_activity"] else None,
                        "is_active": bot["is_active"]
                    }
                    for bot in bots
                ]
            }
            
            # Publicar no Redis
            self.redis_client.publish("bot_status_updates", json.dumps(status_data))
            
        except Exception as e:
            logger.error(f"Erro ao publicar status no Redis: {e}")
        finally:
            if cursor:
                cursor.close()
    
    def start(self):
        """Inicia o monitor"""
        try:
            self.connect_database()
            self.monitor_containers()
        except KeyboardInterrupt:
            logger.info("Monitor interrompido pelo usuário")
            self.running = False
        except Exception as e:
            logger.error(f"Erro fatal no monitor: {e}")
        finally:
            if self.db_connection:
                self.db_connection.close()

if __name__ == "__main__":
    monitor = BotMonitor()
    monitor.start()
