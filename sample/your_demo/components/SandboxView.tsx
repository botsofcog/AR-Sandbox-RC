
import React from 'react';
import { SandboxSettings, ColorStop, GameSettings, MissionState, ErrorInfo } from '../types';
import { useSandboxSimulation, CANVAS_RESOLUTION } from '../hooks/useSandboxSimulation';

interface SandboxViewProps {
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

export const SandboxView: React.FC<SandboxViewProps> = (props) => {
  const {
    canvasRef,
    videoRef,
    isCalibrating,
    handleMouseDown,
    handleMouseUp,
    handleMouseMove,
    handleMouseLeave,
    handleWheel,
  } = useSandboxSimulation(props);

  return (
    <div className="relative w-full h-full">
      <canvas
        ref={canvasRef}
        width={CANVAS_RESOLUTION}
        height={CANVAS_RESOLUTION}
        className="w-full h-full object-contain cursor-crosshair"
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        onWheel={handleWheel}
        onContextMenu={(e) => e.preventDefault()}
      />
      {isCalibrating && (
        <div className="absolute inset-0 bg-black/70 flex flex-col items-center justify-center z-10 pointer-events-none">
          <p className="text-white text-lg font-bold mb-4 animate-pulse">Calibrating...</p>
        </div>
      )}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className={props.settings.displayKinectView ? "absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4/5 h-4/5 object-contain rounded-lg shadow-lg z-20 border-2 border-blue-500/50" : "hidden"}
      />
    </div>
  );
};
