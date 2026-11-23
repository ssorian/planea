import { useState } from "react";
import { Marco, Marcador, numeroTecla, useTeclas, type Atajo } from "../comun";
import type { DatosEncuesta } from "../esquemas";

const ATAJOS: Atajo[] = [
  ["1 – 8", "Revelar la respuesta con ese número"],
  ["R", "Revelar todas las respuestas"],
  ["X / 0", "Marcar un error (máximo 3)"],
  ["←", "Dar los puntos en juego al equipo de la izquierda"],
  ["→", "Dar los puntos en juego al equipo de la derecha"],
  ["N / Enter", "Siguiente ronda (al final, ver el resultado)"],
  ["P", "Ronda anterior"],
];

type EstadoRonda = { rev: boolean[]; errores: number; asignado: number };

const IconoX = () => (
  <svg viewBox="0 0 100 100" aria-hidden="true"><path d="M14 14 L86 86 M86 14 L14 86" stroke="currentColor" strokeWidth="18" strokeLinecap="round" fill="none" /></svg>
);

export default function Encuesta({ d }: { d: DatosEncuesta }) {
  const [r, setR] = useState(0);
  const [fin, setFin] = useState(false);
  const [est, setEst] = useState<EstadoRonda[]>(() => d.rondas.map((x) => ({ rev: x.respuestas.map(() => false), errores: 0, asignado: 0 })));
  const [puntos, setPuntos] = useState([0, 0]);
  const [flash, setFlash] = useState(0);
  const [nueva, setNueva] = useState(-1);

  const ronda = d.rondas[r];
  const est1 = est[r];
  const acumulado = ronda.respuestas.reduce((s, a, i) => s + (est1.rev[i] ? a.puntos : 0), 0) * ronda.multiplicador;
  const banco = acumulado - est1.asignado;

  const cambiar = (f: (x: EstadoRonda) => EstadoRonda) => setEst((l) => l.map((x, i) => (i === r ? f(x) : x)));
  const revelar = (i: number) => {
    if (i >= ronda.respuestas.length || est1.rev[i]) return;
    setNueva(i);
    cambiar((x) => ({ ...x, rev: x.rev.map((v, j) => v || j === i) }));
  };
  const revelarTodas = () => ronda.respuestas.forEach((_, i) => revelar(i));
  const error = () => {
    if (est1.errores >= 3) return;
    cambiar((x) => ({ ...x, errores: x.errores + 1 }));
    setFlash((f) => f + 1);
  };
  const dar = (eq: number) => {
    if (banco <= 0) return;
    setPuntos((p) => p.map((v, i) => (i === eq ? v + banco : v)));
    cambiar((x) => ({ ...x, asignado: acumulado }));
  };
  const siguiente = () => {
    if (r < d.rondas.length - 1) { setR(r + 1); setNueva(-1); } else setFin(true);
  };
  const anterior = () => {
    if (fin) setFin(false);
    else if (r > 0) { setR(r - 1); setNueva(-1); }
  };

  useTeclas((ev) => {
    const n = numeroTecla(ev);
    const k = ev.key.toLowerCase();
    if (fin) {
      if (k === "p" || k === "arrowleft") anterior();
      return;
    }
    if (n !== null && n >= 1) revelar(n - 1);
    else if (n === 0 || k === "x") error();
    else if (k === "r") revelarTodas();
    else if (k === "arrowleft") dar(0);
    else if (k === "arrowright") dar(1);
    else if (k === "n" || k === "enter") siguiente();
    else if (k === "p") anterior();
    else return;
    ev.preventDefault();
  });

  if (fin) {
    const [a, b] = puntos;
    return (
      <Marco titulo={d.titulo} ejemplo={d.ejemplo} atajos={ATAJOS}>
        <div className="centro">
          <h2>Resultado final</h2>
          <p>{a === b ? "¡Empate!" : `¡Ganó ${a > b ? d.equipos[0] : d.equipos[1]}!`}</p>
          <Marcador equipos={d.equipos} puntos={puntos} />
          <p className="nota">Pulsar P para volver a la última ronda.</p>
        </div>
      </Marco>
    );
  }

  return (
    <Marco titulo={d.titulo} ejemplo={d.ejemplo} atajos={ATAJOS}>
      <div className="enc-pregunta">
        <small>
          Ronda {r + 1} de {d.rondas.length}
          {ronda.multiplicador > 1 && <span className="doble">Puntos ×{ronda.multiplicador}</span>}
        </small>
        {ronda.pregunta}
      </div>
      <div className="enc-lista" style={{ gridTemplateRows: `repeat(${Math.ceil(ronda.respuestas.length / 2)}, 1fr)` }}>
        {ronda.respuestas.map((a, i) => (
          <button key={r + "-" + i} className={"enc-resp " + (est1.rev[i] ? (nueva === i ? "nueva" : "") : "oculta")} onClick={() => revelar(i)} aria-label={est1.rev[i] ? `${a.texto}, ${a.puntos * ronda.multiplicador} puntos` : `Respuesta ${i + 1} oculta`}>
            <span className="num">{i + 1}</span>
            <span className="texto">{est1.rev[i] ? a.texto : ""}</span>
            <span className="pts">{a.puntos * ronda.multiplicador}</span>
          </button>
        ))}
      </div>
      <div className="enc-medio">
        <div className="enc-fallos" aria-label={`Errores: ${est1.errores} de 3`}>
          {[0, 1, 2].map((i) => <div key={i} className={"fallo" + (i < est1.errores ? "" : " vacio")}><IconoX /></div>)}
        </div>
        <button className="boton sec" onClick={error} disabled={est1.errores >= 3}>Error (X)</button>
        <div className="enc-banco"><span className="etiqueta">Puntos en juego</span><b>{banco}</b></div>
        <button className="boton sec" onClick={revelarTodas}>Revelar todas (R)</button>
        <button className="boton" onClick={siguiente}>{r < d.rondas.length - 1 ? "Siguiente ronda (N)" : "Ver resultado (N)"}</button>
      </div>
      <Marcador equipos={d.equipos} puntos={puntos} onClic={dar} ayudaClic="Dar los puntos en juego a este equipo" />
      <div className="acciones"><span className="nota" style={{ margin: 0 }}>Clic en un equipo (o ← →) para darle los puntos en juego</span></div>
      {flash > 0 && (
        <div className="x-flash" key={flash}>{Array.from({ length: est1.errores }, (_, i) => <IconoX key={i} />)}</div>
      )}
    </Marco>
  );
}
