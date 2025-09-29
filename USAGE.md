# Návod k použití PM3 Analysis Framework

## Rychlý start

### 1. Základní analýza neznámé karty
```bash
# Spuštění základního analyzátoru
python3 basic_analyzer.py

# Nebo s vlastní výstupní složkou
python3 basic_analyzer.py --output-dir moje_dumpy/
```

### 2. Použití existujících skriptů
```bash
# Rychlá analýza (bash script)
./scripts/quick_analyze.sh

# AI-asistovaná analýza
python3 scripts/ai_analyzer.py --detect --analyze --report

# Interaktivní menu
python3 scripts/interactive_analyzer.py
```

## Protokol analýzy podle typu karty

### MIFARE Classic
```bash
# Automatická analýza
pm3 -c "hf mf autopwn"

# Manuální kroky:
pm3 -c "hf 14a info"        # Základní info
pm3 -c "hf mf info"         # MIFARE info
pm3 -c "hf mf darkside"     # Darkside útok
pm3 -c "hf mf dump"         # Dump po prolomení
```

### MIFARE Ultralight
```bash
# Pokus o dump
pm3 -c "hf mfu dump"

# Pokud je chráněno heslem:
pm3 -c "hf mfu pwdgen -r"           # Generování hesel
pm3 -c "hf mfu dump -k FFFFFFFF"   # Test výchozího hesla
```

### DESFire
```bash
pm3 -c "hf mfdes info"      # Základní informace
pm3 -c "hf mfdes enum"      # Enumerace aplikací
```

### EM410x (LF)
```bash
pm3 -c "lf em 410x_read"    # Čtení ID
pm3 -c "lf em 410x_clone"   # Klonování na T55xx
```

## Struktura výstupních souborů

Po analýze se vytvoří soubory v složce `dump/`:

```
dump/
├── mifare_classic_04A1B2C3_20241228_143022_cracked_metadata.json
├── mifare_classic_04A1B2C3_20241228_143022_cracked_analysis.txt
├── mifare_ultralight_04ECA16A_20241228_143045_dumped_metadata.json
└── mifare_ultralight_04ECA16A_20241228_143045_dumped_analysis.txt
```

### Metadata soubor (JSON)
Obsahuje strukturované informace o kartě a analýze:
- UID karty
- Typ karty
- Čas analýzy
- Použité útoky
- Nalezené klíče
- Status analýzy

### Analysis soubor (TXT)
Obsahuje kompletní výstup PM3 příkazů pro pozdější referenci.

## Magic karty

### Detekce magic karet
```bash
# Test Gen1A
pm3 -c "hf mf cgetblk 0"

# Test Gen2
pm3 -c "hf mf wrbl 0 A FFFFFFFFFFFF 04A1B2C3D4E5F6"

# Test Gen3
pm3 -c "hf 14a raw -a -p -c 90F0CCCC10"

# Test UFUID
pm3 -c "hf 14a raw -a -p -c 4000"
```

### Klonování na magic kartu
```bash
# Na Gen1A
pm3 -c "hf mf cload original_dump.bin"

# Na Gen2
pm3 -c "hf mf restore 1 original_dump.bin"

# MIFARE Ultralight
pm3 -c "hf mfu restore original_dump.json"
```

## Troubleshooting

### Karta se nečte
1. Zkontrolujte vzdálenost (1-3cm od antény)
2. Zkuste různé orientace karty
3. Zkontrolujte anténu: `pm3 -c "hw tune"`

### PM3 nereaguje
1. Zkontrolujte připojení: `pm3 -c "hw status"`
2. Restartujte PM3: odpojte a znovu připojte USB
3. Zkontrolujte firmware: `pm3 -c "hw version"`

### Útoky selhávají
1. Zkuste kombinovaný útok: `pm3 -c "hf mf autopwn"`
2. Použijte dictionary útok: `pm3 -c "hf mf chk *1 ? d"`
3. Pro MIFARE Ultralight zkuste tearoff: `pm3 -c "hf mfu otptear"`

## Bezpečnostní upozornění

⚠️ **DŮLEŽITÉ:**
- Analyzujte pouze karty, které vlastníte
- Respektujte místní zákony
- Nepoužívejte pro nelegální aktivity
- Dokumentujte všechny aktivity

## Pokročilé použití

### Batch analýza více karet
```bash
# Vytvoření skriptu pro více karet
for i in {1..10}; do
    echo "Umístěte kartu $i a stiskněte Enter..."
    read
    python3 basic_analyzer.py --output-dir batch_results/card_$i/
done
```

### Integrace s AI
```bash
# Použití AI analyzátoru pro inteligentní rozhodování
python3 scripts/ai_analyzer.py --card-type auto --profile aggressive
```

### Export do různých formátů
```bash
# Export do různých formátů
pm3 -c "hf mf dump -f dump.bin"     # Binární
pm3 -c "hf mf dump -f dump.eml"     # Email formát
pm3 -c "hf mf dump -f dump.json"    # JSON formát
```

## Další zdroje

- [PM3 Master Guide](pm3_master_guide.md) - Kompletní návod
- [Quick Start Guide](quick_start_guide.md) - Rychlý start
- [Advanced Attacks](advanced_attacks.md) - Pokročilé útoky
- [Magic Cards DB](magic_cards_db.md) - Databáze magic karet

## Podpora

Pro podporu a dotazy:
1. Zkontrolujte dokumentaci v repository
2. Vytvořte Issue na GitHubu
3. Konzultujte PM3 komunitu
