'use client';

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import type { PastRace,Filters } from '@/types/types';
import Slider from 'rc-slider'; 
import 'rc-slider/assets/index.css'; 

const WEATHER_OPTIONS = ['晴', '曇', '雨'];
const TRACK_OPTIONS = ['良', '稍', '重'];
const MAX_RANK = 18;
const MAX_RECENT_RACES = 10;

const INITIAL_FILTERS: Filters = {
  venue: 'all',
  rank: MAX_RANK,
  distance: '',
  weather: [],
  ground_condition: [],
  recentRaces: MAX_RECENT_RACES,
};

interface FilterControlsProps {
  allPastRaces: PastRace[];
  onFilterChange: (filters: Filters) => void;
}

export const FilterControls: React.FC<FilterControlsProps> = ({
  allPastRaces,
  onFilterChange,
}) => {
  const [filters, setFilters] = useState<Filters>(INITIAL_FILTERS);

  useEffect(() => {
    onFilterChange(filters);
  }, [filters, onFilterChange]);

  const venueOptions = useMemo(() => {
    const venues = allPastRaces.map((race) => race.venue_name);
    return ['all', ...Array.from(new Set(venues))];
  }, [allPastRaces]);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      const { name, value, type } = e.target;
      const isCheckbox = type === 'checkbox';
      const checked = isCheckbox
        ? (e.target as HTMLInputElement).checked
        : false;
      setFilters((prev) => ({ ...prev, [name]: isCheckbox ? checked : value }));
    },
    []
  );

  const handleSliderChange = useCallback(
    (name: 'rank' | 'recentRaces', value: number | number[]) => {
      // valueが配列の場合も考慮（RangeSlider用だが、ここでは数値のみ扱う）
      const numValue = Array.isArray(value) ? value[0] : value;
      setFilters((prev) => ({ ...prev, [name]: numValue }));
    },
    []
  );

  const handleMultiCheckboxChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const { name, value, checked } = e.target;
      setFilters((prev) => {
        const currentValues = (prev[name as keyof Filters] as string[]) || [];
        if (checked) {
          return { ...prev, [name]: [...currentValues, value] };
        } else {
          return {
            ...prev,
            [name]: currentValues.filter((item) => item !== value),
          };
        }
      });
    },
    []
  );

  const handleResetClick = useCallback(() => {
    setFilters(INITIAL_FILTERS);
  }, []);

  return (
    <div className='mb-6'>
      <h2 className='text-lg font-semibold mb-4 text-gray-700'>
        ▼ 絞り込み条件
      </h2>
      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 p-4 border rounded-md bg-gray-50'>
        <div>
          <label htmlFor='venue' className='font-medium text-gray-600'>
            開催地
          </label>
          <select
            id='venue'
            name='venue'
            value={filters.venue}
            onChange={handleInputChange}
            className='w-full p-2 border rounded-md mt-1'
          >
            {venueOptions.map((venue) => (
              <option key={venue} value={venue}>
                {venue === 'all' ? 'すべて' : venue}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor='distance' className='font-medium text-gray-600'>
            距離
          </label>
          <input
            id='distance'
            name='distance'
            type='text'
            placeholder='例: 2000'
            value={filters.distance}
            onChange={handleInputChange}
            className='w-full p-2 border rounded-md mt-1'
          />
        </div>
        <div>
          <label className='font-medium text-gray-600'>天気</label>
          <div className='flex items-center gap-4 pt-2'>
            {WEATHER_OPTIONS.map((w) => (
              <label key={w} className='flex items-center gap-1'>
                <input
                  type='checkbox'
                  name='weather'
                  value={w}
                  checked={filters.weather.includes(w)}
                  onChange={handleMultiCheckboxChange}
                  className='form-checkbox h-5 w-5 text-green-600 rounded'
                />
                {w}
              </label>
            ))}
          </div>
        </div>
        <div>
          <label className='font-medium text-gray-600'>馬場</label>
          <div className='flex items-center gap-4 pt-2'>
            {TRACK_OPTIONS.map((t) => (
              <label key={t} className='flex items-center gap-1'>
                <input
                  type='checkbox'
                  name='ground_condition'
                  value={t}
                  checked={filters.ground_condition.includes(t)}
                  onChange={handleMultiCheckboxChange}
                  className='form-checkbox h-5 w-5 text-green-600 rounded'
                />
                {t}
              </label>
            ))}
          </div>
        </div>
        {/* <div className='space-y-6'> */}
          <div>
            <label className='font-medium text-gray-600 flex justify-between'>
              直近のレース
              <span className='font-bold text-green-600'>
                {filters.recentRaces}件
              </span>
            </label>
            <Slider
              min={1}
              max={MAX_RECENT_RACES}
              value={filters.recentRaces}
              onChange={(value) => handleSliderChange('recentRaces', value)}
              className='mt-2 '
              styles={{
                track: { backgroundColor: '#16a34a' },
                handle: { borderColor: '#16a34a' },
              }}
            />
          </div>
          <div>
            <label className='font-medium text-gray-600 flex justify-between'>
              着順
              <span className='font-bold text-green-600'>
                {filters.rank}着以内
              </span>
            </label>
            <Slider
              min={1}
              max={MAX_RANK}
              value={filters.rank}
              onChange={(value) => handleSliderChange('rank', value)}
              className='mt-2'
              trackStyle={{ backgroundColor: '#16a34a' }}
              handleStyle={{ borderColor: '#16a34a' }}
            />
          </div>
        {/* </div> */}
        {/* <div className='flex items-center pt-2'>
          <label className='flex items-center gap-2'>
            <input
              type='checkbox'
              name='rank'
              checked={filters.rank}
              onChange={handleInputChange}
              className='form-checkbox h-5 w-5 text-green-600 rounded'
            />
            3着以内
          </label>
        </div> */}
      </div>
      <div className='flex justify-end gap-4 mt-4'>
        <button
          onClick={handleResetClick}
          className='bg-gray-500 text-white px-6 py-2 rounded-md hover:bg-gray-600'
        >
          リセット
        </button>
      </div>
    </div>
  );
};
