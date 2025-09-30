#!/usr/bin/env python3
"""
Script de Monitoramento - ASBJJ
Verifica saúde do site e envia alertas se necessário
"""

import requests
import time
import json
from datetime import datetime
import subprocess
import sys

# Configurações
SITE_URL = "http://92.113.33.16"
HEALTHZ_ENDPOINT = f"{SITE_URL}/healthz"
TIMEOUT = 10
MAX_RESPONSE_TIME = 2.0  # segundos

# Cores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def check_health():
    """Verifica endpoint de health check"""
    try:
        start_time = time.time()
        response = requests.get(HEALTHZ_ENDPOINT, timeout=TIMEOUT)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'unknown')
            debug = data.get('debug', False)
            
            if status == 'ok':
                print(f"{Colors.GREEN}✅ Health Check OK{Colors.END}")
                print(f"   Tempo de resposta: {response_time:.3f}s")
                print(f"   Debug mode: {'ON' if debug else 'OFF'}")
                
                if response_time > MAX_RESPONSE_TIME:
                    print(f"{Colors.YELLOW}⚠️  Aviso: Resposta lenta ({response_time:.3f}s > {MAX_RESPONSE_TIME}s){Colors.END}")
                    return False
                
                if debug:
                    print(f"{Colors.RED}⚠️  ALERTA: DEBUG=True em produção!{Colors.END}")
                    return False
                
                return True
        else:
            print(f"{Colors.RED}❌ Health Check FAILED - Status: {response.status_code}{Colors.END}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"{Colors.RED}❌ Timeout ao conectar (>{TIMEOUT}s){Colors.END}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}❌ Erro de conexão - Site pode estar offline{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ Erro: {str(e)}{Colors.END}")
        return False

def check_database():
    """Verifica se o banco de dados está acessível"""
    try:
        response = requests.get(f"{SITE_URL}/admin-secure/login/", timeout=TIMEOUT)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✅ Banco de dados OK{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}❌ Banco de dados com problemas{Colors.END}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ Erro ao verificar banco: {str(e)}{Colors.END}")
        return False

def check_static_files():
    """Verifica se arquivos estáticos estão sendo servidos"""
    try:
        response = requests.get(f"{SITE_URL}/static/css/style.css", timeout=TIMEOUT)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✅ Arquivos estáticos OK{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}❌ Arquivos estáticos com problemas{Colors.END}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ Erro ao verificar estáticos: {str(e)}{Colors.END}")
        return False

def check_services():
    """Verifica status dos serviços no servidor"""
    services = {
        'nginx': 'sudo systemctl is-active nginx',
        'supervisor': 'sudo systemctl is-active supervisor',
        'postgresql': 'sudo systemctl is-active postgresql',
        'redis': 'sudo systemctl is-active redis-server',
    }
    
    print(f"\n{Colors.BLUE}🔍 Verificando serviços...{Colors.END}")
    
    all_ok = True
    for service, command in services.items():
        try:
            result = subprocess.run(
                ['sshpass', '-p', '123', 'ssh', '-o', 'StrictHostKeyChecking=no', 
                 'fabianosf@92.113.33.16', f'echo "123" | {command}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            status = result.stdout.strip()
            if status == 'active':
                print(f"{Colors.GREEN}✅ {service.capitalize()}: Running{Colors.END}")
            else:
                print(f"{Colors.RED}❌ {service.capitalize()}: {status}{Colors.END}")
                all_ok = False
        except Exception as e:
            print(f"{Colors.RED}❌ {service.capitalize()}: Erro ao verificar{Colors.END}")
            all_ok = False
    
    return all_ok

def check_disk_space():
    """Verifica espaço em disco"""
    try:
        result = subprocess.run(
            ['sshpass', '-p', '123', 'ssh', '-o', 'StrictHostKeyChecking=no',
             'fabianosf@92.113.33.16', 'df -h /var/www/asbjj | tail -1'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout.strip()
        if output:
            parts = output.split()
            usage = parts[4].replace('%', '')
            
            print(f"\n{Colors.BLUE}💾 Espaço em disco:{Colors.END}")
            print(f"   Uso: {parts[4]}")
            print(f"   Disponível: {parts[3]}")
            
            if int(usage) > 80:
                print(f"{Colors.RED}⚠️  ALERTA: Disco quase cheio ({usage}%)!{Colors.END}")
                return False
            elif int(usage) > 70:
                print(f"{Colors.YELLOW}⚠️  Aviso: Uso de disco alto ({usage}%){Colors.END}")
            
            return True
    except Exception as e:
        print(f"{Colors.RED}❌ Erro ao verificar disco: {str(e)}{Colors.END}")
        return False

def generate_report():
    """Gera relatório completo de saúde"""
    print(f"\n{'='*60}")
    print(f"{Colors.BLUE}🏥 RELATÓRIO DE SAÚDE - ASBJJ{Colors.END}")
    print(f"{'='*60}")
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Site: {SITE_URL}")
    print(f"{'='*60}\n")
    
    checks = {
        'Health Check': check_health(),
        'Banco de Dados': check_database(),
        'Arquivos Estáticos': check_static_files(),
        'Espaço em Disco': check_disk_space(),
    }
    
    check_services()
    
    print(f"\n{'='*60}")
    
    all_ok = all(checks.values())
    
    if all_ok:
        print(f"{Colors.GREEN}✅ TODOS OS SISTEMAS OPERACIONAIS{Colors.END}")
        print(f"{'='*60}\n")
        return 0
    else:
        print(f"{Colors.RED}❌ ALGUNS SISTEMAS COM PROBLEMAS{Colors.END}")
        print(f"{'='*60}\n")
        
        print("Problemas encontrados:")
        for check, result in checks.items():
            if not result:
                print(f"  - {check}")
        
        return 1

if __name__ == "__main__":
    exit_code = generate_report()
    sys.exit(exit_code)

