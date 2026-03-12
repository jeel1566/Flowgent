import React from 'react';
import {
  AbsoluteFill,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {
  ANIMATION_TIMING,
  INTERPOLATIONS,
  SPRING_CONFIGS,
} from './animation';

export const WIDTH = 1920;
export const HEIGHT = 1080;
export const FPS = ANIMATION_TIMING.fps;
export const SCENE_DURATION = ANIMATION_TIMING.sceneDuration;

const palette = {
  bg: '#08110f',
  panel: '#10221d',
  stroke: 'rgba(130, 255, 203, 0.18)',
  text: '#f3fff8',
  muted: 'rgba(229, 255, 242, 0.72)',
  green: '#77f6c7',
  mint: '#38d39a',
  aqua: '#8be1ff',
  amber: '#ffd67a',
  red: '#ff8f96',
};

type PreviewType =
  | 'hero'
  | 'problem'
  | 'surface'
  | 'chat'
  | 'protocol'
  | 'actions'
  | 'tooltip'
  | 'dashboard'
  | 'architecture'
  | 'models'
  | 'reliability'
  | 'close';

type Slide = {
  kicker: string;
  title: string;
  subtitle: string;
  bullets: string[];
  preview: PreviewType;
  accent: string;
};

const slides: Slide[] = [
  {
    kicker: '01 / Overview',
    title: 'Flowgent is an AI copilot for n8n.',
    subtitle:
      'The codebase combines a Chrome side panel, a FastAPI backend, and an agent that helps users build and operate workflows in plain language.',
    bullets: [
      'Chrome extension side panel anchored to the n8n workflow context',
      'Backend routes for chat, workflows, executions, and node info',
      'Designed to reduce the setup and debugging burden around automation',
    ],
    preview: 'hero',
    accent: palette.green,
  },
  {
    kicker: '02 / Problem',
    title: 'n8n is powerful, but it still expects expertise.',
    subtitle:
      'The docs and investor materials align with the implementation: building, fixing, and understanding workflows still takes time and node-level knowledge.',
    bullets: [
      'Users need to know nodes, parameters, and data flow rules',
      'Broken connections and workflow failures slow teams down',
      'People leave the canvas to search docs, examples, and fixes',
    ],
    preview: 'problem',
    accent: palette.amber,
  },
  {
    kicker: '03 / Product Surface',
    title: 'Flowgent lives where the work already happens.',
    subtitle:
      'The extension opens a side panel directly inside Chrome, with Chat, Dashboard, and Settings available in one consistent UI.',
    bullets: [
      'Manifest V3 extension with a dedicated side panel entry point',
      'Persistent connection status in the header',
      'Settings connect both backend and n8n instance credentials',
    ],
    preview: 'surface',
    accent: palette.aqua,
  },
  {
    kicker: '04 / Chat Experience',
    title: 'Users ask for workflows in plain English.',
    subtitle:
      'The side panel chat supports create, edit, debug, explain, and import-style requests without exposing users to raw workflow internals first.',
    bullets: [
      'Natural language prompt entry and conversational replies',
      'Markdown-friendly assistant responses in the UI',
      'Workflow creation feedback loops into the dashboard experience',
    ],
    preview: 'chat',
    accent: palette.green,
  },
  {
    kicker: '05 / Agent Protocol',
    title: 'The backend agent does not treat every task the same.',
    subtitle:
      'In config, Flowgent classifies requests into Fast, Standard, or Deep mode, then follows a research-first workflow before building anything important.',
    bullets: [
      'Fast mode for recipe-driven and simpler workflows',
      'Standard mode for moderate customization work',
      'Deep mode for unfamiliar services, OAuth, and production-grade asks',
    ],
    preview: 'protocol',
    accent: palette.mint,
  },
  {
    kicker: '06 / Workflow Actions',
    title: 'It can manage real workflow operations, not just answer questions.',
    subtitle:
      'The backend exposes tools and routes for node search, template research, validation, workflow CRUD, and execution against n8n.',
    bullets: [
      'Search nodes and community templates before building',
      'Validate workflow JSON before creation',
      'Create, update, and execute workflows through MCP or direct API calls',
    ],
    preview: 'actions',
    accent: palette.aqua,
  },
  {
    kicker: '07 / Information Hand',
    title: 'Hover over a node and get context immediately.',
    subtitle:
      'The tooltip system injects help into the n8n page so users can understand what a node does without leaving the workflow canvas.',
    bullets: [
      'Tooltip script listens for hover-driven node requests',
      'Shows descriptions, usage hints, and fallback summaries',
      'Caches responses to make repeat lookups feel instant',
    ],
    preview: 'tooltip',
    accent: palette.green,
  },
  {
    kicker: '08 / Operations View',
    title: 'The side panel also becomes a workflow operations surface.',
    subtitle:
      'The dashboard code reads workflows and recent executions, then handles empty and error states so the product still communicates when systems fail.',
    bullets: [
      'Workflow list with status and metadata',
      'Recent execution history for quick review',
      'Helpful connection and authentication guidance in the UI',
    ],
    preview: 'dashboard',
    accent: palette.aqua,
  },
  {
    kicker: '09 / Architecture',
    title: 'The stack is pragmatic rather than theoretical.',
    subtitle:
      'The extension talks to FastAPI, and the backend can use MCP or direct n8n API access depending on the data and credentials available.',
    bullets: [
      'Chrome extension on the front end',
      'FastAPI and agent runtime in the middle',
      'Hybrid MCP plus direct n8n client integration on the back end',
    ],
    preview: 'architecture',
    accent: palette.mint,
  },
  {
    kicker: '10 / Models & Deployment',
    title: 'The backend is flexible on both model choice and deployment.',
    subtitle:
      'Config supports OpenRouter by default, with Gemini and Azure paths available, and the project is already shaped for Docker and Cloud Run deployment.',
    bullets: [
      'OpenRouter, Gemini, and Azure-friendly configuration',
      'Health endpoint and permissive CORS for extension use',
      'Backend startup and deployment path already documented in the repo',
    ],
    preview: 'models',
    accent: palette.amber,
  },
  {
    kicker: '11 / Reliability',
    title: 'The code shows attention to failure paths, not only happy paths.',
    subtitle:
      'Across routes and clients, Flowgent tries to degrade gracefully when credentials, network, or execution behavior do not go as planned.',
    bullets: [
      'Helpful auth and connectivity messaging in the dashboard',
      'Direct client cleans deep-linked n8n URLs before use',
      'Execution falls back from one endpoint strategy to another when needed',
    ],
    preview: 'reliability',
    accent: palette.red,
  },
  {
    kicker: '12 / Closing',
    title: 'Flowgent reduces friction before, during, and after workflow build.',
    subtitle:
      'The clean product thesis from the codebase is simple: help users understand, create, fix, and operate n8n workflows without leaving context.',
    bullets: [
      'Before build: research and planning support',
      'During build: chat-driven creation and editing',
      'After build: explainability, status visibility, and execution controls',
    ],
    preview: 'close',
    accent: palette.green,
  },
];

export const SCENE_COUNT = slides.length;

const cardColors = [palette.green, palette.aqua, palette.amber, palette.red];

const PreviewCard: React.FC<{
  title: string;
  body?: string;
  color?: string;
  width?: number;
  height?: number;
  left?: number;
  top?: number;
}> = ({title, body, color = palette.green, width = 190, height = 108, left = 0, top = 0}) => {
  return (
    <div
      style={{
        ...styles.previewCard,
        width,
        height,
        left,
        top,
        borderColor: `${color}55`,
      }}
    >
      <div style={{...styles.previewCardTitle, color}}>{title}</div>
      {body ? <div style={styles.previewCardBody}>{body}</div> : null}
    </div>
  );
};

const Pill: React.FC<{label: string; color?: string}> = ({label, color = palette.green}) => (
  <div style={{...styles.pill, borderColor: `${color}55`, color}}>{label}</div>
);
const SlideScene: React.FC<{slide: Slide; index: number}> = ({slide, index}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const titleProgress = spring({
    frame,
    fps,
    config: SPRING_CONFIGS.smooth,
    durationInFrames: ANIMATION_TIMING.intro.end,
  });

  const subtitleProgress = spring({
    frame: frame - ANIMATION_TIMING.subtitle.start,
    fps,
    config: SPRING_CONFIGS.gentle,
    durationInFrames:
      ANIMATION_TIMING.subtitle.end - ANIMATION_TIMING.subtitle.start,
  });

  const previewProgress = spring({
    frame: frame - ANIMATION_TIMING.preview.start,
    fps,
    config: SPRING_CONFIGS.gentle,
    durationInFrames:
      ANIMATION_TIMING.preview.end - ANIMATION_TIMING.preview.start,
  });

  const footerProgress = spring({
    frame: frame - ANIMATION_TIMING.footer.start,
    fps,
    config: SPRING_CONFIGS.settle,
    durationInFrames:
      ANIMATION_TIMING.footer.end - ANIMATION_TIMING.footer.start,
  });

  const exitOpacity = interpolate(
    frame,
    [ANIMATION_TIMING.exit.start, ANIMATION_TIMING.exit.end],
    [1, 0.92],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    },
  );

  return (
    <AbsoluteFill style={{opacity: exitOpacity}}>
      <div style={styles.stage}>
        <div style={styles.copyCol}>
          <div style={{...styles.kicker, color: slide.accent}}>{slide.kicker}</div>
          <div
            style={{
              ...styles.title,
              opacity: titleProgress,
              transform: `translateY(${interpolate(titleProgress, INTERPOLATIONS.titleY.input, INTERPOLATIONS.titleY.output)}px)`,
            }}
          >
            {slide.title}
          </div>
          <div
            style={{
              ...styles.subtitle,
              opacity: subtitleProgress,
              transform: `translateY(${interpolate(subtitleProgress, INTERPOLATIONS.subtitleY.input, INTERPOLATIONS.subtitleY.output)}px)`,
            }}
          >
            {slide.subtitle}
          </div>
          <div style={styles.bulletWrap}>
            {slide.bullets.map((bullet, bulletIndex) => {
              const bulletProgress = spring({
                frame:
                  frame -
                  (ANIMATION_TIMING.bullets.start +
                    bulletIndex * ANIMATION_TIMING.bullets.delay),
                fps,
                config: SPRING_CONFIGS.snappy,
                durationInFrames: ANIMATION_TIMING.bullets.duration,
              });

              return (
                <div
                  key={bullet}
                  style={{
                    ...styles.bulletRow,
                    opacity: bulletProgress,
                    transform: `translateX(${interpolate(bulletProgress, INTERPOLATIONS.bulletX.input, INTERPOLATIONS.bulletX.output)}px)`,
                  }}
                >
                  <div style={{...styles.bulletDot, backgroundColor: slide.accent}} />
                  <div style={styles.bulletText}>{bullet}</div>
                </div>
              );
            })}
          </div>
        </div>
        <div
          style={{
            ...styles.previewCol,
            opacity: previewProgress,
            transform: `translateY(${interpolate(previewProgress, INTERPOLATIONS.panelY.input, INTERPOLATIONS.panelY.output)}px) scale(${interpolate(previewProgress, INTERPOLATIONS.panelScale.input, INTERPOLATIONS.panelScale.output)})`,
          }}
        >
          <PreviewPanel slide={slide} frame={frame} />
        </div>
      </div>
      <div
        style={{
          ...styles.footer,
          opacity: footerProgress,
        }}
      >
        <span>Slide {String(index + 1).padStart(2, '0')}</span>
        <span>Codebase-grounded walkthrough</span>
        <span>10 seconds per scene</span>
      </div>
    </AbsoluteFill>
  );
};

const PreviewPanel: React.FC<{slide: Slide; frame: number}> = ({slide, frame}) => {
  const drift = Math.sin(frame / 26) * 8;
  const glow = 0.16 + ((Math.sin(frame / 18) + 1) / 2) * 0.08;

  return (
    <div style={styles.previewFrame}>
      <div
        style={{
          ...styles.previewGlow,
          opacity: glow,
          transform: `translateY(${drift}px)`,
        }}
      />
      {slide.preview === 'hero' ? (
        <>
          <div style={styles.heroIconWrap}>
            <Img src={staticFile('flowgent-icon.png')} style={styles.heroIcon} />
          </div>
          <div style={styles.heroMetricRow}>
            <PreviewCard title="Chat" body="Create and edit workflows" color={palette.green} />
            <PreviewCard title="Info Hand" body="Hover docs inside n8n" color={palette.aqua} />
            <PreviewCard title="Ops" body="Status and execution review" color={palette.amber} />
          </div>
        </>
      ) : null}
      {slide.preview === 'problem' ? (
        <>
          {['Node knowledge', 'Broken runs', 'Debug friction', 'Docs hopping'].map((item, index) => (
            <PreviewCard
              key={item}
              title={item}
              color={cardColors[index]}
              left={index % 2 === 0 ? 40 : 320}
              top={index < 2 ? 84 : 260}
              width={250}
              height={120}
              body="Manual effort remains high"
            />
          ))}
          <div style={styles.problemConnectorH} />
          <div style={styles.problemConnectorV} />
        </>
      ) : null}
      {slide.preview === 'surface' ? (
        <>
          <div style={styles.mockPanel}>
            <div style={styles.mockPanelHeader}>
              <span style={styles.mockPanelBrand}>Flowgent</span>
              <span style={styles.mockStatus}>Connected</span>
            </div>
            <div style={styles.mockTabs}>
              <Pill label="Chat" />
              <Pill label="Dashboard" color={palette.aqua} />
              <Pill label="Settings" color={palette.amber} />
            </div>
            <PreviewCard title="Welcome" body="Create, debug, explain, import" left={34} top={126} width={520} height={130} />
            <PreviewCard title="Connection" body="Backend + n8n credentials" color={palette.aqua} left={34} top={276} width={250} height={112} />
            <PreviewCard title="Controls" body="Always in the side panel" color={palette.amber} left={304} top={276} width={250} height={112} />
          </div>
        </>
      ) : null}
      {slide.preview === 'chat' ? (
        <>
          <div style={{...styles.chatBubble, left: 48, top: 90, background: 'rgba(56, 211, 154, 0.18)', borderColor: 'rgba(56, 211, 154, 0.35)'}}>
            Create a workflow that posts new issues to Slack.
          </div>
          <div style={{...styles.chatBubble, left: 160, top: 220, background: 'rgba(139, 225, 255, 0.12)', borderColor: 'rgba(139, 225, 255, 0.28)'}}>
            I can research templates, fetch node docs, validate the JSON, and create it.
          </div>
          <PreviewCard title="Trigger" left={54} top={380} width={120} height={84} />
          <PreviewCard title="GitHub" color={palette.aqua} left={238} top={338} width={120} height={84} />
          <PreviewCard title="Slack" color={palette.green} left={422} top={380} width={120} height={84} />
          <div style={styles.smallConnectorA} />
          <div style={styles.smallConnectorB} />
        </>
      ) : null}
      {slide.preview === 'protocol' ? (
        <>
          <PreviewCard title="Fast" body="Recipe-driven" color={palette.green} width={170} height={96} left={36} top={54} />
          <PreviewCard title="Standard" body="Custom build" color={palette.aqua} width={170} height={96} left={224} top={54} />
          <PreviewCard title="Deep" body="Research-heavy" color={palette.amber} width={170} height={96} left={412} top={54} />
          {['Think', 'Templates', 'Docs', 'Ask', 'Build'].map((step, index) => (
            <div
              key={step}
              style={{
                ...styles.protocolStep,
                top: 190 + index * 62,
                left: 82 + (index % 2) * 36,
              }}
            >
              <span style={styles.protocolNumber}>{String(index + 1).padStart(2, '0')}</span>
              <span>{step}</span>
            </div>
          ))}
        </>
      ) : null}
      {slide.preview === 'actions' ? (
        <>
          <PreviewCard title="search_nodes" body="Find exact node types" left={34} top={62} width={170} height={92} color={palette.aqua} />
          <PreviewCard title="templates" body="Research working examples" left={34} top={176} width={170} height={92} color={palette.green} />
          <PreviewCard title="validate" body="Check workflow JSON" left={34} top={290} width={170} height={92} color={palette.amber} />
          <div style={styles.jsonCard}>
            <div style={styles.jsonLineLong} />
            <div style={styles.jsonLineShort} />
            <div style={styles.jsonLineLong} />
            <div style={styles.jsonLineShort} />
            <div style={styles.jsonLineMid} />
          </div>
          <PreviewCard title="create_workflow" body="Deploy to n8n" left={404} top={120} width={170} height={96} color={palette.green} />
          <PreviewCard title="update_workflow" body="Change existing automation" left={404} top={238} width={170} height={96} color={palette.aqua} />
          <PreviewCard title="execute" body="Run with input data" left={404} top={356} width={170} height={96} color={palette.amber} />
        </>
      ) : null}
      {slide.preview === 'tooltip' ? (
        <>
          <div style={styles.nodeBadge}>HTTP Request</div>
          <div style={styles.tooltipBox}>
            <div style={styles.tooltipTitle}>HTTP Request node</div>
            <div style={styles.tooltipText}>Use cases: APIs, webhooks, polling</div>
            <div style={styles.tooltipText}>How it works: makes outbound requests from workflows</div>
            <div style={styles.tooltipText}>What it does: fetches or sends external data</div>
          </div>
        </>
      ) : null}
      {slide.preview === 'dashboard' ? (
        <>
          <PreviewCard title="14 workflows" body="available" left={34} top={48} width={166} height={92} color={palette.green} />
          <PreviewCard title="96% healthy" body="status view" left={214} top={48} width={166} height={92} color={palette.aqua} />
          <PreviewCard title="10 recent runs" body="history" left={394} top={48} width={166} height={92} color={palette.amber} />
          {['Daily reports   healthy   2m ago', 'Stripe alerts   warning   14m ago', 'Sync jobs   success   1h ago'].map((row, index) => (
            <div key={row} style={{...styles.executionRow, top: 182 + index * 84}}>{row}</div>
          ))}
        </>
      ) : null}
      {slide.preview === 'architecture' ? (
        <>
          <div style={{...styles.archColumn, left: 42}}>
            <div style={styles.archTitle}>Extension</div>
            <div style={styles.archItem}>Side panel UI</div>
            <div style={styles.archItem}>Tooltip injector</div>
          </div>
          <div style={{...styles.archColumn, left: 238}}>
            <div style={styles.archTitle}>FastAPI</div>
            <div style={styles.archItem}>Routes</div>
            <div style={styles.archItem}>Agent runtime</div>
          </div>
          <div style={{...styles.archColumn, left: 434}}>
            <div style={styles.archTitle}>n8n</div>
            <div style={styles.archItem}>MCP server</div>
            <div style={styles.archItem}>Direct API</div>
          </div>
          <div style={styles.archConnectorOne} />
          <div style={styles.archConnectorTwo} />
        </>
      ) : null}
      {slide.preview === 'models' ? (
        <>
          <div style={styles.providerWrap}>
            <Pill label="OpenRouter" />
            <Pill label="Gemini" color={palette.aqua} />
            <Pill label="Azure" color={palette.amber} />
          </div>
          <PreviewCard title="Config" body="Model selection via env vars" left={56} top={164} width={246} height={108} color={palette.green} />
          <PreviewCard title="Health" body="/health exposes backend and MCP status" left={324} top={164} width={246} height={108} color={palette.aqua} />
          <PreviewCard title="Deploy" body="Docker and Cloud Run ready" left={190} top={306} width={246} height={108} color={palette.amber} />
        </>
      ) : null}
      {slide.preview === 'reliability' ? (
        <>
          <PreviewCard title="Auth errors" body="Helpful dashboard messaging" left={42} top={84} width={246} height={112} color={palette.red} />
          <PreviewCard title="URL cleanup" body="Strips deep links before API use" left={316} top={84} width={246} height={112} color={palette.aqua} />
          <PreviewCard title="Execution fallback" body="Try /execute then /run" left={178} top={236} width={246} height={112} color={palette.green} />
          <div style={styles.healthStrip}>
            <span style={{color: palette.green}}>health</span>
            <span style={{color: palette.aqua}}>cache</span>
            <span style={{color: palette.amber}}>graceful UI</span>
          </div>
        </>
      ) : null}
      {slide.preview === 'close' ? (
        <>
          <div style={styles.closeIconWrap}>
            <Img src={staticFile('flowgent-icon.png')} style={styles.closeIcon} />
          </div>
          <PreviewCard title="Before build" body="Research and planning support" left={26} top={324} width={176} height={108} color={palette.aqua} />
          <PreviewCard title="During build" body="Create and edit workflows" left={212} top={324} width={176} height={108} color={palette.green} />
          <PreviewCard title="After build" body="Explain, monitor, execute" left={398} top={324} width={176} height={108} color={palette.amber} />
        </>
      ) : null}
    </div>
  );
};

export const FlowgentPresentation: React.FC = () => {
  const frame = useCurrentFrame();
  const progress = frame / (SCENE_COUNT * SCENE_DURATION - 1);

  return (
    <AbsoluteFill style={styles.canvas}>
      <AbsoluteFill
        style={{
          background: `
            radial-gradient(circle at 18% 18%, rgba(119,246,199,0.12), transparent 25%),
            radial-gradient(circle at 82% 78%, rgba(139,225,255,0.12), transparent 30%),
            linear-gradient(145deg, #050a09 0%, #091412 42%, #07110f 100%)
          `,
        }}
      />
      <div style={styles.grid} />
      <div style={styles.topBar}>
        <div style={styles.brandWrap}>
          <div style={styles.brandDot} />
          <span style={styles.brandText}>FLOWGENT</span>
          <span style={styles.brandSub}>AI-powered n8n workflow assistant</span>
        </div>
        <div style={styles.runtimePill}>2:00 walkthrough</div>
      </div>
      <div style={styles.progressTrack}>
        <div style={{...styles.progressFill, width: `${progress * 100}%`}} />
      </div>
      {slides.map((slide, index) => (
        <Sequence
          key={slide.kicker}
          from={index * SCENE_DURATION}
          durationInFrames={SCENE_DURATION}
          premountFor={24}
        >
          <SlideScene slide={slide} index={index} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
const styles: Record<string, React.CSSProperties> = {
  canvas: {
    fontFamily: '"Segoe UI Variable Display", "Segoe UI", sans-serif',
    color: palette.text,
    backgroundColor: palette.bg,
  },
  grid: {
    position: 'absolute',
    inset: 0,
    backgroundImage:
      'linear-gradient(rgba(255,255,255,0.028) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.028) 1px, transparent 1px)',
    backgroundSize: '84px 84px',
    opacity: 0.26,
  },
  topBar: {
    position: 'absolute',
    top: 28,
    left: 42,
    right: 42,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  brandWrap: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    padding: '14px 18px',
    borderRadius: 999,
    border: `1px solid ${palette.stroke}`,
    background: 'rgba(10, 22, 19, 0.72)',
  },
  brandDot: { width: 10, height: 10, borderRadius: 999, background: palette.green, boxShadow: '0 0 16px rgba(119,246,199,0.75)' },
  brandText: { fontSize: 20, fontWeight: 700, letterSpacing: '0.16em' },
  brandSub: { fontSize: 17, color: palette.muted },
  runtimePill: { padding: '12px 18px', borderRadius: 999, border: `1px solid ${palette.stroke}`, background: 'rgba(10, 22, 19, 0.72)', color: palette.muted, fontSize: 18 },
  progressTrack: { position: 'absolute', left: 42, right: 42, top: 94, height: 4, borderRadius: 999, background: 'rgba(255,255,255,0.08)', overflow: 'hidden' },
  progressFill: { height: '100%', borderRadius: 999, background: 'linear-gradient(90deg, #77f6c7, #8be1ff)' },
  stage: { position: 'absolute', left: 80, right: 80, top: 148, bottom: 118, display: 'flex', gap: 32 },
  copyCol: { width: '48%', padding: '36px 22px 10px 8px', display: 'flex', flexDirection: 'column' },
  kicker: { fontSize: 20, fontWeight: 700, letterSpacing: '0.18em', textTransform: 'uppercase', marginBottom: 24 },
  title: { fontSize: 72, lineHeight: 1.04, fontWeight: 700, letterSpacing: '-0.045em', maxWidth: 860, marginBottom: 22 },
  subtitle: { fontSize: 28, lineHeight: 1.38, color: palette.muted, maxWidth: 780, marginBottom: 34 },
  bulletWrap: { display: 'flex', flexDirection: 'column', gap: 18, maxWidth: 820 },
  bulletRow: { display: 'flex', alignItems: 'flex-start', gap: 14, padding: '18px 20px', borderRadius: 22, background: 'rgba(12, 24, 21, 0.7)', border: `1px solid ${palette.stroke}` },
  bulletDot: { width: 10, height: 10, borderRadius: 999, marginTop: 12, flexShrink: 0 },
  bulletText: { fontSize: 24, lineHeight: 1.4 },
  previewCol: { flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' },
  previewFrame: { position: 'relative', width: 620, height: 520, borderRadius: 34, overflow: 'hidden', background: 'linear-gradient(180deg, rgba(16,34,29,0.96), rgba(11,24,21,0.96))', border: `1px solid ${palette.stroke}`, boxShadow: '0 30px 80px rgba(0,0,0,0.28)' },
  previewGlow: { position: 'absolute', width: 420, height: 420, left: 110, top: 40, borderRadius: 999, background: 'radial-gradient(circle, rgba(119,246,199,0.22), transparent 60%)' },
  previewCard: { position: 'absolute', padding: '16px 18px', borderRadius: 22, background: 'rgba(16, 34, 29, 0.82)', border: `1px solid ${palette.stroke}`, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' },
  previewCardTitle: { fontSize: 22, fontWeight: 700, marginBottom: 8 },
  previewCardBody: { fontSize: 16, lineHeight: 1.35, color: palette.muted },
  heroIconWrap: { position: 'absolute', left: 205, top: 58, width: 210, height: 210, borderRadius: 999, background: 'radial-gradient(circle at 35% 30%, rgba(255,255,255,0.16), rgba(119,246,199,0.1) 55%, rgba(9,17,15,0.98) 76%)', border: `1px solid ${palette.stroke}`, display: 'flex', alignItems: 'center', justifyContent: 'center' },
  heroIcon: { width: '72%', height: '72%', objectFit: 'contain' },
  heroMetricRow: { position: 'absolute', left: 20, right: 20, bottom: 28, display: 'flex', gap: 12 },
  problemConnectorH: { position: 'absolute', left: 170, top: 244, width: 280, height: 2, background: 'rgba(255,255,255,0.12)' },
  problemConnectorV: { position: 'absolute', left: 308, top: 154, width: 2, height: 200, background: 'rgba(255,255,255,0.12)' },
  mockPanel: { position: 'absolute', inset: 24, borderRadius: 28, background: 'rgba(9, 18, 16, 0.74)', border: `1px solid ${palette.stroke}` },
  mockPanelHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '22px 24px 12px' },
  mockPanelBrand: { fontSize: 24, fontWeight: 700 },
  mockStatus: { fontSize: 16, color: palette.green },
  mockTabs: { display: 'flex', gap: 10, padding: '0 24px' },
  pill: { padding: '9px 14px', borderRadius: 999, fontSize: 14, fontWeight: 700, border: `1px solid ${palette.stroke}`, background: 'rgba(14, 28, 24, 0.84)' },
  chatBubble: { position: 'absolute', width: 420, padding: '20px 22px', borderRadius: 24, border: `1px solid ${palette.stroke}`, fontSize: 22, lineHeight: 1.35, color: palette.text },
  smallConnectorA: { position: 'absolute', left: 174, top: 412, width: 68, height: 2, background: 'rgba(255,255,255,0.16)' },
  smallConnectorB: { position: 'absolute', left: 358, top: 412, width: 68, height: 2, background: 'rgba(255,255,255,0.16)' },
  protocolStep: { position: 'absolute', width: 420, padding: '16px 18px', borderRadius: 18, background: 'rgba(14, 28, 24, 0.9)', border: `1px solid ${palette.stroke}`, display: 'flex', alignItems: 'center', gap: 14, fontSize: 24, fontWeight: 650 },
  protocolNumber: { fontSize: 14, letterSpacing: '0.14em', color: palette.muted },
  jsonCard: { position: 'absolute', left: 222, top: 98, width: 160, height: 310, padding: '18px 14px', borderRadius: 24, background: 'rgba(10, 22, 19, 0.84)', border: `1px solid ${palette.stroke}` },
  jsonLineLong: { height: 10, width: 118, borderRadius: 999, background: 'rgba(139,225,255,0.34)', marginBottom: 16 },
  jsonLineMid: { height: 10, width: 92, borderRadius: 999, background: 'rgba(119,246,199,0.34)', marginBottom: 16 },
  jsonLineShort: { height: 10, width: 78, borderRadius: 999, background: 'rgba(255,214,122,0.34)', marginBottom: 16 },
  nodeBadge: { position: 'absolute', left: 52, top: 220, width: 188, height: 104, borderRadius: 26, background: 'rgba(16,34,29,0.92)', border: `1px solid ${palette.stroke}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 28, fontWeight: 700 },
  tooltipBox: { position: 'absolute', left: 266, top: 126, width: 300, height: 270, borderRadius: 26, padding: '20px 20px 16px', background: 'rgba(16,34,29,0.94)', border: `1px solid ${palette.stroke}` },
  tooltipTitle: { fontSize: 24, fontWeight: 700, marginBottom: 14 },
  tooltipText: { fontSize: 16, lineHeight: 1.45, color: palette.muted, marginBottom: 12 },
  executionRow: { position: 'absolute', left: 34, right: 34, height: 58, borderRadius: 18, background: 'rgba(16,34,29,0.84)', border: `1px solid ${palette.stroke}`, display: 'flex', alignItems: 'center', padding: '0 18px', fontSize: 18, color: palette.muted },
  archColumn: { position: 'absolute', top: 118, width: 144, minHeight: 250, borderRadius: 22, padding: '18px 14px', background: 'rgba(16,34,29,0.9)', border: `1px solid ${palette.stroke}` },
  archTitle: { fontSize: 24, fontWeight: 700, marginBottom: 18 },
  archItem: { fontSize: 16, lineHeight: 1.4, color: palette.muted, marginBottom: 10 },
  archConnectorOne: { position: 'absolute', left: 186, top: 246, width: 52, height: 2, background: 'rgba(255,255,255,0.14)' },
  archConnectorTwo: { position: 'absolute', left: 382, top: 246, width: 52, height: 2, background: 'rgba(255,255,255,0.14)' },
  providerWrap: { position: 'absolute', top: 58, left: 50, right: 50, display: 'flex', gap: 12, justifyContent: 'center' },
  healthStrip: { position: 'absolute', left: 96, right: 96, bottom: 56, display: 'flex', justifyContent: 'space-between', fontSize: 18, fontWeight: 700, letterSpacing: '0.04em' },
  closeIconWrap: { position: 'absolute', left: 212, top: 84, width: 196, height: 196, borderRadius: 40, background: 'linear-gradient(145deg, rgba(255,255,255,0.08), rgba(119,246,199,0.08))', border: `1px solid ${palette.stroke}`, display: 'flex', alignItems: 'center', justifyContent: 'center' },
  closeIcon: { width: '72%', height: '72%', objectFit: 'contain' },
  footer: { position: 'absolute', left: 82, right: 82, bottom: 38, display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 18px', borderRadius: 999, border: `1px solid ${palette.stroke}`, background: 'rgba(10,22,19,0.72)', color: palette.muted, fontSize: 17 },
};
