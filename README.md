# PM3 Advanced Analysis Framework

Kompletní framework pro profesionální analýzu RFID/NFC karet pomocí Proxmark3 s AI asistencí přes Claude/Augment.

## 📋 Přehled

Tento projekt poskytuje strukturovaný přístup k analýze RFID/NFC karet s důrazem na:
- **Rychlost a efektivitu** - Automatizované detekce a útoky
- **Profesionalitu** - Strukturované výstupy a dokumentace  
- **AI asistenci** - Inteligentní rozhodování pomocí Claude AI
- **Bezpečnost** - Etické a legální postupy

## 🗂️ Struktura Projektu

```
PM3/
├── 📄 pm3_master_guide.md          # Hlavní návod pro AI a automatizaci
├── 📄 advanced_attacks.md          # Pokročilé techniky útoků
├── 📄 magic_cards_db.md           # Databáze magic karet
├── 📄 legal_guidelines.md         # Právní a etické pokyny
├── 📁 carddata/                   # Existující data karet
├── 📁 dictionaries/               # Slovníky klíčů a hesel
│   ├── 📄 README.md
│   ├── 📄 mfkeys.dic
│   └── 📄 mfu_passwords.dic
├── 📄 basic.md                    # Základní návod (původní)
└── 📄 analyze.md                  # Pokročilý návod (původní)
```

## 🚀 Rychlý Start

### 1. Základní Analýza Karty
```bash
# Automatická detekce
pm3 -c "auto"

# Rychlá analýza podle typu
pm3 -c "hf mf autopwn"        # MIFARE Classic
pm3 -c "hf mfu dump"          # MIFARE Ultralight
pm3 -c "hf mfdes info"        # DESFire
```

### 2. Magic Card Detekce
```bash
# Univerzální magic detekce
pm3 -c "hf 14a info"

# Test specifických typů
pm3 -c "hf mf cgetblk 0"                    # Gen1A
pm3 -c "hf 14a raw -a -p -c 90F0CCCC10"    # Gen3
pm3 -c "hf 14a raw -a -p -c 4000"          # UFUID
```

### 3. Klonování
```bash
# Na Gen1A magic kartu
pm3 -c "hf mf cload original_dump.bin"

# Na Gen2 magic kartu  
pm3 -c "hf mf restore 1 original_dump.bin"

# MIFARE Ultralight
pm3 -c "hf mfu restore original_dump.json"
```

## 📖 Dokumentace

### Hlavní Dokumenty

| Dokument | Popis | Použití |
|----------|-------|---------|
| [pm3_master_guide.md](pm3_master_guide.md) | **Hlavní návod** - Kompletní postupy pro AI | Automatizace, AI asistence |
| [advanced_attacks.md](advanced_attacks.md) | Pokročilé techniky útoků | Specializované útoky |
| [magic_cards_db.md](magic_cards_db.md) | Databáze magic karet | Identifikace a práce s magic kartami |
| [legal_guidelines.md](legal_guidelines.md) | Právní a etické pokyny | Bezpečné a legální testování |

### Specializované Sekce

#### 🎯 Typy Útoků podle Karet

**MIFARE Classic:**
- Darkside (slabý PRNG)
- Nested (známý klíč) 
- Hardnested (silný PRNG)
- Dictionary attack
- Autopwn (kombinovaný)

**MIFARE Ultralight:**
- Password generation (UID-based)
- Dictionary attack
- Tear-off attacks
- Default password testing

**DESFire:**
- Default key testing
- Downgrade attacks
- Application enumeration

**LF Karty:**
- EM4x05 tear-off unlock
- T55xx password recovery
- Brute force attacks

#### 🎴 Magic Karty

| Typ | UID Změna | Block 0 Zápis | Detekce | Příkazy |
|-----|-----------|---------------|---------|---------|
| Gen1A | ✅ | ✅ | Vysoká | Chinese Magic |
| Gen2 | ✅ | ✅ | Střední | Direct Write |
| Gen3 | ✅ | ✅ | Nízká | APDU |
| UFUID | ✅ | ❌ | Střední | Special Commands |

## 🤖 AI Integrace

### Claude/Augment Workflow
```python
# Příklad AI-asistované analýzy
class AIAnalyzer:
    def intelligent_card_analysis(self, card_data):
        # 1. Pošle data do Claude přes Augment
        # 2. Získá AI doporučení pro útoky
        # 3. Automaticky spustí doporučené útoky
        # 4. Interpretuje výsledky pomocí AI
        # 5. Generuje profesionální report
```

### AI Decision Trees
```
Neznámá karta
├── HF Card?
│   ├── MIFARE Classic? → PRNG Test → Darkside/Hardnested
│   ├── MIFARE Ultralight? → Password Gen → Dictionary
│   └── DESFire? → Default Keys → Enumeration
└── LF Card?
    ├── EM410x? → Read ID → Clone
    └── T55xx? → Detect Config → Unlock
```

## 🛠️ Automatizační Skripty

### Rychlá Analýza
```bash
#!/bin/bash
# quick_analyze.sh
pm3 -c "hw status; hw tune"     # Hardware check
pm3 -c "auto"                   # Card detection
# Spustí relevantní útoky podle typu karty
```

### Batch Processing
```python
# batch_process.py
# Zpracování více karet najednou
# Paralelní spouštění útoků
# Agregace výsledků
```

### Magic Card Auto-Detection
```bash
# magic_detector.sh
# Automatická detekce všech typů magic karet
# Klasifikace podle schopností
# Doporučení příkazů
```

## 📊 Data Management

### Pojmenování Souborů
```
Format: [type]_[uid]_[date]_[status].[ext]

Příklady:
- mifare_classic_04A1B2C3_20241228_cracked.bin
- mifare_ultralight_04ECA16A7B1390_20241228_dumped.json
- em410x_1234567890_20241228_cloned.txt
```

### Metadata Tracking
```json
{
  "card_info": {
    "uid": "04ECA16A7B1390",
    "type": "MIFARE Ultralight EV1",
    "detected_at": "2024-12-28T10:30:00Z"
  },
  "analysis": {
    "attacks_attempted": ["dictionary", "password_gen"],
    "successful_attacks": ["password_gen"],
    "keys_found": ["FFFFFFFF"]
  }
}
```

## 🔐 Bezpečnost a Legalita

### ⚠️ DŮLEŽITÉ UPOZORNĚNÍ
- **Pouze autorizované testování** - Nikdy netestujte cizí systémy bez povolení
- **Respektujte místní zákony** - Zákony se liší podle jurisdikce
- **Etické použití** - Používejte pro zlepšení bezpečnosti, ne pro škodu
- **Dokumentace** - Zaznamenávejte všechny aktivity

### Legální Použití
✅ **POVOLENO:**
- Testování vlastních karet
- Autorizované penetrační testování
- Akademický výzkum
- Vzdělávací účely

❌ **ZAKÁZÁNO:**
- Testování cizích karet bez povolení
- Neoprávněný přístup k systémům
- Klonování karet pro podvod
- Porušování bezpečnostních opatření

## 🎓 Vzdělávací Zdroje

### Doporučené Čtení
- [Proxmark3 RRG GitHub](https://github.com/RfidResearchGroup/proxmark3)
- [MIFARE dokumentace NXP](https://www.nxp.com/products/rfid-nfc)
- [RFID Security Research](https://blog.quarkslab.com/)

### Komunita
- [Proxmark3 Forum](https://forum.proxmark.org/)
- [RFID Research Group](https://github.com/RfidResearchGroup)
- [Dangerous Things Forum](https://forum.dangerousthings.com/)

## 🔧 Troubleshooting

### Časté Problémy

#### Karta se nečte
```bash
# Řešení:
hw tune                    # Kontrola antény
# Upravit vzdálenost (1-3cm)
# Zkusit různé orientace
```

#### Útoky selhávají
```bash
# Řešení:
hf mf autopwn             # Zkusit kombinovaný útok
hf mf chk *1 ? d          # Dictionary attack
# Zkontrolovat timing parametry
```

#### Magic karty nefungují
```bash
# Řešení:
hf 14a info               # Ověřit magic schopnosti
# Zkusit různé magic příkazy
# Zkontrolovat pozici karty
```

## 📈 Budoucí Rozšíření

### Plánované Funkce
- [ ] Python CLI nástroj
- [ ] VS Code rozšíření
- [ ] Webové rozhraní
- [ ] Machine Learning klasifikace
- [ ] Automatické reporty
- [ ] Cloud integrace

### Přispívání
Příspěvky jsou vítány! Prosím:
1. Forkněte repository
2. Vytvořte feature branch
3. Commitněte změny
4. Vytvořte Pull Request

## 📄 Licence

Tento projekt je určen výhradně pro:
- Vzdělávací účely
- Bezpečnostní výzkum  
- Autorizované testování
- Akademické použití

**Nepoužívejte pro nelegální aktivity!**

---

## 🤝 Podpora

Pro podporu a dotazy:
- Vytvořte Issue na GitHubu
- Konzultujte dokumentaci
- Kontaktujte bezpečnostní komunitu

**Pamatujte: Cílem je zlepšit bezpečnost, ne způsobit škodu!**
