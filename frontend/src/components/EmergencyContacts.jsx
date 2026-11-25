import { Phone, Clock, Globe } from 'lucide-react';

export default function EmergencyContacts({ contacts }) {
  const handleCall = (phoneNumber) => {
    window.location.href = `tel:${phoneNumber}`;
  };

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-bold text-ink mb-4">긴급 연락처</h3>

      {contacts.map((contact, index) => (
        <div
          key={index}
          className="bg-gradient-to-br from-red-50 dark:from-red-500/10 to-orange-50 dark:to-orange-500/10 rounded-2xl p-4 border border-red-100 dark:border-red-500/20"
        >
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1">
              <h4 className="font-bold text-ink mb-1">{contact.name}</h4>
              <p className="text-sm text-ink-muted mb-2">{contact.description}</p>

              {/* 운영시간 */}
              <div className="flex items-center gap-2 text-xs text-ink-muted mb-1">
                <Clock className="w-4 h-4" />
                <span>{contact.available_hours}</span>
              </div>

              {/* 지원 언어 */}
              {contact.languages && contact.languages.length > 0 && (
                <div className="flex items-center gap-2 text-xs text-ink-muted">
                  <Globe className="w-4 h-4" />
                  <span>{contact.languages.join(', ')}</span>
                </div>
              )}
            </div>

            {/* 전화 버튼 */}
            <button
              onClick={() => handleCall(contact.phone)}
              className="flex-shrink-0 ml-3 bg-red-600 hover:bg-red-700 text-white rounded-full p-3 shadow-lg transition-colors"
              title={`전화 걸기: ${contact.phone}`}
            >
              <Phone className="w-5 h-5" />
            </button>
          </div>

          {/* 전화번호 표시 */}
          <div className="mt-3 pt-3 border-t border-red-200 dark:border-red-500/30">
            <a
              href={`tel:${contact.phone}`}
              className="text-2xl font-bold text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
            >
              {contact.phone}
            </a>
          </div>
        </div>
      ))}
    </div>
  );
}
