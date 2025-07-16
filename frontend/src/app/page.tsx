'use client';

import { useState, FormEvent, ChangeEvent } from 'react';
import { FaSpinner } from 'react-icons/fa';

type Status = 'idle' | 'loading' | 'success' | 'error';

interface PastRace {
  past_race_id: string;
  race_date: string;
  venue_name: string;
  race_name: string;
  weather: string;
  distance: string;
  head_count: number | null; // 18
  rank: number | null; // 5
  odds: number | null; // 10.5
  popularity: number | null; // 4
  umaban: number | null; // 10
  jockey_name: string; // "横山 武史"
}

interface Horse {
  horse_id: string;
  horse_name: string;
  past_races: PastRace[];
}

interface Entry {
  horse: Horse;
  jockey: string | null;
  odds: number;
  popularity: number;
  umaban: number | null;
  waku: number | null;
  weight_carried: number;
}

interface RaceData {
  race_id: string;
  race_name: string;
  race_date: string;
  race_number: string;
  venue: string;
  course_details: string;
  ground_condition: string | null;
  entries: Entry[];
}

export default function RaceAnalyzerPage() {
  const [status, setStatus] = useState<Status>('idle');
  const [raceId, setRaceId] = useState('');

  const [results, setResults] = useState<RaceData | null>(null);
  const [trackConditions, setTrackConditions] = useState({
    ryo: false,
    yayashige: false,
    omo: true,
    furyo: true,
  });
  const [input, setInput] = useState('202510020811');

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
  const getRankClass = (rank: number | null) => {
    if (typeof rank !== 'number' || rank === 0) {
      return 'text-gray-700';
    }

    switch (rank) {
      case 1:
        // 1着: ゴールド系の色で目立たせる
        return 'text-amber-500 font-extrabold';
      case 2:
        // 2着: シルバー系の色
        return 'text-slate-500 font-bold';
      case 3:
        // 3着: ブロンズ系の色
        return 'text-orange-600 font-bold';
      default:
        // 4着以下は通常の文字色
        return 'text-gray-700';
    }
  };
  const handleCheckboxChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = event.target;
    setTrackConditions((prev) => ({ ...prev, [name]: checked }));
  };

  return (
    <div className='bg-gray-100 min-h-screen p-4 sm:p-8 font-sans'>
      <div className='max-w-7xl mx-auto'>
        <header className='bg-green-600 text-white p-4 rounded-t-lg shadow-lg'>
          <h1 className='text-2xl font-bold'>Netkeiba Race Analyzer</h1>
        </header>

        <main className='bg-white p-6 rounded-b-lg shadow-lg relative'>
          {status === 'loading' && (
            <div className='absolute inset-0 bg-white bg-opacity-90 flex flex-col items-center justify-center z-10 rounded-b-lg'>
              <FaSpinner className='animate-spin text-green text-5xl mb-4' />
              <p className='text-xl font-semibold text-gray-700'>
                スクレイピング中です...
              </p>
              <p className='text-gray-500'>しばらくお待ちください</p>
            </div>
          )}

          <div className='flex items-center gap-4 mb-6 pb-6 border-b'>
            <input
              type='text'
              value={input}
              onChange={handleChange}
              placeholder='レースIDまたはURLを入力 (例: 202305050811)'
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
              {/* --- 絞り込み条件と分析結果テーブル (中身は変更なし) --- */}
              <div className='mb-6'>
                <h2 className='text-lg font-semibold mb-4 text-gray-700'>
                  ▼ 絞り込み条件
                </h2>
                <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4 border rounded-md bg-gray-50'>
                  <div className='flex flex-col gap-2'>
                    <label className='font-medium text-gray-600'>開催</label>
                    <select className='p-2 border rounded-md'>
                      <option>東京 ▼</option>
                    </select>
                  </div>
                  <div className='flex flex-col gap-2'>
                    <label className='font-medium text-gray-600'>コース</label>
                    <input
                      type='text'
                      defaultValue='芝2000'
                      className='p-2 border rounded-md'
                    />
                  </div>
                  <div className='flex flex-col gap-2'>
                    <label className='font-medium text-gray-600'>馬場</label>
                    <div className='flex items-center gap-4 pt-2'>
                      <label className='flex items-center gap-1'>
                        <input
                          type='checkbox'
                          name='omo'
                          checked={trackConditions.omo}
                          onChange={handleCheckboxChange}
                          className='form-checkbox h-5 w-5 text-green rounded'
                        />
                        重
                      </label>
                      <label className='flex items-center gap-1'>
                        <input
                          type='checkbox'
                          name='furyo'
                          checked={trackConditions.furyo}
                          onChange={handleCheckboxChange}
                          className='form-checkbox h-5 w-5 text-green rounded'
                        />
                        不良
                      </label>
                    </div>
                  </div>
                </div>
                <div className='flex justify-end gap-4 mt-4'>
                  <button className='bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-600-dark'>
                    適用
                  </button>
                  <button className='bg-gray-500 text-white px-6 py-2 rounded-md hover:bg-gray-600'>
                    リセット
                  </button>
                </div>
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
                {' '}
                {/* カード間のスペース */}
                {results?.entries.map((entry) => (
                  <div
                    key={entry.horse.horse_id}
                    className='border rounded-lg shadow-md overflow-hidden'
                  >
                    {/* カードヘッダー：出走情報 */}
                    <div className='bg-gray-100 p-4'>
                      <h3 className='text-2xl font-bold text-gray-900'>
                        {entry.horse.horse_name}
                      </h3>
                      <div className='flex items-center gap-4 text-sm text-gray-600 mt-1'>
                        <span>騎手: {entry.jockey || '未定'}</span>
                        <span>オッズ: {entry.odds}</span>
                        <span>人気: {entry.popularity}番</span>
                      </div>
                    </div>

                    {/* カードボディ：過去成績テーブル */}
                    <div className='p-4'>
                      <h4 className='text-md font-semibold mb-2 text-gray-700'>
                        過去の成績
                      </h4>
                      <div className='overflow-x-auto shadow-md rounded-lg'>
                        <table className='min-w-full divide-y divide-gray-200 bg-white'>
                          <thead className='bg-gray-50'>
                            <tr>
                              {/* テーブルヘッダー */}
                              <th className='py-3 px-4 text-left text-xs font-medium whitespace-nowrap text-gray-500 uppercase tracking-wider'>
                                日付
                              </th>
                              <th className='py-3 px-4 text-left text-xs font-medium whitespace-nowrap text-gray-500 uppercase tracking-wider'>
                                レース名
                              </th>
                              <th className='py-3 px-4 text-left text-xs font-medium whitespace-nowrap text-gray-500 uppercase tracking-wider'>
                                開催地
                              </th>
                              <th className='py-3 px-4 text-left text-xs font-medium whitespace-nowrap text-gray-500 uppercase tracking-wider'>
                                天気
                              </th>
                              <th className='py-3 px-4 text-left text-xs font-medium whitespace-nowrap text-gray-500 uppercase tracking-wider'>
                                コース
                              </th>
                              <th className='py-3 px-4 text-center text-xs font-medium whitespace-nowrap text-gray-500 uppercase tracking-wider'>
                                頭数
                              </th>
                              <th className='py-3 px-4 text-center text-xs font-medium whitespace-nowrap text-gray-500 uppercase tracking-wider'>
                                着順
                              </th>
                              <th className='py-3 px-4 text-right text-xs font-medium whitespace-nowrap text-gray-500 uppercase tracking-wider'>
                                オッズ
                              </th>
                              <th className='py-3 px-4 text-center text-xs font-medium whitespace-nowrap text-gray-500 uppercase tracking-wider'>
                                人気
                              </th>
                              <th className='py-3 px-4 text-center text-xs font-medium whitespace-nowrap text-gray-500 uppercase tracking-wider'>
                                馬番
                              </th>
                              <th className='py-3 px-4 text-left text-xs font-medium whitespace-nowrap text-gray-500 uppercase tracking-wider'>
                                騎手名
                              </th>
                            </tr>
                          </thead>
                          <tbody className='bg-white divide-y divide-gray-200'>
                            {entry.horse.past_races.map((pastRace) => (
                              <tr
                                key={pastRace.past_race_id}
                                className='hover:bg-gray-50'
                              >
                                <td className='py-3 px-4 whitespace-nowrap text-sm text-gray-900'>
                                  {pastRace.race_date}
                                </td>
                                <td className='py-3 px-4 whitespace-nowrap text-sm text-gray-900 font-medium'>
                                  {pastRace.race_name}
                                </td>
                                <td className='py-3 px-4 whitespace-nowrap text-sm text-gray-900'>
                                  {pastRace.venue_name}
                                </td>
                                <td className='py-3 px-4 whitespace-nowrap text-sm text-gray-900 text-center'>
                                  {pastRace.weather}
                                </td>
                                <td className='py-3 px-4 whitespace-nowrap text-sm text-gray-900'>
                                  {pastRace.distance}
                                </td>

                                <td className='py-3 px-4 whitespace-nowrap text-sm text-gray-900 text-center'>
                                  {pastRace.head_count}
                                </td>
                                <td
                                  className={`py-3 px-4 whitespace-nowrap text-sm text-center ${getRankClass(
                                    pastRace.rank
                                  )}`}
                                >
                                  {pastRace.rank}着
                                </td>
                                <td className='py-3 px-4 whitespace-nowrap text-sm text-gray-900 text-right'>
                                  {pastRace.odds}
                                </td>
                                <td className='py-3 px-4 whitespace-nowrap text-sm text-gray-900 text-center'>
                                  {pastRace.popularity}
                                </td>
                                <td className='py-3 px-4 whitespace-nowrap text-sm text-gray-900 text-center'>
                                  {pastRace.umaban}
                                </td>
                                <td className='py-3 px-4 whitespace-nowrap text-sm text-gray-900 '>
                                  {pastRace.jockey_name}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
