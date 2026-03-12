import type { Restaurant } from '@/shared/types';
import { RestaurantCard } from './RestaurantCard';

interface RestaurantListProps {
  restaurants: Restaurant[];
  variant?: 'compact' | 'default' | 'detailed';
  onSelect?: (restaurant: Restaurant) => void;
}

export function RestaurantList({ restaurants, variant = 'default', onSelect }: RestaurantListProps) {
  if (restaurants.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No restaurants found
      </div>
    );
  }

  return (
    <div className={cn(
      variant === 'detailed' 
        ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'
        : 'space-y-3'
    )}>
      {restaurants.map((restaurant) => (
        <RestaurantCard
          key={restaurant.id}
          restaurant={restaurant}
          variant={variant}
          onSelect={() => onSelect?.(restaurant)}
        />
      ))}
    </div>
  );
}

function cn(...classes: (string | undefined)[]) {
  return classes.filter(Boolean).join(' ');
}
