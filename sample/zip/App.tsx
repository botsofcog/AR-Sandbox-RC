
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { LeftPanel } from './components/LeftPanel';
import { RightPanel } from './components/RightPanel';
import { SandboxView } from './components/SandboxView';
import { Toast } from './components/Toast';
import { ErrorDisplay } from './components/ErrorDisplay';
import { MissionEndDisplay } from './components/MissionEndDisplay';
import { ColorStop, GameSettings, SandboxSettings, MissionState, ErrorInfo } from './types';
import { DEFAULT_COLOR_MAP, DEFAULT_GAME_SETTINGS, DEFAULT_SANDBOX_SETTINGS } from './constants';
import { Logger } from './services/logger';
import { findTreasure } from './services/geminiService';

export interface ToastMessage {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
}

const App: React.FC = () => {
  const [settings, setSettings] = useState<SandboxSettings>(DEFAULT_SANDBOX_SETTINGS);
  const [targetSeaLevel, setTargetSeaLevel] = useState<number>(DEFAULT_SANDBOX_SETTINGS.seaLevel);
  const [gameSettings, setGameSettings] = useState<GameSettings>(DEFAULT_GAME_SETTINGS);
  const [colorMap, setColorMap] = useState<ColorStop[]>(DEFAULT_COLOR_MAP);
  const [selectedColorId, setSelectedColorId] = useState<string | null>(colorMap.length > 0 ? colorMap[0].id : null);
  const [missionState, setMissionState] = useState<MissionState>({ status: 'idle', timeLeft: 180, score: 0 });
  const [toast, setToast] = useState<ToastMessage | null>(null);
  const [calibrationTrigger, setCalibrationTrigger] = useState(0);
  const [regenerationTrigger, setRegenerationTrigger] = useState(1);
  const [appError, setAppError] = useState<ErrorInfo | null>(null);
  const heightMapRef = useRef<Float32Array | null>(null);
  const [fleetMode, setFleetMode] = useState<'work' | 'idle'>('idle');

  const handleSettingsChange = <K extends keyof SandboxSettings>(key: K, value: SandboxSettings[K]) => {
    if (key === 'seaLevel') {
      const newLevel = typeof value === 'number' ? value : parseInt(String(value));
      setTargetSeaLevel(newLevel);
    }
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleGameSettingsChange = <K extends keyof GameSettings>(key: K, value: GameSettings[K]) => {
    setGameSettings(prev => ({ ...prev, [key]: value }));
  };

  const showToast = useCallback((message: string, type: ToastMessage['type']) => {
    setToast({ id: uuidv4(), message, type });
  }, []);

  const startMission = () => {
    if (missionState.status !== 'idle') return;
    Logger.info('Starting Flood Defense Mission');
    showToast("Flood Defense Mission Started! Raise all land above sea level!", 'info');
    setMissionState({ status: 'active', timeLeft: 180, score: 0 });
    setFleetMode('work'); // Automatically set fleet to work when mission starts
  };
  
  const stopMission = useCallback(() => {
    if (missionState.status !== 'active') return;
    Logger.info('Mission stopped by user.');
    showToast("Mission stopped.", 'warning');
    setMissionState({ status: 'idle', timeLeft: 180, score: 0 });
    setFleetMode('idle');
  }, [missionState.status, showToast]);

  const endMission = (status: 'won' | 'lost') => {
      setMissionState(prev => ({ ...prev, status }));
  };


  const handleCalibrate = useCallback(() => {
    setAppError(null); // Clear previous errors before trying again
    setCalibrationTrigger(c => c + 1);
    showToast("Attempting to calibrate from webcam...", 'info');
  }, [showToast]);

  const handleRegenerate = useCallback(() => {
    setRegenerationTrigger(c => c + 1);
    showToast("Generating new terrain...", 'info');
  }, [showToast]);

  const handleCalibrationResult = useCallback((success: boolean, message: string, errorInfo?: ErrorInfo) => {
    if (success) {
      showToast(message, 'success');
    } else {
      Logger.error(message, errorInfo?.error);
      if (errorInfo) {
        setAppError(errorInfo);
      } else {
        setAppError({
          error: new Error(message),
          context: 'An unknown calibration error occurred.'
        });
      }
    }
  }, [showToast]);
  
  const handleTreasureDig = useCallback(async (x: number, y: number) => {
      if (!heightMapRef.current) {
        showToast("Digging failed: height map not available.", 'error');
        return;
      }
      try {
        const result = await findTreasure(x, y, heightMapRef.current, settings);
        if (result.found) {
            showToast(`You found a ${result.item}! ${result.description}`, 'success');
        }
      } catch (error) {
        Logger.error("Treasure digging failed", error);
        showToast("An error occurred while digging for treasure.", 'error');
      }
  }, [showToast, settings]);


  useEffect(() => {
    if (missionState.status === 'active' && missionState.timeLeft > 0) {
      const timerId = setTimeout(() => {
        setMissionState(prev => ({ ...prev, timeLeft: prev.timeLeft - 1 }));
      }, 1000);
      return () => clearTimeout(timerId);
    } else if (missionState.status === 'active' && missionState.timeLeft === 0) {
      Logger.info('Mission Failed: Time ran out.');
      setMissionState(prev => ({ ...prev, status: 'lost' }));
      // Simulate flood by raising sea level
      setTargetSeaLevel(prev => Math.min(255, prev + 50));
    }
  }, [missionState.status, missionState.timeLeft]);
  
  // Animate sea level changes smoothly
  useEffect(() => {
    if (settings.seaLevel === targetSeaLevel) return;

    const animationFrame = requestAnimationFrame(() => {
      setSettings(prev => {
        const diff = targetSeaLevel - prev.seaLevel;
        if (Math.abs(diff) < 1) {
          return { ...prev, seaLevel: targetSeaLevel };
        }
        const newSeaLevel = prev.seaLevel + Math.sign(diff) * Math.max(1, Math.abs(diff) * 0.1);
        return { ...prev, seaLevel: newSeaLevel };
      });
    });

    return () => cancelAnimationFrame(animationFrame);
  }, [settings.seaLevel, targetSeaLevel]);


  if (appError) {
    return <ErrorDisplay errorInfo={appError} onDismiss={() => setAppError(null)} appState={{ settings, gameSettings }} />
  }

  return (
    <div className="flex h-screen w-screen bg-gray-900 font-sans text-sm">
      <LeftPanel
        colorMap={colorMap}
        setColorMap={setColorMap}
        selectedColorId={selectedColorId}
        setSelectedColorId={setSelectedColorId}
        settings={settings}
        onSettingsChange={handleSettingsChange}
        showToast={showToast}
      />
      <main className="flex-1 flex flex-col items-center justify-center p-4">
        <h1 className="text-xl font-bold text-gray-300 mb-2">AR Construction Sandbox</h1>
        <div className="w-full h-full border-2 border-blue-500/50 rounded-lg shadow-2xl shadow-blue-500/20 bg-black overflow-hidden">
          <SandboxView
            settings={settings}
            colorMap={colorMap}
            gameSettings={gameSettings}
            missionState={missionState}
            setMissionState={setMissionState}
            calibrationTrigger={calibrationTrigger}
            regenerationTrigger={regenerationTrigger}
            onCalibrationResult={handleCalibrationResult}
            onTreasureDig={handleTreasureDig}
            showToast={showToast}
            heightMapRef={heightMapRef}
            fleetMode={fleetMode}
          />
        </div>
      </main>
      <RightPanel
        settings={settings}
        onSettingsChange={handleSettingsChange}
        gameSettings={gameSettings}
        onGameSettingsChange={handleGameSettingsChange}
        missionState={missionState}
        onStartMission={startMission}
        onStopMission={stopMission}
        onCalibrate={handleCalibrate}
        onRegenerate={handleRegenerate}
        fleetMode={fleetMode}
        onFleetModeChange={setFleetMode}
      />
      {toast && (
        <Toast
            key={toast.id}
            message={toast.message}
            type={toast.type}
            onDismiss={() => setToast(null)}
        />
      )}
      { (missionState.status === 'won' || missionState.status === 'lost') && (
        <MissionEndDisplay
            status={missionState.status}
            score={missionState.score}
            onRestart={() => setMissionState({ status: 'idle', timeLeft: 180, score: 0})}
        />
      )}
    </div>
  );
};

export default App;
