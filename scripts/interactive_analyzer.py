#!/usr/bin/env python3
"""
PM3 Interactive Analyzer - Menu-driven interface for card analysis
"""

import os
import sys
import subprocess
from pathlib import Path

class InteractiveAnalyzer:
    def __init__(self):
        self.scripts_dir = Path(__file__).parent
        self.project_root = self.scripts_dir.parent
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_banner(self):
        """Print application banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    PM3 Interactive Analyzer                  ║
║              AI-Assisted RFID/NFC Security Testing          ║
╠══════════════════════════════════════════════════════════════╣
║  Professional penetration testing tools for Proxmark3       ║
║  Educational and authorized security testing only            ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def show_main_menu(self):
        """Display main menu options"""
        menu = """
🎯 MAIN MENU:

1. 🔍 Quick Card Detection
2. 🤖 AI-Assisted Full Analysis  
3. 🎴 Magic Card Operations
4. 🔄 Cloning Workflow
5. 📊 Batch Processing
6. 📄 Generate Report
7. ⚙️  Settings & Configuration
8. 📚 Help & Documentation
9. 🚪 Exit

Enter your choice (1-9): """
        return input(menu).strip()
    
    def quick_detection(self):
        """Quick card detection menu"""
        self.clear_screen()
        self.print_banner()
        
        print("\n🔍 QUICK CARD DETECTION")
        print("=" * 50)
        
        options = """
1. Auto-detect card type
2. Test HF cards only
3. Test LF cards only
4. Hardware status check
5. Back to main menu

Choose option (1-5): """
        
        choice = input(options).strip()
        
        if choice == "1":
            print("\n⚡ Running auto-detection...")
            self.run_command("pm3 -c 'auto'")
        elif choice == "2":
            print("\n⚡ Testing HF cards...")
            self.run_command("pm3 -c 'hf search'")
        elif choice == "3":
            print("\n⚡ Testing LF cards...")
            self.run_command("pm3 -c 'lf search'")
        elif choice == "4":
            print("\n⚡ Checking hardware status...")
            self.run_command("pm3 -c 'hw status; hw tune'")
        elif choice == "5":
            return
        else:
            print("❌ Invalid choice!")
        
        input("\nPress Enter to continue...")
    
    def ai_analysis(self):
        """AI-assisted analysis menu"""
        self.clear_screen()
        self.print_banner()
        
        print("\n🤖 AI-ASSISTED ANALYSIS")
        print("=" * 50)
        
        options = """
Analysis Profiles:

1. 🚀 Quick Analysis (30 seconds)
2. 🎯 Standard Analysis (2 minutes)
3. 🔥 Aggressive Analysis (5+ minutes)
4. 🎴 Magic Card Focus
5. 🔍 Detection Only
6. 📊 Custom Analysis
7. Back to main menu

Choose profile (1-7): """
        
        choice = input(options).strip()
        
        if choice == "1":
            print("\n🚀 Running quick analysis...")
            self.run_script("quick_analyze.sh", ["--timeout", "30"])
        elif choice == "2":
            print("\n🎯 Running standard AI analysis...")
            self.run_script("ai_analyzer.py", ["-v"])
        elif choice == "3":
            print("\n🔥 Running aggressive analysis...")
            self.run_script("ai_analyzer.py", ["-v", "--timeout", "300"])
        elif choice == "4":
            print("\n🎴 Testing magic card capabilities...")
            self.run_script("ai_analyzer.py", ["--magic-only", "-v"])
        elif choice == "5":
            print("\n🔍 Detection only...")
            self.run_script("ai_analyzer.py", ["--detect-only", "-v"])
        elif choice == "6":
            self.custom_analysis()
        elif choice == "7":
            return
        else:
            print("❌ Invalid choice!")
        
        if choice != "6":
            input("\nPress Enter to continue...")
    
    def custom_analysis(self):
        """Custom analysis configuration"""
        print("\n📊 CUSTOM ANALYSIS CONFIGURATION")
        print("=" * 40)
        
        # Get parameters
        timeout = input("Timeout in seconds (default 60): ").strip() or "60"
        card_type = input("Force card type (mifare_classic/mifare_ultralight/auto): ").strip() or "auto"
        verbose = input("Verbose output? (y/n): ").strip().lower() == 'y'
        
        # Build command
        args = ["--timeout", timeout]
        if verbose:
            args.append("-v")
        if card_type != "auto":
            args.extend(["--card-type", card_type])
        
        print(f"\n⚡ Running custom analysis with timeout={timeout}, card_type={card_type}, verbose={verbose}")
        self.run_script("ai_analyzer.py", args)
        
        input("\nPress Enter to continue...")
    
    def magic_operations(self):
        """Magic card operations menu"""
        self.clear_screen()
        self.print_banner()
        
        print("\n🎴 MAGIC CARD OPERATIONS")
        print("=" * 50)
        
        options = """
Magic Card Operations:

1. 🔍 Detect Magic Type
2. 🎯 Gen1A Operations
3. 🎯 Gen2 Operations  
4. 🎯 Gen3 Operations
5. 🎯 UFUID Operations
6. 📋 Magic Card Database
7. Back to main menu

Choose operation (1-7): """
        
        choice = input(options).strip()
        
        if choice == "1":
            print("\n🔍 Detecting magic card type...")
            self.run_script("ai_analyzer.py", ["--magic-only", "-v"])
        elif choice == "2":
            self.gen1a_operations()
        elif choice == "3":
            self.gen2_operations()
        elif choice == "4":
            self.gen3_operations()
        elif choice == "5":
            self.ufuid_operations()
        elif choice == "6":
            self.show_magic_database()
        elif choice == "7":
            return
        else:
            print("❌ Invalid choice!")
        
        if choice not in ["2", "3", "4", "5", "6"]:
            input("\nPress Enter to continue...")
    
    def gen1a_operations(self):
        """Gen1A magic card operations"""
        print("\n🎯 GEN1A MAGIC OPERATIONS")
        print("=" * 30)
        
        operations = """
1. Read block 0
2. Set UID
3. Write block
4. Load dump file
5. Save dump file
6. Back

Choose (1-6): """
        
        choice = input(operations).strip()
        
        if choice == "1":
            self.run_command("pm3 -c 'hf mf cgetblk 0'")
        elif choice == "2":
            uid = input("Enter new UID (8 hex chars): ").strip()
            if len(uid) == 8:
                self.run_command(f"pm3 -c 'hf mf csetuid {uid}'")
            else:
                print("❌ Invalid UID format!")
        elif choice == "3":
            block = input("Block number: ").strip()
            data = input("Block data (32 hex chars): ").strip()
            if len(data) == 32:
                self.run_command(f"pm3 -c 'hf mf csetblk {block} {data}'")
            else:
                print("❌ Invalid data format!")
        elif choice == "4":
            filename = input("Dump filename: ").strip()
            self.run_command(f"pm3 -c 'hf mf cload {filename}'")
        elif choice == "5":
            filename = input("Save filename: ").strip()
            self.run_command(f"pm3 -c 'hf mf csave {filename}'")
        elif choice == "6":
            return
        
        if choice != "6":
            input("\nPress Enter to continue...")
    
    def gen2_operations(self):
        """Gen2 magic card operations"""
        print("\n🎯 GEN2 MAGIC OPERATIONS")
        print("=" * 30)
        
        operations = """
1. Write any block
2. Restore from dump
3. Clone card
4. Back

Choose (1-4): """
        
        choice = input(operations).strip()
        
        if choice == "1":
            block = input("Block number: ").strip()
            data = input("Block data (32 hex chars): ").strip()
            if len(data) == 32:
                self.run_command(f"pm3 -c 'hf mf wrbl {block} A FFFFFFFFFFFF {data}'")
            else:
                print("❌ Invalid data format!")
        elif choice == "2":
            filename = input("Dump filename: ").strip()
            self.run_command(f"pm3 -c 'hf mf restore 1 {filename}'")
        elif choice == "3":
            print("🔄 Starting clone workflow...")
            print("1. Place SOURCE card and press Enter")
            input()
            self.run_command("pm3 -c 'hf mf autopwn'")
            print("2. Place TARGET magic card and press Enter")
            input()
            self.run_command("pm3 -c 'hf mf restore 1 hf-mf-*-dump.bin'")
        elif choice == "4":
            return
        
        if choice != "4":
            input("\nPress Enter to continue...")
    
    def gen3_operations(self):
        """Gen3 magic card operations"""
        print("\n🎯 GEN3 MAGIC OPERATIONS")
        print("=" * 30)
        
        operations = """
1. Unlock magic mode
2. Set UID
3. Write block
4. Lock magic mode
5. Back

Choose (1-5): """
        
        choice = input(operations).strip()
        
        if choice == "1":
            self.run_command("pm3 -c 'hf 14a raw -a -p -c 90F0CCCC10'")
        elif choice == "2":
            uid = input("Enter new UID (8 hex chars): ").strip()
            if len(uid) == 8:
                self.run_command(f"pm3 -c 'hf 14a raw -a -p -c 90FBCCCC04{uid}'")
            else:
                print("❌ Invalid UID format!")
        elif choice == "3":
            block = input("Block number: ").strip()
            data = input("Block data (32 hex chars): ").strip()
            if len(data) == 32:
                self.run_command(f"pm3 -c 'hf mf wrbl {block} A FFFFFFFFFFFF {data}'")
            else:
                print("❌ Invalid data format!")
        elif choice == "4":
            self.run_command("pm3 -c 'hf 14a raw -a -p -c 90F1CCCC10'")
        elif choice == "5":
            return
        
        if choice != "5":
            input("\nPress Enter to continue...")
    
    def ufuid_operations(self):
        """UFUID operations"""
        print("\n🎯 UFUID OPERATIONS")
        print("=" * 20)
        
        operations = """
1. Test UFUID capability
2. Set UID
3. Lock UID (PERMANENT!)
4. Back

Choose (1-4): """
        
        choice = input(operations).strip()
        
        if choice == "1":
            self.run_command("pm3 -c 'hf 14a raw -a -p -c 4000'")
        elif choice == "2":
            uid = input("Enter new UID (8 hex chars): ").strip()
            if len(uid) == 8:
                self.run_command(f"pm3 -c 'hf 14a raw -a -p -c 4300{uid}'")
            else:
                print("❌ Invalid UID format!")
        elif choice == "3":
            confirm = input("⚠️  This will PERMANENTLY lock the UID! Type 'CONFIRM' to proceed: ")
            if confirm == "CONFIRM":
                self.run_command("pm3 -c 'hf 14a raw -a -p -c 4200'")
            else:
                print("❌ Operation cancelled")
        elif choice == "4":
            return
        
        if choice != "4":
            input("\nPress Enter to continue...")
    
    def show_magic_database(self):
        """Show magic card database"""
        print("\n📋 MAGIC CARD DATABASE")
        print("=" * 30)
        
        database_file = self.project_root / "magic_cards_db.md"
        if database_file.exists():
            print(f"Opening magic card database: {database_file}")
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", str(database_file)])
            elif sys.platform == "linux":
                subprocess.run(["xdg-open", str(database_file)])
            else:
                print(f"Please open: {database_file}")
        else:
            print("❌ Magic card database not found!")
        
        input("\nPress Enter to continue...")
    
    def cloning_workflow(self):
        """Cloning workflow menu"""
        self.clear_screen()
        self.print_banner()
        
        print("\n🔄 CLONING WORKFLOW")
        print("=" * 50)
        
        print("This workflow will guide you through cloning a card:")
        print("1. Analyze source card")
        print("2. Detect target card capabilities") 
        print("3. Perform cloning")
        print("4. Verify clone")
        
        if input("\nProceed with cloning workflow? (y/n): ").strip().lower() != 'y':
            return
        
        # Step 1: Analyze source
        print("\n📋 STEP 1: Analyze Source Card")
        print("Place the SOURCE card on the antenna and press Enter...")
        input()
        
        print("🔍 Analyzing source card...")
        self.run_script("ai_analyzer.py", ["-v", "--detect-only"])
        
        # Step 2: Detect target
        print("\n📋 STEP 2: Detect Target Card")
        print("Place the TARGET card on the antenna and press Enter...")
        input()
        
        print("🎴 Testing magic capabilities...")
        self.run_script("ai_analyzer.py", ["--magic-only", "-v"])
        
        # Step 3: Clone
        print("\n📋 STEP 3: Perform Cloning")
        print("Place the SOURCE card back on the antenna and press Enter...")
        input()
        
        print("⚡ Running full analysis and dump...")
        self.run_script("ai_analyzer.py", ["-v"])
        
        print("Place the TARGET magic card on the antenna and press Enter...")
        input()
        
        # Simple cloning commands based on common scenarios
        print("🔄 Attempting clone...")
        self.run_command("pm3 -c 'hf mf restore 1 hf-mf-*-dump.bin' || pm3 -c 'hf mf cload hf-mf-*-dump.bin'")
        
        # Step 4: Verify
        print("\n📋 STEP 4: Verify Clone")
        print("🔍 Verifying clone...")
        self.run_command("pm3 -c 'auto'")
        
        print("\n✅ Cloning workflow complete!")
        input("\nPress Enter to continue...")
    
    def batch_processing(self):
        """Batch processing menu"""
        self.clear_screen()
        self.print_banner()
        
        print("\n📊 BATCH PROCESSING")
        print("=" * 50)
        
        count = input("Number of cards to process: ").strip()
        if not count.isdigit():
            print("❌ Invalid number!")
            input("Press Enter to continue...")
            return
        
        output_dir = input("Output directory (default: batch_results): ").strip() or "batch_results"
        
        print(f"\n📊 Processing {count} cards...")
        print("Place each card when prompted and press Enter")
        
        for i in range(1, int(count) + 1):
            print(f"\n🎯 CARD {i}/{count}")
            print("Place card on antenna and press Enter...")
            input()
            
            print(f"⚡ Analyzing card {i}...")
            card_output_dir = f"{output_dir}/card_{i:03d}"
            os.makedirs(card_output_dir, exist_ok=True)
            
            # Run quick analysis for each card
            self.run_script("quick_analyze.sh", ["-o", card_output_dir])
        
        print(f"\n✅ Batch processing complete! Results in: {output_dir}")
        input("Press Enter to continue...")
    
    def generate_report(self):
        """Generate analysis report"""
        print("\n📄 GENERATE REPORT")
        print("=" * 30)
        
        print("Available analysis directories:")
        analysis_dirs = [d for d in os.listdir(".") if d.startswith("analysis_")]
        
        if not analysis_dirs:
            print("❌ No analysis directories found!")
            input("Press Enter to continue...")
            return
        
        for i, dir_name in enumerate(analysis_dirs, 1):
            print(f"{i}. {dir_name}")
        
        choice = input(f"\nSelect directory (1-{len(analysis_dirs)}): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(analysis_dirs):
            selected_dir = analysis_dirs[int(choice) - 1]
            print(f"\n📄 Generating report for: {selected_dir}")
            
            # Simple report generation
            report_file = f"{selected_dir}/final_report.txt"
            with open(report_file, "w") as f:
                f.write(f"=== PM3 Analysis Report ===\n")
                f.write(f"Directory: {selected_dir}\n")
                f.write(f"Generated: {subprocess.check_output(['date']).decode().strip()}\n\n")
                
                # Include summary if exists
                summary_file = f"{selected_dir}/summary.txt"
                if os.path.exists(summary_file):
                    f.write("SUMMARY:\n")
                    with open(summary_file, "r") as sf:
                        f.write(sf.read())
            
            print(f"✅ Report generated: {report_file}")
        else:
            print("❌ Invalid choice!")
        
        input("Press Enter to continue...")
    
    def settings_menu(self):
        """Settings and configuration menu"""
        print("\n⚙️  SETTINGS & CONFIGURATION")
        print("=" * 40)
        
        settings = """
1. Check PM3 connection
2. Hardware diagnostics
3. View configuration files
4. Update dictionaries
5. Back to main menu

Choose (1-5): """
        
        choice = input(settings).strip()
        
        if choice == "1":
            print("\n🔍 Checking PM3 connection...")
            self.run_command("pm3 -c 'hw status'")
        elif choice == "2":
            print("\n🔧 Running hardware diagnostics...")
            self.run_command("pm3 -c 'hw status; hw version; hw tune'")
        elif choice == "3":
            config_dir = self.project_root / "config"
            if config_dir.exists():
                print(f"Configuration directory: {config_dir}")
                for config_file in config_dir.glob("*.yaml"):
                    print(f"  - {config_file.name}")
            else:
                print("❌ Configuration directory not found!")
        elif choice == "4":
            dict_dir = self.project_root / "dictionaries"
            if dict_dir.exists():
                print(f"Dictionary directory: {dict_dir}")
                for dict_file in dict_dir.glob("*.dic"):
                    print(f"  - {dict_file.name}")
            else:
                print("❌ Dictionary directory not found!")
        elif choice == "5":
            return
        
        if choice != "5":
            input("\nPress Enter to continue...")
    
    def show_help(self):
        """Show help and documentation"""
        print("\n📚 HELP & DOCUMENTATION")
        print("=" * 40)
        
        help_text = """
AVAILABLE DOCUMENTATION:

1. README.md - Project overview and quick start
2. pm3_master_guide.md - Complete analysis guide
3. advanced_attacks.md - Advanced attack techniques
4. magic_cards_db.md - Magic card database
5. legal_guidelines.md - Legal and ethical guidelines

QUICK COMMANDS:

• pm3 -c "auto" - Auto-detect card
• pm3 -c "hf mf autopwn" - MIFARE Classic autopwn
• pm3 -c "hf mfu dump" - MIFARE Ultralight dump
• pm3 -c "hf 14a info" - Card information

SAFETY REMINDERS:

⚠️  Only test cards you own or have permission to test
⚠️  Follow local laws and regulations
⚠️  Use for educational and authorized testing only
        """
        
        print(help_text)
        input("\nPress Enter to continue...")
    
    def run_command(self, command):
        """Run a shell command"""
        print(f"💻 Executing: {command}")
        try:
            result = subprocess.run(command, shell=True, capture_output=False)
            if result.returncode != 0:
                print(f"❌ Command failed with return code: {result.returncode}")
        except Exception as e:
            print(f"❌ Error executing command: {e}")
    
    def run_script(self, script_name, args=None):
        """Run a script from the scripts directory"""
        script_path = self.scripts_dir / script_name
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return
        
        command = [str(script_path)]
        if args:
            command.extend(args)
        
        print(f"🚀 Running: {' '.join(command)}")
        try:
            # Make script executable
            os.chmod(script_path, 0o755)
            result = subprocess.run(command, capture_output=False)
            if result.returncode != 0:
                print(f"❌ Script failed with return code: {result.returncode}")
        except Exception as e:
            print(f"❌ Error running script: {e}")
    
    def run(self):
        """Main application loop"""
        while True:
            self.clear_screen()
            self.print_banner()
            
            choice = self.show_main_menu()
            
            if choice == "1":
                self.quick_detection()
            elif choice == "2":
                self.ai_analysis()
            elif choice == "3":
                self.magic_operations()
            elif choice == "4":
                self.cloning_workflow()
            elif choice == "5":
                self.batch_processing()
            elif choice == "6":
                self.generate_report()
            elif choice == "7":
                self.settings_menu()
            elif choice == "8":
                self.show_help()
            elif choice == "9":
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice! Please try again.")
                input("Press Enter to continue...")

def main():
    try:
        analyzer = InteractiveAnalyzer()
        analyzer.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
