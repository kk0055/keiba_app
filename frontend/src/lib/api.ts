import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
});

// データ型を定義
export interface Race {
  id: string;
  race_name: string;
  date: string;
}

export interface Prediction {
  id: number;
  race: Race;
  prediction_model_name: string;
  notes: string;
}

export type PredictionPayload = {
  race: string ; 
  prediction_model_name: string;
  notes: string;
};


// 予想一覧を取得
export const getPredictions = async (): Promise<Prediction[]> => {
  const response = await apiClient.get('/predictions/');
  return response.data;
};

// 予想を作成
export const createPrediction = async (
  data: PredictionPayload
): Promise<Prediction> => {
  const response = await apiClient.post('/predictions/', data);
  return response.data;
};

// 予想を作成
export const updatePrediction = async (
  id: number,
  data: PredictionPayload
): Promise<Prediction> => {
  const response = await apiClient.put(`/predictions/${id}/`, data);
  return response.data;
};

// 予想を削除
export const deletePrediction = async (id: number): Promise<void> => {
  await apiClient.delete(`/predictions/${id}/`);
};

export const getPredictionByRaceId = async (
  raceId: string 
): Promise<Prediction | null> => {
  try {
    const response = await apiClient.get(`/predictions/?race=${raceId}`);
      return response.data.length > 0 ? response.data[0] : null;
  } catch (error) {
    console.error('Prediction fetch failed', error);
    return null;
  }
};