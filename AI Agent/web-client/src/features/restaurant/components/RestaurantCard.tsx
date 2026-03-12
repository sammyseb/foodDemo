import { Card } from '@/shared/components';
import type { Restaurant } from '@/shared/types';
import { Globe, MapPin, Phone, Star } from 'lucide-react';

interface RestaurantCardProps {
  restaurant: Restaurant;
  variant?: 'compact' | 'default' | 'detailed';
  onSelect?: () => void;
}

export function RestaurantCard({ restaurant, variant = 'default', onSelect }: RestaurantCardProps) {
  const priceLevel = restaurant.price_level ? '$'.repeat(restaurant.price_level) : '';

  if (variant === 'compact') {
    return (
      <div 
        className="flex gap-3 p-3 bg-white rounded-lg border border-gray-200 cursor-pointer hover:border-primary-300 transition-colors"
        onClick={onSelect}
      >
        {restaurant.photo_url && (
          <img 
            src={restaurant.photo_url} 
            alt={restaurant.name}
            className="w-16 h-16 rounded-lg object-cover"
          />
        )}
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-gray-900 truncate">{restaurant.name}</h4>
          <p className="text-sm text-gray-500 truncate">{restaurant.address}</p>
          {restaurant.rating && (
            <div className="flex items-center gap-1 mt-1">
              <Star className="w-3 h-3 text-yellow-500 fill-yellow-500" />
              <span className="text-sm text-gray-600">{restaurant.rating}</span>
            </div>
          )}
        </div>
      </div>
    );
  }

  if (variant === 'detailed') {
    return (
      <Card className="overflow-hidden" hover clickable onClick={onSelect}>
        {restaurant.photo_url && (
          <div className="aspect-video relative">
            <img 
              src={restaurant.photo_url} 
              alt={restaurant.name}
              className="w-full h-full object-cover"
            />
            {priceLevel && (
              <span className="absolute top-2 right-2 bg-white/90 px-2 py-1 rounded text-sm font-medium">
                {priceLevel}
              </span>
            )}
          </div>
        )}
        <div className="p-4">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-semibold text-lg text-gray-900">{restaurant.name}</h3>
            {restaurant.rating && (
              <div className="flex items-center gap-1 bg-yellow-50 px-2 py-1 rounded">
                <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                <span className="font-medium">{restaurant.rating}</span>
                {restaurant.review_count && (
                  <span className="text-gray-500 text-sm">({restaurant.review_count})</span>
                )}
              </div>
            )}
          </div>
          
          <div className="mt-3 space-y-2">
            <div className="flex items-center gap-2 text-gray-600">
              <MapPin className="w-4 h-4" />
              <span className="text-sm">{restaurant.address}</span>
            </div>
            
            {restaurant.phone_number && (
              <div className="flex items-center gap-2 text-gray-600">
                <Phone className="w-4 h-4" />
                <span className="text-sm">{restaurant.phone_number}</span>
              </div>
            )}
            
            {restaurant.website && (
              <div className="flex items-center gap-2 text-gray-600">
                <Globe className="w-4 h-4" />
                <a 
                  href={restaurant.website} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-primary-600 hover:underline"
                  onClick={(e) => e.stopPropagation()}
                >
                  Visit Website
                </a>
              </div>
            )}
          </div>

          {restaurant.cuisine_type && restaurant.cuisine_type.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {restaurant.cuisine_type.map((cuisine) => (
                <span 
                  key={cuisine}
                  className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                >
                  {cuisine}
                </span>
              ))}
            </div>
          )}
        </div>
      </Card>
    );
  }

  // Default variant
  return (
    <Card hover clickable onClick={onSelect}>
      <div className="flex gap-4">
        {restaurant.photo_url && (
          <img 
            src={restaurant.photo_url} 
            alt={restaurant.name}
            className="w-24 h-24 rounded-lg object-cover flex-shrink-0"
          />
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h4 className="font-medium text-gray-900">{restaurant.name}</h4>
            {restaurant.rating && (
              <div className="flex items-center gap-1 flex-shrink-0">
                <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                <span className="text-sm">{restaurant.rating}</span>
              </div>
            )}
          </div>
          <p className="text-sm text-gray-500 mt-1 line-clamp-2">{restaurant.address}</p>
          {restaurant.cuisine_type && restaurant.cuisine_type.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {restaurant.cuisine_type.slice(0, 3).map((cuisine) => (
                <span 
                  key={cuisine}
                  className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded"
                >
                  {cuisine}
                </span>
              ))}
              {priceLevel && (
                <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded">
                  {priceLevel}
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}
