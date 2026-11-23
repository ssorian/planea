// Uso: bun capturar.ts <juego.html> <captura.png> [--teclas "1,2,x"] [--ancho 1600] [--alto 900] [--espera ms]
// Abre el HTML con un navegador sin ventana y guarda una captura de pantalla.
// --teclas simula pulsaciones antes de capturar (separadas por comas; «Enter», «ArrowRight», «Space»,
// «Shift+1»...), para obtener una vista previa con respuestas reveladas o una celda abierta.
// Navegador: variable de entorno PLANEA_NAVEGADOR (ruta completa) o detección automática de
// Chromium, Chrome o Edge en Linux, macOS y Windows.
import { existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const args = process.argv.slice(2);
const opc = (n: string, def?: string) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : def; };
const pos = args.filter((a, i) => !a.startsWith("--") && !(i > 0 && args[i - 1].startsWith("--")));
const [html, png] = pos;
if (!html || !png) {
  console.error('Uso: bun capturar.ts <juego.html> <captura.png> [--teclas "1,2,x"] [--ancho 1600] [--alto 900] [--espera ms]');
  process.exit(2);
}
const ancho = Number(opc("--ancho", "1600"));
const alto = Number(opc("--alto", "900"));
const espera = Number(opc("--espera", "0"));
const teclas = (opc("--teclas", "") ?? "").split(",").map((t) => t.trim()).filter(Boolean);

function buscarNavegador(): string {
  const env = process.env.PLANEA_NAVEGADOR;
  if (env) {
    if (!existsSync(env)) { console.error(`PLANEA_NAVEGADOR apunta a una ruta que no existe: ${env}`); process.exit(1); }
    return env;
  }
  const pf = [process.env["ProgramFiles"], process.env["ProgramFiles(x86)"], process.env["LOCALAPPDATA"]].filter(Boolean) as string[];
  const rutas = [
    ...pf.flatMap((b) => [join(b, "Google", "Chrome", "Application", "chrome.exe"), join(b, "Microsoft", "Edge", "Application", "msedge.exe")]),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
  ];
  for (const nombre of ["chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome", "msedge", "microsoft-edge"]) {
    const r = Bun.which(nombre);
    if (r) return r;
  }
  const r = rutas.find((x) => existsSync(x));
  if (r) return r;
  console.error("No se encontró Chromium, Chrome ni Edge. Indicar la ruta del navegador en la variable PLANEA_NAVEGADOR.");
  process.exit(1);
}

const entrada = resolve(process.cwd(), html);
const salida = resolve(process.cwd(), png);
if (!existsSync(entrada)) { console.error(`No existe el archivo: ${entrada}`); process.exit(1); }
mkdirSync(dirname(salida), { recursive: true });

const tmp = mkdtempSync(join(tmpdir(), "kit-juegos-cap-"));
try {
  let destino = pathToFileURL(entrada).href;
  if (teclas.length) {
    // Página envoltorio: carga el juego en un iframe y le envía las pulsaciones.
    const envio = `
      const teclas = ${JSON.stringify(teclas)};
      const f = document.getElementById("j");
      f.onload = () => teclas.forEach((t, i) => setTimeout(() => {
        const mayus = t.startsWith("Shift+"); const k = mayus ? t.slice(6) : t === "Space" ? " " : t;
        const code = /^\\d$/.test(k) ? "Digit" + k : k === " " ? "Space" : k.length === 1 ? "Key" + k.toUpperCase() : k;
        f.contentDocument.dispatchEvent(new f.contentWindow.KeyboardEvent("keydown", { key: k, code, shiftKey: mayus, bubbles: true, cancelable: true }));
      }, 300 + i * 250));`;
    const envoltorio = join(tmp, "envoltorio.html");
    writeFileSync(envoltorio, `<!doctype html><meta charset="utf-8"><style>html,body{margin:0;height:100%}iframe{border:0;width:100%;height:100%}</style><iframe id="j" src="${destino}"></iframe><script>${envio}</script>`);
    destino = pathToFileURL(envoltorio).href;
  }
  const presupuesto = 1500 + teclas.length * 250 + espera; // --espera: tiempo extra (p. ej. 6000 para que termine el giro de la ruleta)
  const r = Bun.spawnSync([buscarNavegador(), "--headless", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
    `--user-data-dir=${join(tmp, "perfil")}`, `--window-size=${ancho},${alto}`, `--virtual-time-budget=${presupuesto}`, `--screenshot=${salida}`, destino],
    { stdout: "pipe", stderr: "pipe" });
  if (!existsSync(salida)) { console.error(r.stderr.toString()); console.error("El navegador no generó la captura."); process.exit(1); }
  console.log(`Captura guardada: ${salida}`);
} finally {
  rmSync(tmp, { recursive: true, force: true });
}
