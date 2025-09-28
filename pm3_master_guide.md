# Proxmark3 Master Guide - AI Automation & Card Operations

> **🆕 NOVÉ SKRIPTY DOSTUPNÉ!** Pro rychlé spuštění použijte:
> - `./scripts/quick_analyze.sh` - Rychlá analýza
> - `python3 scripts/ai_analyzer.py` - AI-asistovaná analýza
> - `python3 scripts/interactive_analyzer.py` - Interaktivní menu
>
> **📖 Kompletní návod:** [quick_start_guide.md](quick_start_guide.md)

## Table of Contents
1. [Hardware Setup & Verification](#hardware-setup--verification)
2. [Card Detection & Analysis](#card-detection--analysis)
3. [Attack Methodologies](#attack-methodologies)
4. [Cloning Operations](#cloning-operations)
5. [Magic Card Operations](#magic-card-operations)
6. [UID Unlock Procedures](#uid-unlock-procedures)
7. [Automation Scripts](#automation-scripts)
8. [AI Decision Trees](#ai-decision-trees)
9. [Data Management](#data-management)
10. [Troubleshooting](#troubleshooting)

---

## Hardware Setup & Verification

### Initial Connection Check
```bash
# Connect to Proxmark3
pm3 -p /dev/ttyACM0

# Verify hardware status
hw status
hw version
hw tune

# Expected output validation:
# - USB connection: OK
# - FPGA image: OK
# - Bootrom version: displayed
# - OS version: displayed
# - LF antenna: ~95kHz (optimal)
# - HF antenna: ~13.56MHz (optimal)
```

### Hardware Diagnostics
```bash
# Complete hardware check sequence
hw status && hw version && hw tune && hw dbg -l 1
```

**AI Decision Point**: If any hardware check fails, refer to [Troubleshooting](#troubleshooting) section.

---

## Card Detection & Analysis

### Universal Detection Protocol
```bash
# Step 1: Automatic detection
auto

# Step 2: Manual HF detection if auto fails
hf search

# Step 3: Manual LF detection if needed
lf search

# Step 4: Specific protocol testing
hf 14a info    # ISO14443-A (MIFARE)
hf 14b info    # ISO14443-B
hf 15 info     # ISO15693
lf em 410x_read # EM410x
lf hid read    # HID Prox
```

### Card Classification Matrix

| Detection Result | Card Type | Next Action |
|-----------------|-----------|-------------|
| `MIFARE Classic` | MIFARE Classic 1K/4K | → [MIFARE Classic Analysis](#mifare-classic-analysis) |
| `MIFARE Ultralight` | MIFARE Ultralight/NTAG | → [MIFARE Ultralight Analysis](#mifare-ultralight-analysis) |
| `MIFARE DESFire` | DESFire EV1/EV2 | → [DESFire Analysis](#desfire-analysis) |
| `iClass` | HID iClass | → [iClass Analysis](#iclass-analysis) |
| `EM410x` | EM4102/EM410x | → [EM410x Analysis](#em410x-analysis) |
| `HID Prox` | HID ProxCard | → [HID Analysis](#hid-analysis) |
| `T55xx` | T5577/ATA5577 | → [T55xx Analysis](#t55xx-analysis) |

---

## Attack Methodologies

### MIFARE Classic Analysis
```bash
# Step 1: Basic information
hf mf info

# Step 2: PRNG detection
hf mf hardnested t 1 000000000000

# Step 3: Attack selection based on PRNG
# If weak PRNG detected:
hf mf darkside

# If strong PRNG or darkside fails:
hf mf hardnested 0 A FFFFFFFFFFFF 4 A

# Step 4: Dictionary attack
hf mf chk *1 ? d

# Step 5: Autopwn (combines multiple attacks)
hf mf autopwn

# Step 6: Full dump after successful key recovery
hf mf dump
```

### MIFARE Ultralight Analysis
```bash
# Step 1: Basic information
hf mfu info

# Step 2: Attempt dump without password
hf mfu dump

# Step 3: If password protected, try common passwords
hf mfu dump -k FFFFFFFF  # Default
hf mfu dump -k 00000000  # Empty

# Step 4: Generate passwords from UID
hf mfu pwdgen -r

# Step 5: Try generated passwords
hf mfu dump -k [generated_password]

# Step 6: Tear-off attack if supported
hf mfu otptear
```

### DESFire Analysis
```bash
# Step 1: Basic information
hf mfdes info

# Step 2: Application enumeration
hf mfdes enum

# Step 3: Try default keys
hf mfdes auth -n 0 -t AES -k 00000000000000000000000000000000
hf mfdes auth -n 0 -t 3DES -k 000000000000000000000000

# Step 4: If successful, dump applications
hf mfdes dump
```

### iClass Analysis
```bash
# Step 1: Basic information
hf iclass info

# Step 2: Dictionary attack
hf iclass chk f iclass_default_keys.dic

# Step 3: Loclass attack
hf iclass loclass

# Step 4: Dump if successful
hf iclass dump
```

### EM410x Analysis
```bash
# Step 1: Read card
lf em 410x_read

# Step 2: Extract ID for cloning
# ID format: [5 bytes hex]
```

### HID Analysis
```bash
# Step 1: Read card
lf hid read

# Step 2: Extract format and ID
# Format: [format_length] [facility_code] [card_number]
```

### T55xx Analysis
```bash
# Step 1: Detection
lf t55xx detect

# Step 2: Information
lf t55xx info

# Step 3: If password protected
lf t55xx bruteforce

# Step 4: Dump configuration
lf t55xx dump
```

---

## Cloning Operations

### MIFARE Classic Cloning

#### To Regular MIFARE Card
```bash
# Prerequisites: Successful key recovery and dump
# Source: original_dump.bin

# Step 1: Verify target card
hf 14a info

# Step 2: Restore dump to target
hf mf restore 1 original_dump.bin

# Step 3: Verify clone
hf mf dump 1 cloned_dump.bin
diff original_dump.bin cloned_dump.bin
```

#### To Magic Card (Gen1A)
```bash
# Step 1: Detect magic card
hf 14a info
# Look for: "Magic capabilities : Gen 1a"

# Step 2: Set UID
hf mf csetuid [original_uid]

# Step 3: Write all blocks
hf mf cload original_dump.bin

# Step 4: Verify
hf mf cgetblk 0  # Check block 0
```

#### To Magic Card (Gen2)
```bash
# Step 1: Detect Gen2 magic card
hf 14a info
# Look for: "Magic capabilities : Gen 2"

# Step 2: Direct block writing
hf mf wrbl 0 A FFFFFFFFFFFF [block0_data]
# Continue for all blocks

# Alternative: Use restore command
hf mf restore 1 original_dump.bin
```

### MIFARE Ultralight Cloning

#### To Regular NTAG
```bash
# Prerequisites: Successful dump
# Source: original_dump.json

# Step 1: Write user data blocks (4-15)
for block in {4..15}; do
    hf mfu wrbl -b $block -d [block_data]
done

# Step 2: Configure if needed
hf mfu wrbl -b 16 -d [config0]
hf mfu wrbl -b 17 -d [config1]
```

#### To Magic NTAG
```bash
# Step 1: Set UID (if magic supports it)
hf mfu setuid [original_uid]

# Step 2: Write all blocks including UID blocks
hf mfu wrbl -b 0 -d [uid_block0]
hf mfu wrbl -b 1 -d [uid_block1]
# Continue for all blocks
```

### LF Card Cloning

#### EM410x Cloning
```bash
# To T55xx card:
# Step 1: Write EM410x data to T55xx
lf em 410x_clone [5_byte_id]

# Step 2: Verify
lf em 410x_read
```

#### HID Cloning
```bash
# To T55xx card:
# Step 1: Clone HID format
lf hid clone [format_length] [facility_code] [card_number]

# Step 2: Verify
lf hid read
```

---

## Magic Card Operations

### Magic Card Detection
```bash
# MIFARE Magic Detection
hf 14a info
# Look for "Magic capabilities" in output

# Test Gen1A magic
hf mf cgetblk 0

# Test Gen2 magic
hf 14a raw -a -p -c 4000

# Test Gen3 magic (APDU)
hf 14a raw -a -p -c 90F0CCCC10
```

### Magic Card Types & Operations

#### Gen1A Magic Cards
```bash
# Characteristics:
# - Responds to Chinese magic commands
# - Can change UID freely
# - Detectable by readers

# Set UID
hf mf csetuid [8_hex_bytes]

# Write block
hf mf csetblk [block_num] [16_hex_bytes]

# Read block
hf mf cgetblk [block_num]

# Load complete dump
hf mf cload [dump_file]

# Save complete dump
hf mf csave [dump_file]
```

#### Gen2 Magic Cards
```bash
# Characteristics:
# - Direct write to any block
# - Can change UID
# - Less detectable

# Write any block (including block 0)
hf mf wrbl [block] A FFFFFFFFFFFF [16_hex_bytes]

# Clone complete card
hf mf restore 1 [dump_file]
```

#### Gen3 Magic Cards
```bash
# Characteristics:
# - APDU commands
# - Most undetectable
# - Requires specific unlock sequence

# Unlock sequence
hf 14a raw -a -p -c 90F0CCCC10

# Write block after unlock
hf mf wrbl [block] A FFFFFFFFFFFF [16_hex_bytes]
```

### UID Unlock Procedures

#### MIFARE Classic UID Unlock
```bash
# For cards with locked UID:

# Method 1: Magic card detection and unlock
hf 14a info
hf mf cgetblk 0  # Test if already magic

# Method 2: Tear-off attack (risky)
hw tearoff --delay 2000
hf mf wrbl 0 A FFFFFFFFFFFF [new_block0]

# Method 3: Specific unlock commands for known cards
hf 14a raw -a -p -c 50[unlock_key]
```

#### MIFARE Ultralight UID Unlock
```bash
# Method 1: Check if already unlocked
hf mfu wrbl -b 0 -d [test_data]

# Method 2: Tear-off unlock
hw tearoff --delay 1500
hf mfu wrbl -b 0 -d [new_uid_block0]

# Method 3: OTP tear-off for specific chips
hf mfu otptear
```

#### LF Card UID Unlock
```bash
# T55xx password unlock
lf t55xx unlock [password]

# EM4x05 tear-off unlock
lf em 4x05_unlock

# Brute force unlock
lf t55xx bruteforce
```

---

## Automation Scripts

### Quick Analysis Script
```bash
#!/bin/bash
# quick_analyze.sh - Automated card analysis

echo "=== PM3 Quick Analysis ==="
echo "Date: $(date)"

# Hardware check
echo "Checking hardware..."
pm3 -c "hw status; hw tune" | tee hardware_check.log

# Card detection
echo "Detecting card..."
pm3 -c "auto" | tee detection.log

# Parse detection results and run appropriate analysis
if grep -q "MIFARE Classic" detection.log; then
    echo "MIFARE Classic detected - running analysis..."
    pm3 -c "hf mf autopwn" | tee mifare_analysis.log
elif grep -q "MIFARE Ultralight" detection.log; then
    echo "MIFARE Ultralight detected - running analysis..."
    pm3 -c "hf mfu info; hf mfu dump" | tee ultralight_analysis.log
fi

echo "Analysis complete. Check log files for results."
```

### Batch Cloning Script
```bash
#!/bin/bash
# batch_clone.sh - Automated cloning operations

SOURCE_DUMP="$1"
TARGET_TYPE="$2"  # regular, gen1a, gen2, gen3

if [ -z "$SOURCE_DUMP" ] || [ -z "$TARGET_TYPE" ]; then
    echo "Usage: $0 <source_dump> <target_type>"
    exit 1
fi

case $TARGET_TYPE in
    "regular")
        pm3 -c "hf mf restore 1 $SOURCE_DUMP"
        ;;
    "gen1a")
        pm3 -c "hf mf cload $SOURCE_DUMP"
        ;;
    "gen2")
        pm3 -c "hf mf restore 1 $SOURCE_DUMP"
        ;;
    *)
        echo "Unknown target type: $TARGET_TYPE"
        exit 1
        ;;
esac
```

---

## AI Decision Trees

### Card Analysis Decision Tree
```
Card Detected
├── HF Card?
│   ├── ISO14443-A?
│   │   ├── MIFARE Classic?
│   │   │   ├── Check PRNG → Weak? → Darkside Attack
│   │   │   │              └── Strong? → Hardnested Attack
│   │   │   └── Dictionary Attack → Autopwn
│   │   ├── MIFARE Ultralight?
│   │   │   ├── Try Default Passwords
│   │   │   ├── Generate UID-based Passwords
│   │   │   └── Tear-off Attack
│   │   └── DESFire?
│   │       ├── Try Default Keys
│   │       └── Application Enumeration
│   └── ISO14443-B/ISO15693?
│       └── Protocol-specific Analysis
└── LF Card?
    ├── EM410x? → Read ID → Clone to T55xx
    ├── HID? → Read Format → Clone to T55xx
    └── T55xx? → Detect Config → Unlock if needed
```

### Cloning Strategy Decision Tree
```
Source Card Analyzed
├── Target Card Type?
│   ├── Regular Card?
│   │   ├── Same Type? → Direct Clone
│   │   └── Different Type? → Convert Format
│   ├── Magic Card?
│   │   ├── Gen1A? → Use Magic Commands
│   │   ├── Gen2? → Direct Block Write
│   │   └── Gen3? → APDU Commands
│   └── UID Locked?
│       ├── Try Unlock Methods
│       └── Use Magic Card Alternative
└── Verify Clone → Compare Dumps
```

---

## Data Management

### File Naming Convention
```
Format: [type]_[uid]_[date]_[status].[ext]

Examples:
- mifare_classic_04A1B2C3_20241228_cracked.bin
- mifare_ultralight_04ECA16A7B1390_20241228_dumped.json
- em410x_1234567890_20241228_cloned.txt
```

### Directory Structure
```
data/
├── dumps/
│   ├── mifare_classic/
│   ├── mifare_ultralight/
│   ├── desfire/
│   ├── iclass/
│   └── lf_cards/
├── logs/
├── reports/
└── dictionaries/
```

### Metadata Tracking
```json
{
  "card_info": {
    "uid": "04ECA16A7B1390",
    "type": "MIFARE Ultralight EV1",
    "size": "48 bytes",
    "detected_at": "2024-12-28T10:30:00Z"
  },
  "analysis": {
    "attacks_attempted": ["dictionary", "password_gen", "tearoff"],
    "successful_attacks": ["password_gen"],
    "keys_found": ["FFFFFFFF"],
    "analysis_duration": "45 seconds"
  },
  "cloning": {
    "cloned_to": "magic_gen2",
    "clone_verified": true,
    "clone_date": "2024-12-28T10:35:00Z"
  }
}
```

---

## Troubleshooting

### Common Issues & Solutions

#### Hardware Connection Issues
```bash
# Issue: Device not found
# Solution:
sudo usermod -a -G dialout $USER
sudo chmod 666 /dev/ttyACM0

# Issue: Permission denied
# Solution:
sudo systemctl stop ModemManager
```

#### Card Reading Issues
```bash
# Issue: No card detected
# Solutions:
1. Check antenna tuning: hw tune
2. Adjust card distance (1-3cm optimal)
3. Try different card orientations
4. Check card for damage

# Issue: Intermittent reading
# Solutions:
1. Clean card surface
2. Check PM3 antenna connections
3. Reduce RF interference
```

#### Attack Failures
```bash
# Issue: Darkside attack fails
# Solutions:
1. Try hardnested: hf mf hardnested 0 A FFFFFFFFFFFF 4 A
2. Use dictionary attack: hf mf chk *1 ? d
3. Try autopwn: hf mf autopwn

# Issue: Password generation fails
# Solutions:
1. Try manual passwords: FFFFFFFF, 00000000
2. Use tear-off attack: hf mfu otptear
3. Check for write protection
```

---

## Related Documents

- [Advanced Attack Techniques](advanced_attacks.md)
- [Magic Card Database](magic_cards_db.md)
- [Dictionary Files](dictionaries/README.md)
- [Hardware Modifications](hardware_mods.md)
- [Legal & Ethical Guidelines](legal_guidelines.md)

---

## Advanced Automation Examples

### Python AI Integration
```python
#!/usr/bin/env python3
# pm3_ai_analyzer.py - AI-assisted card analysis

import subprocess
import json
import re
from datetime import datetime

class PM3AIAnalyzer:
    def __init__(self):
        self.pm3_path = "pm3"
        self.results = {}

    def run_pm3_command(self, command):
        """Execute PM3 command and return output"""
        try:
            result = subprocess.run([self.pm3_path, '-c', command],
                                  capture_output=True, text=True, timeout=60)
            return result.stdout
        except subprocess.TimeoutExpired:
            return "TIMEOUT"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def detect_card_type(self):
        """AI-assisted card detection"""
        output = self.run_pm3_command("auto")

        # AI decision logic
        if "MIFARE Classic" in output:
            return self.analyze_mifare_classic()
        elif "MIFARE Ultralight" in output:
            return self.analyze_mifare_ultralight()
        elif "DESFire" in output:
            return self.analyze_desfire()
        elif "EM410x" in output:
            return self.analyze_em410x()
        else:
            return self.fallback_analysis()

    def analyze_mifare_classic(self):
        """Automated MIFARE Classic analysis"""
        steps = [
            ("info", "hf mf info"),
            ("prng_test", "hf mf hardnested t 1 000000000000"),
            ("autopwn", "hf mf autopwn"),
            ("dump", "hf mf dump")
        ]

        results = {}
        for step_name, command in steps:
            print(f"Executing: {step_name}")
            output = self.run_pm3_command(command)
            results[step_name] = output

            # AI decision points
            if step_name == "prng_test" and "weak" in output.lower():
                # Try darkside attack
                results["darkside"] = self.run_pm3_command("hf mf darkside")

        return results

    def analyze_mifare_ultralight(self):
        """Automated MIFARE Ultralight analysis"""
        steps = [
            ("info", "hf mfu info"),
            ("dump_attempt", "hf mfu dump"),
            ("password_gen", "hf mfu pwdgen -r"),
            ("tearoff", "hf mfu otptear")
        ]

        results = {}
        for step_name, command in steps:
            print(f"Executing: {step_name}")
            output = self.run_pm3_command(command)
            results[step_name] = output

            # Check if dump was successful
            if step_name == "dump_attempt" and "dump completed" in output.lower():
                break  # No need for further attacks

        return results

    def generate_report(self, analysis_results):
        """Generate comprehensive analysis report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "analysis_results": analysis_results,
            "recommendations": self.get_ai_recommendations(analysis_results),
            "next_steps": self.get_next_steps(analysis_results)
        }

        # Save report
        filename = f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        return report

    def get_ai_recommendations(self, results):
        """AI-generated recommendations based on results"""
        recommendations = []

        # Analyze results and provide recommendations
        if "autopwn" in results and "keys found" in results["autopwn"].lower():
            recommendations.append("All keys recovered - card fully compromised")
            recommendations.append("Consider cloning to magic card for testing")

        if "password_gen" in results:
            recommendations.append("Try generated passwords for access")

        return recommendations

# Usage example
if __name__ == "__main__":
    analyzer = PM3AIAnalyzer()
    results = analyzer.detect_card_type()
    report = analyzer.generate_report(results)
    print(f"Analysis complete. Report saved.")
```

### Batch Processing Script
```bash
#!/bin/bash
# batch_card_processor.sh - Process multiple cards automatically

BATCH_DIR="batch_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BATCH_DIR"

echo "=== Batch Card Processing Started ==="
echo "Results will be saved in: $BATCH_DIR"

card_count=0
while true; do
    echo ""
    echo "=== Card #$((++card_count)) ==="
    echo "Place card on antenna and press Enter (or 'q' to quit):"
    read -r input

    if [ "$input" = "q" ]; then
        break
    fi

    # Create card-specific directory
    card_dir="$BATCH_DIR/card_$card_count"
    mkdir -p "$card_dir"

    # Run analysis
    echo "Analyzing card..."
    pm3 -c "auto" > "$card_dir/detection.log" 2>&1

    # Determine card type and run appropriate analysis
    if grep -q "MIFARE Classic" "$card_dir/detection.log"; then
        echo "MIFARE Classic detected"
        pm3 -c "hf mf autopwn" > "$card_dir/analysis.log" 2>&1
        pm3 -c "hf mf dump" > "$card_dir/dump.log" 2>&1
    elif grep -q "MIFARE Ultralight" "$card_dir/detection.log"; then
        echo "MIFARE Ultralight detected"
        pm3 -c "hf mfu info; hf mfu dump" > "$card_dir/analysis.log" 2>&1
    fi

    echo "Card #$card_count processed"
done

echo ""
echo "=== Batch Processing Complete ==="
echo "Processed $card_count cards"
echo "Results saved in: $BATCH_DIR"

# Generate summary report
echo "=== BATCH PROCESSING SUMMARY ===" > "$BATCH_DIR/summary.txt"
echo "Date: $(date)" >> "$BATCH_DIR/summary.txt"
echo "Cards processed: $card_count" >> "$BATCH_DIR/summary.txt"
echo "" >> "$BATCH_DIR/summary.txt"

for i in $(seq 1 $card_count); do
    echo "Card #$i:" >> "$BATCH_DIR/summary.txt"
    if [ -f "$BATCH_DIR/card_$i/detection.log" ]; then
        grep -E "(MIFARE|EM410x|HID)" "$BATCH_DIR/card_$i/detection.log" | head -1 >> "$BATCH_DIR/summary.txt"
    fi
    echo "" >> "$BATCH_DIR/summary.txt"
done
```

### Magic Card Auto-Detection
```bash
#!/bin/bash
# magic_card_detector.sh - Automatically detect and classify magic cards

echo "=== Magic Card Detection ==="

# Test for Gen1A magic
echo "Testing for Gen1A magic..."
gen1a_result=$(pm3 -c "hf mf cgetblk 0" 2>&1)
if echo "$gen1a_result" | grep -q "block data"; then
    echo "✓ Gen1A magic card detected"
    echo "Commands available: csetuid, csetblk, cgetblk, cload, csave"
    exit 0
fi

# Test for Gen2 magic
echo "Testing for Gen2 magic..."
gen2_result=$(pm3 -c "hf 14a info" 2>&1)
if echo "$gen2_result" | grep -q "Magic capabilities.*Gen 2"; then
    echo "✓ Gen2 magic card detected"
    echo "Commands available: wrbl to any block including block 0"
    exit 0
fi

# Test for Gen3 magic
echo "Testing for Gen3 magic..."
gen3_result=$(pm3 -c "hf 14a raw -a -p -c 90F0CCCC10" 2>&1)
if echo "$gen3_result" | grep -q "9000"; then
    echo "✓ Gen3 magic card detected"
    echo "Commands available: APDU-based magic commands"
    exit 0
fi

# Test for UFUID
echo "Testing for UFUID..."
ufuid_result=$(pm3 -c "hf 14a raw -a -p -c 4000" 2>&1)
if echo "$ufuid_result" | grep -q "0A00"; then
    echo "✓ UFUID card detected"
    echo "Commands available: Direct UID modification"
    exit 0
fi

echo "✗ No magic capabilities detected"
echo "This appears to be a regular card"
```

### Automated Cloning Workflow
```bash
#!/bin/bash
# auto_clone.sh - Automated cloning workflow

SOURCE_CARD_DATA=""
TARGET_CARD_TYPE=""

echo "=== Automated Cloning Workflow ==="

# Step 1: Read source card
echo "Step 1: Reading source card..."
echo "Place SOURCE card on antenna and press Enter:"
read

# Detect and analyze source card
source_analysis=$(pm3 -c "auto" 2>&1)
echo "$source_analysis" > source_analysis.log

if echo "$source_analysis" | grep -q "MIFARE Classic"; then
    echo "Source: MIFARE Classic detected"
    pm3 -c "hf mf autopwn" > source_attack.log 2>&1
    pm3 -c "hf mf dump" > source_dump.log 2>&1
    SOURCE_CARD_DATA="hf-mf-*-dump.bin"
elif echo "$source_analysis" | grep -q "MIFARE Ultralight"; then
    echo "Source: MIFARE Ultralight detected"
    pm3 -c "hf mfu dump" > source_dump.log 2>&1
    SOURCE_CARD_DATA="hf-mfu-*-dump.json"
fi

# Step 2: Detect target card
echo ""
echo "Step 2: Detecting target card..."
echo "Place TARGET card on antenna and press Enter:"
read

target_analysis=$(pm3 -c "auto" 2>&1)
echo "$target_analysis" > target_analysis.log

# Detect magic capabilities
magic_test=$(./magic_card_detector.sh)
echo "$magic_test"

# Step 3: Perform cloning based on target type
echo ""
echo "Step 3: Cloning..."

if echo "$magic_test" | grep -q "Gen1A"; then
    echo "Cloning to Gen1A magic card..."
    if [ -f hf-mf-*-dump.bin ]; then
        pm3 -c "hf mf cload $(ls hf-mf-*-dump.bin | head -1)"
    fi
elif echo "$magic_test" | grep -q "Gen2"; then
    echo "Cloning to Gen2 magic card..."
    if [ -f hf-mf-*-dump.bin ]; then
        pm3 -c "hf mf restore 1 $(ls hf-mf-*-dump.bin | head -1)"
    fi
else
    echo "Cloning to regular card..."
    if [ -f hf-mf-*-dump.bin ]; then
        pm3 -c "hf mf restore 1 $(ls hf-mf-*-dump.bin | head -1)"
    elif [ -f hf-mfu-*-dump.json ]; then
        echo "Manual NTAG cloning required - see documentation"
    fi
fi

# Step 4: Verify clone
echo ""
echo "Step 4: Verifying clone..."
pm3 -c "auto" > clone_verification.log 2>&1

echo "Cloning workflow complete!"
echo "Check log files for detailed results."
```

---

## AI Prompt Templates

### Card Analysis Prompt
```
Analyze this Proxmark3 output and provide:
1. Card type identification
2. Security assessment
3. Recommended attack sequence
4. Estimated success probability
5. Alternative approaches if primary fails

PM3 Output:
[INSERT_PM3_OUTPUT_HERE]

Provide structured response with specific commands to execute.
```

### Attack Strategy Prompt
```
Based on this card analysis, create an optimal attack sequence:

Card Info:
- Type: [CARD_TYPE]
- UID: [UID]
- Security: [SECURITY_FEATURES]
- Previous attempts: [FAILED_ATTACKS]

Generate:
1. Prioritized attack list
2. Specific PM3 commands
3. Expected outcomes
4. Fallback strategies
5. Time estimates
```

### Cloning Strategy Prompt
```
Plan cloning strategy for:

Source Card:
- Type: [SOURCE_TYPE]
- Data: [DUMP_INFO]
- Special features: [FEATURES]

Target Card:
- Type: [TARGET_TYPE]
- Magic capabilities: [MAGIC_TYPE]
- Limitations: [LIMITATIONS]

Provide:
1. Step-by-step cloning procedure
2. Specific PM3 commands
3. Verification steps
4. Potential issues and solutions
```

---

**IMPORTANT LEGAL NOTICE**: This guide is for educational and authorized security testing purposes only. Always ensure you have explicit permission before testing any cards or systems. Unauthorized access to RFID/NFC systems may be illegal in your jurisdiction.
