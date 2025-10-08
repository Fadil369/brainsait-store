'use client';

import React, { useState } from 'react';
import { useAppStore } from '@/stores';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { 
  ExclamationCircleIcon, 
  CheckCircleIcon,
  ClockIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline';

export function ComplaintResolution() {
  const { language } = useAppStore();
  const [showNewComplaint, setShowNewComplaint] = useState(false);
  const [complaintForm, setComplaintForm] = useState({
    title: '',
    category: '',
    description: '',
    priority: 'medium'
  });

  const complaints = [
    {
      id: 'CMP-001',
      title: 'Damaged Product Received',
      titleAr: 'تم استلام منتج تالف',
      category: 'Quality',
      categoryAr: 'الجودة',
      description: 'Product A arrived with packaging damage',
      descriptionAr: 'وصل المنتج أ مع تلف في التغليف',
      status: 'in-progress',
      priority: 'high',
      createdAt: '2025-01-14',
      updatedAt: '2025-01-15',
      assignedTo: 'Support Team',
      messages: 3
    },
    {
      id: 'CMP-002',
      title: 'Late Delivery',
      titleAr: 'تأخر التسليم',
      category: 'Delivery',
      categoryAr: 'التسليم',
      description: 'Order ORD-123 was delivered 2 days late',
      descriptionAr: 'تم تسليم الطلب ORD-123 متأخرًا يومين',
      status: 'resolved',
      priority: 'medium',
      createdAt: '2025-01-10',
      updatedAt: '2025-01-12',
      assignedTo: 'Logistics Team',
      messages: 5
    },
    {
      id: 'CMP-003',
      title: 'Wrong Item Shipped',
      titleAr: 'تم شحن عنصر خاطئ',
      category: 'Order',
      categoryAr: 'الطلب',
      description: 'Received Product B instead of Product C',
      descriptionAr: 'تلقيت المنتج ب بدلاً من المنتج ج',
      status: 'open',
      priority: 'high',
      createdAt: '2025-01-13',
      updatedAt: '2025-01-13',
      assignedTo: 'Pending Assignment',
      messages: 1
    }
  ];

  const categories = ['Quality', 'Delivery', 'Order', 'Payment', 'Service', 'Other'];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'bg-blue-400/20 text-blue-400';
      case 'in-progress':
        return 'bg-yellow-400/20 text-yellow-400';
      case 'resolved':
        return 'bg-green-400/20 text-green-400';
      default:
        return 'bg-gray-400/20 text-gray-400';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'text-red-400';
      case 'medium':
        return 'text-yellow-400';
      case 'low':
        return 'text-blue-400';
      default:
        return 'text-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'resolved':
        return <CheckCircleIcon className="h-5 w-5 text-green-400" />;
      case 'in-progress':
        return <ClockIcon className="h-5 w-5 text-yellow-400" />;
      default:
        return <ExclamationCircleIcon className="h-5 w-5 text-blue-400" />;
    }
  };

  const handleSubmitComplaint = () => {
    // Handle form submission
    console.log('Submitting complaint:', complaintForm);
    setShowNewComplaint(false);
    setComplaintForm({ title: '', category: '', description: '', priority: 'medium' });
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-glass-bg border-white/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">
              {language === 'ar' ? 'شكاوى مفتوحة' : 'Open Complaints'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-400">
              {complaints.filter(c => c.status === 'open').length}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-glass-bg border-white/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">
              {language === 'ar' ? 'قيد المعالجة' : 'In Progress'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-yellow-400">
              {complaints.filter(c => c.status === 'in-progress').length}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-glass-bg border-white/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-300">
              {language === 'ar' ? 'تم الحل' : 'Resolved'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-400">
              {complaints.filter(c => c.status === 'resolved').length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* New Complaint Button */}
      {!showNewComplaint && (
        <Button 
          variant="gradient" 
          onClick={() => setShowNewComplaint(true)}
          className="w-full"
        >
          {language === 'ar' ? 'تقديم شكوى جديدة' : 'Submit New Complaint'}
        </Button>
      )}

      {/* New Complaint Form */}
      {showNewComplaint && (
        <Card className="bg-glass-bg border-white/10">
          <CardHeader>
            <CardTitle className="text-white">
              {language === 'ar' ? 'شكوى جديدة' : 'New Complaint'}
            </CardTitle>
            <CardDescription className="text-gray-300">
              {language === 'ar' 
                ? 'قدم شكوى وسنعمل على حلها في أقرب وقت ممكن' 
                : 'Submit a complaint and we\'ll work to resolve it as soon as possible'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-300 mb-2">
                  {language === 'ar' ? 'العنوان' : 'Title'}
                </label>
                <Input
                  value={complaintForm.title}
                  onChange={(e) => setComplaintForm({...complaintForm, title: e.target.value})}
                  placeholder={language === 'ar' ? 'اختصار موجز لمشكلتك' : 'Brief summary of your issue'}
                  className="bg-white/5 border-white/10 text-white"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-300 mb-2">
                  {language === 'ar' ? 'الفئة' : 'Category'}
                </label>
                <select
                  value={complaintForm.category}
                  onChange={(e) => setComplaintForm({...complaintForm, category: e.target.value})}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                >
                  <option value="">{language === 'ar' ? 'اختر فئة' : 'Select category'}</option>
                  {categories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm text-gray-300 mb-2">
                  {language === 'ar' ? 'الأولوية' : 'Priority'}
                </label>
                <div className="flex gap-2">
                  {['low', 'medium', 'high'].map(priority => (
                    <button
                      key={priority}
                      onClick={() => setComplaintForm({...complaintForm, priority})}
                      className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                        complaintForm.priority === priority
                          ? 'bg-vision-green text-black'
                          : 'bg-white/5 text-gray-300 hover:bg-white/10'
                      }`}
                    >
                      {priority.charAt(0).toUpperCase() + priority.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm text-gray-300 mb-2">
                  {language === 'ar' ? 'الوصف' : 'Description'}
                </label>
                <textarea
                  value={complaintForm.description}
                  onChange={(e) => setComplaintForm({...complaintForm, description: e.target.value})}
                  placeholder={language === 'ar' ? 'قدم تفاصيل حول المشكلة' : 'Provide details about the issue'}
                  rows={4}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white resize-none"
                />
              </div>

              <div className="flex gap-2">
                <Button 
                  variant="gradient" 
                  onClick={handleSubmitComplaint}
                  className="flex-1"
                >
                  {language === 'ar' ? 'إرسال' : 'Submit'}
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setShowNewComplaint(false)}
                  className="flex-1"
                >
                  {language === 'ar' ? 'إلغاء' : 'Cancel'}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Complaints List */}
      <Card className="bg-glass-bg border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <ExclamationCircleIcon className="h-6 w-6" />
            {language === 'ar' ? 'سجل الشكاوى' : 'Complaints History'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {complaints.map((complaint) => (
              <div 
                key={complaint.id}
                className="p-5 bg-white/5 border border-white/10 rounded-lg hover:border-vision-green/50 transition-all"
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-start gap-3">
                    {getStatusIcon(complaint.status)}
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-1">
                        {language === 'ar' ? complaint.titleAr : complaint.title}
                      </h3>
                      <p className="text-sm text-gray-400">
                        {complaint.id} • {language === 'ar' ? complaint.categoryAr : complaint.category}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <span className={`text-xs font-semibold px-3 py-1 rounded-full ${getStatusColor(complaint.status)}`}>
                      {complaint.status.replace('-', ' ').toUpperCase()}
                    </span>
                    <span className={`text-xs font-semibold ${getPriorityColor(complaint.priority)}`}>
                      ● {complaint.priority.toUpperCase()}
                    </span>
                  </div>
                </div>

                <p className="text-gray-300 text-sm mb-4">
                  {language === 'ar' ? complaint.descriptionAr : complaint.description}
                </p>

                <div className="flex justify-between items-center pt-3 border-t border-white/10">
                  <div className="flex gap-4 text-xs text-gray-400">
                    <span>{language === 'ar' ? 'تم الإنشاء:' : 'Created:'} {complaint.createdAt}</span>
                    <span>{language === 'ar' ? 'تم التحديث:' : 'Updated:'} {complaint.updatedAt}</span>
                    <span>{language === 'ar' ? 'المعين:' : 'Assigned:'} {complaint.assignedTo}</span>
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    className="text-vision-green hover:bg-vision-green/20"
                  >
                    <ChatBubbleLeftRightIcon className="h-4 w-4 mr-1" />
                    {complaint.messages} {language === 'ar' ? 'رسائل' : 'messages'}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
