import { BarChart3, TrendingUp, Clock, FileText } from 'lucide-react';
import BottomNav from '../components/BottomNav';
import MobileHeader from '../components/MobileHeader';

export default function StatisticsPage() {
  const stats = [
    { icon: FileText, label: '분석한 계약서', value: '0건', color: 'bg-blue-100 text-blue-600' },
    { icon: BarChart3, label: '총 상담 횟수', value: '0회', color: 'bg-green-100 text-green-600' },
    { icon: Clock, label: '총 근무 시간', value: '0시간', color: 'bg-purple-100 text-purple-600' },
    { icon: TrendingUp, label: '절약한 시간', value: '0시간', color: 'bg-orange-100 text-orange-600' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <MobileHeader title="통계" showBack={false} />

      <main className="max-w-md mx-auto px-4 pt-20 pb-8">
        <div className="grid grid-cols-2 gap-4 mb-6">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div key={index} className="bg-white rounded-3xl shadow-sm p-6">
                <div className={`w-12 h-12 ${stat.color} rounded-2xl flex items-center justify-center mb-3`}>
                  <Icon className="w-6 h-6" />
                </div>
                <p className="text-sm text-gray-600 mb-1">{stat.label}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            );
          })}
        </div>

        <div className="bg-white rounded-3xl shadow-sm p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">최근 활동</h3>
          <div className="text-center py-12">
            <BarChart3 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">아직 활동 기록이 없습니다</p>
          </div>
        </div>
      </main>

      <BottomNav />
    </div>
  );
}
