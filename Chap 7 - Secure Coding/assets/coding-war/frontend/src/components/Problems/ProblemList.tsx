import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../ui/Table';
import Badge from '../ui/Badge';
import type { Problem } from '../../types/api';

export interface ProblemListProps {
  problems: Problem[];
  onProblemClick: (problemId: string) => void;
}

export default function ProblemList({ problems, onProblemClick }: ProblemListProps) {
  const difficultyVariant = {
    EASY: 'easy' as const,
    MEDIUM: 'medium' as const,
    HARD: 'hard' as const,
    easy: 'easy' as const,
    medium: 'medium' as const,
    hard: 'hard' as const,
  };

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Title</TableHead>
          <TableHead>Difficulty</TableHead>
          <TableHead>Tags</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {problems.map((problem) => (
          <TableRow
            key={problem.id}
            onClick={() => onProblemClick(problem.id)}
          >
            <TableCell>
              <div className="flex items-center gap-2">
                {problem.userSolved && (
                  <span
                    title="Solved"
                    className="flex-shrink-0 w-5 h-5 rounded-full bg-green-500 flex items-center justify-center text-white text-xs font-bold"
                  >
                    ✓
                  </span>
                )}
                <span className="font-medium text-blue-600 dark:text-blue-400 hover:underline cursor-pointer">
                  {problem.title}
                </span>
              </div>
            </TableCell>
            <TableCell>
              <Badge variant={difficultyVariant[problem.difficulty] ?? 'easy'} size="sm">
                {problem.difficulty.charAt(0).toUpperCase() + problem.difficulty.slice(1).toLowerCase()}
              </Badge>
            </TableCell>
            <TableCell>
              <div className="flex flex-wrap gap-1">
                {problem.tags.slice(0, 3).map((tag) => (
                  <Badge key={tag} variant="gray" size="sm">
                    {tag}
                  </Badge>
                ))}
                {problem.tags.length > 3 && (
                  <Badge variant="gray" size="sm">
                    +{problem.tags.length - 3}
                  </Badge>
                )}
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
