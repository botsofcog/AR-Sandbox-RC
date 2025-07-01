import React from 'react';

interface SelectProps {
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  children: React.ReactNode;
  id?: string;
}

export const Select: React.FC<SelectProps> = ({ label, value, onChange, children, id }) => {
  return (
    <div>
      <label htmlFor={id} className="text-xs text-gray-400 uppercase font-bold tracking-wider">{label}</label>
      <select
        id={id}
        value={value}
        onChange={onChange}
        className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm text-white"
      >
        {children}
      </select>
    </div>
  );
};
