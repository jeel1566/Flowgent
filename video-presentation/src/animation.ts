import {Easing} from 'remotion';

export const SPRING_CONFIGS = {
  smooth: {
    damping: 220,
    mass: 1,
    stiffness: 90,
  },
  gentle: {
    damping: 140,
    mass: 1.05,
    stiffness: 70,
  },
  snappy: {
    damping: 30,
    mass: 0.85,
    stiffness: 180,
  },
  settle: {
    damping: 170,
    mass: 1,
    stiffness: 120,
  },
} as const;

export const ANIMATION_TIMING = {
  fps: 24,
  sceneDuration: 240,
  intro: {start: 0, end: 28},
  subtitle: {start: 10, end: 40},
  preview: {start: 14, end: 52},
  bullets: {
    start: 44,
    delay: 18,
    duration: 24,
  },
  footer: {start: 172, end: 208},
  hold: {start: 96, end: 216},
  exit: {start: 220, end: 240},
} as const;

export const INTERPOLATIONS = {
  titleY: {
    input: [0, 1],
    output: [26, 0],
  },
  subtitleY: {
    input: [0, 1],
    output: [18, 0],
  },
  bulletX: {
    input: [0, 1],
    output: [24, 0],
  },
  panelScale: {
    input: [0, 1],
    output: [0.97, 1],
  },
  panelY: {
    input: [0, 1],
    output: [20, 0],
  },
} as const;

export const EASING_CURVES = {
  smooth: Easing.bezier(0.22, 1, 0.36, 1),
  soft: Easing.inOut(Easing.quad),
  emphasis: Easing.out(Easing.cubic),
} as const;
