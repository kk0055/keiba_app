import { useEffect } from 'react';
import { FiAlertTriangle, FiX } from 'react-icons/fi';

// Toastのプロパティを定義
interface ErrorToastProps {
  message: string| null;
  show: boolean;
  onClose: () => void;
}

export default function Toast({
  message,
  show,
  onClose,
}: ErrorToastProps) {
  // showがtrueになったら、5秒後に自動で閉じるタイマーを設定
  useEffect(() => {
    if (show) {
      const timer = setTimeout(() => {
        onClose();
      }, 5000); // 5秒

      // コンポーネントがアンマウントされたらタイマーをクリア
      return () => clearTimeout(timer);
    }
  }, [show, onClose]);

  return (
    <div
      className={`
        fixed top-5 left-1/2 -translate-x-1/2 z-50
        flex items-center gap-4 w-full max-w-sm p-4 rounded-lg border shadow-lg
        transition-all duration-300 ease-in-out
        /* ▼▼▼ 親しみやすい色に変更 ▼▼▼ */
        bg-amber-50 text-amber-800 border-amber-300
        ${
          show
            ? 'opacity-100 translate-y-0'
            : 'opacity-0 -translate-y-10 pointer-events-none'
        }
      `}
      role='alert'
    >
      <div className='flex-shrink-0 text-xl text-amber-500'>
      
        <FiAlertTriangle />
      </div>
      <div className='flex-grow font-medium'>{message}</div>
      <button
        onClick={onClose}
        className='p-1 rounded-full hover:bg-black/10'
        aria-label='閉じる'
      >
        <FiX />
      </button>
    </div>
  );
}