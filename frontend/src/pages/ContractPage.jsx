import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { contractAPI } from '../services/api';
import { Camera, Upload, FileText, Loader, AlertCircle, CheckCircle } from 'lucide-react';
import BottomNav from '../components/BottomNav';
import MobileHeader from '../components/MobileHeader';

export default function ContractPage() {
  const navigate = useNavigate();
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
  const userLanguage = localStorage.getItem('userLanguage') || 'korean';

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
      setError('JPG, PNG, PDF, DOC, DOCX 파일만 업로드 가능합니다.');
      setFile(null);
      setPreviewUrl(null);
      return;
    }

    if (selectedFile.size > maxSize) {
      setError('파일 크기는 10MB 이하여야 합니다.');
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
      setError(err.response?.data?.detail || '분석 중 오류가 발생했습니다.');
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
    <div className="min-h-screen bg-gray-50 pb-20">
      <MobileHeader title="새 계약서 분석" showBack={true} />

      {/* 메인 컨텐츠 */}
      <main className="max-w-md mx-auto px-4 pt-20 pb-8">
        {!result ? (
          <div>
            <div className="bg-white rounded-3xl shadow-lg p-8 mb-6">
              <h2 className="text-lg font-bold text-gray-900 mb-2">근로계약서 분석</h2>
              <p className="text-sm text-gray-600 mb-6">
                근로계약서의 사진을 찍거나, 파일을 업로드하여 계약조항이 법적으로 옳은지 확인해보세요!
              </p>

              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                  <span className="text-sm">{error}</span>
                </div>
              )}

              {/* 계약서 미리보기 영역 */}
              <div className="bg-gray-100 rounded-2xl aspect-[3/4] mb-6 flex items-center justify-center overflow-hidden">
                {file ? (
                  previewUrl ? (
                    <img src={previewUrl} alt="Preview" className="w-full h-full object-contain" />
                  ) : (
                    <div className="text-center p-4">
                      <FileText className="w-16 h-16 text-primary-600 mx-auto mb-2" />
                      <p className="text-sm font-medium text-gray-900 truncate">{file.name}</p>
                      <p className="text-xs text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                  )
                ) : (
                  <p className="text-gray-400">계약서 이미지</p>
                )}
              </div>

              {/* 파일이 선택되었을 때 삭제 버튼 표시 */}
              {file && (
                <div className="text-center mb-4">
                   <button
                      onClick={() => {
                        setFile(null);
                        setPreviewUrl(null);
                        setResult(null);
                      }}
                      className="text-sm text-red-600 hover:text-red-700 font-medium"
                    >
                      파일 삭제
                    </button>
                </div>
              )}

              {/* 업로드 버튼 */}
              {!file && (
                <div className="grid grid-cols-2 gap-3">
                  <label className="flex flex-col items-center justify-center bg-primary-100 hover:bg-primary-200 rounded-2xl p-6 cursor-pointer transition-colors">
                    <Upload className="w-8 h-8 text-primary-700 mb-2" />
                    <span className="text-sm font-medium text-primary-900">파일 업로드</span>
                    <input
                      type="file"
                      className="hidden"
                      accept="image/*,.pdf,.doc,.docx"
                      onChange={handleFileChange}
                    />
                  </label>

                  <label className="flex flex-col items-center justify-center bg-primary-100 hover:bg-primary-200 rounded-2xl p-6 cursor-pointer transition-colors">
                    <Camera className="w-8 h-8 text-primary-700 mb-2" />
                    <span className="text-sm font-medium text-primary-900">사진 촬영</span>
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

              {/* 분석 버튼 */}
              {file && !isUploading && !isAnalyzing && (
                <button
                  onClick={handleAnalyze}
                  className="w-full mt-6 bg-primary-600 hover:bg-primary-700 text-white font-semibold py-4 rounded-xl transition-colors"
                >
                  분석 시작
                </button>
              )}

              {/* 로딩 상태 */}
              {(isUploading || isAnalyzing) && (
                <div className="mt-6 p-4 bg-primary-50 border border-primary-200 rounded-xl">
                  <div className="flex items-center gap-3">
                    <Loader className="w-6 h-6 animate-spin text-primary-600" />
                    <div>
                      <p className="font-medium text-gray-900">로딩중</p>
                      <p className="text-sm text-gray-600">
                        {isUploading ? '파일을 업로드하고 있습니다' : '계약서를 분석하고 있습니다'}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

        ) : (
          <div>
            <div className="bg-white rounded-3xl shadow-lg p-6 mb-6">
              <div className="flex items-center gap-2 mb-4">
                <CheckCircle className="w-6 h-6 text-green-600" />
                <h2 className="text-lg font-bold text-gray-900">분석 결과</h2>
              </div>

              <p className="text-sm text-gray-600 mb-4">
                분석 날짜: {new Date().toLocaleDateString('ko-KR')}
              </p>

              {/* ... (result display code remains the same) ... */}
              
              {/* 액션 버튼 */}
              <div className="grid grid-cols-2 gap-2 sm:gap-3">
                <button
                  onClick={() => {
                    alert('PDF 내보내기 기능은 준비 중입니다.');
                  }}
                  className="bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 font-medium py-2.5 sm:py-3 px-2 rounded-xl transition-colors text-xs sm:text-sm"
                  title="향후 업데이트 예정"
                >
                  PDF 내보내기
                </button>
                <button
                  onClick={() => {
                    // 분석 결과를 챗봇으로 전달
                    const contractData = {
                      structuredResult: result.structured_result,
                      chatbotAnalysis: result.chatbot_analysis?.analysis,
                      sessionId: result.chatbot_analysis?.session_id,
                      timestamp: new Date().toISOString()
                    };

                    // LocalStorage에 분석 결과 저장
                    localStorage.setItem('contractAnalysisData', JSON.stringify(contractData));

                    // 챗봇 페이지로 이동
                    navigate('/chat');
                  }}
                  className="bg-primary-600 hover:bg-primary-700 text-white font-medium py-2.5 sm:py-3 px-2 rounded-xl transition-colors text-xs sm:text-sm"
                >
                  추가 상담하기
                </button>
              </div>

              <button
                onClick={resetState}
                className="w-full mt-2 sm:mt-3 bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 font-medium py-2.5 sm:py-3 rounded-xl transition-colors text-xs sm:text-sm"
              >
                새로운 계약서 분석
              </button>
            </div>
          </div>
        )}
      </main>

      <BottomNav />
    </div>
  );
}
