import { Phone, Clock, Globe } from 'lucide-react';
import useTranslation from '../hooks/useTranslation';

export default function EmergencyContacts({ contacts }) {
  const { t } = useTranslation();
  const handleCall = (phoneNumber) => {
    window.location.href = `tel:${phoneNumber}`;
  };

  return (
    <div>
      <h3 className="text-lg font-bold text-ink mb-4">{t('support.emergency')}</h3>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
      {contacts.map((contact, index) => (
        <div
          key={index}
          className="bg-danger-soft rounded-card p-4 border border-danger/20"
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
              className="flex-shrink-0 ml-3 bg-danger hover:bg-danger-hover text-white rounded-full p-3 shadow-raised transition-colors focus-visible:outline-none focus-visible:shadow-focus"
              title={t('support.callNumber', { phone: contact.phone })}
              aria-label={t('support.callNumber', { phone: contact.phone })}
            >
              <Phone className="w-5 h-5" />
            </button>
          </div>

          {/* 전화번호 표시 */}
          <div className="mt-3 pt-3 border-t border-danger/20">
            <a
              href={`tel:${contact.phone}`}
              className="text-2xl font-bold text-danger-ink hover:underline"
            >
              {contact.phone}
            </a>
          </div>
        </div>
      ))}
      </div>
    </div>
  );
}
