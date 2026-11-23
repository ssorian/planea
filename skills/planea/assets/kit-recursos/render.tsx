// Uso: bun render.tsx <recurso.tsx> <carpeta-salida> [--png] [--html]
// El recurso exporta `default` (componente sin props) y opcionalmente
// `meta = { nombre: "anexo-03-rubrica", pagina: "letter" | "A4" | "letter landscape" }`.
import { renderToStaticMarkup } from "react-dom/server";
import { createElement } from "react";
import { mkdirSync, readFileSync, writeFileSync, rmSync, existsSync } from "node:fs";
import { resolve, dirname, basename, join } from "node:path";
import { pathToFileURL } from "node:url";

const [entrada, salida, ...flags] = process.argv.slice(2);
if (!entrada || !salida) {
  console.error("Uso: bun render.tsx <recurso.tsx> <carpeta-salida> [--png] [--html]");
  process.exit(2);
}

const ruta = resolve(entrada);
const mod = await import(ruta);
if (typeof mod.default !== "function") throw new Error("El recurso debe exportar un componente por defecto");
const meta = mod.meta ?? {};
const nombre: string = meta.nombre ?? basename(ruta).replace(/\.tsx?$/, "");
const pagina: string = meta.pagina ?? "letter";

const css = readFileSync(join(import.meta.dir, "estilos.css"), "utf8");
const cuerpo = renderToStaticMarkup(createElement(mod.default));
const base = pathToFileURL(dirname(ruta) + "/").href;
const html = `<!doctype html><html lang="es"><head><meta charset="utf-8"><base href="${base}">
<title>${nombre}</title><style>${css}\n@page { size: ${pagina}; }</style></head><body>${cuerpo}</body></html>`;

const dir = resolve(salida);
mkdirSync(dir, { recursive: true });
const htmlPath = join(dir, `${nombre}.html`);
const pdfPath = join(dir, `${nombre}.pdf`);
writeFileSync(htmlPath, html);

// Navegador: variable PLANEA_NAVEGADOR, comandos en PATH o rutas habituales (Linux, macOS, Windows).
function buscarNavegador(): string | undefined {
  if (process.env.PLANEA_NAVEGADOR && existsSync(process.env.PLANEA_NAVEGADOR)) return process.env.PLANEA_NAVEGADOR;
  for (const c of ["chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome", "msedge", "microsoft-edge"]) {
    const w = Bun.which(c);
    if (w) return w;
  }
  const pf = process.env["ProgramFiles"] ?? "C:\\Program Files";
  const pf86 = process.env["ProgramFiles(x86)"] ?? "C:\\Program Files (x86)";
  const local = process.env["LOCALAPPDATA"] ?? "";
  const rutas = [
    `${pf}\\Google\\Chrome\\Application\\chrome.exe`,
    `${pf86}\\Google\\Chrome\\Application\\chrome.exe`,
    `${local}\\Google\\Chrome\\Application\\chrome.exe`,
    `${pf86}\\Microsoft\\Edge\\Application\\msedge.exe`,
    `${pf}\\Microsoft\\Edge\\Application\\msedge.exe`,
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
  ];
  return rutas.find((r) => r && existsSync(r));
}
const chromium = buscarNavegador();
if (!chromium) throw new Error("No se encontró Chrome, Chromium ni Edge. Defina PLANEA_NAVEGADOR con la ruta del ejecutable.");
const pr = Bun.spawnSync([chromium, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
  "--allow-file-access-from-files", `--print-to-pdf=${pdfPath}`, pathToFileURL(htmlPath).href],
  { stdout: "pipe", stderr: "pipe" });
if (!existsSync(pdfPath)) {
  console.error(pr.stderr.toString());
  throw new Error("Chromium no generó el PDF");
}

let paginas = "?";
if (Bun.which("pdfinfo")) {
  const info = Bun.spawnSync(["pdfinfo", pdfPath]).stdout.toString();
  paginas = info.match(/Pages:\s+(\d+)/)?.[1] ?? "?";
} else {
  // Sin Poppler (habitual en Windows): contar objetos /Type /Page del PDF de Chromium.
  const bruto = readFileSync(pdfPath).toString("latin1");
  paginas = String((bruto.match(/\/Type\s*\/Page(?!s)/g) ?? []).length || "?");
}

const pngs: string[] = [];
let vista = "";
if (flags.includes("--png")) {
  if (Bun.which("pdftoppm")) {
    Bun.spawnSync(["pdftoppm", "-png", "-r", "110", pdfPath, join(dir, nombre)]);
    const fs = await import("node:fs");
    for (const f of fs.readdirSync(dir)) if (f.startsWith(nombre) && f.endsWith(".png")) pngs.push(join(dir, f));
    vista = "pdftoppm";
  } else {
    // Sin Poppler: captura del HTML con el navegador (aproximada; solo la primera pantalla).
    const horizontal = /landscape/.test(pagina);
    const tam = horizontal ? "1100,850" : "850,1100";
    const png = join(dir, `${nombre}-1.png`);
    Bun.spawnSync([chromium, "--headless=new", "--disable-gpu", "--hide-scrollbars", `--window-size=${tam}`,
      `--screenshot=${png}`, pathToFileURL(htmlPath).href], { stdout: "pipe", stderr: "pipe" });
    if (existsSync(png)) { pngs.push(png); vista = "captura-navegador (aproximada, primera pantalla)"; }
  }
}
if (!flags.includes("--html")) rmSync(htmlPath);

console.log(JSON.stringify({ pdf: pdfPath, paginas: Number(paginas) || paginas, png: pngs.sort(), vista }));
