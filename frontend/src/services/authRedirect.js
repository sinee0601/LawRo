// 로그인이 필요한 기능에서 로그인 화면으로 보냈다가, 로그인 후 원래 위치로 돌려보내는 데 쓰는 도우미.
// 돌아갈 위치는 /login?next=/chat 처럼 주소에 담아 두어 새로고침이나 회원가입을 거쳐도 유지됩니다.

export const DEFAULT_AFTER_LOGIN = '/contract';

/** 앱 안의 경로만 허용합니다. 외부 주소(//evil.com 등)나 로그인·회원가입 화면으로는 돌려보내지 않습니다. */
export function safeNext(raw) {
  if (typeof raw !== 'string' || !raw.startsWith('/') || raw.startsWith('//') || raw.startsWith('/\\')) {
    return DEFAULT_AFTER_LOGIN;
  }
  if (/^\/(login|signup)(?=$|[/?#])/.test(raw)) return DEFAULT_AFTER_LOGIN;
  return raw;
}

/** 로그인 화면 주소. next 를 주면 로그인 후 그 경로로 돌아옵니다. */
export function loginPath(next) {
  const target = next ? safeNext(next) : null;
  return target && target !== DEFAULT_AFTER_LOGIN ? `/login?next=${encodeURIComponent(target)}` : '/login';
}

/** 회원가입 화면 주소. 로그인 화면에서 넘어갈 때 돌아갈 위치를 그대로 넘깁니다. */
export function signupPath(next) {
  const target = next ? safeNext(next) : null;
  return target && target !== DEFAULT_AFTER_LOGIN ? `/signup?next=${encodeURIComponent(target)}` : '/signup';
}
