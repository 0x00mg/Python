# chmod +x quickscan.sh
# ./quickscan.sh <IP>

#!/bin/bash

# Overenie argumentu
if [ -z "$1" ]; then
    echo "Použitie: $0 <IP-adresa>"
    exit 1
fi

IP=$1

echo "[*] Rýchly scan všetkých portov na $IP..."
ports=$(nmap -p- --min-rate=1000 -Pn -T4 $IP | grep '^[0-9]' | cut -d'/' -f 1 | tr '\n' ',' | sed s/,$//)

if [ -z "$ports" ]; then
    echo "[!] Neboli nájdené žiadne otvorené porty."
    exit 1
fi

echo "[+] Nájdené porty: $ports"
echo "[*] Spúšťam detailný nmap scan..."

nmap -sC -sV -p$ports $IP -oN scan_$IP.txt

echo "[+] Hotovo! Výsledok uložený do scan_$IP.txt"
