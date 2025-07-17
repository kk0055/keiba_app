'use client';

import { useState, useMemo, useCallback } from 'react';
import { FaSpinner } from 'react-icons/fa';
import type { RaceData, Filters } from '@/types/types';
import { FilterControls } from '../components/FilterControls';
import { HorseCard } from '../components/HorseCard';

type Status = 'idle' | 'loading' | 'success' | 'error';

export default function RaceAnalyzerPage() {
  const [status, setStatus] = useState<Status>('idle');
  const [raceId, setRaceId] = useState('');
  const [results, setResults] = useState<RaceData | null>(null);
  const [input, setInput] = useState('202510020811');
  
  const [filters, setFilters] = useState<Filters>({
    venue: 'all',
    rank: 5,
    distance: '',
    weather: [],
    ground_condition: [],
    recentRaces: 10,
  });

  const handleFilterChange = useCallback((newFilters: Filters) => {
    setFilters(newFilters);
  }, []);
  const allPastRaces = useMemo(() => {
    if (!results) return [];
    return results.entries.flatMap((entry) => entry.horse.past_races);
  }, [results]);

  const extractRaceId = (value: string): string | null => {
    const urlParamMatch = value.match(/race_id=(\d{12})/);
    if (urlParamMatch) return urlParamMatch[1];

    const pathMatch = value.match(/\/race\/(\d{12})\/?/);
    if (pathMatch) return pathMatch[1];

    const idOnlyMatch = value.match(/^(\d{12})$/);
    if (idOnlyMatch) return idOnlyMatch[1];

    return null;
  };
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;
    setInput(inputValue);
    const extractedId = extractRaceId(inputValue);
    if (extractedId) {
      setRaceId(extractedId);
    } else {
      setRaceId('');
    }
  };
  const handleFetchRace = async () => {
    setStatus('loading');
    const id = extractRaceId(input.trim());
    if (id) {
      setRaceId(id);
      console.log('抽出された race_id:', id);
      console.log(`[${raceId}] のスクレイピングを開始します...`);
    } else {
      alert('有効なレースIDまたはURLを入力してください。');
    }
    const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
    try {
      const res = await fetch(`${baseUrl}/race/${id}`);

      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }
      const data = await res.json();
      console.log('Results:', data);
      setResults(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        console.error('Fetch error:', err.message);
      }
      setStatus('error');
      setResults(null);
    }

    await new Promise((resolve) => setTimeout(resolve, 2500));
    console.log('スクレイピングが完了しました。');
    setStatus('success');
  };

  return (
    <div className='bg-gray-100 min-h-screen p-4 sm:p-8 font-sans'>
      <div className='max-w-7xl mx-auto'>
        <header className='bg-green-600 text-white p-4 rounded-t-lg shadow-lg'>
          <h1 className='flex items-center space-x-3 text-4xl font-extrabold text-green-100 drop-shadow-lg'>
            <span className='text-5xl'>🐴</span>
            <span>Hoof</span>
            <span className='text-yellow-300 italic'>Picks</span>
          </h1>
        </header>

        <main className='bg-white p-6 rounded-b-lg shadow-lg relative'>
          {status === 'loading' && (
            <div className='absolute inset-0 bg-white bg-opacity-90 flex flex-col items-center justify-center z-10 rounded-b-lg'>
              <FaSpinner className='animate-spin text-green text-5xl mb-4' />
              <p className='text-xl font-semibold text-gray-700'>
                スクレイピング中だよ~🐎💨 5分くらい待ってね〜☕🌈
              </p>
              {/* <p className='text-gray-500'>しばらくお待ちください</p> */}
            </div>
          )}

          <div className='flex items-center gap-4 mb-6 pb-6 border-b'>
            <input
              type='text'
              value={input}
              onChange={handleChange}
              placeholder='netkeiba.comのレースIDまたはURLを入力 (例: 202305050811)'
              className='flex-grow p-2 border rounded-md focus:ring-2 focus:ring-green focus:border-transparent disabled:bg-gray-200'
              disabled={status === 'loading'}
            />
            <button
              onClick={handleFetchRace}
              className='bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-600-dark transition-colors font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed'
              // 「ローディング中」または「raceIdが空」の時にボタンを非活性化する
              disabled={status === 'loading' || !input}
            >
              {status === 'loading' ? '実行中...' : '実行'}
            </button>
          </div>

          {status === 'success' && (
            <div className='animate-fade-in'>
              <FilterControls
                allPastRaces={allPastRaces}
                onFilterChange={handleFilterChange}
              />
              {/* レース情報の表示 */}
              <div className='mb-6 p-4 bg-gray-50 rounded-lg border'>
                <h2 className='text-xl font-bold text-gray-800'>
                  {results?.race_name}
                </h2>
                <p className='text-sm text-gray-600'>
                  {results?.race_date} | {results?.race_number}R |{' '}
                  {results?.venue} | {results?.course_details} | 馬場:{' '}
                  {results?.ground_condition || '未発表'}
                </p>
              </div>
              <div className='space-y-8'>
                {results?.entries.map((entry) => (
                  <HorseCard
                    key={entry.horse.horse_id}
                    entry={entry}
                    filters={filters}
                  />
                ))}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
