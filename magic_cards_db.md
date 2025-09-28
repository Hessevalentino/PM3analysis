# Magic Cards Database & Reference

## Table of Contents
1. [Magic Card Types Overview](#magic-card-types-overview)
2. [Detection Methods](#detection-methods)
3. [Gen1A Magic Cards](#gen1a-magic-cards)
4. [Gen2 Magic Cards](#gen2-magic-cards)
5. [Gen3 Magic Cards](#gen3-magic-cards)
6. [UFUID Cards](#ufuid-cards)
7. [Magic NTAG Cards](#magic-ntag-cards)
8. [Vendor-Specific Cards](#vendor-specific-cards)
9. [Troubleshooting Magic Cards](#troubleshooting-magic-cards)
10. [Purchase Recommendations](#purchase-recommendations)

---

## Magic Card Types Overview

| Type | UID Changeable | Block 0 Writable | Detection Risk | Commands |
|------|----------------|-------------------|----------------|----------|
| Gen1A | ✅ | ✅ | High | Chinese Magic |
| Gen2 | ✅ | ✅ | Medium | Direct Write |
| Gen3 | ✅ | ✅ | Low | APDU |
| Gen4 | ✅ | ✅ | Very Low | GTU Mode |
| UFUID | ✅ | ❌ | Medium | Special Commands |
| Magic NTAG | ✅ | ✅ | Low | NTAG Magic |

---

## Detection Methods

### Universal Magic Detection Script
```bash
#!/bin/bash
# magic_detector.sh - Comprehensive magic card detection

echo "=== Magic Card Detection ==="
echo "Place card on antenna..."

# Basic card info
card_info=$(pm3 -c "hf 14a info" 2>&1)
echo "$card_info"

# Check for explicit magic capabilities
if echo "$card_info" | grep -q "Magic capabilities"; then
    magic_type=$(echo "$card_info" | grep "Magic capabilities" | cut -d: -f2 | xargs)
    echo "✓ Magic card detected: $magic_type"
    exit 0
fi

echo ""
echo "Testing for magic capabilities..."

# Test 1: Gen1A Chinese Magic
echo "Testing Gen1A magic..."
gen1a_test=$(pm3 -c "hf mf cgetblk 0" 2>&1)
if echo "$gen1a_test" | grep -q "block data"; then
    echo "✓ Gen1A magic card detected"
    echo "Available commands: csetuid, csetblk, cgetblk, cload, csave"
    exit 0
fi

# Test 2: Gen2 Direct Write
echo "Testing Gen2 magic..."
gen2_test=$(pm3 -c "hf mf wrbl 0 A FFFFFFFFFFFF" 2>&1)
if echo "$gen2_test" | grep -q -v "failed\|error"; then
    echo "✓ Gen2 magic card detected"
    echo "Available commands: Direct write to any block"
    exit 0
fi

# Test 3: Gen3 APDU
echo "Testing Gen3 magic..."
gen3_test=$(pm3 -c "hf 14a raw -a -p -c 90F0CCCC10" 2>&1)
if echo "$gen3_test" | grep -q "9000"; then
    echo "✓ Gen3 magic card detected"
    echo "Available commands: APDU-based magic"
    exit 0
fi

# Test 4: UFUID
echo "Testing UFUID..."
ufuid_test=$(pm3 -c "hf 14a raw -a -p -c 4000" 2>&1)
if echo "$ufuid_test" | grep -q "0A00"; then
    echo "✓ UFUID card detected"
    echo "Available commands: UID modification only"
    exit 0
fi

# Test 5: Gen4 GTU Mode
echo "Testing Gen4 GTU..."
gen4_test=$(pm3 -c "hf 14a raw -a -p -c CF00000000" 2>&1)
if echo "$gen4_test" | grep -q "9000\|6100"; then
    echo "✓ Gen4 GTU magic card detected"
    echo "Available commands: GTU mode operations"
    exit 0
fi

echo "✗ No magic capabilities detected"
echo "This appears to be a regular card"
```

### Automated Magic Classification
```python
#!/usr/bin/env python3
# magic_classifier.py - AI-assisted magic card classification

import subprocess
import re
import json

class MagicCardClassifier:
    def __init__(self):
        self.magic_signatures = {
            'gen1a': {
                'test_command': 'hf mf cgetblk 0',
                'success_pattern': r'block data.*[0-9A-F]{8}',
                'capabilities': ['uid_change', 'block0_write', 'chinese_magic']
            },
            'gen2': {
                'test_command': 'hf mf wrbl 0 A FFFFFFFFFFFF 04A1B2C3D4E5F6G7',
                'success_pattern': r'(success|ok|written)',
                'capabilities': ['uid_change', 'block0_write', 'direct_write']
            },
            'gen3': {
                'test_command': 'hf 14a raw -a -p -c 90F0CCCC10',
                'success_pattern': r'9000',
                'capabilities': ['uid_change', 'block0_write', 'apdu_magic']
            },
            'gen4': {
                'test_command': 'hf 14a raw -a -p -c CF00000000',
                'success_pattern': r'(9000|6100)',
                'capabilities': ['uid_change', 'block0_write', 'gtu_mode']
            },
            'ufuid': {
                'test_command': 'hf 14a raw -a -p -c 4000',
                'success_pattern': r'0A00',
                'capabilities': ['uid_change']
            }
        }
    
    def run_pm3_command(self, command):
        """Execute PM3 command and return output"""
        try:
            result = subprocess.run(['pm3', '-c', command], 
                                  capture_output=True, text=True, timeout=30)
            return result.stdout.lower()
        except:
            return ""
    
    def test_magic_type(self, magic_type):
        """Test for specific magic card type"""
        signature = self.magic_signatures[magic_type]
        output = self.run_pm3_command(signature['test_command'])
        
        if re.search(signature['success_pattern'], output, re.IGNORECASE):
            return True, signature['capabilities']
        return False, []
    
    def classify_card(self):
        """Classify magic card type"""
        # Get basic card info
        card_info = self.run_pm3_command("hf 14a info")
        
        # Check for explicit magic detection
        if 'magic capabilities' in card_info:
            magic_match = re.search(r'magic capabilities.*?:\s*(.+)', card_info)
            if magic_match:
                return {
                    'type': magic_match.group(1).strip(),
                    'detection_method': 'explicit',
                    'capabilities': ['detected_by_pm3']
                }
        
        # Test each magic type
        results = {}
        for magic_type in self.magic_signatures:
            is_magic, capabilities = self.test_magic_type(magic_type)
            if is_magic:
                results[magic_type] = {
                    'detected': True,
                    'capabilities': capabilities,
                    'confidence': 'high'
                }
            else:
                results[magic_type] = {
                    'detected': False,
                    'capabilities': [],
                    'confidence': 'low'
                }
        
        # Determine primary magic type
        detected_types = [t for t, r in results.items() if r['detected']]
        
        if detected_types:
            primary_type = detected_types[0]  # First detected type
            return {
                'type': primary_type,
                'detection_method': 'testing',
                'capabilities': results[primary_type]['capabilities'],
                'all_results': results
            }
        else:
            return {
                'type': 'regular',
                'detection_method': 'testing',
                'capabilities': [],
                'all_results': results
            }
    
    def generate_usage_commands(self, classification):
        """Generate appropriate commands for detected magic type"""
        magic_type = classification['type']
        commands = {}
        
        if magic_type == 'gen1a':
            commands = {
                'set_uid': 'hf mf csetuid [8_hex_bytes]',
                'write_block': 'hf mf csetblk [block] [16_hex_bytes]',
                'read_block': 'hf mf cgetblk [block]',
                'load_dump': 'hf mf cload [dump_file]',
                'save_dump': 'hf mf csave [dump_file]'
            }
        elif magic_type == 'gen2':
            commands = {
                'write_any_block': 'hf mf wrbl [block] A FFFFFFFFFFFF [16_hex_bytes]',
                'restore_dump': 'hf mf restore 1 [dump_file]',
                'clone_card': 'hf mf restore 1 [source_dump]'
            }
        elif magic_type == 'gen3':
            commands = {
                'unlock': 'hf 14a raw -a -p -c 90F0CCCC10',
                'write_block': 'hf mf wrbl [block] A FFFFFFFFFFFF [16_hex_bytes]',
                'set_uid': 'hf 14a raw -a -p -c 90FBCCCC07[new_uid]'
            }
        elif magic_type == 'ufuid':
            commands = {
                'unlock_uid': 'hf 14a raw -a -p -c 4000',
                'set_uid': 'hf 14a raw -a -p -c 4300[new_uid]'
            }
        
        return commands

if __name__ == "__main__":
    classifier = MagicCardClassifier()
    result = classifier.classify_card()
    
    print(json.dumps(result, indent=2))
    
    if result['type'] != 'regular':
        commands = classifier.generate_usage_commands(result)
        print("\nRecommended commands:")
        for cmd_name, cmd in commands.items():
            print(f"  {cmd_name}: {cmd}")
```

---

## Gen1A Magic Cards

### Characteristics
- **Detection**: Responds to Chinese magic commands
- **UID**: Freely changeable
- **Block 0**: Writable
- **Detection Risk**: High (easily detected by readers)
- **Cost**: Low

### Commands
```bash
# Set UID (7 bytes for Ultralight, 4 bytes for Classic)
hf mf csetuid 04A1B2C3D4E5F6

# Write specific block
hf mf csetblk 0 04A1B2C3D4E5F6G7H8I9J0K1L2M3N4

# Read specific block
hf mf cgetblk 0

# Load complete dump
hf mf cload original_card.bin

# Save complete dump
hf mf csave cloned_card.bin

# Wipe card (set all blocks to 00)
hf mf cwipe
```

### Cloning Workflow
```bash
#!/bin/bash
# gen1a_clone.sh - Gen1A cloning workflow

SOURCE_DUMP="$1"
if [ -z "$SOURCE_DUMP" ]; then
    echo "Usage: $0 <source_dump.bin>"
    exit 1
fi

echo "=== Gen1A Magic Card Cloning ==="

# Step 1: Verify magic card
echo "Step 1: Verifying Gen1A magic card..."
if ! pm3 -c "hf mf cgetblk 0" | grep -q "block data"; then
    echo "ERROR: Gen1A magic card not detected"
    exit 1
fi

# Step 2: Load dump
echo "Step 2: Loading dump to magic card..."
pm3 -c "hf mf cload $SOURCE_DUMP"

# Step 3: Verify clone
echo "Step 3: Verifying clone..."
pm3 -c "hf mf csave verification_dump.bin"

# Step 4: Compare dumps
if cmp -s "$SOURCE_DUMP" "verification_dump.bin"; then
    echo "✓ Clone successful - dumps match"
else
    echo "✗ Clone verification failed - dumps differ"
fi

echo "Gen1A cloning complete"
```

---

## Gen2 Magic Cards

### Characteristics
- **Detection**: Direct write capability to any block
- **UID**: Changeable
- **Block 0**: Writable
- **Detection Risk**: Medium
- **Cost**: Medium

### Commands
```bash
# Write to any block (including block 0)
hf mf wrbl 0 A FFFFFFFFFFFF 04A1B2C3D4E5F6G7H8I9J0K1L2M3N4

# Restore complete dump
hf mf restore 1 original_card.bin

# Clone card directly
hf mf restore 1 source_dump.bin

# Verify write
hf mf rdbl 0 A FFFFFFFFFFFF
```

### Advanced Gen2 Operations
```bash
# Change UID by writing block 0
hf mf wrbl 0 A FFFFFFFFFFFF [new_uid][bcc][sak][atqa][manufacturer]

# Example: Set UID to 04A1B2C3
hf mf wrbl 0 A FFFFFFFFFFFF 04A1B2C3D4080400626364656667686970

# Write manufacturer block (block 0)
# Format: [UID 4 bytes][BCC][SAK][ATQA][Manufacturer data 8 bytes]
```

---

## Gen3 Magic Cards

### Characteristics
- **Detection**: APDU-based commands
- **UID**: Changeable
- **Block 0**: Writable
- **Detection Risk**: Low
- **Cost**: High

### Commands
```bash
# Unlock magic mode
hf 14a raw -a -p -c 90F0CCCC10

# Set UID (after unlock)
hf 14a raw -a -p -c 90FBCCCC07[new_uid_7_bytes]

# Write block (after unlock)
hf mf wrbl [block] A FFFFFFFFFFFF [16_hex_bytes]

# Lock magic mode
hf 14a raw -a -p -c 90F1CCCC10
```

### Gen3 Cloning Script
```bash
#!/bin/bash
# gen3_clone.sh - Gen3 magic card cloning

echo "=== Gen3 Magic Card Cloning ==="

# Step 1: Unlock magic mode
echo "Step 1: Unlocking magic mode..."
unlock_result=$(pm3 -c "hf 14a raw -a -p -c 90F0CCCC10")
if ! echo "$unlock_result" | grep -q "9000"; then
    echo "ERROR: Failed to unlock Gen3 magic mode"
    exit 1
fi

# Step 2: Set UID from source dump
echo "Step 2: Setting UID..."
# Extract UID from dump file (first 8 bytes of block 0)
if [ -f "$1" ]; then
    uid=$(xxd -p -l 4 "$1" | tr -d '\n')
    pm3 -c "hf 14a raw -a -p -c 90FBCCCC04$uid"
fi

# Step 3: Write all blocks
echo "Step 3: Writing blocks..."
pm3 -c "hf mf restore 1 $1"

# Step 4: Lock magic mode
echo "Step 4: Locking magic mode..."
pm3 -c "hf 14a raw -a -p -c 90F1CCCC10"

echo "Gen3 cloning complete"
```

---

## UFUID Cards

### Characteristics
- **Detection**: UID changeable only
- **UID**: Changeable
- **Block 0**: Not writable (except UID portion)
- **Detection Risk**: Medium
- **Cost**: Low

### Commands
```bash
# Unlock UID change mode
hf 14a raw -a -p -c 4000

# Expected response: 0A00 (indicates UFUID capability)

# Set new UID
hf 14a raw -a -p -c 4300[new_uid_4_bytes]

# Lock UID (permanent)
hf 14a raw -a -p -c 4200
```

### UFUID Workflow
```bash
#!/bin/bash
# ufuid_clone.sh - UFUID card UID cloning

NEW_UID="$1"
if [ -z "$NEW_UID" ]; then
    echo "Usage: $0 <new_uid_8_hex_chars>"
    exit 1
fi

echo "=== UFUID Card UID Change ==="

# Step 1: Test UFUID capability
echo "Step 1: Testing UFUID capability..."
test_result=$(pm3 -c "hf 14a raw -a -p -c 4000")
if ! echo "$test_result" | grep -q "0A00"; then
    echo "ERROR: UFUID capability not detected"
    exit 1
fi

# Step 2: Set new UID
echo "Step 2: Setting UID to $NEW_UID..."
pm3 -c "hf 14a raw -a -p -c 4300$NEW_UID"

# Step 3: Verify UID change
echo "Step 3: Verifying UID change..."
pm3 -c "hf 14a info"

echo "UFUID operation complete"
echo "WARNING: Do not run lock command (4200) unless permanent change is desired"
```

---

## Magic NTAG Cards

### Characteristics
- **Type**: MIFARE Ultralight/NTAG magic variants
- **UID**: Changeable
- **Pages**: All writable including UID pages
- **Detection Risk**: Low to Medium

### Commands
```bash
# Set UID for magic NTAG
hf mfu setuid [7_byte_uid]

# Write to UID pages (pages 0-1)
hf mfu wrbl -b 0 -d [page0_data]
hf mfu wrbl -b 1 -d [page1_data]

# Clone complete NTAG
hf mfu restore [dump_file]

# Magic NTAG detection
hf mfu info
# Look for "Magic capabilities" in output
```

---

## Vendor-Specific Cards

### Chinese Magic Cards
```bash
# Common Chinese magic card vendors:
# - Fudan (FM11RF08)
# - Shanghai Fudan Microelectronics

# Detection characteristics:
# - Often respond to Gen1A commands
# - May have non-standard ATQA/SAK values
# - Usually cheaper than original NXP cards

# Testing Chinese cards:
hf 14a info  # Check for non-standard values
hf mf cgetblk 0  # Test Gen1A capability
```

### Specialized Magic Cards
```bash
# UID0 Cards (UID starts with 00)
# - Special handling required
# - May need specific unlock sequences

# Sector 0 Writable Cards
# - Only sector 0 is magic
# - Other sectors behave normally

# Detection:
hf mf wrbl 0 A FFFFFFFFFFFF [test_data]
hf mf wrbl 4 A FFFFFFFFFFFF [test_data]  # Should fail on sector 0 only cards
```

---

## Troubleshooting Magic Cards

### Common Issues

#### Magic Commands Not Working
```bash
# Issue: cgetblk returns error
# Solutions:
1. Check card positioning (1-2cm from antenna)
2. Verify PM3 antenna tuning: hw tune
3. Try different magic detection methods
4. Card may not be Gen1A magic

# Issue: Direct write fails
# Solutions:
1. Try with different keys: A0A1A2A3A4A5, 000000000000
2. Check if card is write-protected
3. Verify correct block number and data format
```

#### UID Change Failures
```bash
# Issue: UID doesn't change
# Solutions:
1. Verify magic card type (some only allow limited UID changes)
2. Check UID format (4 bytes for Classic, 7 bytes for Ultralight)
3. Ensure proper unlock sequence for Gen3/UFUID cards
4. Some cards require specific BCC calculation
```

#### Clone Verification Fails
```bash
# Issue: Clone doesn't match original
# Solutions:
1. Check for write-protected blocks
2. Verify all keys were recovered from original
3. Some magic cards have limitations on certain blocks
4. Access conditions may prevent writing to some sectors
```

### Diagnostic Commands
```bash
# Complete magic card diagnosis
echo "=== Magic Card Diagnosis ==="

# Basic info
pm3 -c "hf 14a info"

# Test all magic types
pm3 -c "hf mf cgetblk 0"  # Gen1A
pm3 -c "hf 14a raw -a -p -c 4000"  # UFUID
pm3 -c "hf 14a raw -a -p -c 90F0CCCC10"  # Gen3

# Hardware check
pm3 -c "hw tune"
pm3 -c "hw status"
```

---

## Purchase Recommendations

### Recommended Magic Cards by Use Case

#### For Learning/Testing
- **Gen1A Chinese Magic Cards**
- **Cost**: $1-3 per card
- **Pros**: Cheap, easy to use, good for learning
- **Cons**: Easily detected, limited lifespan

#### For Professional Testing
- **Gen2 Magic Cards**
- **Cost**: $3-8 per card
- **Pros**: Good balance of features and stealth
- **Cons**: More expensive than Gen1A

#### For Advanced Research
- **Gen3/Gen4 Magic Cards**
- **Cost**: $8-20 per card
- **Pros**: Hardest to detect, most features
- **Cons**: Expensive, complex commands

### Trusted Vendors
```
Note: Vendor recommendations change frequently.
Check current community recommendations on:
- RFID/NFC forums
- Proxmark3 community
- Security research communities

Always verify magic capabilities upon receipt.
```

---

**IMPORTANT**: Magic cards should only be used for authorized security testing, research, and educational purposes. Using magic cards to create fraudulent access cards or bypass security systems without permission is illegal and unethical.
