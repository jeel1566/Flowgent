import {Composition} from 'remotion';
import {
  FlowgentPresentation,
  FPS,
  HEIGHT,
  SCENE_COUNT,
  SCENE_DURATION,
  WIDTH,
} from './FlowgentPresentation';

export const RemotionRoot = () => {
  return (
    <Composition
      id="FlowgentPresentation"
      component={FlowgentPresentation}
      durationInFrames={SCENE_COUNT * SCENE_DURATION}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
  );
};
