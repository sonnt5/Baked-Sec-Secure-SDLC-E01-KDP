import { type ReactNode } from 'react';

export interface TableProps {
  children: ReactNode;
  className?: string;
}

export function Table({ children, className = '' }: TableProps) {
  return (
    <div className="overflow-x-auto">
      <table className={`min-w-full divide-y divide-gray-200 dark:divide-gray-700 ${className}`}>
        {children}
      </table>
    </div>
  );
}

export interface TableHeaderProps {
  children: ReactNode;
  className?: string;
}

export function TableHeader({ children, className = '' }: TableHeaderProps) {
  return (
    <thead className={`bg-gray-50 dark:bg-gray-800 ${className}`}>
      {children}
    </thead>
  );
}

export interface TableBodyProps {
  children: ReactNode;
  className?: string;
}

export function TableBody({ children, className = '' }: TableBodyProps) {
  return (
    <tbody className={`bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700 ${className}`}>
      {children}
    </tbody>
  );
}

export interface TableRowProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}

export function TableRow({ children, className = '', onClick }: TableRowProps) {
  const hoverStyles = onClick ? 'cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800' : '';
  
  return (
    <tr className={`${hoverStyles} ${className}`} onClick={onClick}>
      {children}
    </tr>
  );
}

export interface TableHeadProps {
  children: ReactNode;
  className?: string;
  sortable?: boolean;
  onClick?: () => void;
}

export function TableHead({ children, className = '', sortable = false, onClick }: TableHeadProps) {
  const sortableStyles = sortable ? 'cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700' : '';
  
  return (
    <th
      scope="col"
      className={`px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider ${sortableStyles} ${className}`}
      onClick={onClick}
    >
      {children}
    </th>
  );
}

export interface TableCellProps {
  children: ReactNode;
  className?: string;
}

export function TableCell({ children, className = '' }: TableCellProps) {
  return (
    <td className={`px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white ${className}`}>
      {children}
    </td>
  );
}
