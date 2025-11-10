import { useState, useEffect } from 'react';
import { healthAPI } from '../services/api';
import useChatStore from '../store/chatStore';
import { Activity, Server, Database, Zap, AlertCircle, CheckCircle } from 'lucide-react';

const HealthDashboard = () => {
  const [healthStatus, setHealthStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const getStats = useChatStore(state => state.getStats);

  useEffect(() => {
    fetchHealthStatus();
    const interval = setInterval(fetchHealthStatus, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchHealthStatus = async () => {
    try {
      const [backendHealth, clientMetrics] = await Promise.all([
        healthAPI.getDetailedStatus(),
        Promise.resolve(getStats()),
      ]);

      setHealthStatus({
        backend: backendHealth,
        client: clientMetrics,
      });
      setLoading(false);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch health status:', err);
      setError('헬스 체크를 가져오는데 실패했습니다');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center gap-2 text-red-800">
          <AlertCircle className="h-5 w-5" />
          <span>{error}</span>
        </div>
      </div>
    );
  }

  const { backend, client } = healthStatus;
  const isHealthy = backend?.overall_status;

  return (
    <div className="space-y-6">
      {/* Overall Status */}
      <div className={`rounded-lg p-6 ${isHealthy ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
        <div className="flex items-center gap-3">
          {isHealthy ? (
            <CheckCircle className="h-8 w-8 text-green-600" />
          ) : (
            <AlertCircle className="h-8 w-8 text-red-600" />
          )}
          <div>
            <h3 className={`text-lg font-semibold ${isHealthy ? 'text-green-900' : 'text-red-900'}`}>
              시스템 상태: {isHealthy ? '정상' : '오류'}
            </h3>
            <p className={`text-sm ${isHealthy ? 'text-green-700' : 'text-red-700'}`}>
              {isHealthy ? '모든 서비스가 정상적으로 작동 중입니다' : '일부 서비스에 문제가 있습니다'}
            </p>
          </div>
        </div>
      </div>

      {/* Components Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatusCard
          title="LLM"
          icon={<Server className="h-5 w-5" />}
          status={backend?.components?.llm}
          description="AI 언어 모델"
        />
        <StatusCard
          title="Vector Store"
          icon={<Database className="h-5 w-5" />}
          status={backend?.components?.vectorstore}
          description="문서 검색 데이터베이스"
        />
        <StatusCard
          title="Firestore"
          icon={<Database className="h-5 w-5" />}
          status={backend?.components?.firestore}
          description="세션 저장소"
        />
      </div>

      {/* Performance Metrics */}
      {backend?.performance && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="h-5 w-5 text-yellow-500" />
            <h3 className="text-lg font-semibold text-gray-900">성능 메트릭</h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard
              label="LLM 평균 지연시간"
              value={`${backend.performance.llm_avg_latency_sec}초`}
              color="blue"
            />
            <MetricCard
              label="LLM 성공률"
              value={`${(backend.performance.llm_success_rate * 100).toFixed(1)}%`}
              color="green"
            />
            <MetricCard
              label="RAG 평균 지연시간"
              value={`${backend.performance.rag_avg_latency_sec}초`}
              color="purple"
            />
            <MetricCard
              label="RAG 히트율"
              value={`${(backend.performance.rag_hit_rate * 100).toFixed(1)}%`}
              color="indigo"
            />
          </div>
        </div>
      )}

      {/* Session Statistics */}
      {backend?.session_stats && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="h-5 w-5 text-blue-500" />
            <h3 className="text-lg font-semibold text-gray-900">세션 통계</h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard
              label="전체 세션"
              value={backend.session_stats.total_sessions}
              color="blue"
            />
            <MetricCard
              label="활성 세션"
              value={backend.session_stats.active_sessions}
              color="green"
            />
            <MetricCard
              label="전체 메시지"
              value={backend.session_stats.total_messages}
              color="purple"
            />
            <MetricCard
              label="저장소"
              value={backend.session_stats.storage_backend}
              color="gray"
            />
          </div>
        </div>
      )}

      {/* Client Metrics */}
      {client?.clientMetrics && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">클라이언트 메트릭</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <MetricCard
              label="총 요청 수"
              value={client.clientMetrics.totalRequests}
              color="blue"
            />
            <MetricCard
              label="평균 지연시간"
              value={`${client.clientMetrics.avgLatency}ms`}
              color="yellow"
            />
            <MetricCard
              label="성공률"
              value={`${client.clientMetrics.successRate}%`}
              color="green"
            />
          </div>
        </div>
      )}

      {/* User Session Stats */}
      {client && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">사용자 세션 통계</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <MetricCard
              label="총 메시지"
              value={client.totalMessages}
              color="blue"
            />
            <MetricCard
              label="성공한 메시지"
              value={client.successfulMessages}
              color="green"
            />
            <MetricCard
              label="실패한 메시지"
              value={client.failedMessages}
              color="red"
            />
          </div>
        </div>
      )}

      {/* Configuration */}
      {backend?.config && (
        <div className="bg-gray-50 rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">시스템 설정</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">LLM 모델:</span>
              <span className="font-medium text-gray-900">{backend.config.model}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">임베딩 모델:</span>
              <span className="font-medium text-gray-900">{backend.config.embedding_model}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">검색 문서 수:</span>
              <span className="font-medium text-gray-900">{backend.config.retrieval_k}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">유사도 임계값:</span>
              <span className="font-medium text-gray-900">{backend.config.score_threshold}</span>
            </div>
          </div>
        </div>
      )}

      <div className="text-center text-sm text-gray-500">
        마지막 업데이트: {new Date().toLocaleTimeString('ko-KR')}
      </div>
    </div>
  );
};

const StatusCard = ({ title, icon, status, description }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'unavailable':
        return 'bg-gray-50 border-gray-200 text-gray-600';
      default:
        return 'bg-red-50 border-red-200 text-red-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'healthy':
        return '정상';
      case 'unavailable':
        return '비활성';
      default:
        return '오류';
    }
  };

  return (
    <div className={`rounded-lg border p-4 ${getStatusColor(status)}`}>
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <h4 className="font-semibold">{title}</h4>
      </div>
      <p className="text-sm opacity-80">{description}</p>
      <p className="text-xs mt-2 font-medium">{getStatusText(status)}</p>
    </div>
  );
};

const MetricCard = ({ label, value, color }) => {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-900 border-blue-200',
    green: 'bg-green-50 text-green-900 border-green-200',
    red: 'bg-red-50 text-red-900 border-red-200',
    yellow: 'bg-yellow-50 text-yellow-900 border-yellow-200',
    purple: 'bg-purple-50 text-purple-900 border-purple-200',
    indigo: 'bg-indigo-50 text-indigo-900 border-indigo-200',
    gray: 'bg-gray-50 text-gray-900 border-gray-200',
  };

  return (
    <div className={`rounded-lg border p-4 ${colorClasses[color] || colorClasses.gray}`}>
      <p className="text-xs opacity-75 mb-1">{label}</p>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
};

export default HealthDashboard;
