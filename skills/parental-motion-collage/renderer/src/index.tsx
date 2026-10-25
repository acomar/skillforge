import React from "react";
import {Composition, registerRoot} from "remotion";
import {ParentalShort, Project} from "./Short";
import projectData from "../public/project.json";

const project = projectData as Project;
const frames = project.shots.reduce((total, shot) => total + shot.durationFrames, 0);

export const Root: React.FC = () => (
  <Composition
    id="ParentalShort"
    component={ParentalShort}
    durationInFrames={Math.max(frames, 1)}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={{project}}
  />
);

registerRoot(Root);
