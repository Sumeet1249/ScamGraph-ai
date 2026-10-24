import { forwardRef, type InputHTMLAttributes, type TextareaHTMLAttributes, type SelectHTMLAttributes, type ReactNode } from "react";
import { AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils/cn";

/** Base Input with label, help, error states. */
export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  help?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { label, help, error, className, ...props },
  ref,
) {
  const id = props.id || `input-${Math.random().toString(36).slice(2, 9)}`;
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={id} className="text-label text-text-primary">
          {label}
        </label>
      )}
      <input
        ref={ref}
        id={id}
        aria-invalid={error ? "true" : undefined}
        className={cn(
          "sg-input",
          error
            ? "border-danger focus-visible:border-danger"
            : "",
          className,
        )}
        {...props}
      />
      {error && (
        <div className="sg-field__error flex items-center gap-1.5">
          <AlertCircle className="h-3.5 w-3.5 shrink-0" aria-hidden />
          <span>{error}</span>
        </div>
      )}
      {help && !error && (
        <p className="sg-field__help">{help}</p>
      )}
    </div>
  );
});

/** Textarea with label, help, error states. */
export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  help?: string;
  error?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(function Textarea(
  { label, help, error, className, ...props },
  ref,
) {
  const id = props.id || `textarea-${Math.random().toString(36).slice(2, 9)}`;
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={id} className="text-label text-text-primary">
          {label}
        </label>
      )}
      <textarea
        ref={ref}
        id={id}
        aria-invalid={error ? "true" : undefined}
        className={cn(
          "sg-input resize-none",
          error
            ? "border-danger focus-visible:border-danger"
            : "",
          className,
        )}
        {...props}
      />
      {error && (
        <div className="sg-field__error flex items-center gap-1.5">
          <AlertCircle className="h-3.5 w-3.5 shrink-0" aria-hidden />
          <span>{error}</span>
        </div>
      )}
      {help && !error && (
        <p className="sg-field__help">{help}</p>
      )}
    </div>
  );
});

/** Select with label, help, error states. */
export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  help?: string;
  error?: string;
  placeholder?: string;
  children: ReactNode;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select(
  { label, help, error, placeholder, className, children, ...props },
  ref,
) {
  const id = props.id || `select-${Math.random().toString(36).slice(2, 9)}`;
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={id} className="text-label text-text-primary">
          {label}
        </label>
      )}
      <select
        ref={ref}
        id={id}
        aria-invalid={error ? "true" : undefined}
        className={cn(
          "sg-input appearance-none",
          error
            ? "border-danger focus-visible:border-danger"
            : "",
          className,
        )}
        {...props}
      >
        {placeholder && <option value="">{placeholder}</option>}
        {children}
      </select>
      {error && (
        <div className="sg-field__error flex items-center gap-1.5">
          <AlertCircle className="h-3.5 w-3.5 shrink-0" aria-hidden />
          <span>{error}</span>
        </div>
      )}
      {help && !error && (
        <p className="sg-field__help">{help}</p>
      )}
    </div>
  );
});
