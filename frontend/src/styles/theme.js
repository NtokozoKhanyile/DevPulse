// JS design tokens — import these wherever you need design values in logic
// (e.g. inline stage badge colours, dynamic styles)

export const colors = {
  brand: {
    primary:  '#1A7A3E',
    accent:   '#639922',
    tint:     '#E8F5EE',
    border:   '#C6E6D2',
  },
  surface: {
    white:    '#FFFFFF',
    offwhite: '#F9FAFB',
    dark:     '#111111',
  },
  text: {
    primary:  '#111111',
    body:     '#374151',
    muted:    '#6B7280',
  },
  ui: {
    border:   '#D1D5DB',
    error:    '#DC2626',
    warning:  '#92400E',
  },
}

// Stage badge colour map — used by Badge component and StageSelector
export const stageColors = {
  idea: {
    bg:     '#F3F4F6',
    text:   '#374151',
    border: '#D1D5DB',
  },
  building: {
    bg:     '#E8F5EE',
    text:   '#1A7A3E',
    border: '#C6E6D2',
  },
  testing: {
    bg:     '#FFF7ED',
    text:   '#92400E',
    border: '#FDE68A',
  },
  shipped: {
    bg:     '#EFF6FF',
    text:   '#1E40AF',
    border: '#BFDBFE',
  },
  completed: {
    bg:     '#F0FFF4',
    text:   '#166534',
    border: '#BBF7D0',
  },
}

// Stage progression order — single source of truth
export const STAGE_ORDER = ['idea', 'building', 'testing', 'shipped', 'completed']

export const spacing = {
  xs:  '0.25rem',
  sm:  '0.5rem',
  md:  '1rem',
  lg:  '1.5rem',
  xl:  '2rem',
  xxl: '3rem',
}