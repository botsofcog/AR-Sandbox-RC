







import { useRef, useEffect, useCallback, useState, useMemo } from 'react';
import { SandboxSettings, ColorStop, GameSettings, Vehicle, MissionState, ErrorInfo, VEHICLE_TYPES, TerrainType, VehicleMode } from '../types';
import { createNoise2D, Noise2D } from 'simplex-noise';
import { v4 as uuidv4 } from 'uuid';
import { VEHICLE_SPECS, PHYSICS, AI } from '../constants';
import { Logger } from '../services/logger';

export const CANVAS_RESOLUTION = 512;
const DIG_STRENGTH = 2;
const TILT_EFFECT_MULTIPLIER = 2.5;

// Physics constants
const SLUMP_FACTOR = 0.25; // More aggressive slumping
const TALUS_ANGLE = 4;     // Land wants to be much flatter
const FLOW_SPEED = 0.4;    
const EROSION_FACTOR = 0.002;
const EROSION_FLOW_THRESHOLD = 0.05;

// AI and Vehicle Action Constants
const VEHICLE_ACTION_RADIUS = 15;
const VEHICLE_ACTION_STRENGTH = 0.8; 
const VEHICLE_ACTION_COOLDOWN = 60; // Frames for a task cycle
const VEHICLE_SEARCH_RADIUS = 150; 
const AI_SEARCH_TIMEOUT = 300;


interface SandboxSimulationProps {
  settings: SandboxSettings;
  colorMap: ColorStop[];
  gameSettings: GameSettings;
  missionState: MissionState;
  setMissionState: React.Dispatch<React.SetStateAction<MissionState>>;
  calibrationTrigger: number;
  regenerationTrigger: number;
  onCalibrationResult: (success: boolean, message: string, errorInfo?: ErrorInfo) => void;
  onTreasureDig: (x: number, y: number) => void;
  showToast: (message: string, type: 'success' | 'error' | 'info' | 'warning') => void;
  heightMapRef: React.MutableRefObject<Float32Array | null>;
  fleetMode: 'work' | 'idle';
}

// Memoized color parser to improve rendering performance
const parseColor = (() => {
    const cache = new Map<string, [number, number, number]>();
    return (colorStr: string): [number, number, number] => {
        if (cache.has(colorStr)) return cache.get(colorStr)!;
        if (colorStr.startsWith('#')) {
            const r = parseInt(colorStr.slice(1, 3), 16), g = parseInt(colorStr.slice(3, 5), 16), b = parseInt(colorStr.slice(5, 7), 16);
            const result: [number, number, number] = [r, g, b];
            cache.set(colorStr, result);
            return result;
        }
        return [0, 0, 0]; // Fallback
    };
})();


export const useSandboxSimulation = ({ settings, colorMap, gameSettings, missionState, setMissionState, calibrationTrigger, regenerationTrigger, onCalibrationResult, onTreasureDig, heightMapRef, fleetMode }: SandboxSimulationProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const processorCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const initialSeaLevel = useRef<number>(settings.seaLevel);
  const vehiclesRef = useRef<Vehicle[]>([]);
  const animationFrameId = useRef<number>();
  const isDragging = useRef(false);
  const [isCalibrating, setIsCalibrating] = useState(false);
  const mousePositionRef = useRef<{x: number, y: number} | null>(null);
  const [brushSize, setBrushSize] = useState(30);
  const noise2D = useMemo(() => createNoise2D(Math.random), []);
  const [mediaStream, setMediaStream] = useState<MediaStream | null>(null);
  
  const landRef = useRef<Float32Array | null>(null);
  const waterRef = useRef<Float32Array | null>(null);

  const R = CANVAS_RESOLUTION;
  
  const generateTerrain = useCallback((terrainType: TerrainType, noise: Noise2D) => {
    const data = new Float32Array(R * R);
    const scale = 0.02, persistence = 0.5, lacunarity = 2.0, octaves = 6;
    for (let y = 0; y < R; y++) {
      for (let x = 0; x < R; x++) {
        let amp = 1, freq = 1, noiseH = 0;
        for (let i = 0; i < octaves; i++) {
          noiseH += noise(x * freq * scale, y * freq * scale) * amp;
          amp *= persistence; freq *= lacunarity;
        }
        let v: number;
        switch(terrainType) {
            case 'mountains': v = Math.pow((noiseH + 1) / 2, 2) * 255; break;
            case 'canyons': v = Math.pow(1 - Math.abs(noise((noiseH + 1) / 2 * 5, (noiseH + 1) / 2 * 5)), 3) * 255; break;
            case 'plains': v = ((noise(x*scale*0.5, y*scale*0.5) + 1)/2) * 100 + (noise(x*scale*2, y*scale*2) * 15); break;
            case 'islands': default:
                const dX = (x-R/2)/(R/2), dY = (y-R/2)/(R/2);
                v = ((noiseH + 1)/2) * (1-Math.sqrt(dX*dX+dY*dY)) * 255; break;
        }
        data[y * R + x] = Math.max(0, Math.min(255, v));
      }
    }
    return data;
  }, [R]);

  const runPhysicsStep = useCallback((land: Float32Array, water: Float32Array, seaLevel: number) => {
    const landDeltas = new Float32Array(R * R), waterDeltas = new Float32Array(R*R);
    for (let y = 0; y < R; y++) for (let x = 0; x < R; x++) {
        const i = y*R+x, i_land_h = land[i];
        const neighbors = [i-1, i+1, i-R, i+R];
        // Land Slumping
        for (const ni of neighbors) {
            if (ni<0||ni>=R*R||(x===0&&ni===i-1)||(x===R-1&&ni===i+1)) continue;
            const diff = i_land_h - land[ni];
            if (diff > TALUS_ANGLE) {
                const amount = (diff-TALUS_ANGLE)*SLUMP_FACTOR*0.5;
                landDeltas[i] -= amount; landDeltas[ni] += amount;
            }
        }
        // Water Flow & Erosion
        const i_water_h = water[i];
        if (i_water_h > 0) {
            const totalH = i_land_h + i_water_h; let totalFlowOut = 0;
            for (const ni of neighbors) {
                if (ni<0||ni>=R*R||(x===0&&ni===i-1)||(x===R-1&&ni===i+1)) continue;
                const diff = totalH - (land[ni] + water[ni]);
                if (diff > 0) {
                    let flow = Math.min(i_water_h - totalFlowOut, diff/2) * FLOW_SPEED;
                    flow = Math.max(0, flow);
                    waterDeltas[i] -= flow; waterDeltas[ni] += flow;
                    totalFlowOut += flow;
                    if (flow > EROSION_FLOW_THRESHOLD) {
                        const erosion = Math.min(i_land_h, flow*EROSION_FACTOR);
                        landDeltas[i] -= erosion; landDeltas[ni] += erosion;
                    }
                }
            }
        }
    }
    for (let i = 0; i < R*R; i++) {
        land[i] += landDeltas[i]; if(isNaN(land[i])) land[i] = 0;
        water[i] += waterDeltas[i]; if(isNaN(water[i])) water[i] = 0;
        if(water[i]<0.01) water[i] = 0;
    }
    // Sea acts as infinite source/sink at edges
    for (let i=0;i<R;i++){for(let j of[0,R-1]){[i*R+j,j*R+i].forEach(idx=>{if(land[idx]+water[idx]<seaLevel)water[idx]=seaLevel-land[idx];});}}
  }, [R]);

  const modifyTerrain = useCallback((x: number, y: number, brushSize: number, strength: number) => {
      if (!landRef.current) return 0;
      const cX=Math.floor(x), cY=Math.floor(y), rad=Math.floor(brushSize/2), rSq=rad*rad; let totalChange=0;
      for (let i=-rad;i<=rad;i++) for (let j=-rad;j<=rad;j++) {
        const cX_j=cX+j, cY_i=cY+i, dSq=j*j+i*i;
        if(dSq<rSq&&cX_j>=0&&cX_j<R&&cY_i>=0&&cY_i<R){
            const falloff=1-(dSq/rSq), change=strength*falloff, idx=cY_i*R+cX_j, origH=landRef.current[idx];
            landRef.current[idx]+=change;
            if(landRef.current[idx]<0)landRef.current[idx]=0; if(landRef.current[idx]>255)landRef.current[idx]=255;
            totalChange+=(landRef.current[idx]-origH);
        }
      } return totalChange;
  }, [R]);

  const drawHeightMap = useCallback((ctx: CanvasRenderingContext2D, heightMap: Float32Array, sortedColorMap: ColorStop[]) => {
    const imgData=ctx.createImageData(R,R), data=imgData.data, displayHM=new Float32Array(heightMap);
    const tiltXRad=settings.tiltX*(Math.PI/180)*TILT_EFFECT_MULTIPLIER, tiltYRad=settings.tiltY*(Math.PI/180)*TILT_EFFECT_MULTIPLIER;
    for(let y=0;y<R;y++)for(let x=0;x<R;x++){displayHM[y*R+x]+=(Math.sin(tiltXRad)*((y/R)-0.5)+Math.sin(tiltYRad)*((x/R)-0.5))*128;}
    for (let i=0;i<heightMap.length;i++){
        const h=Math.max(0,Math.min(255,displayHM[i])); let color:[number,number,number]=[0,0,0];
        for (let j=0;j<sortedColorMap.length-1;j++) {
            const c1=sortedColorMap[j],c2=sortedColorMap[j+1];
            if(h>=c2.height&&h<=c1.height){
                const t=c1.height===c2.height?1:(h-c2.height)/(c1.height-c2.height),rgb1=parseColor(c1.color),rgb2=parseColor(c2.color);
                color=[rgb2[0]+(rgb1[0]-rgb2[0])*t,rgb2[1]+(rgb1[1]-rgb2[1])*t,rgb2[2]+(rgb1[2]-rgb2[2])*t];
                break;
            }
        } if(h<sortedColorMap[sortedColorMap.length-1].height) color=parseColor(sortedColorMap[sortedColorMap.length-1].color);
        const idx=i*4; data[idx]=color[0]; data[idx+1]=color[1]; data[idx+2]=color[2]; data[idx+3]=255;
        if(settings.contourLines&&Math.max(0,Math.min(255,heightMap[i]))>settings.seaLevel&&Math.floor(heightMap[i])%settings.linesDistance<1){data[idx]=data[idx+1]=data[idx+2]=0;}
    } ctx.putImageData(imgData,0,0);
  }, [R, settings.contourLines, settings.linesDistance, settings.seaLevel, settings.tiltX, settings.tiltY]);
  
  const isLandDry = useCallback(() => {
    if(!landRef.current||missionState.status!=='active')return false;
    for (let i=0;i<landRef.current.length;i++) if(landRef.current[i]<initialSeaLevel.current) return false;
    return true;
  }, [missionState.status]);

  // --- NEW AI HELPER FUNCTIONS ---
  const findHighestPointNearby = (v: Vehicle, heightMap: Float32Array) => {
    let best: {x:number, y:number, h:number} | null = null;
    for (let i = 0; i < 30; i++) {
        const a = Math.random()*2*Math.PI, r = Math.random()*VEHICLE_SEARCH_RADIUS;
        const x = Math.floor(v.x+Math.cos(a)*r), y = Math.floor(v.y+Math.sin(a)*r);
        if(x<0||x>=R||y<0||y>=R) continue;
        const h = heightMap[y*R+x];
        if (h > settings.seaLevel + 10 && (!best || h > best.h)) best = {x,y,h};
    }
    return best ? {x: best.x, y: best.y} : null;
  };

  const findLowestPointNearby = (v: Vehicle, heightMap: Float32Array) => {
    let best: {x:number, y:number, h:number} | null = null;
    for (let i = 0; i < 30; i++) {
        const a = Math.random()*2*Math.PI, r = Math.random()*VEHICLE_SEARCH_RADIUS;
        const x = Math.floor(v.x+Math.cos(a)*r), y = Math.floor(v.y+Math.sin(a)*r);
        if(x<0||x>=R||y<0||y>=R) continue;
        const h = heightMap[y*R+x];
        if (h < settings.seaLevel && (!best || h < best.h)) best = {x,y,h};
    }
    return best ? {x: best.x, y: best.y} : null;
  };
  
  const findSteepestSlopeNearby = (v: Vehicle, heightMap: Float32Array) => {
      let best: {x:number, y:number, lowX: number, lowY: number, grad: number} | null = null;
      for (let i = 0; i < 30; i++) {
        const a = Math.random()*2*Math.PI, r = Math.random()*VEHICLE_SEARCH_RADIUS;
        const x = Math.floor(v.x+Math.cos(a)*r), y = Math.floor(v.y+Math.sin(a)*r);
        if(x<0||x>=R||y<0||y>=R) continue;
        const h = heightMap[y*R+x];
        if (h < settings.seaLevel + 5) continue; // Don't level ground that's already low
        const neighbors = [[x,y-1], [x+1,y], [x,y+1], [x-1,y]];
        for (const [nx, ny] of neighbors) {
            if (nx<0||nx>=R||ny<0||ny>=R) continue;
            const nh = heightMap[ny*R+nx];
            const grad = h-nh;
            if (grad > AI.BULLDOZER_MIN_GRADIENT && (!best || grad > best.grad)) best = {x,y,lowX:nx, lowY:ny, grad};
        }
    }
    return best ? {x: best.x, y: best.y, lowX: best.lowX, lowY: best.lowY } : null;
  }

  const drawVehicle = useCallback((ctx: CanvasRenderingContext2D, v: Vehicle) => {
      ctx.save(); ctx.translate(v.x, v.y); ctx.rotate(v.angle);
      const spec=VEHICLE_SPECS[v.type],w=spec.size,h=spec.size*0.8;
      ctx.fillStyle=spec.color; ctx.fillRect(-w/2,-h/2,w,h);
      ctx.fillStyle="rgba(0,0,0,0.4)"; ctx.fillRect(-w/2,-h/2,w,h*0.3);
      if(v.type==='bulldozer'){ctx.fillStyle='#666'; ctx.fillRect(w/2,-h/2-2,3,h+4);}
      if(v.type==='excavator'){ctx.strokeStyle='#555';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(w*0.1,0);ctx.lineTo(w*0.6,0);ctx.lineTo(w*0.7,-3);ctx.stroke();}
      ctx.strokeStyle='#000'; ctx.lineWidth=1; ctx.strokeRect(-w/2,-h/2,w,h);
      ctx.restore();
  }, []);

  // --- REBUILT AI AND VEHICLE LOGIC ---
  const updateAndDrawVehicles = useCallback((ctx: CanvasRenderingContext2D, heightMap: Float32Array, fleetMode: 'work' | 'idle', missionActive: boolean) => {
    vehiclesRef.current.forEach(v => {
        if (v.taskCooldown > 0) v.taskCooldown--;

        // --- GLOBAL MODE MANAGEMENT ---
        const isWorking = fleetMode === 'work' && missionActive;
        if (isWorking && (v.mode === 'PARKED' || v.mode === 'RETURNING_TO_BASE')) v.mode = 'IDLE';
        if (!isWorking && v.mode !== 'PARKED' && v.mode !== 'RETURNING_TO_BASE') v.mode = 'RETURNING_TO_BASE';
        if (v.mode === 'IDLE') {
             v.mode = isWorking ? 'SEEKING_WORK_SITE' : 'RETURNING_TO_BASE';
        }
        
        // --- AI STATE MACHINE ---
        switch(v.mode) {
            case 'RETURNING_TO_BASE':
                if (!v.target) v.target = { x: AI.BASE_LOCATION.x + (Math.random()-0.5)*AI.BASE_PARKING_RADIUS, y: AI.BASE_LOCATION.y + (Math.random()-0.5)*AI.BASE_PARKING_RADIUS };
                if (Math.hypot(v.x-v.target.x, v.y-v.target.y) < 10) { v.mode = 'PARKED'; v.target = null; }
                break;
            case 'PARKED': v.vx*=0.8; v.vy*=0.8; break; // Slow to a stop
            case 'SEEKING_WORK_SITE':
                if(v.type === 'excavator') {
                    const site = findHighestPointNearby(v, heightMap);
                    if(site){ v.target = site; v.mode = 'MOVING_TO_WORK_SITE';}
                } else if (v.type === 'bulldozer') {
                    const site = findSteepestSlopeNearby(v, heightMap);
                    if(site){ v.target = {x:site.x, y:site.y}; v.secondaryTarget = {x:site.lowX, y:site.lowY}; v.mode = 'MOVING_TO_WORK_SITE'; }
                }
                break;
            case 'MOVING_TO_WORK_SITE':
                if(!v.target) { v.mode = 'SEEKING_WORK_SITE'; break; }
                if(Math.hypot(v.x-v.target.x, v.y-v.target.y) < 10) { v.mode = 'WORKING'; v.taskCooldown = VEHICLE_ACTION_COOLDOWN; }
                break;
            case 'WORKING':
                if (v.taskCooldown <= 1) { v.mode = 'SEEKING_WORK_SITE'; break; }
                if(v.type === 'excavator') { // Digging
                    modifyTerrain(v.x, v.y, VEHICLE_ACTION_RADIUS, -VEHICLE_ACTION_STRENGTH * 0.5);
                    v.payload += 0.5;
                    v.angle -= 0.05;
                    if (v.payload >= AI.EXCAVATOR_PAYLOAD_CAPACITY) { v.mode = 'MOVING_TO_DUMP_SITE'; v.target = null; }
                } else if (v.type === 'bulldozer') { // Leveling
                    if (!v.secondaryTarget) { v.mode = 'SEEKING_WORK_SITE'; break; }
                    v.angle = Math.atan2(v.secondaryTarget.y - v.y, v.secondaryTarget.x - v.x);
                    const spec=VEHICLE_SPECS[v.type];
                    const pushPointX = v.x + Math.cos(v.angle) * (spec.size/2);
                    const pushPointY = v.y + Math.sin(v.angle) * (spec.size/2);
                    modifyTerrain(v.x, v.y, VEHICLE_ACTION_RADIUS*0.8, -AI.BULLDOZER_LEVELING_STRENGTH);
                    const change = modifyTerrain(pushPointX, pushPointY, VEHICLE_ACTION_RADIUS*0.8, AI.BULLDOZER_LEVELING_STRENGTH);
                    setMissionState(prev => ({...prev, score: prev.score + change * 10}));
                }
                break;
            case 'MOVING_TO_DUMP_SITE':
                if (!v.target) v.target = findLowestPointNearby(v, heightMap);
                if (!v.target) { v.mode = 'SEEKING_WORK_SITE'; break; }
                if (Math.hypot(v.x-v.target.x, v.y-v.target.y) < 10) v.mode = 'DUMPING';
                break;
            case 'DUMPING':
                if (v.taskCooldown <= 1 || v.payload <= 0) { v.payload = 0; v.mode = 'SEEKING_WORK_SITE'; break; }
                const change = modifyTerrain(v.x, v.y, VEHICLE_ACTION_RADIUS, VEHICLE_ACTION_STRENGTH);
                setMissionState(prev => ({...prev, score: prev.score + change * 10}));
                v.payload -= 1;
                v.angle += 0.05;
                break;
        }

        // --- MOVEMENT LOGIC ---
        let targetAngle = v.angle;
        let acceleration = PHYSICS.ACCELERATION_FORCE;

        const v_idx = Math.floor(v.y) * R + Math.floor(v.x);
        const isInWater = v_idx >= 0 && v_idx < R * R && waterRef.current![v_idx] > 0.1;

        if (isInWater) {
            acceleration *= 0.2; // Slow down significantly in water
            let nearestLand = null;
            let minDistanceSq = Infinity;
            
            // Spiraling search for land
            for (let r = 5; r < 60; r += 5) {
                for (let a = 0; a < Math.PI * 2; a += Math.PI / 4) {
                    const sx = Math.floor(v.x + Math.cos(a) * r);
                    const sy = Math.floor(v.y + Math.sin(a) * r);
                    if(sx >= 0 && sx < R && sy >= 0 && sy < R) {
                        const s_idx = sy * R + sx;
                        if(waterRef.current![s_idx] < 0.1) {
                            const distSq = (sx-v.x)**2 + (sy-v.y)**2;
                            if (distSq < minDistanceSq) {
                                minDistanceSq = distSq;
                                nearestLand = {x: sx, y: sy};
                            }
                        }
                    }
                }
                if (nearestLand) break; // Found land, stop searching
            }
            
            if (nearestLand) {
                targetAngle = Math.atan2(nearestLand.y - v.y, nearestLand.x - v.x);
            } else if (v.target) {
                targetAngle = Math.atan2(v.target.y - v.y, v.target.x - v.x);
            }
        } else if (v.target) {
            targetAngle = Math.atan2(v.target.y - v.y, v.target.x - v.x);
        }
        
        if(v.mode === 'PARKED' || v.mode === 'WORKING') acceleration = 0;
        
        v.angle += Math.sin(targetAngle-v.angle)*0.2;
        v.vx += Math.cos(v.angle)*acceleration; v.vy += Math.sin(v.angle)*acceleration;
        v.vx *= PHYSICS.FRICTION; v.vy *= PHYSICS.FRICTION;
        const speed=Math.hypot(v.vx,v.vy); if(speed>PHYSICS.MAX_SPEED){v.vx=(v.vx/speed)*PHYSICS.MAX_SPEED;v.vy=(v.vy/speed)*PHYSICS.MAX_SPEED;}
        v.x+=v.vx; v.y+=v.vy;
        if (v.x<0){v.x=0;v.vx*=-1;} if(v.x>=R){v.x=R-1;v.vx*=-1;} if (v.y<0){v.y=0;v.vy*=-1;} if(v.y>=R){v.y=R-1;v.vy*=-1;}
        drawVehicle(ctx, v);
    });
  }, [R, modifyTerrain, setMissionState, drawVehicle, settings.seaLevel]);

  const animate = useCallback(() => {
    const canvas=canvasRef.current; if(!canvas)return;
    const ctx=canvas.getContext('2d',{willReadFrequently:true});
    if(!ctx||!landRef.current||!waterRef.current||!heightMapRef.current){animationFrameId.current=requestAnimationFrame(animate); return;}
    runPhysicsStep(landRef.current, waterRef.current, settings.seaLevel);
    
    if(settings.displayKinectView&&videoRef.current&&!videoRef.current.paused){
        if(!processorCanvasRef.current){processorCanvasRef.current=document.createElement('canvas');processorCanvasRef.current.width=R;processorCanvasRef.current.height=R;}
        const pCtx=processorCanvasRef.current.getContext('2d',{willReadFrequently:true});
        if(pCtx){
            pCtx.drawImage(videoRef.current,0,0,R,R); const data=pCtx.getImageData(0,0,R,R).data;
            for(let i=0;i<R*R;i++)landRef.current[i]=255-((data[i*4]+data[i*4+1]+data[i*4+2])/3);
            waterRef.current.fill(0);
        }
    }
    
    for(let i=0;i<heightMapRef.current.length;i++) heightMapRef.current[i]=landRef.current[i]+waterRef.current[i];
    
    const sortedColorMap=[...colorMap].sort((a,b)=>b.height-a.height);
    drawHeightMap(ctx, heightMapRef.current, sortedColorMap);
    updateAndDrawVehicles(ctx, heightMapRef.current, fleetMode, missionState.status==='active');

    if(mousePositionRef.current){const{x,y}=mousePositionRef.current;ctx.beginPath();ctx.arc(x,y,brushSize/2,0,2*Math.PI);ctx.strokeStyle='rgba(255,255,255,0.7)';ctx.lineWidth=1;ctx.stroke();}
    if(missionState.status==='active'&&isLandDry()){Logger.info('Mission Won');setMissionState(prev=>({...prev,status:'won'}));}
    animationFrameId.current=requestAnimationFrame(animate);
  }, [settings, colorMap, fleetMode, brushSize, isLandDry, setMissionState, drawHeightMap, runPhysicsStep, updateAndDrawVehicles]);

  useEffect(() => {
    const totalVehicles=Object.values(gameSettings).reduce((s,c)=>s+c,0); if(totalVehicles===vehiclesRef.current.length)return;
    const newVehicles:Vehicle[]=[];
    VEHICLE_TYPES.forEach(type=>{
        const count=gameSettings[`${type}Count`], existing=vehiclesRef.current.filter(v=>v.type===type);
        newVehicles.push(...existing.slice(0,count));
        for(let i=0;i<count-existing.length;i++)newVehicles.push({
            id:uuidv4(),type,x:Math.random()*R,y:Math.random()*R,vx:0,vy:0,angle:Math.random()*2*Math.PI,
            mode:'IDLE',target:null,secondaryTarget:null,taskCooldown:0,payload:0,searchTimeout:0,
        });
    }); vehiclesRef.current=newVehicles;
  }, [gameSettings, R]);

  useEffect(() => {
    Logger.info("Regen triggered", regenerationTrigger);
    initialSeaLevel.current=settings.seaLevel;
    const newLand=generateTerrain(settings.terrainType,noise2D); landRef.current=newLand;
    const newWater=new Float32Array(R*R).fill(0); waterRef.current=newWater;
    if(!heightMapRef.current||heightMapRef.current.length!==newLand.length) heightMapRef.current=new Float32Array(R*R);
    for(let i=0; i<heightMapRef.current.length; i++) heightMapRef.current[i]=newLand[i]+newWater[i];
  }, [regenerationTrigger, settings.terrainType, settings.seaLevel, generateTerrain, noise2D, heightMapRef, R]);

  useEffect(() => {
    if(calibrationTrigger===0)return;
    setIsCalibrating(true); if(mediaStream)mediaStream.getTracks().forEach(t=>t.stop());
    navigator.mediaDevices.getUserMedia({video:{width:R,height:R}}).then(stream=>{
        setMediaStream(stream); if(videoRef.current)videoRef.current.srcObject=stream; setIsCalibrating(false);
        onCalibrationResult(true,"Webcam calibrated. Enable 'Display Kinect View' to see feed.");
    }).catch(err=>{
        Logger.error("Webcam error:",err);
        onCalibrationResult(false,"Failed to access webcam.",{error:err as Error,context:"Failed to access webcam.",troubleshooting:["Ensure browser has camera permission.","Check if another app is using the camera."]});
        setIsCalibrating(false);
    });
    return ()=>mediaStream?.getTracks().forEach(t=>t.stop());
  }, [calibrationTrigger, onCalibrationResult, R, mediaStream]);

  useEffect(() => {
    animationFrameId.current=requestAnimationFrame(animate);
    return ()=>{if(animationFrameId.current)cancelAnimationFrame(animationFrameId.current);};
  }, [animate]);

  const handleMouseDown = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    isDragging.current=true; const rect=e.currentTarget.getBoundingClientRect(),x=(e.clientX-rect.left)*(R/rect.width),y=(e.clientY-rect.top)*(R/rect.height);
    if(e.button===0){modifyTerrain(x,y,brushSize,-DIG_STRENGTH);onTreasureDig(x,y);}
    else if(e.button===2){const c=modifyTerrain(x,y,brushSize,DIG_STRENGTH);if(missionState.status==='active')setMissionState(p=>({...p,score:p.score+c*10}));}
  }, [brushSize, modifyTerrain, onTreasureDig, R, missionState.status, setMissionState]);

  const handleMouseUp=useCallback(()=>{isDragging.current=false;},[]);
  const handleMouseMove=useCallback((e:React.MouseEvent<HTMLCanvasElement>)=>{
    const rect=e.currentTarget.getBoundingClientRect(),x=(e.clientX-rect.left)*(R/rect.width),y=(e.clientY-rect.top)*(R/rect.height);
    mousePositionRef.current={x,y};
    if(isDragging.current){
        if(e.buttons===1)modifyTerrain(x,y,brushSize,-DIG_STRENGTH);
        else if(e.buttons===2){const c=modifyTerrain(x,y,brushSize,DIG_STRENGTH);if(missionState.status==='active')setMissionState(p=>({...p,score:p.score+c*10}));}
    }
  },[brushSize,modifyTerrain,R,missionState.status,setMissionState]);
  const handleMouseLeave=useCallback(()=>{isDragging.current=false;mousePositionRef.current=null;},[]);
  const handleWheel=useCallback((e:React.WheelEvent<HTMLCanvasElement>)=>{e.preventDefault();setBrushSize(p=>Math.max(10,Math.min(200,p-e.deltaY*0.1)));},[]);

  return {canvasRef,videoRef,isCalibrating,handleMouseDown,handleMouseUp,handleMouseMove,handleMouseLeave,handleWheel};
};