import React, { useState, useEffect } from 'react';
import { api } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { ScrollArea } from '../components/ui/scroll-area';
import {
  Bell, CheckCircle, AlertTriangle, Info, RefreshCw,
  Clock, Check, Trash2
} from 'lucide-react';
import { toast } from 'sonner';

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      const response = await api.get('/notifications/history');
      setNotifications(response.data);
    } catch (error) {
      // Mock notifications for demo
      setNotifications([
        { id: '1', title: 'Payment Received', message: 'Payment of $25,000 received from ABC Corp', type: 'success', read: false, created_at: new Date().toISOString() },
        { id: '2', title: 'GST Refund Approved', message: 'Your GST refund application has been approved', type: 'success', read: false, created_at: new Date(Date.now() - 86400000).toISOString() },
        { id: '3', title: 'LUT Renewal Reminder', message: 'Your LUT expires in 45 days', type: 'warning', read: true, created_at: new Date(Date.now() - 172800000).toISOString() },
        { id: '4', title: 'Shipment Delivered', message: 'Shipment SH-2024-001 has been delivered', type: 'info', read: true, created_at: new Date(Date.now() - 259200000).toISOString() },
        { id: '5', title: 'Payment Overdue', message: 'Invoice INV-2024-005 is overdue by 30 days', type: 'error', read: false, created_at: new Date(Date.now() - 345600000).toISOString() },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = (id) => {
    setNotifications(notifications.map(n => 
      n.id === id ? { ...n, read: true } : n
    ));
    toast.success('Marked as read');
  };

  const markAllAsRead = () => {
    setNotifications(notifications.map(n => ({ ...n, read: true })));
    toast.success('All notifications marked as read');
  };

  const deleteNotification = (id) => {
    setNotifications(notifications.filter(n => n.id !== id));
    toast.success('Notification deleted');
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'success': return <CheckCircle className="w-5 h-5 text-neon" />;
      case 'warning': return <AlertTriangle className="w-5 h-5 text-amber" />;
      case 'error': return <AlertTriangle className="w-5 h-5 text-destructive" />;
      default: return <Info className="w-5 h-5 text-primary" />;
    }
  };

  const getTypeBg = (type) => {
    switch (type) {
      case 'success': return 'bg-neon/10';
      case 'warning': return 'bg-amber/10';
      case 'error': return 'bg-destructive/10';
      default: return 'bg-primary/10';
    }
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="space-y-6 animate-fade-in" data-testid="notifications-page">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="font-heading text-4xl text-foreground">Notifications</h1>
          <p className="text-muted-foreground mt-1">
            {unreadCount > 0 ? `${unreadCount} unread notifications` : 'All caught up!'}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchNotifications} data-testid="refresh-notifications-btn">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          {unreadCount > 0 && (
            <Button variant="outline" onClick={markAllAsRead} data-testid="mark-all-read-btn">
              <Check className="w-4 h-4 mr-2" />
              Mark All Read
            </Button>
          )}
        </div>
      </div>

      {/* Notifications List */}
      <Card className="bg-card border-border" data-testid="notifications-list">
        <CardHeader>
          <CardTitle className="font-heading text-lg flex items-center gap-2">
            <Bell className="w-5 h-5 text-primary" />
            Recent Notifications
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-6 h-6 animate-spin text-primary" />
            </div>
          ) : notifications.length === 0 ? (
            <div className="text-center py-12">
              <Bell className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">No notifications</p>
            </div>
          ) : (
            <ScrollArea className="h-[500px]">
              <div className="divide-y divide-border">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`p-4 hover:bg-surface-highlight/50 transition-colors ${!notification.read ? 'bg-primary/5' : ''}`}
                    data-testid={`notification-${notification.id}`}
                  >
                    <div className="flex gap-4">
                      <div className={`w-10 h-10 rounded-md flex items-center justify-center flex-shrink-0 ${getTypeBg(notification.type)}`}>
                        {getTypeIcon(notification.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <p className={`font-medium ${!notification.read ? 'text-foreground' : 'text-muted-foreground'}`}>
                              {notification.title}
                            </p>
                            <p className="text-sm text-muted-foreground mt-1">
                              {notification.message}
                            </p>
                          </div>
                          {!notification.read && (
                            <Badge className="bg-primary/20 text-primary text-xs flex-shrink-0">New</Badge>
                          )}
                        </div>
                        <div className="flex items-center justify-between mt-3">
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Clock className="w-3 h-3" />
                            {new Date(notification.created_at).toLocaleString()}
                          </div>
                          <div className="flex items-center gap-2">
                            {!notification.read && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => markAsRead(notification.id)}
                                className="text-xs h-7"
                                data-testid={`mark-read-${notification.id}`}
                              >
                                <Check className="w-3 h-3 mr-1" />
                                Mark Read
                              </Button>
                            )}
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => deleteNotification(notification.id)}
                              className="text-xs h-7 text-destructive hover:text-destructive"
                              data-testid={`delete-${notification.id}`}
                            >
                              <Trash2 className="w-3 h-3" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
