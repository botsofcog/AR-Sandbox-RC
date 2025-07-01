

import React from 'react';
import { GameSettings, MissionState, SandboxSettings, VEHICLE_TYPES, TERRAIN_TYPES } from '../types';
import { ControlGroup } from './ControlGroup';
import { Slider } from './Slider';
import { Toggle } from './Toggle';
import { VEHICLE_SPECS } from '../constants';
import { SegmentedControl } from './SegmentedControl';

interface RightPanelProps {
  settings: SandboxSettings;
  onSettingsChange: <K extends keyof SandboxSettings>(key: K, value: SandboxSettings[K]) => void;
  gameSettings: GameSettings;
  onGameSettingsChange: <K extends keyof GameSettings>(key: K, value: GameSettings[K]) => void;
  missionState: MissionState;
  onStartMission: () => void;
  onStopMission: () => void;
  onCalibrate: () => void;
  onRegenerate: () => void;
  fleetMode: 'work' | 'idle';
  onFleetModeChange: (mode: 'work' | 'idle') => void;
}

const SimpleButton: React.FC<{ onClick: () => void; children: React.ReactNode; disabled?: boolean; className?: string; }> = ({ onClick, children, disabled, className }) => (
    <button onClick={onClick} disabled={disabled} className={`w-full px-2 py-2 text-xs font-semibold text-gray-200 bg-gray-700 hover:bg-gray-600 rounded-md transition-colors disabled:bg-gray-800 disabled:text-gray-500 disabled:cursor-not-allowed ${className}`}>
        {children}
    </button>
);

const MissionDisplay: React.FC<{timeLeft: number, score: number}> = ({timeLeft, score}) => {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    return (
        <div className="bg-red-900/50 border border-red-500 rounded-lg text-center p-2 space-y-2">
            <div className="flex justify-around items-center">
                <div>
                    <div className="text-xs text-red-300 uppercase font-bold tracking-widest">Time Left</div>
                    <div className="text-2xl font-mono text-white">{`${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`}</div>
                </div>
                 <div>
                    <div className="text-xs text-green-300 uppercase font-bold tracking-widest">Score</div>
                    <div className="text-2xl font-mono text-white">{Math.floor(score)}</div>
                </div>
            </div>
        </div>
    );
};

export const RightPanel: React.FC<RightPanelProps> = (props) => {
  const {
    settings,
    onSettingsChange,
    gameSettings,
    onGameSettingsChange,
    missionState,
    onStartMission,
    onStopMission,
    onCalibrate,
    onRegenerate,
    fleetMode,
    onFleetModeChange
  } = props;

  return (
    <aside className="w-72 bg-gray-800/80 p-4 overflow-y-auto flex flex-col h-full shadow-lg">
      <h2 className="text-lg font-bold text-gray-300 text-center mb-4">CONTROLS</h2>

      <ControlGroup title="Mission Control" initialOpen={true}>
        {missionState.status === 'active' ? (
          <div className="space-y-2">
            <MissionDisplay timeLeft={missionState.timeLeft} score={missionState.score} />
            <SimpleButton onClick={onStopMission} className="bg-red-800/80 hover:bg-red-700/80">
              STOP MISSION
            </SimpleButton>
          </div>
        ) : (
          <SimpleButton onClick={onStartMission} disabled={missionState.status !== 'idle'}>
            START FLOOD DEFENSE
          </SimpleButton>
        )}
      </ControlGroup>
      
      <ControlGroup title="Fleet Commands">
         <SegmentedControl
            label="GLOBAL FLEET MODE"
            options={[{label: 'Work', value: 'work'}, {label: 'Idle', value: 'idle'}]}
            value={fleetMode}
            onChange={onFleetModeChange}
        />
      </ControlGroup>

      <ControlGroup title="Fleet Management" initialOpen={true}>
        {VEHICLE_TYPES.map(type => (
          <Slider
            key={type}
            label={VEHICLE_SPECS[type].name.toUpperCase()}
            min={0}
            max={10}
            value={gameSettings[`${type}Count`]}
            onChange={(e) => onGameSettingsChange(`${type}Count`, parseInt(e.target.value))}
          />
        ))}
      </ControlGroup>
      
       <ControlGroup title="Terrain">
         <SegmentedControl
            label="TERRAIN TYPE"
            options={TERRAIN_TYPES.map(t => ({label: t.charAt(0).toUpperCase() + t.slice(1), value: t}))}
            value={settings.terrainType}
            onChange={(val) => onSettingsChange('terrainType', val)}
        />
        <div className="pt-2">
            <SimpleButton onClick={onRegenerate} className="bg-blue-800/80 hover:bg-blue-700/80">REGENERATE TERRAIN</SimpleButton>
        </div>
      </ControlGroup>

      <ControlGroup title="Environment">
        <Slider label="SEA LEVEL" min={0} max={255} value={settings.seaLevel} onChange={e => onSettingsChange('seaLevel', parseInt(e.target.value))} />
        <Slider label="TILT X-AXIS" min={-45} max={45} value={settings.tiltX} onChange={e => onSettingsChange('tiltX', parseFloat(e.target.value))} step={0.01} displayValue={settings.tiltX.toFixed(2)}/>
        <Slider label="TILT Y-AXIS" min={-45} max={45} value={settings.tiltY} onChange={e => onSettingsChange('tiltY', parseFloat(e.target.value))} step={0.01} displayValue={settings.tiltY.toFixed(2)}/>
      </ControlGroup>

      <ControlGroup title="Calibration">
        <Toggle label="DISPLAY KINECT VIEW" enabled={settings.displayKinectView} onChange={val => onSettingsChange('displayKinectView', val)} />
        <div className="grid grid-cols-2 gap-2 pt-2">
             <SimpleButton onClick={onCalibrate}>WEBCAM CALIBRATE</SimpleButton>
             <SimpleButton onClick={() => {}} disabled>FILE CALIBRATE</SimpleButton>
        </div>
        <Slider label="CEILING (KINECT)" min={0} max={255} value={settings.ceiling} onChange={e => onSettingsChange('ceiling', parseInt(e.target.value))} />
      </ControlGroup>

      <ControlGroup title="Advanced Settings">
        <Toggle label="SPATIAL FILTERING" enabled={settings.spatialFiltering} onChange={val => onSettingsChange('spatialFiltering', val)} />
        <Toggle label="QUICK REACTION" enabled={settings.quickReaction} onChange={val => onSettingsChange('quickReaction', val)} />
        <Slider label="AVERAGING" min={1} max={100} value={settings.averaging} onChange={e => onSettingsChange('averaging', parseInt(e.target.value))} />
      </ControlGroup>
    </aside>
  );
};
