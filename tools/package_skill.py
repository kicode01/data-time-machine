#!/usr/bin/env python3
"""
tools/package_skill.py
Packages the skill into a standalone .zip archive ready to upload to:
- Claude.ai / Claude Desktop (Settings -> Capabilities -> Skills)
- GitHub Releases
"""

import os
import zipfile

def package_skill(skill_dir: str):
    skill_name = os.path.basename(os.path.abspath(skill_dir))
    dist_dir = os.path.join(skill_dir, "dist")
    os.makedirs(dist_dir, exist_ok=True)
    zip_path = os.path.join(dist_dir, f"{skill_name}.zip")

    exclude_extensions = {".pyc", ".pyo", ".DS_Store"}
    exclude_dirs = {"__pycache__", ".git", "dist"}

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if any(file.endswith(ext) for ext in exclude_extensions):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, skill_dir)
                zipf.write(full_path, arcname=os.path.join(skill_name, rel_path))

    print(f"[+] Successfully packaged {skill_name} -> {zip_path}")
    print(f"    Size: {os.path.getsize(zip_path) / 1024:.1f} KB")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    package_skill(current_dir)
