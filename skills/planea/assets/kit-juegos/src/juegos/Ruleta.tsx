import { useRef, useState } from "react";
import { Marco, useTeclas, type Atajo } from "../comun";
import type { DatosRuleta } from "../esquemas";

const ATAJOS: Atajo[] = [
  ["Enter / Espacio", "Girar la ruleta"],
  ["R", "Mostrar la respuesta del elemento (si la tiene)"],
  ["M", "Activar o desactivar «no repetir»"],
  ["N", "Reiniciar: vuelven a participar todos los elementos"],
];

const COLORES = ["#2f6f73", "#3b5b92", "#8a4f7d", "#a65e2e", "#4e7d3a", "#6b5b95"];
const DURACION = 4.8; // segundos

const azar = (n: number) => crypto.getRandomValues(new Uint32Array(1))[0] % n;
// Punto a «grados» desde la parte superior, en sentido horario.
const punto = (grados: number, r: number) => {
  const a = ((grados - 90) * Math.PI) / 180;
  return [r * Math.cos(a), r * Math.sin(a)];
};

export default function Ruleta({ d }: { d: DatosRuleta }) {
  const n = d.elementos.length;
  const [rot, setRot] = useState(0);
  const [girando, setGirando] = useState(false);
  const [sale, setSale] = useState<number | null>(null);
  const [salidos, setSalidos] = useState<Set<number>>(new Set());
  const [noRep, setNoRep] = useState(d.noRepetir);
  const [verResp, setVerResp] = useState(false);
  const reducido = useRef(window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false);
  const dur = reducido.current ? 0.6 : DURACION;

  const disponibles = d.elementos.map((_, i) => i).filter((i) => !noRep || !salidos.has(i));
  const agotada = disponibles.length === 0;

  const girar = () => {
    if (girando || agotada) return;
    const elegido = disponibles[azar(disponibles.length)];
    const seg = 360 / n;
    const desvio = (Math.random() - 0.5) * 0.7 * seg; // nunca cae sobre el borde del sector
    const destino = (((360 - (elegido + 0.5) * seg - desvio) % 360) + 360) % 360;
    const actual = ((rot % 360) + 360) % 360;
    setRot(rot + 360 * (reducido.current ? 1 : 5) + ((destino - actual + 360) % 360));
    setGirando(true);
    setVerResp(false);
    setSale(null);
    setTimeout(() => {
      setGirando(false);
      setSale(elegido);
      setSalidos((s) => new Set(s).add(elegido));
    }, dur * 1000 + 80);
  };
  const reiniciar = () => { if (!girando) { setSalidos(new Set()); setSale(null); } };

  useTeclas((ev) => {
    const k = ev.key.toLowerCase();
    if (k === "enter" || k === " ") girar();
    else if (k === "r") setVerResp(true);
    else if (k === "m") setNoRep((v) => !v);
    else if (k === "n") reiniciar();
    else return;
    ev.preventDefault();
  });

  const seg = 360 / n;
  const tam = n <= 8 ? 7 : n <= 16 ? 5.6 : n <= 30 ? 4 : 0;
  const el = sale !== null ? d.elementos[sale] : null;

  return (
    <Marco titulo={d.titulo} ejemplo={d.ejemplo} atajos={ATAJOS}>
      <div className="rul">
        <div className="rul-rueda">
          <svg viewBox="-104 -104 208 208" role="img" aria-label="Ruleta">
            <g className="rul-giro" style={{ transform: `rotate(${rot}deg)`, transition: girando ? `transform ${dur}s cubic-bezier(0.12, 0.6, 0.15, 1)` : "none" }}>
              {d.elementos.map((e, i) => {
                const gastado = noRep && salidos.has(i);
                let c = COLORES[i % COLORES.length];
                if (i === n - 1 && n % COLORES.length === 1) c = COLORES[2];
                const [x1, y1] = punto(i * seg, 100);
                const [x2, y2] = punto((i + 1) * seg, 100);
                const camino = `M0 0 L${x1} ${y1} A100 100 0 ${seg > 180 ? 1 : 0} 1 ${x2} ${y2} Z`;
                const etiqueta = d.modo === "preguntas" ? String(i + 1) : e.texto.length > 16 ? e.texto.slice(0, 15) + "…" : e.texto;
                return (
                  <g key={i}>
                    <path d={camino} fill={gastado ? "#c5ccd3" : c} stroke="#fff" strokeWidth="1" />
                    {tam > 0 && (
                      <text transform={`rotate(${(i + 0.5) * seg - 90})`} x="92" y="0" textAnchor="end" dominantBaseline="central"
                        fontSize={d.modo === "preguntas" ? tam * 1.3 : tam} fontWeight="700" fill={gastado ? "#3d4a57" : "#fff"}>{etiqueta}</text>
                    )}
                  </g>
                );
              })}
              <circle r="9" fill="#fff" stroke="#14202b" strokeWidth="1.5" />
            </g>
            <polygon points="-7,-106 7,-106 0,-86" fill="#14202b" stroke="#fff" strokeWidth="1.5" />
          </svg>
        </div>
        <div className="rul-der">
          <div className="rul-res" aria-live="polite">
            {girando ? <div className="grande">Girando…</div>
              : el ? (
                <>
                  {d.modo === "preguntas" && <span className="etiqueta">Pregunta {sale! + 1}</span>}
                  <div className={"grande" + (el.texto.length > 40 ? " largo" : "")}>{el.texto}</div>
                  {el.respuesta && (verResp ? <div className="resp">{el.respuesta}</div> : <div className="rul-info">Pulsar R para ver la respuesta</div>)}
                </>
              )
              : <div className="grande" style={{ color: "var(--suave)", fontWeight: 600, fontSize: "2.2rem" }}>{agotada ? "Ya salieron todos" : "Pulsar Enter para girar"}</div>}
          </div>
          <div className="acciones">
            <button className="boton" onClick={girar} disabled={girando || agotada}>Girar (Enter)</button>
            <button className="boton sec" onClick={reiniciar} disabled={girando || salidos.size === 0}>Reiniciar (N)</button>
          </div>
          <label className="rul-info" style={{ fontSize: "1.5rem", display: "flex", gap: "0.6rem", alignItems: "center" }}>
            <input type="checkbox" checked={noRep} onChange={(e) => setNoRep(e.target.checked)} style={{ width: "1.4rem", height: "1.4rem" }} />
            No repetir (M) · quedan {disponibles.length} de {n}
          </label>
        </div>
      </div>
    </Marco>
  );
}
