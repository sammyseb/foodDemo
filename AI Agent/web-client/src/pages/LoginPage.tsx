import { APP_NAME } from '@/config';
import { useAuthStore } from '@/features/auth/stores/authStore';
import { login } from '@/services/api/auth';
import { Button, Card, Input } from '@/shared/components';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export function LoginPage() {
  const navigate = useNavigate();
  const { login: storeLogin, setLoading, isLoading } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // For demo purposes, accept any credentials
      // In production, this would validate against the backend
      const response = await login({ username: email, password });
      storeLogin(
        { id: '1', email, name: email.split('@')[0] },
        response.access_token
      );
      navigate('/');
    } catch {
      // For demo, allow login without backend
      storeLogin(
        { id: '1', email, name: email.split('@')[0] },
        'demo-token-12345'
      );
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">{APP_NAME}</h1>
          <p className="text-gray-500 mt-2">Sign in to continue</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
          />

          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
          />

          {error && (
            <p className="text-sm text-red-600">{error}</p>
          )}

          <Button
            type="submit"
            className="w-full"
            isLoading={isLoading}
          >
            Sign In
          </Button>
        </form>
      </Card>
    </div>
  );
}
