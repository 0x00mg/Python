# chmod +x quickscan.sh
# ./quickscan.sh 10.10.10.245

#!/bin/bash

# Overenie argumentu
if [ -z "$1" ]; then
    echo "Použitie: $0 <IP-adresa>"
    exit 1
fi

IP=$1
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
OUTPUT_SCAN="scan_$IP_$TIMESTAMP"

mkdir -p "$OUTPUT_SCAN"

echo "[*] Výsledky budú uložené do priečinka: $OUTPUT_SCAN"

# 1. Rýchly full-port scan
echo "[*] Rýchly scan všetkých portov na $IP..."
nmap -p- --min-rate=1000 -Pn -T4 $IP -oN "$OUTPUT_SCAN/fullport_scan.txt"

# Extrahovanie otvorených portov
ports=$(grep '^[0-9]' "$OUTPUT_SCAN/fullport_scan.txt" | cut -d'/' -f1 | tr '\n' ',' | sed 's/,$//')

if [ -z "$ports" ]; then
    echo "[!] Neboli nájdené žiadne otvorené porty."
    exit 1
fi

echo "[+] Nájdené porty: $ports" | tee "$OUTPUT_SCAN/open_ports.txt"

# 2. Detailný nmap scan na zistených portoch
echo "[*] Spúšťam detailný nmap scan..."
nmap -sC -sV -p$ports $IP -oN "$OUTPUT_SCAN/detailed_scan.txt"

echo "[+] Hotovo!"
echo "[*] Súbory:"
echo "    - $OUTPUT_SCAN/fullport_scan.txt  (výsledok full-port scanu)"
echo "    - $OUTPUT_SCAN/open_ports.txt     (len zoznam portov)"
echo "    - $OUTPUT_SCAN/detailed_scan.txt  (detailný scan s verziami)"
