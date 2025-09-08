#čítanie exportu CSV z Logic 2
#SPI komunikácia

import pandas as pd

# Načítanie CSV súboru z logického analyzátora
df = pd.read_csv("digital.csv")

# Mapovanie kanálov podľa CSV
# Predpoklad: Channel 0 = MOSI, Channel 1 = MISO, Channel 2 = CS, Channel 3 = SCK
MOSI = df["Channel 0"].values  # Data posielané z mastera
MISO = df["Channel 1"].values  # Data posielané z periférie (tu zatiaľ nepoužívame)
CS   = df["Channel 2"].values  # Chip Select, aktívny low
SCK  = df["Channel 3"].values  # Hodinový signál SPI

# Funkcia na dekódovanie SPI dát z MOSI
def spi_decode(MOSI, MISO, SCK, CS):
    prev_clk = 0          # Predchádzajúci stav hodinového signálu (pre detekciu nábežnej hrany)
    current_byte = 0      # Premenná na skladanie jednotlivých bitov do bytu
    bit_count = 0         # Počet bitov nazbieraných do aktuálneho bytu
    byte_list = []        # Výsledný zoznam dekódovaných bytov

    # Prejdenie všetkých vzoriek súčasne (CS, SCK, MOSI)
    for cs, clk, mosi in zip(CS, SCK, MOSI):
        if cs == 0:  # Ak je CS aktívne (low), prebieha komunikácia
            if prev_clk == 0 and clk == 1:  # Detekcia nábežnej hrany hodinového signálu
                # Posuň predchádzajúce bity doľava a pridaj nový bit
                current_byte = (current_byte << 1) | mosi
                bit_count += 1

                # Ak máme 8 bitov, uložíme byte a resetujeme premenné
                if bit_count == 8:
                    byte_list.append(current_byte)
                    current_byte = 0
                    bit_count = 0
        else:
            # Ak CS nie je aktívne (high), resetujeme aktuálny byte a počet bitov
            # To zabráni nesprávnej akumulácii dát mimo rámca SPI prenosu
            current_byte = 0
            bit_count = 0

        # Aktualizujeme predchádzajúci stav hodín
        prev_clk = clk

    # Vrátime zoznam všetkých dekódovaných bytov
    return byte_list

# Zavolanie funkcie a získanie dekódovaných bytov
bytes_out = spi_decode(MOSI, MISO, SCK, CS)

# Konverzia bajtov na ASCII
# Znaky mimo čitateľného rozsahu (32–126) nahradíme bodkou '.'
ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in bytes_out)

# Výpis výsledkov
print("Dekódované byty:", bytes_out)
print("ASCII reťazec:", ascii_str)

