#!/bin/bash
# quick_analyze.sh - Rychlá analýza RFID/NFC karty
# Usage: ./quick_analyze.sh [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PM3_DEVICE="${PM3_DEVICE:-/dev/ttyACM0}"
TIMEOUT=60
OUTPUT_DIR="analysis_$(date +%Y%m%d_%H%M%S)"
VERBOSE=false

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    cat << EOF
PM3 Quick Analyzer - Rychlá analýza RFID/NFC karet

Usage: $0 [OPTIONS]

OPTIONS:
    -h, --help          Show this help message
    -v, --verbose       Verbose output
    -d, --device PATH   PM3 device path (default: $PM3_DEVICE)
    -t, --timeout SEC   Timeout in seconds (default: $TIMEOUT)
    -o, --output DIR    Output directory (default: auto-generated)
    --magic-only        Test only for magic card capabilities
    --no-attacks        Skip attack phase, detection only

EXAMPLES:
    $0                  # Basic quick analysis
    $0 -v               # Verbose analysis
    $0 --magic-only     # Test only magic capabilities
    $0 -o my_analysis   # Custom output directory

EOF
}

check_pm3_connection() {
    log_info "Checking PM3 connection..."
    
    if ! command -v pm3 &> /dev/null; then
        log_error "PM3 client not found in PATH"
        return 1
    fi
    
    # Test PM3 connection
    if ! timeout 10 pm3 -c "hw status" &> /dev/null; then
        log_error "Cannot connect to PM3 device"
        log_info "Make sure PM3 is connected and accessible at $PM3_DEVICE"
        return 1
    fi
    
    log_success "PM3 connection OK"
    return 0
}

check_hardware() {
    log_info "Checking PM3 hardware status..."
    
    hw_status=$(pm3 -c "hw status" 2>&1)
    if [[ $VERBOSE == true ]]; then
        echo "$hw_status"
    fi
    
    # Check antenna tuning
    log_info "Checking antenna tuning..."
    tune_result=$(pm3 -c "hw tune" 2>&1)
    if [[ $VERBOSE == true ]]; then
        echo "$tune_result"
    fi
    
    # Basic validation
    if echo "$hw_status" | grep -q "OK"; then
        log_success "Hardware status OK"
    else
        log_warning "Hardware status may have issues"
    fi
}

detect_card() {
    log_info "Detecting card type..."
    
    # Try automatic detection first
    auto_result=$(timeout $TIMEOUT pm3 -c "auto" 2>&1 || true)
    echo "$auto_result" > "$OUTPUT_DIR/detection.log"
    
    if [[ $VERBOSE == true ]]; then
        echo "$auto_result"
    fi
    
    # Parse detection results
    if echo "$auto_result" | grep -q "MIFARE Classic"; then
        echo "mifare_classic"
    elif echo "$auto_result" | grep -q "MIFARE Ultralight"; then
        echo "mifare_ultralight"
    elif echo "$auto_result" | grep -q "MIFARE DESFire"; then
        echo "desfire"
    elif echo "$auto_result" | grep -q "iClass"; then
        echo "iclass"
    elif echo "$auto_result" | grep -q "EM410x"; then
        echo "em410x"
    elif echo "$auto_result" | grep -q "HID"; then
        echo "hid"
    elif echo "$auto_result" | grep -q "T55"; then
        echo "t55xx"
    else
        echo "unknown"
    fi
}

test_magic_capabilities() {
    log_info "Testing magic card capabilities..."
    
    magic_results="$OUTPUT_DIR/magic_test.log"
    echo "=== Magic Card Detection ===" > "$magic_results"
    
    # Test Gen1A
    log_info "Testing Gen1A magic..."
    gen1a_result=$(timeout 10 pm3 -c "hf mf cgetblk 0" 2>&1 || true)
    echo "Gen1A Test:" >> "$magic_results"
    echo "$gen1a_result" >> "$magic_results"
    
    if echo "$gen1a_result" | grep -q "block data"; then
        log_success "Gen1A magic card detected!"
        echo "gen1a" > "$OUTPUT_DIR/magic_type.txt"
        return 0
    fi
    
    # Test Gen2
    log_info "Testing Gen2 magic..."
    gen2_result=$(timeout 10 pm3 -c "hf 14a info" 2>&1 || true)
    echo "Gen2 Test:" >> "$magic_results"
    echo "$gen2_result" >> "$magic_results"
    
    if echo "$gen2_result" | grep -q "Magic capabilities.*Gen 2"; then
        log_success "Gen2 magic card detected!"
        echo "gen2" > "$OUTPUT_DIR/magic_type.txt"
        return 0
    fi
    
    # Test Gen3
    log_info "Testing Gen3 magic..."
    gen3_result=$(timeout 10 pm3 -c "hf 14a raw -a -p -c 90F0CCCC10" 2>&1 || true)
    echo "Gen3 Test:" >> "$magic_results"
    echo "$gen3_result" >> "$magic_results"
    
    if echo "$gen3_result" | grep -q "9000"; then
        log_success "Gen3 magic card detected!"
        echo "gen3" > "$OUTPUT_DIR/magic_type.txt"
        return 0
    fi
    
    # Test UFUID
    log_info "Testing UFUID..."
    ufuid_result=$(timeout 10 pm3 -c "hf 14a raw -a -p -c 4000" 2>&1 || true)
    echo "UFUID Test:" >> "$magic_results"
    echo "$ufuid_result" >> "$magic_results"
    
    if echo "$ufuid_result" | grep -q "0A00"; then
        log_success "UFUID card detected!"
        echo "ufuid" > "$OUTPUT_DIR/magic_type.txt"
        return 0
    fi
    
    log_info "No magic capabilities detected"
    echo "none" > "$OUTPUT_DIR/magic_type.txt"
    return 1
}

analyze_mifare_classic() {
    log_info "Analyzing MIFARE Classic card..."
    
    # Basic info
    log_info "Getting card information..."
    pm3 -c "hf mf info" > "$OUTPUT_DIR/mifare_info.log" 2>&1
    
    # Try autopwn first (fastest)
    log_info "Running autopwn attack..."
    if timeout $TIMEOUT pm3 -c "hf mf autopwn" > "$OUTPUT_DIR/autopwn.log" 2>&1; then
        log_success "Autopwn successful!"
        
        # Try to dump
        log_info "Dumping card data..."
        if pm3 -c "hf mf dump" > "$OUTPUT_DIR/dump.log" 2>&1; then
            log_success "Card dump completed!"
        fi
    else
        log_warning "Autopwn failed, trying dictionary attack..."
        pm3 -c "hf mf chk *1 ? d" > "$OUTPUT_DIR/dictionary.log" 2>&1
    fi
}

analyze_mifare_ultralight() {
    log_info "Analyzing MIFARE Ultralight card..."
    
    # Basic info
    log_info "Getting card information..."
    pm3 -c "hf mfu info" > "$OUTPUT_DIR/ultralight_info.log" 2>&1
    
    # Try dump without password
    log_info "Attempting dump without password..."
    if pm3 -c "hf mfu dump" > "$OUTPUT_DIR/dump_no_pwd.log" 2>&1; then
        if grep -q -E "(MFU dump file information|Reading tag memory|block#|Version\.\.\.\.\.)" "$OUTPUT_DIR/dump_no_pwd.log"; then
            log_success "Dump successful without password!"
            return 0
        fi
    fi
    
    # Try common passwords
    log_info "Trying common passwords..."
    common_passwords=("FFFFFFFF" "00000000" "12345678" "ABCDEFAB")
    
    for pwd in "${common_passwords[@]}"; do
        log_info "Trying password: $pwd"
        if pm3 -c "hf mfu dump -k $pwd" > "$OUTPUT_DIR/dump_$pwd.log" 2>&1; then
            if grep -q -E "(MFU dump file information|Reading tag memory|block#|Version\.\.\.\.\.)" "$OUTPUT_DIR/dump_$pwd.log"; then
                log_success "Dump successful with password: $pwd"
                return 0
            fi
        fi
    done
    
    # Try UID-based password generation
    log_info "Generating UID-based passwords..."
    pm3 -c "hf mfu pwdgen -r" > "$OUTPUT_DIR/pwdgen.log" 2>&1
}

analyze_em410x() {
    log_info "Analyzing EM410x card..."
    
    # Read card
    log_info "Reading EM410x card..."
    pm3 -c "lf em 410x_read" > "$OUTPUT_DIR/em410x_read.log" 2>&1
    
    if grep -q "EM410x" "$OUTPUT_DIR/em410x_read.log"; then
        log_success "EM410x card read successfully!"
        
        # Extract ID for potential cloning
        card_id=$(grep -oP "EM410x ID:\s*\K[A-F0-9]+" "$OUTPUT_DIR/em410x_read.log" || true)
        if [[ -n "$card_id" ]]; then
            echo "$card_id" > "$OUTPUT_DIR/card_id.txt"
            log_info "Card ID: $card_id"
        fi
    fi
}

generate_summary() {
    log_info "Generating analysis summary..."
    
    summary_file="$OUTPUT_DIR/summary.txt"
    
    cat > "$summary_file" << EOF
=== PM3 Quick Analysis Summary ===
Date: $(date)
Analysis Directory: $OUTPUT_DIR

CARD DETECTION:
EOF
    
    if [[ -f "$OUTPUT_DIR/detection.log" ]]; then
        echo "Card Type: $(cat "$OUTPUT_DIR/detection.log" | grep -oP "(MIFARE Classic|MIFARE Ultralight|DESFire|EM410x|HID|T55)" | head -1 || echo "Unknown")" >> "$summary_file"
    fi
    
    if [[ -f "$OUTPUT_DIR/magic_type.txt" ]]; then
        magic_type=$(cat "$OUTPUT_DIR/magic_type.txt")
        echo "Magic Type: $magic_type" >> "$summary_file"
    fi
    
    echo "" >> "$summary_file"
    echo "ANALYSIS RESULTS:" >> "$summary_file"
    
    # Check for successful attacks
    if [[ -f "$OUTPUT_DIR/autopwn.log" ]] && grep -q "keys found" "$OUTPUT_DIR/autopwn.log"; then
        echo "✅ MIFARE Classic autopwn successful" >> "$summary_file"
    fi
    
    if [[ -f "$OUTPUT_DIR/dump.log" ]] || ls "$OUTPUT_DIR"/dump_*.log &> /dev/null; then
        echo "✅ Card dump completed" >> "$summary_file"
    fi
    
    if [[ -f "$OUTPUT_DIR/card_id.txt" ]]; then
        echo "✅ Card ID extracted: $(cat "$OUTPUT_DIR/card_id.txt")" >> "$summary_file"
    fi
    
    echo "" >> "$summary_file"
    echo "FILES GENERATED:" >> "$summary_file"
    ls -la "$OUTPUT_DIR"/ >> "$summary_file"
    
    log_success "Summary saved to: $summary_file"
}

# Main execution
main() {
    # Parse command line arguments
    MAGIC_ONLY=false
    NO_ATTACKS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -d|--device)
                PM3_DEVICE="$2"
                shift 2
                ;;
            -t|--timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            --magic-only)
                MAGIC_ONLY=true
                shift
                ;;
            --no-attacks)
                NO_ATTACKS=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    echo "=== PM3 Quick Analysis Started ==="
    echo "Output directory: $OUTPUT_DIR"
    echo "Timestamp: $(date)"
    echo ""
    
    # Check PM3 connection
    if ! check_pm3_connection; then
        exit 1
    fi
    
    # Check hardware
    check_hardware
    
    # Test magic capabilities
    test_magic_capabilities
    
    if [[ $MAGIC_ONLY == true ]]; then
        log_info "Magic-only mode - skipping further analysis"
        generate_summary
        exit 0
    fi
    
    # Detect card type
    card_type=$(detect_card)
    log_info "Detected card type: $card_type"
    echo "$card_type" > "$OUTPUT_DIR/card_type.txt"
    
    if [[ $NO_ATTACKS == true ]]; then
        log_info "No-attacks mode - skipping attack phase"
        generate_summary
        exit 0
    fi
    
    # Run appropriate analysis
    case $card_type in
        "mifare_classic")
            analyze_mifare_classic
            ;;
        "mifare_ultralight")
            analyze_mifare_ultralight
            ;;
        "em410x")
            analyze_em410x
            ;;
        *)
            log_warning "No specific analysis available for card type: $card_type"
            ;;
    esac
    
    # Generate summary
    generate_summary
    
    echo ""
    echo "=== Analysis Complete ==="
    log_success "Results saved in: $OUTPUT_DIR"
    
    if [[ -f "$OUTPUT_DIR/summary.txt" ]]; then
        echo ""
        echo "=== SUMMARY ==="
        cat "$OUTPUT_DIR/summary.txt"
    fi
}

# Run main function
main "$@"
