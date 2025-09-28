# Proxmark3 - Základní návod

## Úvod
Proxmark3 je výkonný nástroj pro analýzu a práci s RFID/NFC kartami a tagy. Tento návod pokrývá základní operace a postupy.

## Připojení a spuštění

### Připojení zařízení
1. Připojte Proxmark3 k počítači pomocí USB kabelu
2. Zkontrolujte, že je zařízení rozpoznáno:
   ```bash
   lsusb | grep -i proxmark
   ```

### Spuštění klienta
```bash
./proxmark3 /dev/ttyACM0
```
nebo
```bash
./proxmark3 -p /dev/ttyACM0
```

## Základní příkazy

### Informace o zařízení
```
hw version      # Verze firmware a hardware
hw status       # Stav zařízení
hw tune         # Ladění antény
```

### Detekce karet
```
hf search       # Automatická detekce HF karet
lf search       # Automatická detekce LF karet
```

## Práce s HF kartami (13.56 MHz)

### ISO14443A karty (Mifare)
```
hf 14a info     # Základní informace o kartě
hf 14a reader   # Čtení karty
hf 14a dump     # Dump celé karty
```

### Mifare Classic
```
hf mf chk *1 ?  # Kontrola výchozích klíčů
hf mf dump 1    # Dump karty s klíči
hf mf restore 1 # Obnovení karty z dumpu
```

### Mifare Ultralight
```
hf mfu info     # Informace o kartě
hf mfu dump     # Dump karty
hf mfu wrbl 4 00112233  # Zápis do bloku 4
```

## Práce s LF kartami (125 kHz)

### EM410x karty
```
lf em 410x_read    # Čtení EM410x karty
lf em 410x_sim 1234567890  # Simulace EM410x s ID
```

### HID Prox
```
lf hid read        # Čtení HID karty
lf hid sim 2006ec0c86  # Simulace HID karty
```

### T55xx karty
```
lf t55xx detect    # Detekce T55xx karty
lf t55xx info      # Informace o kartě
lf t55xx dump      # Dump karty
```

## Simulace a klonování

### Simulace HF karet
```
hf 14a sim t 1 u 12345678  # Simulace Mifare Classic
hf mf sim u 12345678       # Simulace s UID
```

### Simulace LF karet
```
lf em 410x_sim 1234567890  # Simulace EM410x
lf hid sim 2006ec0c86      # Simulace HID
```

### Klonování
```
# 1. Přečtěte originální kartu
hf 14a info

# 2. Uložte data
hf mf dump 1

# 3. Zapište na prázdnou kartu
hf mf restore 1
```

## Užitečné tipy

### Kontrola antény
```
hw tune
```
- Červená LED: LF anténa aktivní
- Zelená LED: HF anténa aktivní
- Optimální hodnoty: LF ~95kHz, HF ~13.56MHz

### Uložení dat
```
hf mf dump 1 dumpfile    # Uložení do souboru
hf mf restore 1 dumpfile # Obnovení ze souboru
```

### Práce se soubory
- Soubory se ukládají do složky `dumps/`
- Formát: `.bin`, `.eml`, `.json`

## Časté problémy

### Zařízení se nepřipojí
1. Zkontrolujte USB kabel
2. Zkontrolujte oprávnění: `sudo usermod -a -G dialout $USER`
3. Restartujte systém

### Karta se nečte
1. Zkontrolujte vzdálenost (1-3 cm)
2. Zkontrolujte orientaci karty
3. Použijte `hw tune` pro kontrolu antény

### Chyby při zápisu
1. Zkontrolujte, že karta je zapisovatelná
2. Ověřte správné klíče
3. Zkontrolujte ochranu bloků

## Bezpečnostní upozornění

⚠️ **DŮLEŽITÉ:**
- Používejte pouze na vlastní karty nebo s povolením
- Respektujte místní zákony
- Nepoužívajte pro nelegální aktivity
- Proxmark3 je nástroj pro výzkum a testování

## Další zdroje

- Oficiální dokumentace: https://github.com/RfidResearchGroup/proxmark3
- Wiki: https://github.com/RfidResearchGroup/proxmark3/wiki
- Fórum: https://forum.dangerousthings.com/

## Základní workflow

1. **Připojení**: `./proxmark3 /dev/ttyACM0`
2. **Detekce**: `hf search` nebo `lf search`
3. **Analýza**: `hf 14a info` nebo příslušný příkaz
4. **Akce**: čtení, zápis, simulace podle potřeby
5. **Uložení**: dump dat pro pozdější použití
