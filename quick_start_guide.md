# Quick Start Guide - Spuštění PM3 Analýzy

## 🚀 Způsoby Spuštění Analýzy

### 1. Rychlá Analýza (30 sekund)
```bash
# Jednoduché spuštění pro rychlou identifikaci
./quick_analyze.sh

# Nebo přímo PM3 příkazy
pm3 -c "auto"                    # Automatická detekce
pm3 -c "hf mf autopwn"          # MIFARE Classic autopwn
pm3 -c "hf mfu dump"            # MIFARE Ultralight dump
```

### 2. AI-Asistovaná Analýza
```bash
# Spuštění s AI asistencí (doporučeno)
python3 ai_analyzer.py --card-detect --auto-attack

# Nebo s konkrétními parametry
python3 ai_analyzer.py --card-type mifare_classic --profile pentest
```

### 3. Kompletní Analýza
```bash
# Úplná analýza se všemi útoky
./comprehensive_analysis.sh --full --report

# Batch analýza více karet
./batch_analyzer.sh --count 10 --output batch_results/
```

---

## 📋 Workflow Spuštění

### Krok 1: Příprava Prostředí
```bash
# Kontrola PM3 připojení
pm3 -c "hw status"
pm3 -c "hw tune"

# Kontrola, že všechny nástroje fungují
./check_environment.sh
```

### Krok 2: Umístění Karty
```
1. Umístěte kartu na PM3 anténu (1-3cm vzdálenost)
2. Ujistěte se, že LED indikátory svítí
3. Karta by měla být stabilně na místě
```

### Krok 3: Spuštění Analýzy
```bash
# Základní workflow
./pm3_analyzer.py --detect --analyze --report

# Pokročilý workflow s AI
./pm3_analyzer.py --ai-assist --full-analysis --magic-detect
```

---

## 🎯 Konkrétní Příklady Použití

### Scénář 1: Neznámá Karta
```bash
# Spuštění univerzální analýzy
python3 pm3_analyzer.py --unknown-card

# Co se stane:
# 1. Automatická detekce typu karty
# 2. AI doporučí optimální útoky
# 3. Spustí sekvenci útoků
# 4. Vygeneruje report
# 5. Uloží výsledky
```

### Scénář 2: MIFARE Classic Karta
```bash
# Specifická analýza MIFARE Classic
python3 pm3_analyzer.py --card-type mifare_classic --profile aggressive

# Workflow:
# 1. hf 14a info
# 2. hf mf info  
# 3. PRNG test
# 4. Darkside/Hardnested podle PRNG
# 5. Dictionary attack
# 6. Full dump
# 7. Verification
```

### Scénář 3: Magic Card Detekce
```bash
# Detekce a klasifikace magic karty
python3 pm3_analyzer.py --magic-detect --classify

# Workflow:
# 1. Test Gen1A (cgetblk)
# 2. Test Gen2 (direct write)
# 3. Test Gen3 (APDU)
# 4. Test UFUID
# 5. Klasifikace typu
# 6. Doporučení příkazů
```

### Scénář 4: Klonování
```bash
# Kompletní klonování workflow
python3 pm3_analyzer.py --clone-workflow

# Kroky:
# 1. Analýza source karty
# 2. Detekce target karty (magic)
# 3. Výběr klonování strategie
# 4. Provedení klonování
# 5. Verifikace klonu
```

---

## 🔧 Konfigurační Soubory

### config/settings.yaml
```yaml
# Základní nastavení
pm3_device: "/dev/ttyACM0"
timeout: 60
debug_level: 1

# AI nastavení
ai_enabled: true
ai_model: "claude-3"
ai_temperature: 0.3

# Profily útoků
profiles:
  quick:
    timeout: 30
    attacks: ["dictionary", "default_keys"]
  
  standard:
    timeout: 120
    attacks: ["dictionary", "darkside", "nested"]
  
  aggressive:
    timeout: 300
    attacks: ["all_applicable"]
```

### config/attack_profiles.yaml
```yaml
# Profily pro různé typy karet
mifare_classic:
  detection_commands:
    - "hf 14a info"
    - "hf mf info"
  
  attack_sequence:
    - name: "dictionary"
      command: "hf mf chk *1 ? d"
      timeout: 60
    
    - name: "darkside"
      command: "hf mf darkside"
      timeout: 120
      condition: "weak_prng"
    
    - name: "hardnested"
      command: "hf mf hardnested 0 A FFFFFFFFFFFF 4 A"
      timeout: 300
      condition: "strong_prng"

mifare_ultralight:
  detection_commands:
    - "hf mfu info"
  
  attack_sequence:
    - name: "default_passwords"
      passwords: ["FFFFFFFF", "00000000"]
    
    - name: "uid_based_passwords"
      command: "hf mfu pwdgen -r"
    
    - name: "tearoff"
      command: "hf mfu otptear"
```

---

## 🖥️ Praktické Skripty

### quick_analyze.sh
```bash
#!/bin/bash
# Rychlá analýza karty

echo "=== PM3 Quick Analysis ==="
echo "Date: $(date)"

# Hardware check
echo "Checking hardware..."
if ! pm3 -c "hw status" | grep -q "OK"; then
    echo "ERROR: PM3 hardware not ready"
    exit 1
fi

# Card detection
echo "Detecting card..."
detection_result=$(pm3 -c "auto" 2>&1)
echo "$detection_result"

# Parse results and run appropriate analysis
if echo "$detection_result" | grep -q "MIFARE Classic"; then
    echo "Running MIFARE Classic analysis..."
    pm3 -c "hf mf autopwn"
elif echo "$detection_result" | grep -q "MIFARE Ultralight"; then
    echo "Running MIFARE Ultralight analysis..."
    pm3 -c "hf mfu dump"
elif echo "$detection_result" | grep -q "EM410x"; then
    echo "Running EM410x analysis..."
    pm3 -c "lf em 410x_read"
else
    echo "Unknown card type, running comprehensive detection..."
    pm3 -c "hf search"
    pm3 -c "lf search"
fi

echo "Analysis complete!"
```

### ai_analyzer.py
```python
#!/usr/bin/env python3
# AI-asistovaná analýza karet

import subprocess
import json
import argparse
from datetime import datetime

class PM3AIAnalyzer:
    def __init__(self):
        self.pm3_device = "/dev/ttyACM0"
        self.results = {}
        
    def run_pm3_command(self, command):
        """Spustí PM3 příkaz a vrátí výstup"""
        try:
            result = subprocess.run(['pm3', '-c', command], 
                                  capture_output=True, text=True, timeout=60)
            return result.stdout
        except subprocess.TimeoutExpired:
            return "TIMEOUT"
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def detect_card_type(self):
        """AI-asistovaná detekce typu karty"""
        print("🔍 Detecting card type...")
        
        # Automatická detekce
        auto_result = self.run_pm3_command("auto")
        print(f"Auto detection result:\n{auto_result}")
        
        # AI rozhodování na základě výstupu
        if "MIFARE Classic" in auto_result:
            return self.analyze_mifare_classic()
        elif "MIFARE Ultralight" in auto_result:
            return self.analyze_mifare_ultralight()
        elif "DESFire" in auto_result:
            return self.analyze_desfire()
        elif "EM410x" in auto_result:
            return self.analyze_em410x()
        else:
            return self.fallback_analysis()
    
    def analyze_mifare_classic(self):
        """Analýza MIFARE Classic karty"""
        print("🎯 MIFARE Classic detected - running specialized analysis...")
        
        steps = [
            ("Basic Info", "hf mf info"),
            ("PRNG Test", "hf mf hardnested t 1 000000000000"),
            ("Dictionary Attack", "hf mf chk *1 ? d"),
            ("Autopwn", "hf mf autopwn")
        ]
        
        results = {}
        for step_name, command in steps:
            print(f"  ⚡ {step_name}...")
            output = self.run_pm3_command(command)
            results[step_name] = output
            
            # AI decision points
            if step_name == "PRNG Test" and "weak" in output.lower():
                print("  🎯 Weak PRNG detected - trying Darkside attack...")
                results["Darkside"] = self.run_pm3_command("hf mf darkside")
        
        return results
    
    def analyze_mifare_ultralight(self):
        """Analýza MIFARE Ultralight karty"""
        print("🎯 MIFARE Ultralight detected - running specialized analysis...")
        
        steps = [
            ("Basic Info", "hf mfu info"),
            ("Dump Attempt", "hf mfu dump"),
            ("Password Generation", "hf mfu pwdgen -r"),
            ("Tearoff Attack", "hf mfu otptear")
        ]
        
        results = {}
        for step_name, command in steps:
            print(f"  ⚡ {step_name}...")
            output = self.run_pm3_command(command)
            results[step_name] = output
            
            # Early exit if dump successful
            if step_name == "Dump Attempt" and "dump completed" in output.lower():
                print("  ✅ Dump successful - no further attacks needed")
                break
        
        return results
    
    def generate_report(self, analysis_results):
        """Generuje komprehensivní report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "analysis_results": analysis_results,
            "ai_recommendations": self.get_ai_recommendations(analysis_results),
            "next_steps": self.get_next_steps(analysis_results)
        }
        
        # Uložení reportu
        filename = f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved: {filename}")
        return report

def main():
    parser = argparse.ArgumentParser(description='PM3 AI-Assisted Analyzer')
    parser.add_argument('--detect', action='store_true', help='Detect card type')
    parser.add_argument('--analyze', action='store_true', help='Run analysis')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--card-type', help='Specify card type')
    parser.add_argument('--profile', default='standard', help='Attack profile')
    
    args = parser.parse_args()
    
    analyzer = PM3AIAnalyzer()
    
    if args.detect or not any([args.analyze, args.report]):
        results = analyzer.detect_card_type()
        
        if args.report:
            analyzer.generate_report(results)
    
    print("🎉 Analysis complete!")

if __name__ == "__main__":
    main()
```

---

## 🎮 Interaktivní Režim

### Spuštění interaktivního analyzátoru
```bash
# Interaktivní režim s menu
python3 interactive_analyzer.py

# Menu options:
# 1. Quick card detection
# 2. Full analysis with AI
# 3. Magic card operations
# 4. Cloning workflow
# 5. Batch processing
# 6. Generate report
```

### VS Code Integration
```json
// .vscode/tasks.json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "PM3 Quick Analysis",
            "type": "shell",
            "command": "./quick_analyze.sh",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            }
        },
        {
            "label": "PM3 AI Analysis",
            "type": "shell",
            "command": "python3",
            "args": ["ai_analyzer.py", "--detect", "--analyze", "--report"],
            "group": "build"
        }
    ]
}
```

---

## 📊 Výstup Analýzy

### Konzolový výstup
```
=== PM3 AI Analysis Started ===
🔍 Detecting card type...
🎯 MIFARE Classic 1K detected
  ⚡ Basic Info... ✅
  ⚡ PRNG Test... ✅ (Weak PRNG detected)
  🎯 Weak PRNG detected - trying Darkside attack...
  ⚡ Darkside Attack... ✅ (Keys found!)
  ⚡ Full Dump... ✅
📄 Report saved: analysis_report_20241228_143022.json
🎉 Analysis complete!
```

### JSON Report
```json
{
  "timestamp": "2024-12-28T14:30:22",
  "card_info": {
    "uid": "04A1B2C3",
    "type": "MIFARE Classic 1K",
    "size": "1024 bytes"
  },
  "attacks_performed": [
    {
      "name": "darkside",
      "success": true,
      "keys_found": ["FFFFFFFFFFFF", "A0A1A2A3A4A5"],
      "duration": "45 seconds"
    }
  ],
  "ai_recommendations": [
    "All keys recovered successfully",
    "Card is fully compromised",
    "Consider cloning to magic card for testing"
  ],
  "next_steps": [
    "Clone to Gen2 magic card",
    "Test access control bypass",
    "Document findings for client"
  ]
}
```

Chcete, abych vytvořil některé z těchto skriptů nebo ukázal konkrétní implementaci?
