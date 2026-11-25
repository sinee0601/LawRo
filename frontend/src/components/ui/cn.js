// className 조각을 합칩니다. false, null, undefined 는 건너뜁니다.
export function cn(...parts) {
  return parts.filter(Boolean).join(' ');
}
