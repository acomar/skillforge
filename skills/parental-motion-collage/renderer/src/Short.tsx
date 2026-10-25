import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export type LayerSpec = {
  id: string;
  kind: "image" | "text" | "tag" | "shape";
  x: number;
  y: number;
  w: number;
  h: number;
  text?: string;
  src?: string;
  color?: string;
  background?: string;
  fontSize?: number;
  rotate?: number;
  startFrame?: number;
  enter?: "pop" | "rise" | "slide-left" | "slide-right" | "fade";
  depth?: number;
};
export type ShotSpec = {
  id: string;
  durationFrames: number;
  background: string;
  caption?: string;
  narration?: string;
  camera?: {zoomFrom?: number; zoomTo?: number; panX?: number; panY?: number};
  layers: LayerSpec[];
};
export type Project = {
  title: string;
  editorialStatus: string;
  audio?: {voice?: string; music?: string};
  shots: ShotSpec[];
};

const INK = "#243047";
const PAPER = "#FFF9F0";

const Layer: React.FC<{
  layer: LayerSpec;
  parallaxX: number;
  parallaxY: number;
}> = ({layer, parallaxX, parallaxY}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  // A camada inicial já está visível no primeiro frame; as demais entram em sequência.
  const progress =
    (layer.startFrame ?? 0) === 0
      ? 1
      : spring({frame, fps, config: {damping: 16, stiffness: 125, mass: 0.7}});
  const opacity = Math.max(0, Math.min(1, progress));
  const enter = layer.enter ?? "pop";
  const distance = 150 * (1 - progress);
  const dx = enter === "slide-left" ? -distance : enter === "slide-right" ? distance : 0;
  const dy = enter === "rise" ? distance : 0;
  const scale = enter === "pop" ? 0.78 + 0.22 * progress : 1;
  const depth = layer.depth ?? 0.05;
  const rotate = layer.rotate ?? 0;
  const style: React.CSSProperties = {
    position: "absolute",
    left: layer.x - layer.w / 2,
    top: layer.y - layer.h / 2,
    width: layer.w,
    height: layer.h,
    opacity,
    transform: `translate(${dx + parallaxX * depth}px, ${dy + parallaxY * depth}px) rotate(${rotate}deg) scale(${scale})`,
    transformOrigin: "center",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 10 + Math.round(depth * 100),
  };

  if (layer.kind === "image" && layer.src) {
    return (
      <div style={style}>
        <Img
          src={staticFile(layer.src)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "contain",
            filter: "drop-shadow(5px 10px 12px rgba(36,48,71,0.18))",
          }}
        />
      </div>
    );
  }
  if (layer.kind === "shape") {
    return (
      <div style={style}>
        <div style={{
          width: "100%",
          height: "100%",
          borderRadius: "28px 32px 26px 34px",
          background: layer.background ?? layer.color ?? "#FFD761",
          boxShadow: "8px 11px 0 rgba(36,48,71,0.10)",
          border: "5px solid rgba(255,255,255,0.35)",
        }}/>
      </div>
    );
  }
  const tag = layer.kind === "tag";
  return (
    <div style={style}>
      <div style={{
        maxWidth: "100%",
        fontFamily: "Arial, Helvetica, sans-serif",
        fontSize: layer.fontSize ?? (tag ? 52 : 78),
        fontWeight: 900,
        lineHeight: 1.04,
        letterSpacing: "-0.02em",
        textAlign: "center",
        color: layer.color ?? INK,
        background: tag ? (layer.background ?? PAPER) : "transparent",
        padding: tag ? "14px 25px" : "0",
        borderRadius: tag ? 22 : 0,
        boxShadow: tag ? "5px 7px 0 rgba(36,48,71,0.12)" : "none",
        whiteSpace: "pre-wrap",
        overflowWrap: "break-word",
      }}>
        {layer.text}
      </div>
    </div>
  );
};

const Shot: React.FC<{shot: ShotSpec}> = ({shot}) => {
  const frame = useCurrentFrame();
  const last = Math.max(1, shot.durationFrames - 1);
  const progress = Math.min(1, frame / last);
  const cam = shot.camera ?? {};
  const zoom = interpolate(progress, [0, 1], [cam.zoomFrom ?? 1, cam.zoomTo ?? 1.035]);
  const panX = (cam.panX ?? 15) * progress;
  const panY = (cam.panY ?? -12) * progress;

  return (
    <AbsoluteFill style={{background: shot.background, overflow: "hidden"}}>
      <AbsoluteFill style={{
        backgroundImage: "radial-gradient(rgba(36,48,71,0.10) 1.25px, transparent 1.25px)",
        backgroundSize: "26px 26px",
        opacity: 0.36,
      }}/>
      <AbsoluteFill style={{
        transform: `translate(${panX}px, ${panY}px) scale(${zoom})`,
        transformOrigin: "50% 50%",
      }}>
        {shot.layers.map((layer) => {
          const start = layer.startFrame ?? 0;
          return (
            <Sequence
              key={layer.id}
              from={start}
              durationInFrames={shot.durationFrames - start}
              layout="none"
            >
              <Layer layer={layer} parallaxX={panX} parallaxY={panY}/>
            </Sequence>
          );
        })}
      </AbsoluteFill>
      {shot.caption && (
        <div style={{
          position: "absolute",
          left: 110,
          right: 155,
          top: 1500,
          minHeight: 100,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}>
          <span style={{
            padding: "12px 21px",
            borderRadius: 20,
            background: "rgba(36,48,71,0.94)",
            color: "#FFFFFF",
            font: "bold 47px/1.18 Arial, sans-serif",
            textAlign: "center",
          }}>
            {shot.caption}
          </span>
        </div>
      )}
    </AbsoluteFill>
  );
};

export const ParentalShort: React.FC<{project: Project}> = ({project}) => {
  let from = 0;
  return (
    <AbsoluteFill style={{background: PAPER}}>
      {project.shots.map((shot) => {
        const start = from;
        from += shot.durationFrames;
        return (
          <Sequence key={shot.id} from={start} durationInFrames={shot.durationFrames}>
            <Shot shot={shot}/>
          </Sequence>
        );
      })}
      {project.audio?.music && <Audio src={staticFile(project.audio.music)} volume={0.12}/>}
      {project.audio?.voice && <Audio src={staticFile(project.audio.voice)} volume={1}/>}
    </AbsoluteFill>
  );
};
