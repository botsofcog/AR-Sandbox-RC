import React from 'react';

interface SegmentedControlProps<T extends string> {
  label: string;
  options: { label: string; value: T }[];
  value: T;
  onChange: (value: T) => void;
}

export const SegmentedControl = <T extends string>({ label, options, value, onChange }: SegmentedControlProps<T>) => {
  return (
    <div>
        <span className="text-xs text-gray-400">{label}</span>
        <div className="mt-1 flex w-full bg-gray-900/50 p-1 rounded-md">
        {options.map((option) => (
            <button
            key={option.value}
            onClick={() => onChange(option.value)}
            className={`w-full px-2 py-1.5 text-xs font-semibold rounded-md transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-800 ${
                value === option.value ? 'bg-blue-600 text-white shadow' : 'text-gray-300 hover:bg-gray-700/50'
            }`}
            >
            {option.label}
            </button>
        ))}
        </div>
    </div>
  );
};
