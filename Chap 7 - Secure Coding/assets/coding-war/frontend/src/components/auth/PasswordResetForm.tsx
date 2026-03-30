import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { resetPasswordSchema, type ResetPasswordFormData } from '../../utils/validation';
import { Button, Input } from '../ui';
import { useState } from 'react';

interface PasswordResetFormProps {
  onSubmit: (password: string) => Promise<void>;
  isLoading?: boolean;
}

export default function PasswordResetForm({ onSubmit, isLoading = false }: PasswordResetFormProps) {
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
  });

  const handleFormSubmit = async (data: ResetPasswordFormData) => {
    try {
      setError(null);
      await onSubmit(data.password);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Password reset failed. Please try again.');
    }
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
          {error}
        </div>
      )}

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
          New Password
        </label>
        <Input
          id="password"
          type="password"
          {...register('password')}
          error={errors.password?.message}
          disabled={isLoading}
        />
        {errors.password && (
          <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
          Confirm Password
        </label>
        <Input
          id="confirmPassword"
          type="password"
          {...register('confirmPassword')}
          error={errors.confirmPassword?.message}
          disabled={isLoading}
        />
        {errors.confirmPassword && (
          <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>
        )}
      </div>

      <Button
        type="submit"
        variant="primary"
        className="w-full"
        disabled={isLoading}
      >
        {isLoading ? 'Resetting...' : 'Reset Password'}
      </Button>
    </form>
  );
}
