
export interface ColorStop {
  id: string;
  height: number;
  color: string;
}

export const TERRAIN_TYPES = ['islands', 'mountains', 'plains', 'canyons'] as const;
export type TerrainType = typeof TERRAIN_TYPES[number];

export interface SandboxSettings {
  contourLines: boolean;
  linesDistance: number;
  seaLevel: number;
  tiltX: number;
  tiltY: number;
  verticalOffset: number;
  displayKinectView: boolean;
  ceiling: number;
  spatialFiltering: boolean;
  quickReaction: boolean;
  averaging: number;
  terrainType: TerrainType;
}

export const VEHICLE_TYPES = ['excavator', 'bulldozer', 'dumpTruck', 'crane', 'compactor'] as const;
export type VehicleType = typeof VEHICLE_TYPES[number];

export type VehicleMode = 
  | 'IDLE'                      // Inactive, waiting for fleet-wide command
  | 'RETURNING_TO_BASE'         // Fleet command is 'idle', heading to parking
  | 'PARKED'                    // In parking area, minimal movement
  // Generic work states
  | 'SEEKING_WORK_SITE'         // Looking for a location to perform a task
  | 'MOVING_TO_WORK_SITE'       // Target acquired, en route
  | 'WORKING'                   // Performing main task (digging, leveling)
  | 'MOVING_TO_DUMP_SITE'       // (Excavator-specific) Moving payload to a low spot
  | 'DUMPING';                  // (Excavator-specific) Dumping payload

export interface Vehicle {
    id: string;
    type: VehicleType;
    x: number;
    y: number;
    vx: number; // velocity x
    vy: number; // velocity y
    angle: number;
    mode: VehicleMode;
    payload: number; // e.g., amount of dirt carried
    target: { x: number; y: number } | null;
    secondaryTarget: { x: number; y: number } | null; // For bulldozer push direction
    taskCooldown: number;
    searchTimeout: number;
}

export interface GameSettings {
  excavatorCount: number;
  bulldozerCount: number;
  dumpTruckCount: number;
  craneCount: number;
  compactorCount: number;
}

export interface MissionState {
  status: 'idle' | 'active' | 'won' | 'lost';
  timeLeft: number; // in seconds
  score: number;
}

export interface TreasureResult {
  found: boolean;
  item: string;
  description: string;
}

export interface ErrorInfo {
  error: Error;
  context: string;
  troubleshooting?: string[];
}
