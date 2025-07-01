
import React from 'react';
import { ColorStop, SandboxSettings } from '../types';
import { ControlGroup } from './ControlGroup';
import { Slider } from './Slider';
import { Toggle } from './Toggle';
import { Select } from './Select';
import { v4 as uuidv4 } from 'uuid';
import { DEFAULT_COLOR_MAP, COLOR_MAP_PRESETS } from '../constants';

interface LeftPanelProps {
  colorMap: ColorStop[];
  setColorMap: React.Dispatch<React.SetStateAction<ColorStop[]>>;
  selectedColorId: string | null;
  setSelectedColorId: React.Dispatch<React.SetStateAction<string | null>>;
  settings: SandboxSettings;
  onSettingsChange: <K extends keyof SandboxSettings>(key: K, value: SandboxSettings[K]) => void;
  showToast: (message: string, type: 'success' | 'error' | 'info' | 'warning') => void;
}

const SmallButton: React.FC<{ onClick: () => void; children: React.ReactNode; className?: string, disabled?: boolean }> = ({ onClick, children, className = '', disabled=false }) => (
    <button onClick={onClick} disabled={disabled} className={`w-full px-2 py-1.5 text-xs font-semibold text-gray-200 bg-gray-700 hover:bg-gray-600 rounded-md transition-colors disabled:bg-gray-800 disabled:text-gray-500 disabled:cursor-not-allowed ${className}`}>
        {children}
    </button>
);

const ColorEditor: React.FC<{ color: ColorStop; onUpdate: (updatedColor: ColorStop) => void; onRemove: (id: string) => void; onMove: (id: string, direction: 'up' | 'down') => void; onInsert: (id: string) => void }> = ({ color, onUpdate, onRemove, onMove, onInsert }) => {
    if (!color) return null;

    return (
        <div className="bg-gray-900 p-3 rounded-lg space-y-3">
            <div className="flex items-center justify-between">
                <label htmlFor="height" className="text-xs text-gray-400">HEIGHT</label>
                <input
                    type="number"
                    id="height"
                    value={color.height}
                    onChange={(e) => onUpdate({ ...color, height: parseInt(e.target.value) || 0 })}
                    className="w-24 bg-gray-700 text-white p-1 rounded-md text-right text-xs"
                />
            </div>
            <div className="flex items-center justify-between">
                <label htmlFor="color" className="text-xs text-gray-400">COLOR</label>
                <input
                    type="color"
                    id="color"
                    value={color.color}
                    onChange={(e) => onUpdate({ ...color, color: e.target.value })}
                    className="w-24 h-7 p-0 border-none rounded-md cursor-pointer bg-gray-700"
                />
            </div>
             <div className="grid grid-cols-2 gap-2 pt-2">
                <SmallButton onClick={() => onMove(color.id, 'up')}>MOVE UP</SmallButton>
                <SmallButton onClick={() => onMove(color.id, 'down')}>MOVE DOWN</SmallButton>
                <SmallButton onClick={() => onInsert(color.id)}>INSERT AFTER</SmallButton>
                <SmallButton onClick={() => onRemove(color.id)} className="bg-red-800/80 hover:bg-red-700/80">REMOVE</SmallButton>
            </div>
        </div>
    );
};


export const LeftPanel: React.FC<LeftPanelProps> = ({ colorMap, setColorMap, selectedColorId, setSelectedColorId, settings, onSettingsChange, showToast }) => {
    const sortedColorMap = [...colorMap].sort((a, b) => b.height - a.height);
    const selectedColor = colorMap.find(c => c.id === selectedColorId);
    
    const [presetKey, setPresetKey] = React.useState('default');

    const handleUpdateColor = (updatedColor: ColorStop) => {
        setColorMap(prev => prev.map(c => c.id === updatedColor.id ? updatedColor : c));
    };

    const handleRemoveColor = (id: string) => {
        if (colorMap.length <= 2) { // Keep at least 2 colors
             showToast("Cannot remove color. A minimum of two color stops are required.", 'warning');
             return;
        }
        setColorMap(prev => prev.filter(c => c.id !== id));
        if (selectedColorId === id) {
            setSelectedColorId(colorMap.length > 1 ? colorMap[0].id : null);
        }
    };
    
    const handleMoveColor = (id: string, direction: 'up' | 'down') => {
        const sortedArr = [...colorMap].sort((a, b) => b.height - a.height);
        const index = sortedArr.findIndex(c => c.id === id);

        let swapIndex = -1;
        if (direction === 'up' && index > 0) {
            swapIndex = index - 1;
        } else if (direction === 'down' && index < sortedArr.length - 1) {
            swapIndex = index + 1;
        }

        if (swapIndex !== -1) {
            const currentItem = sortedArr[index];
            const swapItem = sortedArr[swapIndex];

            // Swap the heights between the two items
            const newCurrentHeight = swapItem.height;
            const newSwapHeight = currentItem.height;

            setColorMap(prevMap => prevMap.map(c => {
                if (c.id === currentItem.id) {
                    return { ...c, height: newCurrentHeight };
                }
                if (c.id === swapItem.id) {
                    return { ...c, height: newSwapHeight };
                }
                return c;
            }));
        }
    };

    const handleInsertColor = (afterId: string) => {
        const newColor: ColorStop = { id: uuidv4(), height: 0, color: '#808080' };
        const index = colorMap.findIndex(c => c.id === afterId);
        const refColor = colorMap[index];
        const prevColor = colorMap.sort((a,b) => b.height - a.height)[index+1];
        
        newColor.height = refColor && prevColor ? Math.round((refColor.height + prevColor.height)/2) : refColor.height - 10;
        newColor.color = refColor.color;
        
        const newMap = [...colorMap, newColor];
        setColorMap(newMap);
        setSelectedColorId(newColor.id);
    };

    const handleResetColors = () => {
        setColorMap(DEFAULT_COLOR_MAP);
        setSelectedColorId(DEFAULT_COLOR_MAP[0].id);
        setPresetKey('default');
        showToast("Color map reset to default.", 'info');
    };

    const handlePresetChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const key = e.target.value;
        const preset = COLOR_MAP_PRESETS[key];
        if (preset) {
            setPresetKey(key);
            setColorMap(preset.map);
            setSelectedColorId(preset.map.length > 0 ? preset.map[0].id : null);
            showToast(`Loaded "${preset.name}" color preset.`, 'info');
        }
    };

    const gradient = [...colorMap]
        .sort((a, b) => a.height - b.height)
        .map(c => `${c.color} ${ (c.height / 255) * 100}%`)
        .join(', ');

    return (
        <aside className="w-72 bg-gray-800/80 p-4 overflow-y-auto flex flex-col h-full shadow-lg">
            <h2 className="text-lg font-bold text-gray-300 text-center mb-4">DISPLAY</h2>
            <ControlGroup title="Contour Lines">
                <Toggle label="CONTOUR LINES" enabled={settings.contourLines} onChange={val => onSettingsChange('contourLines', val)} />
                <Slider label="LINES DISTANCE" min={1} max={50} value={settings.linesDistance} onChange={e => onSettingsChange('linesDistance', parseInt(e.target.value))} />
            </ControlGroup>
            <ControlGroup title="Color Map">
                <div className="w-full h-8 rounded-md border border-gray-600" style={{ background: `linear-gradient(to right, ${gradient})` }}></div>
                <div className="space-y-2 mt-2">
                    <Select label="COLOR PRESETS" value={presetKey} onChange={handlePresetChange}>
                        {Object.entries(COLOR_MAP_PRESETS).map(([key, preset]) => (
                            <option key={key} value={key}>{preset.name}</option>
                        ))}
                    </Select>
                    <SmallButton onClick={handleResetColors}>RESET TO DEFAULT</SmallButton>
                </div>
            </ControlGroup>
            <ControlGroup title="Browse Colors" initialOpen={true}>
                <div className="max-h-48 overflow-y-auto bg-gray-900/50 rounded-lg p-1 space-y-1">
                    {sortedColorMap.map(c => (
                        <button key={c.id} onClick={() => setSelectedColorId(c.id)}
                            className={`w-full p-2 rounded-md flex items-center justify-between text-left text-xs transition-colors ${selectedColorId === c.id ? 'bg-blue-500/30 ring-2 ring-blue-500' : 'bg-gray-700/50 hover:bg-gray-700'}`}
                        >
                            <span className="font-semibold text-gray-300">HEIGHT: {c.height}</span>
                            <div className="w-5 h-5 rounded" style={{ backgroundColor: c.color }}></div>
                        </button>
                    ))}
                </div>
            </ControlGroup>
            <ControlGroup title="Edit Color" initialOpen={true}>
                {selectedColor && <ColorEditor color={selectedColor} onUpdate={handleUpdateColor} onRemove={handleRemoveColor} onMove={handleMoveColor} onInsert={handleInsertColor} />}
            </ControlGroup>
        </aside>
    );
};