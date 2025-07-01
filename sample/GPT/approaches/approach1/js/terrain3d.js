// Grab your container
const container = document.getElementById('container');

// Scene + camera + renderer
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x001122);
const cam = new THREE.PerspectiveCamera(45, container.clientWidth/container.clientHeight, 0.1, 1000);
cam.position.set(0, 80, 120);
cam.lookAt(0,0,0);

const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
container.appendChild(renderer.domElement);

// Lighting for better terrain visualization
const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
directionalLight.position.set(50, 100, 50);
directionalLight.castShadow = true;
directionalLight.shadow.mapSize.width = 2048;
directionalLight.shadow.mapSize.height = 2048;
scene.add(directionalLight);

// Create a simple texture instead of webcam for reliability
const canvas = document.createElement('canvas');
canvas.width = 512;
canvas.height = 512;
const ctx = canvas.getContext('2d');

// Create a simple gradient texture
const gradient = ctx.createLinearGradient(0, 0, 512, 512);
gradient.addColorStop(0, '#1e3a8a');
gradient.addColorStop(0.5, '#059669');
gradient.addColorStop(1, '#d97706');
ctx.fillStyle = gradient;
ctx.fillRect(0, 0, 512, 512);

const videoTex = new THREE.CanvasTexture(canvas);

// Enhanced terrain geometry with topographic coloring
const grid = 128;
const geo = new THREE.PlaneGeometry(100, 100, grid, grid);

// Create height-based color material
const vertexShader = `
  varying vec3 vPosition;
  varying vec2 vUv;
  void main() {
    vPosition = position;
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const fragmentShader = `
  varying vec3 vPosition;
  varying vec2 vUv;
  uniform sampler2D videoTexture;

  vec3 getHeightColor(float height) {
    // Topographic color mapping
    if (height < -5.0) return vec3(0.0, 0.2, 0.8);      // Deep water (blue)
    if (height < 0.0) return vec3(0.2, 0.4, 0.9);       // Shallow water (light blue)
    if (height < 5.0) return vec3(0.8, 0.7, 0.4);       // Sand/beach (tan)
    if (height < 15.0) return vec3(0.3, 0.7, 0.2);      // Grass (green)
    if (height < 25.0) return vec3(0.5, 0.4, 0.2);      // Hills (brown)
    return vec3(0.9, 0.9, 0.9);                         // Peaks (white)
  }

  void main() {
    vec3 heightColor = getHeightColor(vPosition.y);
    vec4 videoColor = texture2D(videoTexture, vUv);

    // Blend height color with video for reference
    vec3 finalColor = mix(heightColor, videoColor.rgb, 0.3);

    gl_FragColor = vec4(finalColor, 1.0);
  }
`;

const mat = new THREE.ShaderMaterial({
  uniforms: {
    videoTexture: { value: videoTex }
  },
  vertexShader: vertexShader,
  fragmentShader: fragmentShader,
  side: THREE.DoubleSide
});

const mesh = new THREE.Mesh(geo, mat);
mesh.rotation.x = -Math.PI/2;
mesh.receiveShadow = true;
scene.add(mesh);

// Enhanced terrain interaction system
const ray = new THREE.Raycaster(), mouse = new THREE.Vector2();
let isMouseDown = false;
let brushSize = 5.0;
let brushStrength = 0.5;
let isRaising = true;

// Terrain modification function
function modifyTerrain(intersectionPoint, raise = true) {
  const positions = geo.attributes.position;
  const vertex = new THREE.Vector3();

  for (let i = 0; i < positions.count; i++) {
    vertex.fromBufferAttribute(positions, i);
    const distance = intersectionPoint.distanceTo(vertex);

    if (distance < brushSize) {
      const influence = Math.cos((distance / brushSize) * Math.PI * 0.5);
      const heightChange = influence * brushStrength * (raise ? 1 : -1);
      positions.setY(i, positions.getY(i) + heightChange);
    }
  }

  positions.needsUpdate = true;
  geo.computeVertexNormals();
}

// Mouse interaction events
renderer.domElement.addEventListener('mousedown', e => {
  isMouseDown = true;
  isRaising = e.button === 0; // Left click raises, right click lowers
});

renderer.domElement.addEventListener('mouseup', () => {
  isMouseDown = false;
});

renderer.domElement.addEventListener('mousemove', e => {
  if (!isMouseDown) return;

  mouse.x = (e.clientX / renderer.domElement.clientWidth) * 2 - 1;
  mouse.y = -(e.clientY / renderer.domElement.clientHeight) * 2 + 1;
  ray.setFromCamera(mouse, cam);

  const hits = ray.intersectObject(mesh);
  if (hits.length) {
    modifyTerrain(hits[0].point, isRaising);
  }
});

// Prevent context menu on right click
renderer.domElement.addEventListener('contextmenu', e => e.preventDefault());

// Keyboard controls for brush settings
document.addEventListener('keydown', e => {
  switch(e.key) {
    case '=':
    case '+':
      brushSize = Math.min(brushSize + 1, 20);
      console.log('Brush size:', brushSize);
      break;
    case '-':
      brushSize = Math.max(brushSize - 1, 1);
      console.log('Brush size:', brushSize);
      break;
    case '[':
      brushStrength = Math.max(brushStrength - 0.1, 0.1);
      console.log('Brush strength:', brushStrength.toFixed(1));
      break;
    case ']':
      brushStrength = Math.min(brushStrength + 0.1, 2.0);
      console.log('Brush strength:', brushStrength.toFixed(1));
      break;
    case 'r':
      // Reset terrain
      const positions = geo.attributes.position;
      for (let i = 0; i < positions.count; i++) {
        positions.setY(i, 0);
      }
      positions.needsUpdate = true;
      geo.computeVertexNormals();
      console.log('Terrain reset');
      break;
  }
});

// Camera controls
let cameraAngle = 0;
document.addEventListener('keydown', e => {
  switch(e.key) {
    case 'ArrowLeft':
      cameraAngle -= 0.1;
      cam.position.x = Math.sin(cameraAngle) * 120;
      cam.position.z = Math.cos(cameraAngle) * 120;
      cam.lookAt(0, 0, 0);
      break;
    case 'ArrowRight':
      cameraAngle += 0.1;
      cam.position.x = Math.sin(cameraAngle) * 120;
      cam.position.z = Math.cos(cameraAngle) * 120;
      cam.lookAt(0, 0, 0);
      break;
    case 'ArrowUp':
      cam.position.y = Math.min(cam.position.y + 5, 150);
      cam.lookAt(0, 0, 0);
      break;
    case 'ArrowDown':
      cam.position.y = Math.max(cam.position.y - 5, 20);
      cam.lookAt(0, 0, 0);
      break;
  }
});

// Add some initial terrain features
function createInitialTerrain() {
  const positions = geo.attributes.position;

  for (let i = 0; i < positions.count; i++) {
    const x = positions.getX(i);
    const z = positions.getZ(i);

    // Create some hills and valleys
    const height = Math.sin(x * 0.1) * Math.cos(z * 0.1) * 10 +
                   Math.sin(x * 0.05) * Math.sin(z * 0.05) * 5;

    positions.setY(i, height);
  }

  positions.needsUpdate = true;
  geo.computeVertexNormals();
}

// Initialize terrain
setTimeout(createInitialTerrain, 1000);

// Animation loop with enhanced features
(function animate(){
  requestAnimationFrame(animate);
  if (videoTex) videoTex.needsUpdate = true;

  // Gentle camera rotation for demo effect
  // cam.position.x = Math.sin(Date.now() * 0.0005) * 120;
  // cam.position.z = Math.cos(Date.now() * 0.0005) * 120;
  // cam.lookAt(0, 0, 0);

  renderer.render(scene, cam);
})();

// Display controls
console.log(`
AR Sandbox Controls:
- Left click + drag: Raise terrain
- Right click + drag: Lower terrain
- +/- keys: Adjust brush size
- [/] keys: Adjust brush strength
- Arrow keys: Move camera
- R key: Reset terrain
`);

// Add UI overlay for controls
const controlsDiv = document.createElement('div');
controlsDiv.style.position = 'absolute';
controlsDiv.style.top = '10px';
controlsDiv.style.left = '10px';
controlsDiv.style.color = 'white';
controlsDiv.style.fontFamily = 'monospace';
controlsDiv.style.fontSize = '14px';
controlsDiv.style.background = 'rgba(0,0,0,0.7)';
controlsDiv.style.padding = '10px';
controlsDiv.style.borderRadius = '5px';
controlsDiv.innerHTML = `
<strong>AR Sandbox Controls:</strong><br>
🖱️ Left drag: Raise terrain<br>
🖱️ Right drag: Lower terrain<br>
⌨️ +/- : Brush size<br>
⌨️ [/] : Brush strength<br>
⌨️ Arrows: Camera<br>
⌨️ R : Reset terrain
`;
document.body.appendChild(controlsDiv);
