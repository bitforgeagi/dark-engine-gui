import os
import sys
import subprocess
from datetime import datetime
import shutil

def create_dmg():
    """Create a DMG file from the .app bundle"""
    if sys.platform != 'darwin':
        print("Error: DMG creation is only supported on macOS")
        return False

    app_name = "Dark Engine GUI"
    version = "1.0.0"
    date_stamp = datetime.now().strftime("%Y%m%d")
    
    # Paths
    app_path = f"dist/{app_name}.app"
    dmg_name = f"Dark-Engine-GUI-{version}-{date_stamp}"
    dmg_path = f"dist/{dmg_name}.dmg"
    
    # Check if .app exists
    if not os.path.exists(app_path):
        print(f"Error: {app_path} not found! Run build.py first.")
        return False
    
    print(f"Creating DMG: {dmg_name}.dmg")
    
    # Remove existing DMG if it exists
    if os.path.exists(dmg_path):
        os.remove(dmg_path)
    
    # Create temporary directory for DMG contents
    temp_dir = 'dist/dmg_temp'
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # Copy .app to temporary directory
    temp_app_path = os.path.join(temp_dir, f"{app_name}.app")
    shutil.copytree(app_path, temp_app_path)
    
    # Create symbolic link to /Applications
    os.symlink('/Applications', os.path.join(temp_dir, 'Applications'))
    
    # Sign the app bundle
    subprocess.run([
        'codesign',
        '--force',
        '--sign', '-',  # Ad-hoc signing
        '--entitlements', 'entitlements.plist',
        '--deep',
        app_path
    ], check=True)
    
    # Create DMG
    try:
        subprocess.run([
            'hdiutil', 'create',
            '-volname', app_name,
            '-srcfolder', temp_dir,
            '-ov',  # Overwrite if exists
            '-format', 'UDZO',  # Compressed
            dmg_path
        ], check=True)
        
        # Sign the DMG
        subprocess.run([
            'codesign',
            '--force',
            '--sign', '-',  # Ad-hoc signing
            dmg_path
        ], check=True)
        
        print(f"\nDMG created successfully: {dmg_path}")
        
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error creating DMG: {e}")
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
        return False

def main():
    if create_dmg():
        print("\nDMG build complete! Ready for distribution.")
    else:
        print("\nDMG creation failed!")

if __name__ == "__main__":
    main() 