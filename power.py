#!/usr/bin/env python3
"""
POWER SCRIPT "Tokinsh" – Interfaz militar PC‑industrial en Python
Adaptado para PC y Termux
Autor: Felipe Monroy  ✦  Empresa: TOKINSH
Licencia: Uso educacional / auditorías autorizadas
"""
import os
import sys
import subprocess
import time
import getpass
from pathlib import Path

# ANSI Colors
RED    = '\033[91m'
GREEN  = '\033[92m'
YELLOW = '\033[93m'
BLUE   = '\033[94m'
NC     = '\033[0m'

# Paths
HOME            = Path.home()
LOGDIR          = HOME / 'Tokinsh-logs'; LOGDIR.mkdir(exist_ok=True)
LOGFILE         = LOGDIR / f"{time.strftime('%F')}.log"
WORDDIR         = HOME / 'wordlists'; WORDDIR.mkdir(exist_ok=True)
M5PORT_DEFAULT  = '/dev/ttyACM0'

# Stub for PC environment
def check_termux(): return

# Utilities
def slow_print(text, delay=0.01):
    for c in text:
        sys.stdout.write(c); sys.stdout.flush(); time.sleep(delay)
    sys.stdout.write('\n')

def progress_bar(duration=2.0, length=20):
    interval = duration / length
    for i in range(length+1):
        bar = '█'*i + ' '*(length-i)
        pct = int(i*100/length)
        sys.stdout.write(f"\r{RED}[{bar}]{NC} {pct}%")
        sys.stdout.flush(); time.sleep(interval)
    # Clear the progress bar line
    sys.stdout.write("\r" + " "*(length+8) + "\r")

def pause():
    input('\n↵ Enter para continuar…')

def log_action(action: str):
    with open(LOGFILE,'a') as f:
        f.write(f"[{time.strftime('%F %T')}] {action}\n")

def confirm_perm() -> bool:
    ans = input(f"{YELLOW}⚠️ Solo con permiso EXPRESO. ¿Continuar? (S/N) ➤ {NC}")
    return ans.strip().lower().startswith('s')

def ensure_wordlist():
    wl = WORDDIR / 'rockyou.txt'
    if wl.exists(): return wl
    ans = input("No se encontró rockyou.txt. ¿Descargar (~14 MB)? (S/N) ➤ ")
    if not ans.strip().lower().startswith('s'):
        return None
    url = 'https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt'
    subprocess.run(['curl','-L','-o',str(wl),url], check=True)
    slow_print(f"Descargado en {wl}")
    return wl

# Install dependencies
def install_deps():
    slow_print("\n🔄 Actualizando…")
    subprocess.run(['pkg','update','-y'], check=False)
    slow_print("🛠️ Instalando paquetes…")
    pkgs = [
        'curl','git','nmap','nikto','gobuster','dirb','whois','dnsenum','mtr',
        'sqlmap','metasploit','hydra','john','hashcat','exploitdb','python-pip',
        'ruby','esptool','pyserial','rshell','screen'
    ]
    subprocess.run(['pkg','install','-y'] + pkgs, check=False)
    subprocess.run([sys.executable,'-m','pip','install','--upgrade',
                    'theharvester','mpremote','adafruit-ampy'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['gem','install','wpscan'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    slow_print("✅ Dependencias listas.")
    pause()

# Pentest functions
def nmap_scan():
    if not confirm_perm(): return
    tgt = input("Objetivo ➤ ")
    log_action(f"Nmap -> {tgt}")
    subprocess.run(['nmap','-sV','-T4',tgt])
    pause()

def nikto_scan():
    if not confirm_perm(): return
    url = input("URL ➤ ")
    log_action(f"Nikto -> {url}")
    subprocess.run(['nikto','-h',url])
    pause()

def sqlmap_auto():
    if not confirm_perm(): return
    u = input("URL vuln ➤ ")
    log_action(f"SQLMap -> {u}")
    subprocess.run(['sqlmap','-u',u,'--batch','--banner'])
    pause()

def metasploit_launch():
    if not confirm_perm(): return
    log_action("Metasploit")
    subprocess.run(['msfconsole','-q'])

def hydra_brute_services():
    if not confirm_perm(): return
    ip = input("IP ➤ ")
    srv = input("Servicio (ssh/ftp/…) ➤ ")
    users = input("Lista usuarios ➤ ")
    pwds = input("Lista passwords ➤ ")
    log_action(f"HydraSvc -> {srv} {ip}")
    subprocess.run(['hydra','-L',users,'-P',pwds,ip,srv])
    pause()

def hydra_web_form():
    if not confirm_perm(): return
    wl = ensure_wordlist()
    dom = input("Dominio (sin https://) ➤ ")
    ruta = input("Ruta login (/path.php) ➤ ")
    ufield = input("Campo usuario ➤ ")
    pfield = input("Campo pass ➤ ")
    ferr = input("Texto de error (ej: Invalid) ➤ ")
    users = input(f"Lista usuarios [{WORDDIR/'users.txt'}] ➤ ") or str(WORDDIR/'users.txt')
    pwds  = input(f"Lista passwords [{wl}] ➤ ") or str(wl)
    cmd = ['hydra','-L',users,'-P',pwds,dom,'http-post-form',
           f"{ruta}:{ufield}=^USER^&{pfield}=^PASS^:F={ferr}"]
    slow_print(f"Ejecutando: {' '.join(cmd)}")
    log_action(f"HydraForm -> https://{dom}{ruta}")
    subprocess.run(cmd)
    pause()

def dirb_scan():
    if not confirm_perm(): return
    url = input("URL ➤ ")
    log_action(f"Dirb -> {url}")
    subprocess.run(['dirb',url])
    pause()

def gobuster_dir():
    if not confirm_perm(): return
    url = input("URL ➤ ")
    log_action(f"Gobuster -> {url}")
    subprocess.run(['gobuster','dir','-u',url,'-w','/usr/share/wordlists/dirb/common.txt'])
    pause()

def theharvester_osint():
    dom = input("Dominio ➤ ")
    log_action(f"Harvester -> {dom}")
    subprocess.run(['theHarvester','-d',dom,'-b','all','-f',str(LOGDIR/f"{dom}_harv.html")])
    pause()

def whois_lookup():
    d = input("Dominio/IP ➤ ")
    log_action(f"Whois -> {d}")
    subprocess.run(['whois',d])
    pause()

def dns_enum():
    d = input("Dominio ➤ ")
    log_action(f"DNSenum -> {d}")
    subprocess.run(['dnsenum',d])
    pause()

def tracer_mtr():
    h = input("Host ➤ ")
    log_action(f"MTR -> {h}")
    subprocess.run(['mtr','-rwzbc','5',h])
    pause()

def john_crack():
    wl = ensure_wordlist()
    f = input("Archivo hashes ➤ ")
    log_action(f"John -> {f}")
    subprocess.run(['john',f])
    pause()

def hashcat_crack():
    wl = ensure_wordlist()
    f = input("Archivo hashes ➤ ")
    w = input("Wordlist ➤ ") or str(wl)
    log_action(f"Hashcat -> {f}")
    subprocess.run(['hashcat','-a','0',f,w])
    pause()

def aircrack_audit():
    if os.geteuid() != 0:
        slow_print("Necesitas root para Aircrack.")
        pause()
        return
    log_action("Aircrack")
    subprocess.run(['airmon-ng','start','wlan0'])
    c = input("Canal ➤ ")
    subprocess.run(['airodump-ng','--channel',c,'wlan0mon'])
    pause()

def http_requests():
    if not confirm_perm(): return
    url = input("URL ➤ ")
    num = int(input("Peticiones ➤ "))
    log_action(f"HTTPreq {num} -> {url}")
    procs = []
    for i in range(1, num+1):
        p = subprocess.Popen(['curl','-s','-o','/dev/null',url])
        procs.append(p)
        sys.stdout.write(f"\r{i}/{num}")
        sys.stdout.flush()
    for p in procs: p.wait()
    slow_print("Completo.")
    pause()

def searchsploit_find():
    k = input("Keyword ➤ ")
    log_action(f"searchsploit {k}")
    subprocess.run(['searchsploit',k])
    pause()

# M5Stack Core2 helpers
def m5_install():
    slow_print("\nInstalando entorno M5Stack…")
    subprocess.run(['pkg','install','-y','esptool','pyserial'], check=False)
    subprocess.run([sys.executable,'-m','pip','install','-U','mpremote','adafruit-ampy'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    slow_print("✅ Entorno listo.")
    pause()

def m5_flash_micropython():
    if not confirm_perm(): return
    p = input(f"Puerto [{M5PORT_DEFAULT}] ➤ ") or M5PORT_DEFAULT
    slow_print("Descargando firmware Core2…")
    fw = HOME / 'micropython_m5core2.bin'
    subprocess.run(['curl','-L','-o',str(fw),
                    'https://static-cdn.m5stack.com/resource/firmware/core2/CORE2_20230421-v1.20.1.bin'], check=True)
    log_action(f"M5Flash -> {p}")
    subprocess.run(['esptool.py','--chip','esp32','--port',p,'erase_flash'], check=True)
    subprocess.run(['esptool.py','--chip','esp32','--port',p,'--baud','460800','write_flash','-z','0x1000',str(fw)], check=True)
    slow_print("✅ MicroPython flasheado.")
    pause()

def m5_upload_script():
    if not confirm_perm(): return
    p = input(f"Puerto [{M5PORT_DEFAULT}] ➤ ") or M5PORT_DEFAULT
    f = input("Archivo .py a subir ➤ ")
    if not os.path.isfile(f):
        slow_print("Archivo no encontrado.")
        pause()
        return
    log_action(f"M5Upload -> {f} on {p}")
    subprocess.run(['mpremote','connect',p,'fs','put',f,':main.py'], check=True)
    slow_print("Subido como main.py. Reiniciando…")
    subprocess.run(['mpremote','connect',p,'reset'], check=True)
    pause()

def m5_serial():
    p = input(f"Puerto [{M5PORT_DEFAULT}] ➤ ") or M5PORT_DEFAULT
    slow_print("Abriendo terminal (Ctrl-a Ctrl-a para salir)…")
    subprocess.run(['screen',p,'115200'], check=False)

# About us
def show_about():
    os.system('cls' if os.name=='nt' else 'clear')
    slow_print(f"{BLUE}Sobre nosotros{NC}\n")
    slow_print("• Nombre: Felipe Monroy")
    slow_print("• Fundador de TOKINSH")
    slow_print("• Empresa creadora de Atankinsh v1.0")
    slow_print("  – Herramienta pentest y gestión integrada.")
    slow_print("• Responsabilidad: Uso con permiso expreso; TOKINSH no se hace responsable.")
    slow_print("• Contacto: WhatsApp +31 6 19386274")
    pause()

# Welcome and menus
def welcome_screen():
    os.system('cls' if os.name=='nt' else 'clear')
    slow_print(f"{YELLOW}INTERFAZ MILITAR PC INDUSTRIAL EN TERMUX{NC}\n")
    ascii_art = r"""
  .----------------. .----------------. .----------------. .-----------------. .----------------. .----------------. .-----------------. .----------------. .----------------. 
 | .--------------. | .--------------. | .--------------. | .--------------. | .--------------. | .--------------. | .--------------. | .--------------. | .--------------. |
 | |      __      | | |  _________   | | |      __      | | | ____  _____  | | |  ___  ____   | | |     _____    | | | ____  _____  | | |    _______   | | |  ____  ____  | |
 | |     /  \     | | | |  _   _  |  | | |     /  \     | | ||_   \|_   _| | | | |_  ||_  _|  | | |    |_   _|   | | ||_   \|_   _| | | |   /  ___  |  | | | |_   ||   _| | |
 | |    / /\ \    | | | |_/ | | \_|  | | |    / /\ \    | | |  |   \ | |   | | |   | |_/ /    | | |      | |     | | |  |   \ | |   | | |  |  (__ \_|  | | |   | |__| |   | |
 | |   / ____ \   | | |     | |      | | |   / ____ \   | | |  | |\ \| |   | | |   |  __'.    | | |      | |     | | |  | |\ \| |   | | |   '.___`-.   | | |   |  __  |   | |
 | | _/ /    \ \_ | | |    _| |_     | | | _/ /    \ \_ | | | _| |_\   |_  | | | _| |  \ \_  | | |     _| |_    | | | _| |_\   |_  | | |  |`\____) |  | | |  _| |  | |_  | |
 | ||____|  |____|| | |   |_____|    | | ||____|  |____|| | ||_____|\\____| | ||_____|\\____| | | |    |_____|   | | ||_____|\\____| | | |  |_______.'  | | | |____||____| | |
 | |              | | |              | | |              | | |              | | |              | | |              | | |              | | |              | | |              | |
 | '--------------' | '--------------' | '--------------' | '--------------' | '--------------' | '--------------' | '--------------' | '--------------' | '--------------' |
  '----------------' '----------------' '----------------' '----------------' '----------------' '----------------' '----------------' '----------------' '----------------'   
"""
    print(RED + ascii_art + NC)
    slow_print("Cargando Tokinsh...")
    progress_bar()
    slow_print(f"{GREEN}Empresa creadora: TOKINSH{NC}")
    slow_print(f"{GREEN}Desarrollado por Felipe Monroy{NC}")
    slow_print(f"{YELLOW}⚠️ Uso con permiso expreso. No nos hacemos responsables.{NC}\n")
    if not input("¿Aceptas TyC? (S/N) ➤ ").strip().lower().startswith('s'):
        sys.exit(0)

def login_menu():
    while True:
        os.system('cls' if os.name=='nt' else 'clear')
        slow_print(f"{GREEN}Tokinsh Suite — Login{NC}\n")
        print("1) Iniciar sesión\n2) Instalar dependencias\n3) Sobre nosotros\n4) Salir")
        o = input("➡️ ")
        if o == '1':
            code = getpass.getpass("Código ➤ ")
            if code == '01020304':
                slow_print("Acceso concedido.\n"); time.sleep(0.5); return
            slow_print("Código incorrecto.\n")
        elif o == '2':
            install_deps()
        elif o == '3':
            show_about()
        elif o == '4':
            sys.exit(0)

def main_menu():
    while True:
        os.system('cls' if os.name=='nt' else 'clear')
        slow_print(f"{BLUE}Tokinsh Pentest + M5Stack Suite{NC}\n")
        print("""
 1) Nmap              2) Nikto             3) SQLMap            4) Metasploit
 5) Hydra servicios   6) Hydra login web   7) Dirb              8) Gobuster
 9) John             10) Hashcat          11) WPScan           12) Whois
13) DNSenum          14) MTR              15) TheHarvester     16) HTTP requests
17) searchsploit     18) Aircrack (root) 19) M5: Entorno      20) M5: Flashear
21) M5: Subir script 22) M5: Serial        0) Salir
""")
        c = input("Seleccione ➤ ")
        actions = {
            '1': nmap_scan, '2': nikto_scan, '3': sqlmap_auto, '4': metasploit_launch,
            '5': hydra_brute_services, '6': hydra_web_form, '7': dirb_scan, '8': gobuster_dir,
            '9': john_crack, '10': hashcat_crack, '11': lambda: (slow_print("WPScan wrapper pendiente."), pause()),
            '12': whois_lookup, '13': dns_enum, '14': tracer_mtr, '15': theharvester_osint,
            '16': http_requests, '17': searchsploit_find, '18': aircrack_audit,
            '19': m5_install, '20': m5_flash_micropython,
            '21': m5_upload_script, '22': m5_serial,
            '0': lambda: sys.exit(0)
        }
        fn = actions.get(c)
        if fn:
            fn()

if __name__ == '__main__':
    check_termux()
    welcome_screen()
    login_menu()
    main_menu()
