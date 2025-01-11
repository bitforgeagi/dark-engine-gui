import os
import shutil
import sys
import subprocess
from datetime import datetime
import fnmatch

def clean_builds():
    """Remove old build artifacts and cached apps"""
    dirs_to_clean = ['build', 'dist']
    files_to_clean = ['*.spec']
    
    print("Cleaning old builds...")
    
    # Remove directories
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Removing {dir_name}/")
            shutil.rmtree(dir_name)
    
    # Remove files
    for file_pattern in files_to_clean:
        for file in os.listdir('.'):
            if file.endswith('.spec') and file not in ['macos.spec', 'windows.spec']:
                print(f"Removing {file}")
                os.remove(file)
    
    # Clean macOS specific caches
    if sys.platform == 'darwin':
        print("Cleaning macOS application cache...")
        home = os.path.expanduser("~")
        cache_paths = [
            f"{home}/Library/Caches/Dark Engine GUI",
            f"{home}/Library/Saved Application State/com.darkengine.app.savedState",
            "/Applications/Dark Engine GUI.app",  # Remove existing application
        ]
        
        for path in cache_paths:
            if os.path.exists(path):
                print(f"Removing {path}")
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                except Exception as e:
                    print(f"Warning: Could not remove {path}: {e}")
        
        # Clear application quarantine attributes
        try:
            subprocess.run(['xattr', '-cr', '/Applications/Dark Engine GUI.app'], check=False)
        except Exception:
            pass

def create_icons():
    """Create platform-specific icons"""
    if not os.path.exists('convert_icon.py'):
        print("Error: convert_icon.py not found!")
        return False
        
    print("Creating icons...")
    subprocess.run([sys.executable, 'convert_icon.py'])
    return True

def build_app():
    """Build the application"""
    print("Building application...")
    if sys.platform == 'win32':
        spec_file = 'windows.spec'
    elif sys.platform == 'darwin':
        spec_file = 'macos.spec'
    else:
        spec_file = 'linux.spec'
    
    subprocess.run([
        sys.executable, 
        '-m', 
        'PyInstaller',
        spec_file,
        '--noconfirm'
    ])
    
    # For Linux, create AppImage
    if sys.platform == 'linux':
        create_appimage()

def create_appimage():
    """Create AppImage for Linux distribution"""
    if sys.platform != 'linux':
        return
    
    print("\nCreating AppImage...")
    try:
        # Download AppImage tool if not present
        if not os.path.exists('appimagetool'):
            subprocess.run([
                'wget', 'https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage',
                '-O', 'appimagetool'
            ])
            os.chmod('appimagetool', 0o755)
        
        # Create AppImage
        subprocess.run([
            './appimagetool',
            'dist/Dark Engine GUI',
            'dist/Dark-Engine-GUI.AppImage'
        ])
        
        # Sign the AppImage
        subprocess.run([
            'gpg', '--detach-sign',
            'dist/Dark-Engine-GUI.AppImage'
        ])
        
        print("AppImage created and signed successfully!")
    except Exception as e:
        print(f"Error creating AppImage: {e}")

def create_dmg():
    """Create DMG file on macOS"""
    if sys.platform == 'darwin':
        print("\nCreating DMG...")
        if os.path.exists('build_dmg.py'):
            subprocess.run([sys.executable, 'build_dmg.py'])
        else:
            print("Warning: build_dmg.py not found, skipping DMG creation")

def cleanup_old_files():
    """Clean up old DMG files and temporary artifacts"""
    print("Cleaning up old files...")
    
    # Files to remove (using patterns)
    patterns_to_remove = [
        'ModernChat.dmg',
        'rw.*.dmg',
        'Dark Engine GUI.dmg',
        # Add any other patterns here
    ]
    
    # Files to keep
    files_to_keep = [
        'Dark-Engine-GUI-1.0.0-' + datetime.now().strftime("%Y%m%d") + '.dmg',
        'ModernChat.spec',
        'build.py',
        'build_dmg.py',
        'convert_icon.py',
        'main.py',
        'LICENSE',
        'README.md',
        'requirements.txt'
    ]
    
    for file in os.listdir('.'):
        # Skip directories and files we want to keep
        if os.path.isdir(file) or file in files_to_keep:
            continue
            
        # Check if file matches any pattern to remove
        for pattern in patterns_to_remove:
            if fnmatch.fnmatch(file, pattern):
                try:
                    print(f"Removing: {file}")
                    os.remove(file)
                except Exception as e:
                    print(f"Warning: Could not remove {file}: {e}")
                break

def main():
    # Clean old builds
    clean_builds()
    
    # Create icons if needed
    if sys.platform == 'win32':
        create_icons()
    
    # Build the app
    build_app()
    
    # Create DMG on macOS
    create_dmg()
    
    # Clean up old files
    cleanup_old_files()
    
    print("\nBuild complete!")
    
if __name__ == "__main__":
    main() 