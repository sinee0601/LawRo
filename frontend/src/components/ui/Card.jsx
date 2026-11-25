import { cn } from './cn';

const paddings = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
};

/**
 * 흰 배경, 카드 모서리, 카드 그림자를 가진 기본 컨테이너.
 * as 로 section, article 등 다른 태그를 쓸 수 있습니다.
 */
export default function Card({ as = 'div', padding = 'md', className, children, ...props }) {
  const Tag = as;
  return (
    <Tag className={cn('bg-surface rounded-card shadow-card', paddings[padding], className)} {...props}>
      {children}
    </Tag>
  );
}
