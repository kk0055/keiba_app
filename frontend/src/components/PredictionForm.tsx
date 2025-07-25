'use client';

import { useForm, SubmitHandler } from 'react-hook-form';
import {
  createPrediction,
  updatePrediction,
  Prediction,
  PredictionPayload,
} from '@/lib/api';
import { useEffect } from 'react';

type FormValues = Omit<PredictionPayload, 'race'>;


// Propsの型定義
interface PredictionFormProps {
  raceId: string; // 親から必須で受け取る
  editingPrediction: Prediction | null; // 既存の予想データ、なければnull
  onSuccess: () => void;
}

export default function PredictionForm({ raceId, editingPrediction, onSuccess }: PredictionFormProps) {
  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<FormValues>();

  // 編集モードの場合、フォームに初期値をセット
  useEffect(() => {
    if (editingPrediction) {
      reset({
        prediction_model_name: editingPrediction.prediction_model_name,
        notes: editingPrediction.notes,
      });
    } else {
      // 新規作成モードのデフォルト値
      reset({
        prediction_model_name: 'Gemini 2.5 Pro',
        notes: '',
      });
    }
  }, [editingPrediction, reset]);

  const onSubmit: SubmitHandler<FormValues> = async (formData) => {
    // 親から受け取ったraceIdをマージしてAPIに送るデータを作成
    const payload: PredictionPayload = {
      ...formData,
      race: raceId,
    };

    try {
      if (editingPrediction) {
        // 更新処理
        await updatePrediction(editingPrediction.id, payload);
      } else {
        // 新規作成処理
        await createPrediction(payload);
      }
      onSuccess(); // 親に成功を通知
    } catch (error) {
      console.error('フォームの送信に失敗しました', error);
      alert('エラーが発生しました。');
    }
  };

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className='space-y-4 p-6 bg-white shadow-md rounded-lg'
    >
      <h2 className='text-2xl font-bold mb-4'>AI予想</h2>

      <div>
        <label
          htmlFor='prediction_model_name'
          className='block text-sm font-medium text-gray-700'
        >
          AIモデル名
        </label>
        <input
          id='prediction_model_name'
          type='text'
          {...register('prediction_model_name', {
            required: 'モデル名は必須です',
          })}
          className='mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm'
        />
        {errors.prediction_model_name && (
          <p className='text-red-500 text-xs mt-1'>
            {errors.prediction_model_name.message}
          </p>
        )}
      </div>

      <div>
        <label
          htmlFor='notes'
          className='block text-sm font-medium text-gray-700'
        >
          予想内容
        </label>
        <textarea
          id='notes'
          rows={15}
          {...register('notes', { required: '予想内容は必須です' })}
          className='mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm'
        />
        {errors.notes && (
          <p className='text-red-500 text-xs mt-1'>{errors.notes.message}</p>
        )}
      </div>

      <div className='flex justify-end items-center space-x-4'>
        <button
          type='submit'
          disabled={isSubmitting}
          className='px-4 py-2 bg-green-600 text-white font-semibold rounded-md shadow hover:bg-green-700 disabled:bg-gray-400'
        >
          {isSubmitting ? '保存中...' : '予想を保存する'}
        </button>
      </div>
    </form>
  );
}