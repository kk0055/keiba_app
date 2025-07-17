'use client';

import React, { useMemo } from 'react';
import type { HorseCardProps } from '@/types/types';

const getRankClass = (rank: number | null) => {
  const baseClasses =
    'text-sm rounded-full inline-flex items-center justify-center px-2.5 py-0.5';
  if (typeof rank !== 'number' || rank === 0) return 'text-gray-700 bg-white ';
  switch (rank) {
    case 1:
      return `${baseClasses} text-black font-extrabold bg-amber-300`;
    case 2:
      return `${baseClasses} text-black font-extrabold bg-slate-300`;
    case 3:
      return `${baseClasses} text-black font-extrabold bg-orange-400`;
    default:
      return 'text-gray-700 bg-white';
  }
};

export const HorseCard: React.FC<HorseCardProps> = ({ entry, filters }) => {
  const displayedPastRaces = useMemo(() => {
    let filteredData = [...entry.horse.past_races].slice(
      0,
      filters.recentRaces
    );
    if (filters.venue !== 'all') {
      filteredData = filteredData.filter((r) => r.venue_name === filters.venue);
    }
    if (filters.rank < 18) {
      // 18はスライダーの最大値
      filteredData = filteredData.filter(
        (r) => r.rank !== null && r.rank <= filters.rank
      );
    }
    if (filters.distance) {
      filteredData = filteredData.filter((r) =>
        r.distance.includes(filters.distance)
      );
    }
    if (filters.weather.length > 0) {
      filteredData = filteredData.filter((r) =>
        filters.weather.includes(r.weather)
      );
    }
    if (filters.ground_condition.length > 0) {
      filteredData = filteredData.filter((r) => {
        // const match = r.distance.match(/$(.*?)$/);
        // const condition = match ? match[1] : '';
        return (
          r.ground_condition &&
          filters.ground_condition.includes(r.ground_condition)
        );
      });
    }
    return filteredData;
  }, [entry.horse.past_races, filters]);

  return (
    <div className='border rounded-lg shadow-md overflow-hidden'>
      <div className='bg-gray-100 p-4'>
        <h3 className='text-2xl font-bold text-gray-900'>
          {entry.horse.horse_name}
        </h3>
        <div className='flex items-center gap-4 text-sm text-gray-600 mt-1'>
          <span>騎手: {entry?.jockey?.jockey_name || '未定'}</span>
          <span>オッズ: {entry.odds}</span>
          <span>人気: {entry.popularity}番</span>
        </div>
      </div>
      <div className='p-4'>
        <h4 className='text-md font-semibold mb-2 text-gray-700'>
          過去の成績 ({displayedPastRaces.length}件表示)
        </h4>
        <div className='overflow-x-auto shadow-md rounded-lg'>
          <table className='min-w-full divide-y divide-gray-200 bg-white table-fixed'>
            <thead className='bg-gray-50'>
              <tr>
                {/* テーブルヘッダー */}
                <th className='py-3 px-4 text-left text-xs font-medium whitespace-nowrap text-gray-500 uppercase tracking-wider'>
                  日付
                </th>
                <th className='py-3 px-4 text-left text-xs font-medium whitespace-nowrap text-gray-500 uppercase tracking-wider w-32'>
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
                  馬場
                </th>
                <th className='py-3 px-4 text-center text-xs font-medium whitespace-nowrap text-gray-500 uppercase tracking-wider'>
                  頭数
                </th>
                <th className='py-3 px-4 text-center text-xs font-medium whitespace-nowrap text-gray-500 uppercase tracking-wider'>
                  着順
                </th>
                <th className='py-3 px-4 text-center text-xs font-medium whitespace-nowrap text-gray-500 uppercase tracking-wider'>
                  上り
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
              {displayedPastRaces.map((pastRace) => (
                <tr key={pastRace.past_race_id} className='hover:bg-gray-50'>
                  <td className='py-3 px-4 whitespace-nowrap text-sm text-gray-900'>
                    {pastRace.race_date}
                  </td>

                  <td
                    className='py-3 px-4 text-sm text-gray-900 font-medium '
                    title={pastRace.race_name}
                  >
                    <div className='w-40 truncate' title={pastRace.race_name}>
                      {pastRace.race_name}
                    </div>
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
                    {pastRace.ground_condition}
                  </td>
                  <td className='py-3 px-4 whitespace-nowrap text-sm text-gray-900 text-center'>
                    {pastRace.head_count}
                  </td>
                  <td className='py-3 px-4 whitespace-nowrap text-sm text-gray-900 text-center '>
                    <span className={getRankClass(pastRace.rank)}>
                      {pastRace.rank}
                    </span>
                  </td>
                  <td className='py-3 px-4 whitespace-nowrap text-sm text-gray-900 text-center'>
                    <span className={getRankClass(pastRace.last_3f_rank)}>
                      {pastRace.last_3f}
                    </span>
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
  );
};
