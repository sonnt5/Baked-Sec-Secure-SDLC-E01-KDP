import { useNavigate } from 'react-router-dom';
import Card from '../ui/Card';
import Badge from '../ui/Badge';
import type { Problem } from '../../types/api';

export interface ProblemCardProps {
  problem: Problem;
}

export default function ProblemCard({ problem }: ProblemCardProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/problems/${problem.id}`);
  };

  const difficultyVariant = {
    easy: 'easy' as const,
    medium: 'medium' as const,
    hard: 'hard' as const,
  };

  return (
    <Card hover padding="md" className="cursor-pointer" onClick={handleClick}>
      <div className="flex flex-col space-y-3">
        <div className="flex items-start justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
            {problem.title}
          </h3>
          <Badge variant={difficultyVariant[problem.difficulty]} size="sm">
            {problem.difficulty.charAt(0).toUpperCase() + problem.difficulty.slice(1)}
          </Badge>
        </div>

        <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
          <span>
            Acceptance: <span className="font-medium">{problem.acceptanceRate.toFixed(1)}%</span>
          </span>
          <span>•</span>
          <span>
            Submissions: <span className="font-medium">{problem.totalSubmissions}</span>
          </span>
        </div>

        {problem.tags && problem.tags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {problem.tags.map((tag) => (
              <Badge key={tag} variant="gray" size="sm">
                {tag}
              </Badge>
            ))}
          </div>
        )}
      </div>
    </Card>
  );
}
