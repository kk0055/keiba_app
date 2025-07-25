import { useEffect } from 'react';
import { FiAlertTriangle, FiCheckCircle, FiX } from 'react-icons/fi';

// 1. Toastのタイプ（成功 or エラー）を定義
type ToastType = 'success' | 'error';

// 2. Propsのインターフェースを汎用的に変更
interface ToastProps {
  message: string | null;
  show: boolean;
  onClose: () => void;
  type: ToastType; // typeプロパティを追加
}

// 3. タイプごとのスタイルとアイコンをオブジェクトで管理
const toastStyles: {
  [key in ToastType]: {
    containerClasses: string;
    icon: React.ElementType;
    iconClasses: string;
  };
} = {
  success: {
    containerClasses: 'bg-emerald-50 text-emerald-800 border-emerald-300',
    icon: FiCheckCircle,
    iconClasses: 'text-emerald-500',
  },
  error: {
    containerClasses: 'bg-amber-50 text-amber-800 border-amber-300',
    icon: FiAlertTriangle,
    iconClasses: 'text-amber-500',
  },
};

export default function Toast({
  message,
  show,
  onClose,
  type, // propsとしてtypeを受け取る
}: ToastProps) {
  // 5秒後に自動で閉じる
  useEffect(() => {
    if (show) {
      const timer = setTimeout(() => {
        onClose();
      }, 5000);

      return () => clearTimeout(timer);
    }
  }, [show, onClose]);

  // 4. propsのtypeに応じてスタイルとアイコンを決定
  const { containerClasses, icon: Icon, iconClasses } = toastStyles[type];

  return (
    <div
      className={`
        fixed top-5 left-1/2 -translate-x-1/2 z-50
        flex items-center gap-4 w-full max-w-sm p-4 rounded-lg border shadow-lg
        transition-all duration-300 ease-in-out
        ${containerClasses} 
        ${
          show
            ? 'opacity-100 translate-y-0'
            : 'opacity-0 -translate-y-10 pointer-events-none'
        }
      `}
      role='alert'
    >
      <div className={`flex-shrink-0 text-xl ${iconClasses}`}>
        <Icon /> 
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
