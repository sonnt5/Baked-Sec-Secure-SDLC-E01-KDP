import { useState, useEffect } from 'react';
import Input from '../ui/Input';
import Dropdown, { DropdownItem } from '../ui/Dropdown';
import Button from '../ui/Button';
import { ChevronDown, X } from 'lucide-react';

export interface FilterState {
  difficulty?: 'easy' | 'medium' | 'hard';
  tags: string[];
  search: string;
}

export interface ProblemFiltersProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  availableTags?: string[];
}

export default function ProblemFilters({ 
  filters, 
  onFiltersChange,
  availableTags = ['Array', 'String', 'Dynamic Programming', 'Graph', 'Tree', 'Math', 'Greedy', 'Binary Search', 'Sorting', 'Hash Table']
}: ProblemFiltersProps) {
  const [searchInput, setSearchInput] = useState(filters.search);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchInput !== filters.search) {
        onFiltersChange({ ...filters, search: searchInput });
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchInput]);

  const handleDifficultySelect = (difficulty?: 'easy' | 'medium' | 'hard') => {
    onFiltersChange({ ...filters, difficulty });
  };

  const handleTagToggle = (tag: string) => {
    const newTags = filters.tags.includes(tag)
      ? filters.tags.filter(t => t !== tag)
      : [...filters.tags, tag];
    onFiltersChange({ ...filters, tags: newTags });
  };

  const handleClearFilters = () => {
    setSearchInput('');
    onFiltersChange({ difficulty: undefined, tags: [], search: '' });
  };

  const hasActiveFilters = filters.difficulty || filters.tags.length > 0 || filters.search;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 mb-6">
      <div className="flex flex-col md:flex-row gap-4">
        {/* Search Input */}
        <div className="flex-1">
          <Input
            type="text"
            placeholder="Search problems by title or description..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="w-full"
          />
        </div>

        {/* Difficulty Filter */}
        <div className="w-full md:w-48">
          <Dropdown
            trigger={
              <Button variant="secondary" className="w-full justify-between">
                <span>
                  {filters.difficulty 
                    ? filters.difficulty.charAt(0).toUpperCase() + filters.difficulty.slice(1)
                    : 'All Difficulties'}
                </span>
                <ChevronDown className="w-4 h-4 ml-2" />
              </Button>
            }
            align="left"
          >
            <DropdownItem onClick={() => handleDifficultySelect(undefined)}>
              All Difficulties
            </DropdownItem>
            <DropdownItem onClick={() => handleDifficultySelect('easy')}>
              Easy
            </DropdownItem>
            <DropdownItem onClick={() => handleDifficultySelect('medium')}>
              Medium
            </DropdownItem>
            <DropdownItem onClick={() => handleDifficultySelect('hard')}>
              Hard
            </DropdownItem>
          </Dropdown>
        </div>

        {/* Tags Filter */}
        <div className="w-full md:w-48">
          <Dropdown
            trigger={
              <Button variant="secondary" className="w-full justify-between">
                <span>
                  {filters.tags.length > 0 
                    ? `${filters.tags.length} Tag${filters.tags.length > 1 ? 's' : ''}`
                    : 'All Tags'}
                </span>
                <ChevronDown className="w-4 h-4 ml-2" />
              </Button>
            }
            align="left"
          >
            <div className="max-h-64 overflow-y-auto">
              {availableTags.map((tag) => (
                <DropdownItem key={tag} onClick={() => handleTagToggle(tag)}>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={filters.tags.includes(tag)}
                      onChange={() => {}}
                      className="mr-2"
                    />
                    {tag}
                  </div>
                </DropdownItem>
              ))}
            </div>
          </Dropdown>
        </div>

        {/* Clear Filters Button */}
        {hasActiveFilters && (
          <Button
            variant="ghost"
            onClick={handleClearFilters}
            className="w-full md:w-auto"
          >
            <X className="w-4 h-4 mr-2" />
            Clear
          </Button>
        )}
      </div>

      {/* Active Filters Display */}
      {(filters.difficulty || filters.tags.length > 0) && (
        <div className="flex flex-wrap gap-2 mt-4">
          {filters.difficulty && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
              Difficulty: {filters.difficulty.charAt(0).toUpperCase() + filters.difficulty.slice(1)}
              <button
                onClick={() => handleDifficultySelect(undefined)}
                className="ml-2 hover:text-blue-600"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          )}
          {filters.tags.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200"
            >
              {tag}
              <button
                onClick={() => handleTagToggle(tag)}
                className="ml-2 hover:text-gray-600"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
