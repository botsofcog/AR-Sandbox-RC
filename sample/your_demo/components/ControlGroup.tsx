
import React, { useState } from 'react';

interface ControlGroupProps {
  title: string;
  children: React.ReactNode;
  initialOpen?: boolean;
}

const ChevronDownIcon: React.FC<{className: string}> = ({ className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
    <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
  </svg>
);

export const ControlGroup: React.FC<ControlGroupProps> = ({ title, children, initialOpen = true }) => {
  const [isOpen, setIsOpen] = useState(initialOpen);

  return (
    <div className="border-t border-gray-600/50 py-3">
      <button
        className="w-full flex justify-between items-center text-left text-gray-300 hover:text-white"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="font-bold uppercase text-xs tracking-wider">{title}</span>
        <ChevronDownIcon className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      {isOpen && <div className="mt-4 space-y-4">{children}</div>}
    </div>
  );
};
