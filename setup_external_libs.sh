#!/bin/bash
# 🔧 AR Sandbox RC - External Libraries Setup Script (Bash)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    local message="$1"
    local color="$2"
    echo -e "${color}${message}${NC}"
}

print_status "🚀 AR Sandbox RC - External Libraries Setup" "$BLUE"
print_status "=============================================" "$BLUE"

# Create external_libs directory
mkdir -p external_libs
cd external_libs

# Download Three.js
if [ ! -d "three.js" ]; then
    print_status "📥 Downloading Three.js..." "$BLUE"
    wget -q https://github.com/mrdoob/three.js/archive/refs/heads/dev.zip -O three.js.zip
    unzip -q three.js.zip
    mv three.js-dev three.js
    rm three.js.zip
    print_status "✅ Three.js ready" "$GREEN"
else
    print_status "⚠️ Three.js already exists" "$YELLOW"
fi

# Download Matter.js
if [ ! -d "matter-js" ]; then
    print_status "📥 Downloading Matter.js..." "$BLUE"
    wget -q https://github.com/liabru/matter-js/archive/refs/heads/master.zip -O matter-js.zip
    unzip -q matter-js.zip
    mv matter-js-master matter-js
    rm matter-js.zip
    print_status "✅ Matter.js ready" "$GREEN"
else
    print_status "⚠️ Matter.js already exists" "$YELLOW"
fi

# Download ML5.js
if [ ! -d "ml5-library" ]; then
    print_status "📥 Downloading ML5.js..." "$BLUE"
    wget -q https://github.com/ml5js/ml5-library/archive/refs/heads/main.zip -O ml5.zip
    unzip -q ml5.zip
    mv ml5-library-main ml5-library
    rm ml5.zip
    print_status "✅ ML5.js ready" "$GREEN"
else
    print_status "⚠️ ML5.js already exists" "$YELLOW"
fi

# Clone Divine Voxel Engine
if [ ! -d "Divine-Voxel-Engine" ]; then
    print_status "🔄 Cloning Divine Voxel Engine..." "$BLUE"
    git clone --quiet https://github.com/Divine-Star-Software/DivineVoxelEngine.git Divine-Voxel-Engine
    print_status "✅ Divine Voxel Engine ready" "$GREEN"
else
    print_status "⚠️ Divine Voxel Engine already exists" "$YELLOW"
fi

# Clone Shader Web Background
if [ ! -d "shader-web-background" ]; then
    print_status "🔄 Cloning Shader Web Background..." "$BLUE"
    git clone --quiet https://github.com/xemantic/shader-web-background.git
    print_status "✅ Shader Web Background ready" "$GREEN"
else
    print_status "⚠️ Shader Web Background already exists" "$YELLOW"
fi

# Clone Sandboxels
if [ ! -d "sandboxels" ]; then
    print_status "🔄 Cloning Sandboxels..." "$BLUE"
    git clone --quiet https://github.com/R74n/sandboxels.git
    print_status "✅ Sandboxels ready" "$GREEN"
else
    print_status "⚠️ Sandboxels already exists" "$YELLOW"
fi

# Create CDN fallback file
cat > cdn_fallbacks.html << 'EOF'
<!-- CDN Fallbacks for External Libraries -->
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
</script>
EOF

cd ..

print_status "=============================================" "$BLUE"
print_status "🎉 External libraries setup complete!" "$GREEN"
print_status "📁 All libraries are in the external_libs/ folder" "$BLUE"
print_status "💡 CDN fallbacks available if local files fail" "$BLUE"
print_status "🚀 Your AR Sandbox RC is ready to go!" "$GREEN"
