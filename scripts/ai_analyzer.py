#!/usr/bin/env python3
"""
PM3 AI Analyzer - AI-assisted RFID/NFC card analysis
Integrates with Claude/Augment for intelligent decision making
"""

import subprocess
import json
import argparse
import sys
import os
import time
from datetime import datetime
from pathlib import Path

class PM3AIAnalyzer:
    def __init__(self, device="/dev/ttyACM0", timeout=60, verbose=False):
        self.device = device
        self.timeout = timeout
        self.verbose = verbose
        self.results = {}
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path(f"analysis_{self.session_id}")
        self.output_dir.mkdir(exist_ok=True)
        
    def log(self, message, level="INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "\033[0;34m",
            "SUCCESS": "\033[0;32m", 
            "WARNING": "\033[1;33m",
            "ERROR": "\033[0;31m"
        }
        color = colors.get(level, "")
        reset = "\033[0m"
        
        print(f"{color}[{timestamp}] {level}: {message}{reset}")
        
        # Also log to file
        with open(self.output_dir / "analysis.log", "a") as f:
            f.write(f"[{timestamp}] {level}: {message}\n")
    
    def run_pm3_command(self, command, timeout=None):
        """Execute PM3 command and return output"""
        if timeout is None:
            timeout = self.timeout
            
        self.log(f"Executing: {command}")
        
        try:
            result = subprocess.run(
                ['pm3', '-c', command], 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            output = result.stdout
            if self.verbose:
                print(f"Command output:\n{output}")
                
            # Save command output
            cmd_file = self.output_dir / f"cmd_{command.replace(' ', '_').replace('/', '_')}.log"
            with open(cmd_file, 'w') as f:
                f.write(f"Command: {command}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Return code: {result.returncode}\n")
                f.write(f"STDOUT:\n{result.stdout}\n")
                f.write(f"STDERR:\n{result.stderr}\n")
            
            return output
            
        except subprocess.TimeoutExpired:
            self.log(f"Command timeout: {command}", "WARNING")
            return "TIMEOUT"
        except Exception as e:
            self.log(f"Command error: {str(e)}", "ERROR")
            return f"ERROR: {str(e)}"
    
    def check_pm3_connection(self):
        """Check PM3 connection and hardware status"""
        self.log("Checking PM3 connection...")
        
        # Test basic connection
        hw_status = self.run_pm3_command("hw status", timeout=10)
        if "ERROR" in hw_status or "TIMEOUT" in hw_status:
            self.log("PM3 connection failed", "ERROR")
            return False
            
        # Check antenna tuning
        hw_tune = self.run_pm3_command("hw tune", timeout=10)
        
        self.log("PM3 connection OK", "SUCCESS")
        return True
    
    def detect_card_type(self):
        """AI-assisted card type detection"""
        self.log("🔍 Detecting card type...")
        
        # Try automatic detection first
        auto_result = self.run_pm3_command("auto")
        
        # AI decision logic based on output patterns
        card_info = {
            "detection_output": auto_result,
            "timestamp": datetime.now().isoformat()
        }
        
        if "MIFARE Classic" in auto_result:
            card_info["type"] = "mifare_classic"
            card_info["subtype"] = self._detect_mifare_classic_subtype(auto_result)
        elif "MIFARE Ultralight" in auto_result:
            card_info["type"] = "mifare_ultralight" 
            card_info["subtype"] = self._detect_ultralight_subtype(auto_result)
        elif "MIFARE DESFire" in auto_result:
            card_info["type"] = "desfire"
        elif "iClass" in auto_result:
            card_info["type"] = "iclass"
        elif "EM410x" in auto_result:
            card_info["type"] = "em410x"
        elif "HID" in auto_result:
            card_info["type"] = "hid"
        elif "T55" in auto_result:
            card_info["type"] = "t55xx"
        else:
            card_info["type"] = "unknown"
            # Try manual detection
            card_info = self._fallback_detection(card_info)
        
        # Extract UID if available
        uid_match = self._extract_uid(auto_result)
        if uid_match:
            card_info["uid"] = uid_match
            
        self.log(f"Card type detected: {card_info['type']}")
        
        # Save card info
        with open(self.output_dir / "card_info.json", "w") as f:
            json.dump(card_info, f, indent=2)
            
        return card_info
    
    def _detect_mifare_classic_subtype(self, output):
        """Detect MIFARE Classic subtype"""
        if "1K" in output or "1024" in output:
            return "1k"
        elif "4K" in output or "4096" in output:
            return "4k"
        else:
            return "unknown"
    
    def _detect_ultralight_subtype(self, output):
        """Detect MIFARE Ultralight subtype"""
        if "EV1" in output:
            return "ev1"
        elif "NTAG213" in output:
            return "ntag213"
        elif "NTAG215" in output:
            return "ntag215"
        elif "NTAG216" in output:
            return "ntag216"
        else:
            return "standard"
    
    def _extract_uid(self, output):
        """Extract UID from PM3 output"""
        import re
        # Common UID patterns
        patterns = [
            r"UID.*?:\s*([A-F0-9\s]+)",
            r"Card UID:\s*([A-F0-9\s]+)",
            r"ID:\s*([A-F0-9\s]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1).replace(" ", "")
        return None
    
    def _fallback_detection(self, card_info):
        """Fallback detection for unknown cards"""
        self.log("Running fallback detection...")
        
        # Try HF search
        hf_result = self.run_pm3_command("hf search")
        if "found" in hf_result.lower():
            card_info["hf_detection"] = hf_result
            
        # Try LF search  
        lf_result = self.run_pm3_command("lf search")
        if "found" in lf_result.lower():
            card_info["lf_detection"] = lf_result
            
        return card_info
    
    def test_magic_capabilities(self):
        """Test for magic card capabilities"""
        self.log("🎴 Testing magic card capabilities...")
        
        magic_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        # Test Gen1A
        self.log("Testing Gen1A magic...")
        gen1a_result = self.run_pm3_command("hf mf cgetblk 0", timeout=10)
        magic_results["tests"]["gen1a"] = {
            "output": gen1a_result,
            "detected": "block data" in gen1a_result.lower()
        }
        
        if magic_results["tests"]["gen1a"]["detected"]:
            self.log("Gen1A magic card detected!", "SUCCESS")
            magic_results["type"] = "gen1a"
            magic_results["capabilities"] = ["uid_change", "block0_write", "chinese_magic"]
            return magic_results
        
        # Test Gen2
        self.log("Testing Gen2 magic...")
        gen2_result = self.run_pm3_command("hf 14a info", timeout=10)
        magic_results["tests"]["gen2"] = {
            "output": gen2_result,
            "detected": "magic capabilities" in gen2_result.lower() and "gen 2" in gen2_result.lower()
        }
        
        if magic_results["tests"]["gen2"]["detected"]:
            self.log("Gen2 magic card detected!", "SUCCESS")
            magic_results["type"] = "gen2"
            magic_results["capabilities"] = ["uid_change", "block0_write", "direct_write"]
            return magic_results
        
        # Test Gen3
        self.log("Testing Gen3 magic...")
        gen3_result = self.run_pm3_command("hf 14a raw -a -p -c 90F0CCCC10", timeout=10)
        magic_results["tests"]["gen3"] = {
            "output": gen3_result,
            "detected": "9000" in gen3_result
        }
        
        if magic_results["tests"]["gen3"]["detected"]:
            self.log("Gen3 magic card detected!", "SUCCESS")
            magic_results["type"] = "gen3"
            magic_results["capabilities"] = ["uid_change", "block0_write", "apdu_magic"]
            return magic_results
        
        # Test UFUID
        self.log("Testing UFUID...")
        ufuid_result = self.run_pm3_command("hf 14a raw -a -p -c 4000", timeout=10)
        magic_results["tests"]["ufuid"] = {
            "output": ufuid_result,
            "detected": "0A00" in ufuid_result
        }
        
        if magic_results["tests"]["ufuid"]["detected"]:
            self.log("UFUID card detected!", "SUCCESS")
            magic_results["type"] = "ufuid"
            magic_results["capabilities"] = ["uid_change"]
            return magic_results
        
        self.log("No magic capabilities detected")
        magic_results["type"] = "none"
        magic_results["capabilities"] = []
        
        # Save magic test results
        with open(self.output_dir / "magic_test.json", "w") as f:
            json.dump(magic_results, f, indent=2)
            
        return magic_results
    
    def analyze_mifare_classic(self, card_info):
        """AI-assisted MIFARE Classic analysis"""
        self.log("🎯 Analyzing MIFARE Classic card...")
        
        analysis_results = {
            "card_type": "mifare_classic",
            "timestamp": datetime.now().isoformat(),
            "attacks": {}
        }
        
        # Get detailed card info
        self.log("Getting card information...")
        mf_info = self.run_pm3_command("hf mf info")
        analysis_results["card_info"] = mf_info
        
        # Test PRNG strength
        self.log("Testing PRNG strength...")
        prng_test = self.run_pm3_command("hf mf hardnested t 1 000000000000", timeout=30)
        analysis_results["prng_test"] = prng_test
        
        # AI decision: choose attack based on PRNG
        if "weak" in prng_test.lower():
            self.log("Weak PRNG detected - trying Darkside attack...", "SUCCESS")
            darkside_result = self.run_pm3_command("hf mf darkside", timeout=120)
            analysis_results["attacks"]["darkside"] = {
                "output": darkside_result,
                "success": "key found" in darkside_result.lower()
            }
        else:
            self.log("Strong PRNG detected - trying Hardnested attack...")
            hardnested_result = self.run_pm3_command("hf mf hardnested 0 A FFFFFFFFFFFF 4 A", timeout=300)
            analysis_results["attacks"]["hardnested"] = {
                "output": hardnested_result,
                "success": "key found" in hardnested_result.lower()
            }
        
        # Dictionary attack
        self.log("Running dictionary attack...")
        dict_result = self.run_pm3_command("hf mf chk *1 ? d", timeout=60)
        analysis_results["attacks"]["dictionary"] = {
            "output": dict_result,
            "success": "key found" in dict_result.lower()
        }
        
        # Autopwn as fallback
        self.log("Running autopwn...")
        autopwn_result = self.run_pm3_command("hf mf autopwn", timeout=180)
        analysis_results["attacks"]["autopwn"] = {
            "output": autopwn_result,
            "success": "keys found" in autopwn_result.lower()
        }
        
        # Try dump if any attack succeeded
        if any(attack["success"] for attack in analysis_results["attacks"].values()):
            self.log("Attempting card dump...", "SUCCESS")
            dump_result = self.run_pm3_command("hf mf dump")
            analysis_results["dump"] = {
                "output": dump_result,
                "success": "dump completed" in dump_result.lower()
            }
        
        return analysis_results
    
    def analyze_mifare_ultralight(self, card_info):
        """AI-assisted MIFARE Ultralight analysis"""
        self.log("🎯 Analyzing MIFARE Ultralight card...")
        
        analysis_results = {
            "card_type": "mifare_ultralight",
            "timestamp": datetime.now().isoformat(),
            "attacks": {}
        }
        
        # Get card info
        self.log("Getting card information...")
        mfu_info = self.run_pm3_command("hf mfu info")
        analysis_results["card_info"] = mfu_info
        
        # Try dump without password
        self.log("Attempting dump without password...")
        dump_no_pwd = self.run_pm3_command("hf mfu dump")
        analysis_results["attacks"]["no_password"] = {
            "output": dump_no_pwd,
            "success": "dump completed" in dump_no_pwd.lower()
        }
        
        if analysis_results["attacks"]["no_password"]["success"]:
            self.log("Dump successful without password!", "SUCCESS")
            return analysis_results
        
        # Try common passwords
        self.log("Trying common passwords...")
        common_passwords = ["FFFFFFFF", "00000000", "12345678", "ABCDEFAB"]
        
        for pwd in common_passwords:
            self.log(f"Trying password: {pwd}")
            pwd_result = self.run_pm3_command(f"hf mfu dump -k {pwd}")
            analysis_results["attacks"][f"password_{pwd}"] = {
                "output": pwd_result,
                "success": "dump completed" in pwd_result.lower()
            }
            
            if analysis_results["attacks"][f"password_{pwd}"]["success"]:
                self.log(f"Dump successful with password: {pwd}", "SUCCESS")
                return analysis_results
        
        # Generate UID-based passwords
        self.log("Generating UID-based passwords...")
        pwdgen_result = self.run_pm3_command("hf mfu pwdgen -r")
        analysis_results["password_generation"] = pwdgen_result
        
        # Try tear-off attack
        self.log("Attempting tear-off attack...")
        tearoff_result = self.run_pm3_command("hf mfu otptear", timeout=30)
        analysis_results["attacks"]["tearoff"] = {
            "output": tearoff_result,
            "success": "success" in tearoff_result.lower()
        }
        
        return analysis_results
    
    def generate_ai_recommendations(self, card_info, magic_results, analysis_results):
        """Generate AI recommendations based on analysis"""
        recommendations = {
            "timestamp": datetime.now().isoformat(),
            "card_summary": {
                "type": card_info.get("type", "unknown"),
                "uid": card_info.get("uid", "unknown"),
                "magic_type": magic_results.get("type", "none")
            },
            "security_assessment": [],
            "attack_success": [],
            "recommendations": [],
            "next_steps": []
        }
        
        # Analyze attack success
        if analysis_results:
            for attack_name, attack_data in analysis_results.get("attacks", {}).items():
                if attack_data.get("success", False):
                    recommendations["attack_success"].append(f"{attack_name} attack successful")
        
        # Security assessment
        if recommendations["attack_success"]:
            recommendations["security_assessment"].append("Card security compromised")
            recommendations["security_assessment"].append("Multiple attack vectors successful")
        else:
            recommendations["security_assessment"].append("Card shows resistance to common attacks")
        
        # Magic card recommendations
        if magic_results.get("type") != "none":
            recommendations["recommendations"].append(f"Magic card detected ({magic_results['type']})")
            recommendations["recommendations"].append("Can be used for cloning and testing")
            recommendations["next_steps"].append("Consider cloning original cards to this magic card")
        
        # General recommendations
        if card_info.get("type") == "mifare_classic":
            if any("darkside" in attack for attack in recommendations["attack_success"]):
                recommendations["recommendations"].append("Weak PRNG detected - card easily compromised")
                recommendations["next_steps"].append("Recommend upgrading to newer card technology")
        
        return recommendations
    
    def generate_report(self, card_info, magic_results, analysis_results, recommendations):
        """Generate comprehensive analysis report"""
        report = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "card_info": card_info,
            "magic_results": magic_results,
            "analysis_results": analysis_results,
            "ai_recommendations": recommendations,
            "files_generated": list(str(f.name) for f in self.output_dir.iterdir())
        }
        
        # Save JSON report
        report_file = self.output_dir / "analysis_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        # Generate human-readable summary
        summary_file = self.output_dir / "summary.txt"
        with open(summary_file, "w") as f:
            f.write("=== PM3 AI Analysis Report ===\n")
            f.write(f"Session ID: {self.session_id}\n")
            f.write(f"Timestamp: {report['timestamp']}\n\n")
            
            f.write("CARD INFORMATION:\n")
            f.write(f"Type: {card_info.get('type', 'unknown')}\n")
            f.write(f"UID: {card_info.get('uid', 'unknown')}\n")
            f.write(f"Magic Type: {magic_results.get('type', 'none')}\n\n")
            
            f.write("ATTACK RESULTS:\n")
            for attack in recommendations.get("attack_success", []):
                f.write(f"✅ {attack}\n")
            
            if not recommendations.get("attack_success"):
                f.write("❌ No successful attacks\n")
            
            f.write("\nRECOMMENDATIONS:\n")
            for rec in recommendations.get("recommendations", []):
                f.write(f"• {rec}\n")
            
            f.write("\nNEXT STEPS:\n")
            for step in recommendations.get("next_steps", []):
                f.write(f"• {step}\n")
        
        self.log(f"Report generated: {report_file}", "SUCCESS")
        self.log(f"Summary generated: {summary_file}", "SUCCESS")
        
        return report

def main():
    parser = argparse.ArgumentParser(description='PM3 AI-Assisted Analyzer')
    parser.add_argument('--device', '-d', default='/dev/ttyACM0', help='PM3 device path')
    parser.add_argument('--timeout', '-t', type=int, default=60, help='Command timeout in seconds')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--detect-only', action='store_true', help='Detection only, no attacks')
    parser.add_argument('--magic-only', action='store_true', help='Test magic capabilities only')
    parser.add_argument('--card-type', help='Force specific card type analysis')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = PM3AIAnalyzer(
        device=args.device,
        timeout=args.timeout,
        verbose=args.verbose
    )
    
    try:
        # Check PM3 connection
        if not analyzer.check_pm3_connection():
            sys.exit(1)
        
        # Detect card type
        card_info = analyzer.detect_card_type()
        
        # Test magic capabilities
        magic_results = analyzer.test_magic_capabilities()
        
        if args.magic_only:
            analyzer.log("Magic-only mode - analysis complete")
            return
        
        analysis_results = None
        
        if not args.detect_only:
            # Run appropriate analysis
            card_type = args.card_type or card_info.get("type")
            
            if card_type == "mifare_classic":
                analysis_results = analyzer.analyze_mifare_classic(card_info)
            elif card_type == "mifare_ultralight":
                analysis_results = analyzer.analyze_mifare_ultralight(card_info)
            else:
                analyzer.log(f"No specific analysis available for: {card_type}", "WARNING")
        
        # Generate AI recommendations
        recommendations = analyzer.generate_ai_recommendations(
            card_info, magic_results, analysis_results
        )
        
        # Generate final report
        report = analyzer.generate_report(
            card_info, magic_results, analysis_results, recommendations
        )
        
        analyzer.log("🎉 Analysis complete!", "SUCCESS")
        analyzer.log(f"Results saved in: {analyzer.output_dir}")
        
        # Print summary
        print("\n=== ANALYSIS SUMMARY ===")
        print(f"Card Type: {card_info.get('type', 'unknown')}")
        print(f"Magic Type: {magic_results.get('type', 'none')}")
        
        if recommendations.get("attack_success"):
            print("Attack Results:")
            for attack in recommendations["attack_success"]:
                print(f"  ✅ {attack}")
        else:
            print("  ❌ No successful attacks")
        
    except KeyboardInterrupt:
        analyzer.log("Analysis interrupted by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        analyzer.log(f"Analysis failed: {str(e)}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()
