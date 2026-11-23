import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from "react";

export type Atajo = [teclas: string, descripcion: string];

const CtxAyuda = createContext(false);

const esCampo = (t: EventTarget | null) => t instanceof HTMLElement && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable);

/** Número 1–9 de una tecla (fila superior o teclado numérico), sin depender de la distribución. */
export function numeroTecla(e: KeyboardEvent): number | null {
  const m = /^(?:Digit|Numpad)(\d)$/.exec(e.code);
  return m ? Number(m[1]) : null;
}

/** Atajos del juego. Se ignoran con la ayuda abierta, dentro de campos de texto y con Ctrl/Alt. */
export function useTeclas(fn: (e: KeyboardEvent) => void) {
  const ayuda = useContext(CtxAyuda);
  const ref = useRef(fn);
  ref.current = fn;
  const ay = useRef(ayuda);
  ay.current = ayuda;
  useEffect(() => {
    const f = (e: KeyboardEvent) => {
      if (ay.current || esCampo(e.target) || e.ctrlKey || e.metaKey || e.altKey) return;
      if (["f", "h", "?"].includes(e.key.toLowerCase())) return;
      ref.current(e);
    };
    window.addEventListener("keydown", f);
    return () => window.removeEventListener("keydown", f);
  }, []);
}

function pantallaCompleta() {
  if (document.fullscreenElement) void document.exitFullscreen();
  else void document.documentElement.requestFullscreen?.().catch(() => {});
}

export function Marco({ titulo, ejemplo, atajos, children }: { titulo: string; ejemplo: boolean; atajos: Atajo[]; children: ReactNode }) {
  const [ayuda, setAyuda] = useState(false);
  useEffect(() => {
    document.title = titulo;
  }, [titulo]);
  useEffect(() => {
    const tecla = (e: KeyboardEvent) => {
      if (esCampo(e.target) || e.ctrlKey || e.metaKey || e.altKey) return;
      const k = e.key.toLowerCase();
      if (k === "f") { e.preventDefault(); pantallaCompleta(); }
      else if (k === "h" || k === "?") { e.preventDefault(); setAyuda((a) => !a); }
      else if (k === "escape") setAyuda(false);
    };
    // Tras un clic en un botón se quita el foco: así Espacio/Enter no lo activan otra vez.
    const clic = () => { const a = document.activeElement; if (a instanceof HTMLButtonElement) a.blur(); };
    window.addEventListener("keydown", tecla);
    document.addEventListener("click", clic);
    return () => { window.removeEventListener("keydown", tecla); document.removeEventListener("click", clic); };
  }, []);
  return (
    <CtxAyuda.Provider value={ayuda}>
      <header className="barra">
        <h1>{titulo}</h1>
        {ejemplo && <span className="insignia-ejemplo">EJEMPLO · contenido ilustrativo</span>}
      </header>
      <main className="cuerpo">{children}</main>
      <footer className="pie">
        <span><kbd>H</kbd> ayuda</span>
        <span><kbd>F</kbd> pantalla completa</span>
      </footer>
      {ayuda && (
        <div className="ayuda" onClick={() => setAyuda(false)}>
          <div className="ayuda-caja" onClick={(e) => e.stopPropagation()}>
            <h2>Controles</h2>
            <table>
              <tbody>
                {[...atajos, ["F", "Pantalla completa (entrar y salir)"], ["H", "Mostrar u ocultar esta ayuda"]].map(([k, d]) => (
                  <tr key={k + d}><th>{k.split(" / ").map((t) => <kbd key={t}>{t}</kbd>)}</th><td>{d}</td></tr>
                ))}
              </tbody>
            </table>
            <p className="nota">También se puede usar el ratón o el dedo en la pantalla táctil. Pulsar H o Esc para cerrar.</p>
          </div>
        </div>
      )}
    </CtxAyuda.Provider>
  );
}

/** Figuras de las tarjetas A–D: color + letra + forma, para no depender solo del color. */
export const OPCIONES = [
  { letra: "A", nombre: "rojo", color: "#c8372d", texto: "#ffffff" },
  { letra: "B", nombre: "azul", color: "#1f5fae", texto: "#ffffff" },
  { letra: "C", nombre: "amarillo", color: "#f2b800", texto: "#14202b" },
  { letra: "D", nombre: "verde", color: "#2a7d4f", texto: "#ffffff" },
] as const;

export function Forma({ i, tam = "2rem" }: { i: number; tam?: string }) {
  const formas = [
    <polygon key="a" points="50,10 94,88 6,88" />, // triángulo
    <circle key="b" cx="50" cy="50" r="42" />, // círculo
    <rect key="c" x="12" y="12" width="76" height="76" />, // cuadrado
    <polygon key="d" points="50,6 92,50 50,94 8,50" />, // rombo
  ];
  return <svg viewBox="0 0 100 100" width={tam} height={tam} fill="currentColor" aria-hidden="true">{formas[i]}</svg>;
}

/** Marcador de equipos con puntos. */
export function Marcador({ equipos, puntos, onClic, ayudaClic }: { equipos: string[]; puntos: number[]; onClic?: (i: number) => void; ayudaClic?: string }) {
  const max = Math.max(...puntos);
  return (
    <div className="marcador">
      {equipos.map((n, i) => (
        <button key={i} className={"equipo" + (max > 0 && puntos[i] === max ? " lidera" : "")} onClick={() => onClic?.(i)} title={ayudaClic} disabled={!onClic}>
          <span className="equipo-nombre">{n}</span>
          <span className="equipo-puntos">{puntos[i]}</span>
        </button>
      ))}
    </div>
  );
}
