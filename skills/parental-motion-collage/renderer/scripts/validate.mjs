import fs from "node:fs";
import path from "node:path";

const cwd = process.cwd();
const publicDir = path.resolve(cwd, "public");
const projectFile = path.join(publicDir, "project.json");
const errors = [];
let project;

try {
  project = JSON.parse(fs.readFileSync(projectFile, "utf8"));
} catch (error) {
  console.error("project.json inacessível ou JSON inválido:", String(error));
  process.exit(1);
}
const allowedKinds = new Set(["text", "tag", "shape", "image"]);
const allowedEntrances = new Set(["pop", "rise", "slide-left", "slide-right", "fade"]);
const isFiniteNumber = (x) => typeof x === "number" && Number.isFinite(x);
function checkMedia(relative, ref) {
  if (typeof relative !== "string" || !relative.trim()) {
    errors.push(ref + ": caminho de mídia inválido");
    return;
  }
  const resolved = path.resolve(publicDir, relative);
  if (!resolved.startsWith(publicDir + path.sep) || !fs.existsSync(resolved)) {
    errors.push(ref + ": arquivo ausente ou fora de public/: " + relative);
  }
}
if (project.editorialStatus !== "approved_for_render") errors.push("editorialStatus precisa ser approved_for_render após revisão editorial real");
if (typeof project.title !== "string" || !project.title.trim()) errors.push("title obrigatório");
if (!Array.isArray(project.shots) || !project.shots.length) errors.push("shots precisa conter cenas");
const ids = new Set();
let frameTotal = 0;
for (const [index, shot] of (project.shots ?? []).entries()) {
  const p = "shots[" + index + "]";
  if (typeof shot.id !== "string" || ids.has(shot.id)) errors.push(p + ": id vazio/duplicado");
  ids.add(shot.id);
  if (!Number.isInteger(shot.durationFrames) || shot.durationFrames < 1 || shot.durationFrames > 900) errors.push(p + ": durationFrames inválido");
  else frameTotal += shot.durationFrames;
  if (typeof shot.background !== "string" || !/^#[0-9a-fA-F]{6}$/.test(shot.background)) errors.push(p + ": cor de fundo precisa ser #RRGGBB");
  if (!Array.isArray(shot.layers) || !shot.layers.length) errors.push(p + ": sem camadas");
  const layerIds = new Set();
  for (const [li, layer] of (shot.layers ?? []).entries()) {
    const q = p + ".layers[" + li + "]";
    if (typeof layer.id !== "string" || layerIds.has(layer.id)) errors.push(q + ": id vazio/duplicado");
    layerIds.add(layer.id);
    if (!allowedKinds.has(layer.kind)) errors.push(q + ": kind inválido");
    for (const n of ["x", "y", "w", "h"]) if (!isFiniteNumber(layer[n])) errors.push(q + ": " + n + " deve ser número");
    if (layer.w <= 0 || layer.h <= 0) errors.push(q + ": dimensões positivas obrigatórias");
    if (layer.enter && !allowedEntrances.has(layer.enter)) errors.push(q + ": transição inválida");
    if (layer.startFrame !== undefined && (!Number.isInteger(layer.startFrame) || layer.startFrame < 0 || layer.startFrame >= shot.durationFrames)) errors.push(q + ": startFrame inválido");
    if ((layer.kind === "text" || layer.kind === "tag") && !layer.text) errors.push(q + ": texto ausente");
    if (layer.kind === "image") checkMedia(layer.src, q);
  }
}
for (const [name, media] of Object.entries(project.audio ?? {})) if (media) checkMedia(media, "audio." + name);
if (frameTotal > 180 * 30) errors.push("Excede 180 segundos: revisar o formato Shorts");
if (errors.length) {
  console.error("ERROS (" + errors.length + "):\n- " + errors.join("\n- "));
  process.exit(1);
}
fs.mkdirSync(path.join(cwd, "render"), {recursive: true});
console.log("OK: " + project.shots.length + " cenas / " + (frameTotal / 30).toFixed(2) + " segundos. Validação estrutural apenas, não substitui QA editorial.");
