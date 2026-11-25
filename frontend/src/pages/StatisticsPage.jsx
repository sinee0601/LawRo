import { BarChart3, TrendingUp, Clock, FileText } from 'lucide-react';
import { Card } from '../components/ui';
import AppLayout from '../components/layout/AppLayout';

export default function StatisticsPage() {
  const stats = [
    { icon: FileText, label: '분석한 계약서', value: '0건', color: 'bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400' },
    { icon: BarChart3, label: '총 상담 횟수', value: '0회', color: 'bg-green-100 dark:bg-green-500/20 text-green-600 dark:text-green-400' },
    { icon: Clock, label: '총 근무 시간', value: '0시간', color: 'bg-purple-100 dark:bg-purple-500/20 text-purple-600 dark:text-purple-400' },
    { icon: TrendingUp, label: '절약한 시간', value: '0시간', color: 'bg-orange-100 dark:bg-orange-500/20 text-orange-600 dark:text-orange-400' },
  ];

  return (
    <AppLayout title="통계" width="default">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div key={index} className="bg-surface rounded-card shadow-card p-6">
                <div className={`w-12 h-12 ${stat.color} rounded-2xl flex items-center justify-center mb-3`}>
                  <Icon className="w-6 h-6" />
                </div>
                <p className="text-sm text-ink-muted mb-1">{stat.label}</p>
                <p className="text-2xl font-bold text-ink">{stat.value}</p>
              </div>
            );
          })}
        </div>

        <Card>
          <h3 className="text-lg font-bold text-ink mb-4">최근 활동</h3>
          <div className="text-center py-12">
            <BarChart3 className="w-16 h-16 text-ink-subtle mx-auto mb-4" />
            <p className="text-ink-muted">아직 활동 기록이 없습니다</p>
          </div>
        </Card>
      </AppLayout>
  );
}
