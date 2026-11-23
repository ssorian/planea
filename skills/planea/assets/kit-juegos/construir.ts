// Uso: bun construir.ts <juego> <datos.json> <salida.html>
// Valida el JSON contra el esquema del juego, lo incrusta en el build y deja UN solo archivo
// HTML (sin internet) en <salida.html>. Las rutas de datos y salida son relativas a donde se
// ejecuta el comando; el script puede invocarse desde cualquier carpeta.
import { build } from "vite";
import react from "@vitejs/plugin-react";
import { viteSingleFile } from "vite-plugin-singlefile";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { JUEGOS, validar, type Juego } from "./src/esquemas";

const AQUI = import.meta.dir;
const [juego, entrada, salida] = process.argv.slice(2);

function fallar(msg: string, codigo = 1): never {
  console.error(msg);
  process.exit(codigo);
}

if (!juego || !entrada || !salida) {
  fallar(`Uso: bun construir.ts <juego> <datos.json> <salida.html>\nJuegos disponibles: ${JUEGOS.join(", ")}`, 2);
}
if (!JUEGOS.includes(juego as Juego)) fallar(`Juego desconocido «${juego}». Juegos disponibles: ${JUEGOS.join(", ")}`, 2);

const rutaDatos = resolve(process.cwd(), entrada);
if (!existsSync(rutaDatos)) fallar(`No se encontró el archivo de datos: ${rutaDatos}`);
let crudo: unknown;
try {
  crudo = JSON.parse(readFileSync(rutaDatos, "utf8"));
} catch (e) {
  fallar(`El archivo ${entrada} no es JSON válido (detalle del analizador: ${(e as Error).message}).\nRevisar comas, comillas dobles y llaves.`);
}

const res = validar(juego as Juego, crudo);
if (!res.ok) {
  fallar(`Los datos de «${juego}» tienen ${res.errores.length} problema(s) en ${entrada}:\n` + res.errores.slice(0, 40).map((e) => `  - ${e}`).join("\n") + (res.errores.length > 40 ? "\n  ... (hay más)" : ""));
}
const datos = res.datos as { titulo: string };

let destino = resolve(process.cwd(), salida);
if (existsSync(destino) && statSync(destino).isDirectory()) destino = join(destino, `${juego}.html`);

const tmp = mkdtempSync(join(tmpdir(), "kit-juegos-"));
try {
  await build({
    root: AQUI,
    configFile: false,
    logLevel: "warn",
    base: "./",
    plugins: [react(), viteSingleFile()],
    define: {
      __JUEGO__: JSON.stringify(juego),
      // «<» escapado para que ningún texto pueda cerrar la etiqueta <script> del HTML.
      __DATOS__: JSON.stringify(datos).replace(/</g, "\\u003c"),
    },
    build: { outDir: tmp, emptyOutDir: true, target: "es2020", minify: true, reportCompressedSize: false },
  });
  let html = readFileSync(join(tmp, "index.html"), "utf8");
  const titulo = datos.titulo.replace(/&/g, "&amp;").replace(/</g, "&lt;");
  html = html.replace(/<title>.*?<\/title>/, () => `<title>${titulo}</title>`);
  mkdirSync(dirname(destino), { recursive: true });
  writeFileSync(destino, html);
  console.log(`Listo: ${destino} (${(html.length / 1024).toFixed(0)} KB). Abrir con doble clic; funciona sin internet.`);
} finally {
  rmSync(tmp, { recursive: true, force: true });
}
