import { type ButtonHTMLAttributes, type AnchorHTMLAttributes } from 'react';
import { Link, type LinkProps } from 'react-router';
import { cn } from '@/utils/cn';
import './Button.css';

type Variant = 'primary' | 'secondary' | 'tertiary';
type Size = 'sm' | 'md' | 'lg';

interface ButtonBaseProps {
  variant?: Variant;
  size?: Size;
  fullWidth?: boolean;
  className?: string;
}

type ButtonAsButton = ButtonBaseProps &
  ButtonHTMLAttributes<HTMLButtonElement> & {
    as?: 'button';
    to?: never;
    href?: never;
  };

type ButtonAsLink = ButtonBaseProps &
  Omit<LinkProps, 'className'> & {
    as: 'link';
    href?: never;
  };

type ButtonAsAnchor = ButtonBaseProps &
  AnchorHTMLAttributes<HTMLAnchorElement> & {
    as: 'anchor';
    to?: never;
  };

export type ButtonProps = ButtonAsButton | ButtonAsLink | ButtonAsAnchor;

export function Button(props: ButtonProps) {
  const {
    variant = 'primary',
    size = 'md',
    fullWidth = false,
    className,
  } = props;

  const classes = cn(
    'gf-btn',
    `gf-btn--${variant}`,
    size !== 'md' && `gf-btn--${size}`,
    fullWidth && 'gf-btn--full',
    className,
  );

  if (props.as === 'link') {
    const { as: _, variant: _v, size: _s, fullWidth: _f, className: _c, ...linkProps } = props;
    return <Link {...linkProps} className={classes} />;
  }

  if (props.as === 'anchor') {
    const { as: _, variant: _v, size: _s, fullWidth: _f, className: _c, ...anchorProps } = props;
    return <a {...anchorProps} className={classes} />;
  }

  const { as: _, variant: _v, size: _s, fullWidth: _f, className: _c, ...buttonProps } = props;
  return <button {...buttonProps} className={classes} />;
}
