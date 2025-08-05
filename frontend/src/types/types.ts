// src/types/types.ts

/**
 * 絞り込み条件の状態を表す型
 */
export interface Filters {
  venue: string;
  rank: number;
  distance: string;
  weather: string[];
  ground_condition: string[];
  recentRaces: number;
  jockeyMatch: boolean;
}

export interface PastRace {
  past_race_id: string;
  race_date: string;
  venue_name: string;
  race_name: string;
  race_grade_score: number | null;
  weather: string;
  distance: string;
  head_count: number | null; // 18
  rank: number | null; // 5
  last_3f: number | null; // 5
  last_3f_rank: number | null; // 5
  odds: number | null; // 10.5
  popularity: number | null; // 4
  umaban: number | null; // 10
  ground_condition: string | null;
  jockey_name: string; // "横山 武史"
  jockey_id: string;
  time: string | null;
}

export interface Horse {
  horse_id: string;
  horse_name: string;
  past_races: PastRace[];
}
export interface Jockey {
  jockey_id: string; 
  jockey_name: string;
}
export interface Entry {
  horse: Horse;
  jockey: Jockey | null;
  odds: number;
  popularity: number;
  umaban: number | null;
  waku: number | null;
  weight_carried: number;
  horse_past_race_grade_score_total: number | null;
}

export interface RaceData {
  race_id: string;
  race_name: string;
  race_date: string;
  race_number: string;
  venue: string;
  course_details: string;
  ground_condition: string | null;
  head_count: number | null;
  entries: Entry[];
}

export interface HorseCardProps {
  entry: Entry;
  filters: Filters;
}
