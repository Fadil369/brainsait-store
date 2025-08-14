'use client';

import React from 'react';
import { createPortal } from 'react-dom';
import { 
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XCircleIcon,
  XMarkIcon 
} from '@heroicons/react/24/outline';
import { Button } from './Button';
import { useAppStore } from '@/stores';
import { cn } from '@/lib/utils';

const NotificationContainer: React.FC = () => {
  const { notifications, removeNotification } = useAppStore();

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-success" />;
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-warning" />;
      default:
        return <InformationCircleIcon className="h-5 w-5 text-blue-500" />;
    }
  };

  const getBackgroundColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-success/90';
      case 'error':
        return 'bg-red-500/90';
      case 'warning':
        return 'bg-warning/90';
      default:
        return 'bg-blue-500/90';
    }
  };

  if (notifications.length === 0) {
    return null;
  }

  const notificationContent = (
    <div className="fixed top-20 right-4 z-notification space-y-2 pointer-events-none">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={cn(
            'pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-xl backdrop-blur-lg border border-white/10 text-white font-medium shadow-lg animate-slide-in max-w-sm',
            getBackgroundColor(notification.type)
          )}
        >
          {getIcon(notification.type)}
          
          <span className="flex-1 text-sm">
            {notification.message}
          </span>
          
          <Button
            variant="ghost"
            size="icon"
            onClick={() => removeNotification(notification.id)}
            className="w-6 h-6 text-white/80 hover:text-white hover:bg-white/10 flex-shrink-0"
          >
            <XMarkIcon className="h-4 w-4" />
          </Button>
        </div>
      ))}
    </div>
  );

  return createPortal(notificationContent, document.body);
};

export default NotificationContainer;