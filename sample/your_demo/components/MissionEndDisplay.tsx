
import React from 'react';

interface MissionEndDisplayProps {
  status: 'won' | 'lost';
  score: number;
  onRestart: () => void;
}

const WinIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-20 w-20 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

const LoseIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-20 w-20 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

export const MissionEndDisplay: React.FC<MissionEndDisplayProps> = ({ status, score, onRestart }) => {
    const isWin = status === 'won';
    const title = isWin ? "Mission Accomplished!" : "Mission Failed";
    const message = isWin ? "You successfully defended the area!" : "The flood waters have risen!";
    const containerClasses = isWin 
        ? "bg-gray-800 border-green-500/50 shadow-green-500/20" 
        : "bg-gray-800 border-red-500/50 shadow-red-500/20";
    
    return (
        <div className="fixed inset-0 bg-gray-900/80 backdrop-blur-sm flex items-center justify-center z-50 p-4" role="dialog" aria-modal="true" aria-labelledby="mission-end-title">
            <div className={`w-full max-w-md ${containerClasses} border rounded-lg shadow-2xl text-gray-200 flex flex-col items-center p-8 text-center`}>
                <div className="mb-4">
                    {isWin ? <WinIcon /> : <LoseIcon />}
                </div>
                <h2 id="mission-end-title" className={`text-3xl font-bold ${isWin ? 'text-green-300' : 'text-red-300'}`}>{title}</h2>
                <p className="mt-2 text-gray-400">{message}</p>

                <div className="mt-6 bg-gray-900/50 p-4 rounded-lg">
                    <p className="text-sm text-gray-400 uppercase tracking-wider">Final Score</p>
                    <p className="text-4xl font-bold text-white mt-1">{score}</p>
                </div>
                
                <button onClick={onRestart} className="mt-8 px-8 py-3 text-lg font-semibold text-gray-200 bg-blue-600 hover:bg-blue-500 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-blue-500">
                    Play Again
                </button>
            </div>
        </div>
    );
};
