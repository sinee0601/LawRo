import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { contractAPI } from '../services/api';
import { Camera, Upload, FileText, CheckCircle } from 'lucide-react';
import AppLayout from '../components/layout/AppLayout';
import { toast } from '../store/notifyStore';
import { Alert, Button, Card, Spinner } from '../components/ui';
import ContractAnalysisResult from '../components/ContractAnalysisResult';
import useTranslation from '../hooks/useTranslation';
import { toServerCode } from '../i18n/languages';

export default function ContractPage() {
  const navigate = useNavigate();
  const { t, language } = useTranslation();
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null); // For image preview
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Clean up object URL on component unmount to prevent memory leaks
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  // 사용자 정보 가져오기
  const userId = localStorage.getItem('userId') || 'default_user';
  // 분석 결과도 지금 앱 언어로 받습니다 (서버는 'korean' 같은 코드를 씁니다).
  const userLanguage = toServerCode(language);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (selectedFile) => {
    const allowedTypes = [
      'image/jpeg',
      'image/jpg',
      'image/png',
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];
    const maxSize = 10 * 1024 * 1024; // 10MB

    // Revoke previous URL if it exists
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    if (!allowedTypes.includes(selectedFile.type)) {
      setError(t('contract.new.invalidType'));
      setFile(null);
      setPreviewUrl(null);
      return;
    }

    if (selectedFile.size > maxSize) {
      setError(t('contract.new.tooLarge'));
      setFile(null);
      setPreviewUrl(null);
      return;
    }

    setFile(selectedFile);
    setError(null);
    setResult(null);

    // Create a preview URL only if the file is an image
    if (selectedFile.type.startsWith('image/')) {
      setPreviewUrl(URL.createObjectURL(selectedFile));
    } else {
      setPreviewUrl(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setIsUploading(true);
    setError(null);

    try {
      // 1. 파일 업로드 (진행률 추적)
      const uploadData = await contractAPI.uploadContract(
        file,
        (percent) => {
          console.log(`Upload progress: ${percent}%`);
        },
        userId,
        userLanguage
      );
      const contractId = uploadData.contract_id;

      setIsUploading(false);
      setIsAnalyzing(true);

      // 2. 계약서 분석 (챗봇 통합)
      const analysisData = await contractAPI.analyzeWithChatbot(
        contractId,
        userId,
        userLanguage
      );

      setResult(analysisData);
      setIsAnalyzing(false);
    } catch (err) {
      setError(err.response?.data?.detail || t('contract.new.failed'));
      setIsUploading(false);
      setIsAnalyzing(false);
    }
  };
  
  const resetState = () => {
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
  };

  return (
    <AppLayout title={t('contract.new.title')} showBack>
        {!result ? (
          <div>
            {/* 모바일: 안내 → 미리보기 → 버튼 순서. PC: 왼쪽 미리보기, 오른쪽 안내와 버튼 */}
            <Card padding="lg" className="lg:grid lg:grid-cols-2 lg:grid-rows-[auto_1fr] lg:gap-x-10">
              <div className="lg:col-start-2 lg:row-start-1">
              <h2 className="text-lg font-bold text-ink mb-2">{t('contract.new.heading')}</h2>
              <p className="text-sm text-ink-muted mb-6">
                {t('contract.new.description')}
              </p>

              {error && (
                <Alert tone="danger" className="mb-4">{error}</Alert>
              )}

              </div>

              {/* 계약서 미리보기 영역 */}
              <div className="bg-surface-muted rounded-2xl aspect-[3/4] mb-6 lg:mb-0 lg:col-start-1 lg:row-start-1 lg:row-span-2 flex items-center justify-center overflow-hidden">
                {file ? (
                  previewUrl ? (
                    <img src={previewUrl} alt={t('contract.new.previewAlt')} className="w-full h-full object-contain" />
                  ) : (
                    <div className="text-center p-4">
                      <FileText className="w-16 h-16 text-primary-600 dark:text-primary-400 mx-auto mb-2" />
                      <p className="text-sm font-medium text-ink truncate">{file.name}</p>
                      <p className="text-xs text-ink-muted">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                  )
                ) : (
                  <p className="text-ink-subtle">{t('contract.new.previewPlaceholder')}</p>
                )}
              </div>

              <div className="lg:col-start-2 lg:row-start-2">
              {/* 파일이 선택되었을 때 삭제 버튼 표시 */}
              {file && (
                <div className="text-center mb-4">
                   <button
                      onClick={() => {
                        setFile(null);
                        setPreviewUrl(null);
                        setResult(null);
                      }}
                      className="text-sm text-danger hover:text-danger-hover font-medium"
                    >
                      {t('contract.new.removeFile')}
                    </button>
                </div>
              )}

              {/* 업로드 버튼 */}
              {!file && (
                <div className="grid grid-cols-2 gap-3">
                  <label className="flex flex-col items-center justify-center bg-primary-100 dark:bg-primary-500/20 hover:bg-primary-200 dark:hover:bg-primary-500/30 rounded-2xl p-6 cursor-pointer transition-colors">
                    <Upload className="w-8 h-8 text-primary-700 dark:text-primary-300 mb-2" />
                    <span className="text-sm font-medium text-primary-900 dark:text-primary-200">{t('contract.new.upload')}</span>
                    <input
                      type="file"
                      className="hidden"
                      accept="image/*,.pdf,.doc,.docx"
                      onChange={handleFileChange}
                    />
                  </label>

                  <label className="flex flex-col items-center justify-center bg-primary-100 dark:bg-primary-500/20 hover:bg-primary-200 dark:hover:bg-primary-500/30 rounded-2xl p-6 cursor-pointer transition-colors">
                    <Camera className="w-8 h-8 text-primary-700 dark:text-primary-300 mb-2" />
                    <span className="text-sm font-medium text-primary-900 dark:text-primary-200">{t('contract.new.camera')}</span>
                    <input
                      type="file"
                      className="hidden"
                      accept="image/*"
                      capture="environment"
                      onChange={handleFileChange}
                    />
                  </label>
                </div>
              )}

              <p className="mt-4 text-xs text-ink-subtle text-center lg:text-left">
                {t('contract.new.fileHint')}
              </p>

              {/* 분석 버튼 */}
              {file && !isUploading && !isAnalyzing && (
                <Button size="xl" fullWidth onClick={handleAnalyze} className="mt-6">
                  {t('contract.new.analyze')}
                </Button>
              )}

              {/* 로딩 상태 */}
              {(isUploading || isAnalyzing) && (
                <div className="mt-6 p-4 bg-primary-soft border border-primary-200 dark:border-primary-500/30 rounded-control" aria-live="polite">
                  <div className="flex items-center gap-3">
                    <Spinner size="md" label={t('contract.new.working')} />
                    <div>
                      <p className="font-medium text-ink">{t('contract.new.working')}</p>
                      <p className="text-sm text-ink-muted">
                        {isUploading ? t('contract.new.uploading') : t('contract.new.analyzing')}
                      </p>
                    </div>
                  </div>
                </div>
              )}
              </div>
            </Card>
          </div>

        ) : (
          <Card className="max-w-4xl mx-auto">
            <div className="flex items-center gap-2 mb-1">
              <CheckCircle className="w-6 h-6 text-success" />
              <h2 className="text-lg font-bold text-ink">{t('contract.new.resultTitle')}</h2>
            </div>
            <p className="text-sm text-ink-muted mb-5">
              {t('contract.new.analyzedOn', { date: new Date().toLocaleDateString(language) })}
            </p>

            <ContractAnalysisResult
              structured={result.structured_result}
              chatbotText={result.chatbot_analysis?.analysis}
            />

            {/* 액션 버튼 */}
            <div className="grid grid-cols-2 gap-2 sm:gap-3 mt-6">
              <Button
                variant="outline"
                onClick={() => toast.info(t('contract.new.exportPdfSoon'))}
              >
                {t('contract.new.exportPdf')}
              </Button>
              <Button
                onClick={() => {
                  // 분석 결과를 챗봇으로 전달
                  const contractData = {
                    structuredResult: result.structured_result,
                    chatbotAnalysis: result.chatbot_analysis?.analysis,
                    sessionId: result.chatbot_analysis?.session_id,
                    timestamp: new Date().toISOString()
                  };
                  localStorage.setItem('contractAnalysisData', JSON.stringify(contractData));
                  navigate('/chat');
                }}
              >
                {t('contract.new.askMore')}
              </Button>
            </div>
            <Button variant="ghost" fullWidth onClick={resetState} className="mt-2">
              {t('contract.new.analyzeAnother')}
            </Button>
          </Card>
        )}
    </AppLayout>
  );
}
