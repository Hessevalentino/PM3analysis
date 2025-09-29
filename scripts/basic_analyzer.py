#!/usr/bin/env python3
"""
PM3 Basic Analyzer - Základní analýza neznámých karet podle protokolu
Vytvoří dump odemčených karet do složky dump/
"""

import subprocess
import json
import os
import sys
from datetime import datetime
import argparse

class PM3BasicAnalyzer:
    def __init__(self, output_dir="dump"):
        self.output_dir = output_dir
        self.results = {}
        self.card_info = {}
        
        # Vytvoření výstupní složky
        os.makedirs(self.output_dir, exist_ok=True)
        
    def run_pm3_command(self, command, timeout=60):
        """Spustí PM3 příkaz a vrátí výstup"""
        try:
            print(f"🔧 Spouštím: pm3 -c \"{command}\"")
            result = subprocess.run(['pm3', '-c', command], 
                                  capture_output=True, text=True, timeout=timeout)
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "TIMEOUT", "", -1
        except FileNotFoundError:
            print("❌ CHYBA: PM3 není nainstalováno nebo není v PATH")
            return "PM3_NOT_FOUND", "", -1
        except Exception as e:
            return f"ERROR: {str(e)}", "", -1
    
    def check_hardware(self):
        """Kontrola PM3 hardware"""
        print("🔍 Kontrola PM3 hardware...")
        
        stdout, stderr, returncode = self.run_pm3_command("hw status")
        if returncode != 0:
            print("❌ PM3 hardware není připraven")
            return False
            
        if "OK" in stdout:
            print("✅ PM3 hardware je připraven")
            return True
        else:
            print("⚠️ PM3 hardware možná není správně připojen")
            return False
    
    def detect_card(self):
        """Automatická detekce karty podle protokolu"""
        print("\n🔍 Detekce karty...")
        
        # Krok 1: Automatická detekce
        stdout, stderr, returncode = self.run_pm3_command("auto")
        print(f"Auto detekce výsledek:\n{stdout}")
        
        if "MIFARE Classic" in stdout:
            return self.analyze_mifare_classic(stdout)
        elif "MIFARE Ultralight" in stdout:
            return self.analyze_mifare_ultralight(stdout)
        elif "DESFire" in stdout:
            return self.analyze_desfire(stdout)
        elif "EM410x" in stdout:
            return self.analyze_em410x(stdout)
        else:
            # Krok 2: Manuální HF detekce
            print("🔍 Zkouším manuální HF detekci...")
            stdout_hf, _, _ = self.run_pm3_command("hf search")
            if stdout_hf and "found" in stdout_hf.lower():
                return self.analyze_hf_card(stdout_hf)
            
            # Krok 3: Manuální LF detekce
            print("🔍 Zkouším manuální LF detekci...")
            stdout_lf, _, _ = self.run_pm3_command("lf search")
            if stdout_lf and "found" in stdout_lf.lower():
                return self.analyze_lf_card(stdout_lf)
            
            print("❌ Karta nebyla detekována")
            return None
    
    def analyze_mifare_classic(self, detection_output):
        """Analýza MIFARE Classic karty podle protokolu"""
        print("🎯 MIFARE Classic detekována - spouštím specializovanou analýzu...")
        
        self.card_info["type"] = "MIFARE Classic"
        
        # Základní informace
        print("  📋 Získávám základní informace...")
        info_stdout, _, _ = self.run_pm3_command("hf mf info")
        
        # Extrakce UID
        uid = self.extract_uid(info_stdout)
        self.card_info["uid"] = uid
        
        # PRNG test
        print("  🎲 Testujem PRNG...")
        prng_stdout, _, _ = self.run_pm3_command("hf mf hardnested t 1 000000000000")
        
        # Autopwn útok
        print("  ⚡ Spouštím autopwn útok...")
        autopwn_stdout, _, _ = self.run_pm3_command("hf mf autopwn", timeout=300)
        
        # Kontrola úspěchu
        if "found" in autopwn_stdout.lower() and "key" in autopwn_stdout.lower():
            print("  ✅ Klíče nalezeny!")
            self.card_info["status"] = "cracked"
            
            # Dump karty
            print("  💾 Vytvářím dump...")
            dump_stdout, _, _ = self.run_pm3_command("hf mf dump")
            
            return self.save_results("mifare_classic", {
                "info": info_stdout,
                "prng_test": prng_stdout,
                "autopwn": autopwn_stdout,
                "dump": dump_stdout
            })
        else:
            print("  ❌ Nepodařilo se prolomit kartu")
            self.card_info["status"] = "failed"
            return None
    
    def analyze_mifare_ultralight(self, detection_output):
        """Analýza MIFARE Ultralight karty podle protokolu"""
        print("🎯 MIFARE Ultralight detekována - spouštím specializovanou analýzu...")
        
        self.card_info["type"] = "MIFARE Ultralight"
        
        # Základní informace
        print("  📋 Získávám základní informace...")
        info_stdout, _, _ = self.run_pm3_command("hf mfu info")
        
        # Extrakce UID
        uid = self.extract_uid(info_stdout)
        self.card_info["uid"] = uid
        
        # Pokus o dump
        print("  💾 Pokus o dump...")
        dump_stdout, _, _ = self.run_pm3_command("hf mfu dump")
        
        # Kontrola úspěchu dumpu - hledáme indikátory úspěšného čtení
        if ("mfu dump file information" in dump_stdout.lower() or
            "reading tag memory" in dump_stdout.lower() or
            "block#" in dump_stdout.lower() or
            "version....." in dump_stdout.lower()):
            print("  ✅ Dump úspěšný!")
            self.card_info["status"] = "dumped"

            return self.save_results("mifare_ultralight", {
                "info": info_stdout,
                "dump": dump_stdout
            })
        else:
            print("  🔐 Karta je chráněna heslem, zkouším útoky...")

            # Password generation útok
            print("  🎯 Generuji hesla na základě UID...")
            pwdgen_stdout, _, _ = self.run_pm3_command("hf mfu pwdgen -r")

            # Dictionary útok
            print("  📚 Dictionary útok...")
            dict_stdout, _, _ = self.run_pm3_command("hf mfu dump -k FFFFFFFF")

            # Kontrola úspěchu dictionary útoku
            if ("mfu dump file information" in dict_stdout.lower() or
                "reading tag memory" in dict_stdout.lower() or
                "block#" in dict_stdout.lower()):
                print("  ✅ Dump úspěšný s dictionary útokem!")
                self.card_info["status"] = "cracked"
                return self.save_results("mifare_ultralight", {
                    "info": info_stdout,
                    "pwdgen": pwdgen_stdout,
                    "dump": dict_stdout
                })
            else:
                print("  ❌ Nepodařilo se prolomit kartu")
                self.card_info["status"] = "failed"
                return None
    
    def analyze_desfire(self, detection_output):
        """Analýza DESFire karty"""
        print("🎯 DESFire detekována - základní analýza...")
        
        self.card_info["type"] = "DESFire"
        
        info_stdout, _, _ = self.run_pm3_command("hf mfdes info")
        uid = self.extract_uid(info_stdout)
        self.card_info["uid"] = uid
        self.card_info["status"] = "partial"
        
        return self.save_results("desfire", {"info": info_stdout})
    
    def analyze_em410x(self, detection_output):
        """Analýza EM410x karty"""
        print("🎯 EM410x detekována - čtení ID...")
        
        self.card_info["type"] = "EM410x"
        
        read_stdout, _, _ = self.run_pm3_command("lf em 410x_read")
        uid = self.extract_uid(read_stdout)
        self.card_info["uid"] = uid
        self.card_info["status"] = "dumped"
        
        return self.save_results("em410x", {"read": read_stdout})
    
    def analyze_hf_card(self, detection_output):
        """Analýza neznámé HF karty"""
        print("🎯 Neznámá HF karta - základní analýza...")
        
        info_stdout, _, _ = self.run_pm3_command("hf 14a info")
        self.card_info["type"] = "Unknown HF"
        self.card_info["status"] = "partial"
        
        return self.save_results("unknown_hf", {"info": info_stdout})
    
    def analyze_lf_card(self, detection_output):
        """Analýza neznámé LF karty"""
        print("🎯 Neznámá LF karta - základní analýza...")
        
        self.card_info["type"] = "Unknown LF"
        self.card_info["status"] = "partial"
        
        return self.save_results("unknown_lf", {"detection": detection_output})
    
    def extract_uid(self, output):
        """Extrakce UID z výstupu PM3"""
        lines = output.split('\n')
        for line in lines:
            if 'UID' in line or 'uid' in line:
                # Hledání hex hodnot
                parts = line.split()
                for part in parts:
                    if len(part) >= 8 and all(c in '0123456789ABCDEFabcdef' for c in part):
                        return part.upper()
        return "UNKNOWN"
    
    def save_results(self, card_type, analysis_data):
        """Uložení výsledků podle protokolu"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        uid = self.card_info.get("uid", "UNKNOWN")
        status = self.card_info.get("status", "unknown")
        
        # Název souboru podle protokolu
        base_filename = f"{card_type}_{uid}_{timestamp}_{status}"
        
        # Uložení JSON metadata
        metadata = {
            "card_info": {
                "uid": uid,
                "type": self.card_info.get("type", "Unknown"),
                "detected_at": datetime.now().isoformat(),
                "analyzer": "PM3 Basic Analyzer v1.0"
            },
            "analysis": analysis_data,
            "files": {
                "metadata_file": f"{base_filename}_metadata.json",
                "analysis_file": f"{base_filename}_analysis.txt"
            }
        }
        
        # Uložení souborů
        metadata_path = os.path.join(self.output_dir, f"{base_filename}_metadata.json")
        analysis_path = os.path.join(self.output_dir, f"{base_filename}_analysis.txt")
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        with open(analysis_path, 'w', encoding='utf-8') as f:
            f.write(f"ANALÝZA KARTY - {self.card_info.get('type', 'Unknown')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Datum: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
            f.write(f"UID: {uid}\n")
            f.write(f"Status: {status}\n\n")
            
            for step, output in analysis_data.items():
                f.write(f"{step.upper()}:\n")
                f.write("-" * 30 + "\n")
                f.write(output)
                f.write("\n\n")
        
        print(f"💾 Výsledky uloženy:")
        print(f"  📄 Metadata: {metadata_path}")
        print(f"  📄 Analýza: {analysis_path}")
        
        return metadata_path

def main():
    parser = argparse.ArgumentParser(description='PM3 Basic Analyzer - Analýza neznámých karet')
    parser.add_argument('--output-dir', default='dump', help='Výstupní složka pro dump soubory')
    parser.add_argument('--no-hardware-check', action='store_true', help='Přeskočit kontrolu hardware')
    
    args = parser.parse_args()
    
    print("🚀 PM3 Basic Analyzer - Analýza neznámých karet")
    print("=" * 50)
    
    analyzer = PM3BasicAnalyzer(args.output_dir)
    
    # Kontrola hardware
    if not args.no_hardware_check:
        if not analyzer.check_hardware():
            print("❌ Ukončuji kvůli problémům s hardware")
            sys.exit(1)
    
    # Detekce a analýza karty
    result = analyzer.detect_card()
    
    if result:
        print(f"\n✅ Analýza dokončena! Výsledky uloženy v: {result}")
    else:
        print("\n❌ Analýza se nezdařila")
        sys.exit(1)

if __name__ == "__main__":
    main()
