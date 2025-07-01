

import { ColorStop, GameSettings, SandboxSettings, VehicleType, TerrainType } from "./types";
import { v4 as uuidv4 } from 'uuid';

export const DEFAULT_COLOR_MAP: ColorStop[] = [
  { id: uuidv4(), height: 255, color: '#FFFFFF' }, // Snow
  { id: uuidv4(), height: 200, color: '#A0A0A0' }, // Rock
  { id: uuidv4(), height: 120, color: '#3A912C' }, // High Grass
  { id: uuidv4(), height: 80, color: '#57C146' },  // Low Grass
  { id: uuidv4(), height: 60, color: '#D2B48C' },  // Sand
  { id: uuidv4(), height: 50, color: '#3E83C9' },  // Shallow Water
  { id: uuidv4(), height: 0, color: '#1E4A94' },    // Deep Water
];

export const COLOR_MAP_PRESETS: Record<string, { name: string, map: ColorStop[] }> = {
  default: { name: 'Default', map: DEFAULT_COLOR_MAP },
  volcanic: {
    name: 'Volcanic',
    map: [
      { id: uuidv4(), height: 255, color: '#FAD4C0' }, // Ash Cloud
      { id: uuidv4(), height: 200, color: '#5A5A5A' }, // Cooled Rock
      { id: uuidv4(), height: 150, color: '#2B2B2B' }, // Basalt
      { id: uuidv4(), height: 100, color: '#FF4500' }, // Flowing Lava
      { id: uuidv4(), height: 50, color: '#8B0000' },  // Hardened Lava
      { id: uuidv4(), height: 0, color: '#1B0000' },    // Deep Magma
    ],
  },
  arctic: {
    name: 'Arctic',
    map: [
      { id: uuidv4(), height: 255, color: '#FFFFFF' }, // Fresh Snow
      { id: uuidv4(), height: 180, color: '#E8F4F8' }, // Packed Snow
      { id: uuidv4(), height: 120, color: '#B0E0E6' }, // Glacier Ice
      { id: uuidv4(), height: 80, color: '#87CEEB' },  // Icy Shore
      { id: uuidv4(), height: 60, color: '#4682B4' },  // Shallow Water
      { id: uuidv4(), height: 0, color: '#00008B' },    // Deep Ocean
    ],
  },
  desert: {
    name: 'Desert',
    map: [
      { id: uuidv4(), height: 255, color: '#CD853F' }, // Mountain Rock
      { id: uuidv4(), height: 180, color: '#D2B48C' }, // Tan Sand
      { id: uuidv4(), height: 120, color: '#F4A460' }, // Sandy Brown
      { id: uuidv4(), height: 80, color: '#FFDEAD' },  // Light Sand
      { id: uuidv4(), height: 70, color: '#BDB76B' },  // Oasis Scrub
      { id: uuidv4(), height: 65, color: '#2E8B57' },  // Oasis Water
      { id: uuidv4(), height: 0, color: '#006400' },    // Deep Oasis
    ],
  },
  alien: {
      name: 'Alien',
      map: [
          { id: uuidv4(), height: 255, color: '#F0F8FF' }, // Crystalline Peaks
          { id: uuidv4(), height: 200, color: '#98FB98' }, // Glowing Flora
          { id: uuidv4(), height: 150, color: '#AFEEEE' }, // Pale Turquoise Ground
          { id: uuidv4(), height: 100, color: '#DA70D6' }, // Orchid Purple Plains
          { id: uuidv4(), height: 50, color: '#4B0082' },  // Indigo Slime
          { id: uuidv4(), height: 0, color: '#000030' },    // Void Pits
      ],
  },
};


export const DEFAULT_SANDBOX_SETTINGS: SandboxSettings = {
  contourLines: true,
  linesDistance: 10,
  seaLevel: 55,
  tiltX: 0,
  tiltY: 0,
  verticalOffset: -15,
  displayKinectView: false,
  ceiling: 0,
  spatialFiltering: true,
  quickReaction: false,
  averaging: 30,
  terrainType: 'islands',
};

export const DEFAULT_GAME_SETTINGS: GameSettings = {
    excavatorCount: 2,
    bulldozerCount: 2,
    dumpTruckCount: 0,
    craneCount: 0,
    compactorCount: 0,
};

export const VEHICLE_SPECS: Record<VehicleType, { name: string, color: string, size: number }> = {
  excavator: { name: "Excavator", color: '#FFD700', size: 8 },  // Gold
  bulldozer: { name: "Bulldozer", color: '#FFA500', size: 10 }, // Orange
  dumpTruck: { name: "Dump Truck", color: '#FF4500', size: 9 }, // OrangeRed
  crane:     { name: "Crane", color: '#FFFF00', size: 7 },       // Yellow
  compactor: { name: "Compactor", color: '#B0B0B0', size: 10 }, // Gray
};

// Physics and AI Constants
export const PHYSICS = {
    FRICTION: 0.95,
    MAX_SPEED: 1.5,
    ACCELERATION_FORCE: 0.1,
    TERRAIN_SLOPE_SENSITIVITY: 0.05,
};

export const AI = {
    WANDER_STRENGTH: 0.1,
    SEEK_STRENGTH: 0.05,
    SEPARATION_RADIUS: 30,
    SEPARATION_STRENGTH: 0.1,
    COHESION_RADIUS: 60,
    COHESION_STRENGTH: 0.01,
    BASE_LOCATION: { x: 30, y: 30 },
    BASE_PARKING_RADIUS: 40,
    EXCAVATOR_PAYLOAD_CAPACITY: 10,
    BULLDOZER_LEVELING_STRENGTH: 0.5,
    BULLDOZER_MIN_GRADIENT: 5,
};
