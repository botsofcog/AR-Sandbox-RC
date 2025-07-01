#!/usr/bin/env python3
"""
🔧 AR Sandbox RC - External Libraries Setup Script
Downloads and organizes all external dependencies
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path

def print_status(message, status="INFO"):
    """Print colored status messages"""
    colors = {
        "INFO": "\033[94m",      # Blue
        "SUCCESS": "\033[92m",   # Green  
        "WARNING": "\033[93m",   # Yellow
        "ERROR": "\033[91m",     # Red
        "RESET": "\033[0m"       # Reset
    }
    print(f"{colors.get(status, '')}{message}{colors['RESET']}")

def download_file(url, destination):
    """Download file with progress"""
    try:
        print_status(f"📥 Downloading {os.path.basename(destination)}...")
        urllib.request.urlretrieve(url, destination)
        print_status(f"✅ Downloaded {os.path.basename(destination)}", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"❌ Failed to download {url}: {e}", "ERROR")
        return False

def extract_zip(zip_path, extract_to):
    """Extract ZIP file"""
    try:
        print_status(f"📦 Extracting {os.path.basename(zip_path)}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        os.remove(zip_path)  # Clean up ZIP file
        print_status(f"✅ Extracted {os.path.basename(zip_path)}", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"❌ Failed to extract {zip_path}: {e}", "ERROR")
        return False

def clone_repo(repo_url, destination):
    """Clone git repository"""
    try:
        print_status(f"🔄 Cloning {repo_url}...")
        subprocess.run(['git', 'clone', repo_url, destination], 
                      check=True, capture_output=True)
        print_status(f"✅ Cloned {os.path.basename(destination)}", "SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"❌ Failed to clone {repo_url}: {e}", "ERROR")
        return False

def setup_external_libs():
    """Main setup function"""
    print_status("🚀 AR Sandbox RC - External Libraries Setup", "INFO")
    print_status("=" * 60, "INFO")
    
    # Create external_libs directory
    external_dir = Path("external_libs")
    external_dir.mkdir(exist_ok=True)
    
    # Define external libraries to download
    libraries = {
        # JavaScript Libraries (CDN downloads)
        "three.js": {
            "type": "zip",
            "url": "https://github.com/mrdoob/three.js/archive/refs/heads/dev.zip",
            "extract_name": "three.js-dev"
        },
        "matter-js": {
            "type": "zip", 
            "url": "https://github.com/liabru/matter-js/archive/refs/heads/master.zip",
            "extract_name": "matter-js-master"
        },
        "ml5-library": {
            "type": "zip",
            "url": "https://github.com/ml5js/ml5-library/archive/refs/heads/main.zip", 
            "extract_name": "ml5-library-main"
        },
        
        # Voxel Engines
        "Divine-Voxel-Engine": {
            "type": "git",
            "url": "https://github.com/Divine-Star-Software/DivineVoxelEngine.git"
        },
        
        # Shader Effects
        "shader-web-background": {
            "type": "git", 
            "url": "https://github.com/xemantic/shader-web-background.git"
        },
        
        # Sandbox Engines
        "sandboxels": {
            "type": "git",
            "url": "https://github.com/R74n/sandboxels.git"
        }
    }
    
    success_count = 0
    total_count = len(libraries)
    
    for lib_name, lib_info in libraries.items():
        print_status(f"\n🔧 Setting up {lib_name}...", "INFO")
        lib_path = external_dir / lib_name
        
        # Skip if already exists
        if lib_path.exists():
            print_status(f"⚠️ {lib_name} already exists, skipping...", "WARNING")
            success_count += 1
            continue
            
        if lib_info["type"] == "zip":
            # Download and extract ZIP
            zip_path = external_dir / f"{lib_name}.zip"
            if download_file(lib_info["url"], zip_path):
                if extract_zip(zip_path, external_dir):
                    # Rename extracted folder
                    extracted_path = external_dir / lib_info["extract_name"]
                    if extracted_path.exists():
                        extracted_path.rename(lib_path)
                        success_count += 1
                        
        elif lib_info["type"] == "git":
            # Clone git repository
            if clone_repo(lib_info["url"], lib_path):
                success_count += 1
    
    # Create CDN fallback HTML
    create_cdn_fallback()
    
    # Summary
    print_status("\n" + "=" * 60, "INFO")
    print_status(f"📊 Setup Summary:", "INFO")
    print_status(f"✅ Successfully set up: {success_count}/{total_count} libraries", "SUCCESS")
    
    if success_count == total_count:
        print_status("🎉 All external libraries ready!", "SUCCESS")
    else:
        print_status("⚠️ Some libraries failed to download", "WARNING")
        print_status("💡 You can use CDN fallbacks in HTML demos", "INFO")

def create_cdn_fallback():
    """Create CDN fallback configuration"""
    cdn_config = """<!-- CDN Fallbacks for External Libraries -->
<script>
// CDN URLs for external libraries
window.CDN_FALLBACKS = {
    'three.js': 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js',
    'matter-js': 'https://cdnjs.cloudflare.com/ajax/libs/matter-js/0.17.1/matter.min.js',
    'ml5': 'https://unpkg.com/ml5@latest/dist/ml5.min.js'
};

// Function to load library with fallback
function loadLibraryWithFallback(localPath, cdnUrl) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = localPath;
        script.onload = resolve;
        script.onerror = () => {
            console.warn(`Loading ${localPath} failed, trying CDN...`);
            const fallbackScript = document.createElement('script');
            fallbackScript.src = cdnUrl;
            fallbackScript.onload = resolve;
            fallbackScript.onerror = reject;
            document.head.appendChild(fallbackScript);
        };
        document.head.appendChild(script);
    });
}
</script>"""
    
    with open("external_libs/cdn_fallbacks.html", "w") as f:
        f.write(cdn_config)
    
    print_status("✅ Created CDN fallback configuration", "SUCCESS")

if __name__ == "__main__":
    try:
        setup_external_libs()
    except KeyboardInterrupt:
        print_status("\n🛑 Setup interrupted by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_status(f"\n❌ Setup failed: {e}", "ERROR")
        sys.exit(1)
