'use client';

import { useState, useMemo, useCallback } from 'react';
import { FaSpinner } from 'react-icons/fa';
import type { RaceData, Filters } from '@/types/types';
import { FilterControls } from '../components/FilterControls';
import { HorseCard } from '../components/HorseCard';
import Toast from '@/components/Toast'; 
import useSWR, { mutate } from 'swr';
import { getPredictionByRaceId } from '@/lib/api';
import PredictionForm from '@/components/PredictionForm';

type Status = 'idle' | 'loading' | 'success' | 'error';



export default function RaceAnalyzerPage() {
  const [status, setStatus] = useState<Status>('idle');
  const [raceId, setRaceId] = useState('');
  const [results, setResults] = useState<RaceData | null>(null);
  const [input, setInput] = useState('');

  const [toast, setToast] = useState<{
    show: boolean;
    message: string | null;
    type: 'success' | 'error';
  }>({
    show: false,
    message: '',
    type: 'success',
  });

  const [filters, setFilters] = useState<Filters>({
    venue: 'all',
    rank: 5,
    distance: '',
    weather: [],
    ground_condition: [],
    recentRaces: 10,
    jockeyMatch: false,
  });

  const {
    data: prediction,
  } = useSWR(
    raceId ? `/predictions/?race=${raceId}` : null, 
    () => getPredictionByRaceId(raceId)
  );

  const handleSuccess = () => {
    mutate(`/predictions/?race=${raceId}`);
    setToast({
      show: true,
      message: '保存!',
      type: 'success',
    });
  };

  const handleCloseToast = () => {
    setToast({ ...toast, show: false });
  };

  /**
   * フィルター状態を更新するメモ化されたコールバック。
   * 子コンポーネントの不要な再レンダリングを防ぐためにuseCallbackを使用。
   * @param newFilters 新しいフィルターオブジェクト
   */
  const handleFilterChange = useCallback((newFilters: Filters) => {
    setFilters(newFilters);
  }, []);

  /**
   * 全ての馬の過去レース情報をフラットな配列に変換してメモ化。
   * resultsが変更されるまで再計算されないため、パフォーマンスが向上する。
   */
  const allPastRaces = useMemo(() => {
    if (!results) return [];
    return results.entries.flatMap((entry) => entry.horse.past_races);
  }, [results]);

  /**
   * 様々な形式の文字列から12桁のrace_idを抽出するユーティリティ関数。
   * @param {string} value - race_idを含む可能性のある入力文字列。
   * @returns {string | null} 抽出された12桁のrace_id。見つからない場合はnull。
   */
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
  const showJockeyFilter = useMemo(() => {
    if (!results || !results.entries) return false;
    // entriesの中に、jockeyがnullでないものが1つでもあればtrueを返す
    return results.entries.some(
      (entry) => entry.jockey !== null && entry.jockey !== undefined
    );
  }, [results]);

  /**
   * 入力された値からrace_idを抽出し、バックエンドAPIにレースデータの取得を要求する非同期関数。
   * 処理の進行状況に応じて、コンポーネントの状態 (status) を更新する。
   */
  const handleFetchRace = async () => {
    setToast({
      show: false,
      message: '',
      type: 'success',
    });
    const id = extractRaceId(input.trim());
    if (!id) {
      setToast({
        show: true,
        message:
          'ヒヒーン！そのIDじゃゲートインできないよ！正しいIDかURLを教えてくれないと、走り出せないんだ！',
        type: 'error',
      });
      return;
    }

    setStatus('loading');
    setRaceId(id);
    setResults(null); // 新しいリクエストの前に古い結果をクリアする
    console.log(`[${id}] のスクレイピングを開始します...`); // 更新前のraceIdではなく、抽出したidを使う
    const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
    try {
      const res = await fetch(`${baseUrl}/race/${id}/`);

      if (!res.ok) {
        const errorData = await res.json().catch(() => null);
        const message =
          errorData?.message ||
          `ブルルッ…そのレース番号、どこを探しても見つからないなぁ…`;
  
        setToast({
          show: true,
          message: message,
          type: 'error',
        });
        throw new Error(message);
      }
      const data = await res.json();
      console.log('Results:', data);
      setResults(data);
      setStatus('success');
      console.log('スクレイピングが完了しました。');
    } catch (err: unknown) {
      if (err instanceof Error) {
        console.error('Fetch error:', err.message);
      }
      setStatus('error');
      setResults(null);
    }
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
                スクレイピング中だよ〜🐎💨 5分くらい待ってね〜☕🌈
              </p>
              {/* <p className='text-gray-500'>しばらくお待ちください</p> */}
            </div>
          )}
          <label
            htmlFor='raceIdInput'
            className='block text-xs sm:text-sm font-medium text-gray-700 mb-2'
          >
            netkeiba.comのレースIDかURLをゲートイン🏇！(例:202510020811)
          </label>
          <div className='flex items-center gap-4 mb-6 pb-6 border-b'>
            <input
              id='raceIdInput'
              type='text'
              value={input}
              onChange={handleChange}
              placeholder='勝ち馬を探そう！'
              className='flex-grow p-2 border rounded-md focus:ring-2 focus:ring-green focus:border-transparent disabled:bg-gray-200'
              disabled={status === 'loading'}
            />
            <button
              onClick={handleFetchRace}
              className='bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-600-dark transition-colors font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed'
              // 「ローディング中」または「inputが空」の時にボタンを非活性化する
              disabled={status === 'loading'}
            >
              {status === 'loading' ? '実行中...' : '実行'}
            </button>
          </div>
          <Toast
            show={toast.show}
            message={toast.message}
            onClose={handleCloseToast}
            type={toast.type}
          />
          {status === 'success' && (
            <div className='animate-fade-in'>
              <FilterControls
                allPastRaces={allPastRaces}
                onFilterChange={handleFilterChange}
                showJockeyFilter={showJockeyFilter}
              />
              <div>
                <PredictionForm
                  raceId={raceId}
                  editingPrediction={prediction || null}
                  onSuccess={handleSuccess}
                />
              </div>
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
