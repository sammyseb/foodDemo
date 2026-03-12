import { RestaurantCard, RestaurantList } from '@/features/restaurant/components';
import { Button, Input } from '@/shared/components';
import type { Restaurant } from '@/shared/types';
import { Search, SlidersHorizontal } from 'lucide-react';
import React, { useState } from 'react';

// Mock data for demo
const MOCK_RESTAURANTS: Restaurant[] = [
  {
    id: '1',
    name: 'Pasta Palace',
    address: '123 Italian Way, San Francisco, CA',
    rating: 4.5,
    review_count: 234,
    price_level: 2,
    cuisine_type: ['Italian', 'Pasta', 'Pizza'],
    phone_number: '+1 (415) 555-0123',
    website: 'https://example.com',
    photo_url: 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400',
  },
  {
    id: '2',
    name: 'Sushi Zen',
    address: '456 Japanese St, San Francisco, CA',
    rating: 4.8,
    review_count: 567,
    price_level: 3,
    cuisine_type: ['Japanese', 'Sushi', 'Asian'],
    phone_number: '+1 (415) 555-0456',
    website: 'https://example.com',
    photo_url: 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=400',
  },
  {
    id: '3',
    name: 'Thai Orchid',
    address: '789 Thai Ave, San Francisco, CA',
    rating: 4.3,
    review_count: 189,
    price_level: 2,
    cuisine_type: ['Thai', 'Asian', 'Curry'],
    phone_number: '+1 (415) 555-0789',
    photo_url: 'https://images.unsplash.com/photo-1559314809-0d155014e29e?w=400',
  },
  {
    id: '4',
    name: 'The Burger Joint',
    address: '321 Grill Rd, San Francisco, CA',
    rating: 4.2,
    review_count: 412,
    price_level: 1,
    cuisine_type: ['American', 'Burgers', 'Fast Food'],
    phone_number: '+1 (415) 555-0321',
    photo_url: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400',
  },
  {
    id: '5',
    name: 'Taco Fiesta',
    address: '654 Mexican Blvd, San Francisco, CA',
    rating: 4.6,
    review_count: 298,
    price_level: 1,
    cuisine_type: ['Mexican', 'Tacos', 'Latin'],
    phone_number: '+1 (415) 555-0654',
    photo_url: 'https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=400',
  },
];

export function SearchPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setHasSearched(true);
    // In production, this would call an API
    // For demo, filter mock data
    if (searchQuery.trim()) {
      const filtered = MOCK_RESTAURANTS.filter(r => 
        r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.cuisine_type?.some(c => c.toLowerCase().includes(searchQuery.toLowerCase())) ||
        r.address.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setRestaurants(filtered);
    } else {
      setRestaurants(MOCK_RESTAURANTS);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-6">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Find Restaurants</h1>
          
          {/* Search Bar */}
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="flex-1">
              <Input
                placeholder="Search by name, cuisine, or location..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                leftIcon={<Search className="w-5 h-5" />}
              />
            </div>
            <Button type="submit">
              Search
            </Button>
          </form>

          {/* Quick Filters */}
          <div className="flex gap-2 mt-4 overflow-x-auto pb-2">
            <Button variant="ghost" size="sm">
              <SlidersHorizontal className="w-4 h-4 mr-1" />
              Filters
            </Button>
            {['Italian', 'Japanese', 'Thai', 'Mexican', 'American'].map((cuisine) => (
              <Button
                key={cuisine}
                variant="secondary"
                size="sm"
                onClick={() => {
                  setSearchQuery(cuisine);
                  setHasSearched(true);
                  setRestaurants(
                    MOCK_RESTAURANTS.filter(r => 
                      r.cuisine_type?.some(c => c.toLowerCase() === cuisine.toLowerCase())
                    )
                  );
                }}
              >
                {cuisine}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        {!hasSearched ? (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">Search for restaurants to get started</p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {MOCK_RESTAURANTS.slice(0, 6).map((restaurant) => (
                <RestaurantCard
                  key={restaurant.id}
                  restaurant={restaurant}
                  variant="default"
                />
              ))}
            </div>
          </div>
        ) : (
          <div>
            <p className="text-gray-600 mb-4">
              {restaurants.length} restaurant{restaurants.length !== 1 ? 's' : ''} found
            </p>
            <RestaurantList 
              restaurants={restaurants} 
              variant="detailed"
            />
          </div>
        )}
      </div>
    </div>
  );
}
