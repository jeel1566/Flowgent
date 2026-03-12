# Animation Configuration: Flowgent Walkthrough

## Status
- Done: animation parameters defined for the long-form presentation
- Next: integrate into Remotion components and render

## Presentation Rhythm
- Total runtime: 120 seconds
- FPS: 24
- Scene count: 12
- Scene duration: 240 frames each
- Cut style: hard cuts with equal timing between every scene
- Motion goal: slow enough for reading and live narration, with restrained motion on every element

## Spring Configurations

```typescript
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
```

## Interpolation Mappings

```typescript
export const INTERPOLATIONS = {
  titleY: {
    input: [0, 1],
    output: [26, 0],
    extrapolate: 'clamp',
  },
  subtitleY: {
    input: [0, 1],
    output: [18, 0],
    extrapolate: 'clamp',
  },
  bulletX: {
    input: [0, 1],
    output: [24, 0],
    extrapolate: 'clamp',
  },
  panelScale: {
    input: [0, 1],
    output: [0.97, 1],
    extrapolate: 'clamp',
  },
  panelY: {
    input: [0, 1],
    output: [20, 0],
    extrapolate: 'clamp',
  },
} as const;
```

## Animation Timing

```typescript
export const ANIMATION_TIMING = {
  fps: 24,
  sceneDuration: 240,
  intro: { start: 0, end: 28 },
  subtitle: { start: 10, end: 40 },
  preview: { start: 14, end: 52 },
  bullets: {
    start: 44,
    delay: 18,
    duration: 24,
  },
  footer: { start: 172, end: 208 },
  hold: { start: 96, end: 216 },
  exit: { start: 220, end: 240 },
} as const;
```

## Easing

```typescript
export const EASING_CURVES = {
  smooth: Easing.bezier(0.22, 1, 0.36, 1),
  soft: Easing.inOut(Easing.quad),
  emphasis: Easing.out(Easing.cubic),
} as const;
```

## Progress Patterns

```typescript
const titleProgress = spring({
  frame,
  fps,
  config: SPRING_CONFIGS.smooth,
  durationInFrames: ANIMATION_TIMING.intro.end,
});

const previewProgress = spring({
  frame: frame - ANIMATION_TIMING.preview.start,
  fps,
  config: SPRING_CONFIGS.gentle,
  durationInFrames: ANIMATION_TIMING.preview.end - ANIMATION_TIMING.preview.start,
});

const bulletProgress = spring({
  frame: frame - (ANIMATION_TIMING.bullets.start + index * ANIMATION_TIMING.bullets.delay),
  fps,
  config: SPRING_CONFIGS.snappy,
  durationInFrames: ANIMATION_TIMING.bullets.duration,
});
```

## Motion Rules
- Titles should settle quickly and then hold.
- Bullets should stagger slowly enough for reading, not like a launch trailer.
- Preview panels should drift or pulse subtly, never compete with the text.
- No rapid zooms, glitch effects, or aggressive overshoot.
- Every scene should reserve at least 4 seconds of calm hold time for narration.

## Scene Timing Intent
1. Scene opens and establishes context.
2. Headline becomes readable in the first second.
3. Preview panel settles in shortly after.
4. Bullets reveal one by one between seconds 2 and 5.
5. Remaining time is mostly hold for speaker explanation.
6. Final second stays visually quiet before the hard cut.
