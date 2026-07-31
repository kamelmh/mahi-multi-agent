import os
import json
import sys

# Fix encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Check which key files exist in LifeWorkspace
base = "C:/Users/Admin/My Drive/LifeWorkspace"

# Key files referenced in brain map and MOCs
key_files = [
    # Brain Map core
    "00-Brain-Map.md",
    "00-Master-Integration.md",
    "00-ULTIMATE-SYSTEM.md",
    
    # Identity MOC
    "01_Identities_&_Assets/00-MOC-Identity.md",
    "01_Identities_&_Assets/Personal_Profile.md",
    "01_Identities_&_Assets/Financial_Summary.md",
    "01_Identities_&_Assets/Health_Tracker.md",
    
    # Skills MOC
    "02_Skills_&_Development/00-MOC-Skills.md",
    "02_Skills_&_Development/Skills_Inventory.md",
    "02_Skills_&_Development/Skill_Gaps.md",
    "02_Skills_&_Development/Learning_Roadmap.md",
    "02_Skills_&_Development/Certifications.md",
    "02_Skills_&_Development/Programming_Languages.md",
    "02_Skills_&_Development/AI_ML_Skills.md",
    
    # Career MOC
    "03_Career_&_Planning/00-MOC-Career.md",
    "03_Career_&_Planning/Career_Roadmap.md",
    "03_Career_&_Planning/Freelancing/00-MOC-Freelancing.md",
    "03_Career_&_Planning/Freelancing/30_Day_Action_Plan.md",
    "03_Career_&_Planning/Freelancing/Fiverr_Gigs.md",
    "03_Career_&_Planning/Thirduni_Application.md",
    "03_Career_&_Planning/Humphrey_Fellowship.md",
    "03_Career_&_Planning/Free_TOEFL_Prep.md",
    
    # Projects MOC
    "04_Ideas_&_Projects/00-MOC-Projects.md",
    "04_Ideas_&_Projects/Academix_DSS/00-MOC-Academix.md",
    
    # Education
    "10_Education_Project/00-MOC-Education.md",
    
    # Astrology
    "12_Astrology/00-MOC-Astrology.md",
    
    # Advanced Tools
    "15_Advanced_Tools/00-MOC-Advanced-Tools.md",
    "15_Advanced_Tools/CLAUDE_GUI_MASTER_MEMORY.md",
    
    # System files
    "AGENTS.md",
    "CLAUDE.md",
    ".session-state.json",
    
    # Knowledge Base
    "15_Advanced_Tools/Knowledge_Base/00-INDEX.md",
    "15_Advanced_Tools/Knowledge_Base/academic.md",
    "15_Advanced_Tools/Knowledge_Base/spiritual.md",
    "15_Advanced_Tools/Knowledge_Base/logistics.md",
    "15_Advanced_Tools/Knowledge_Base/teaching.md",
    
    # Templates
    "Templates/00-Template-MOC.md",
    "Templates/00-Template-Note.md",
]

# Check existence
results = {"exists": [], "missing": []}

for f in key_files:
    full_path = os.path.join(base, f)
    if os.path.exists(full_path):
        results["exists"].append(f)
    else:
        results["missing"].append(f)

# Print results
print(f"=== LifeWorkspace File Check ===")
print(f"Total checked: {len(key_files)}")
print(f"Found: {len(results['exists'])}")
print(f"Missing: {len(results['missing'])}")

if results["missing"]:
    print(f"\n=== MISSING FILES ===")
    for f in results["missing"]:
        print(f"  [MISSING] {f}")

if results["exists"]:
    print(f"\n=== FOUND FILES ===")
    for f in results["exists"]:
        print(f"  [OK] {f}")

# Save results
with open(os.path.join(base, "15_Advanced_Tools", "FILE_CHECK_RESULTS.json"), "w") as fh:
    json.dump(results, fh, indent=2)

print(f"\nResults saved to: 15_Advanced_Tools/FILE_CHECK_RESULTS.json")
