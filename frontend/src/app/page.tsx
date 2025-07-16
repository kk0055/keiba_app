'use client';

import { useState } from 'react';
import { FaSpinner } from 'react-icons/fa';

// ダミーデータ
const dummyResults = [
  {
    type: '出走情報',
    horseName: 'イクイノックス',
    jockey: 'ルメール',
    odds: 1.5,
    popularity: 1,
  },
  {
    type: '出走情報',
    horseName: 'リバティアイランド',
    jockey: '川田',
    odds: 3.2,
    popularity: 2,
  },
  {
    type: '過去成績',
    horseName: 'イクイノックス',
    raceName: '天皇賞(秋)',
    rank: 1,
    date: '2023-10-29',
  },
];

type Status = 'idle' | 'loading' | 'success' | 'error';

export default function RaceAnalyzerPage() {
  const [status, setStatus] = useState<Status>('idle');
  const [raceId, setRaceId] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [trackConditions, setTrackConditions] = useState({
    ryo: false,
    yayashige: false,
    omo: true,
    furyo: true,
  });

  const handleExecute = async () => {
    if (!raceId || status === 'loading') return;

    setStatus('loading');
    setResults([]);

    console.log(`[${raceId}] のスクレイピングを開始します...`);
    await new Promise((resolve) => setTimeout(resolve, 2500));
    console.log('スクレイピングが完了しました。');

    setResults(dummyResults);
    setStatus('success');
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
              value={raceId}
              onChange={(e) => setRaceId(e.target.value)}
              placeholder='レースIDを入力 (例: 202305050811)'
              className='flex-grow p-2 border rounded-md focus:ring-2 focus:ring-green focus:border-transparent disabled:bg-gray-200'
              disabled={status === 'loading'}
            />
            <button
              onClick={handleExecute}
              className='bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-600-dark transition-colors font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed'
              // 「ローディング中」または「raceIdが空」の時にボタンを非活性化する
              disabled={status === 'loading' || !raceId}
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
              <div>
                <h2 className='text-lg font-semibold mb-4 text-gray-700'>
                  ▼ 分析結果テーブル (ソート可能)
                </h2>
                <div className='overflow-x-auto'>
                  <table className='min-w-full bg-white border'>
                    <thead className='bg-gray-200'>
                      <tr>
                        <th className='py-3 px-4 text-left font-semibold text-gray-600'>
                          レコード種別
                        </th>
                        <th className='py-3 px-4 text-left font-semibold text-gray-600'>
                          馬名
                        </th>
                        <th className='py-3 px-4 text-left font-semibold text-gray-600'>
                          騎手/レース名
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.map((row, index) => (
                        <tr key={index} className='border-b hover:bg-gray-50'>
                          <td className='py-3 px-4'>
                            <span
                              className={`px-2 py-1 text-xs font-semibold rounded-full ${
                                row.type === '出走情報'
                                  ? 'bg-blue-100 text-blue-800'
                                  : 'bg-green-100 text-green-800'
                              }`}
                            >
                              {row.type}
                            </span>
                          </td>
                          <td className='py-3 px-4 font-medium'>
                            {row.horseName}
                          </td>
                          <td className='py-3 px-4'>
                            {row.type === '出走情報'
                              ? row.jockey
                              : row.raceName}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
