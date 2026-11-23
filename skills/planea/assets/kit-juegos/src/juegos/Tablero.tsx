import { useState } from "react";
import { Marco, Marcador, numeroTecla, useTeclas, type Atajo } from "../comun";
import type { DatosTablero } from "../esquemas";

const ATAJOS: Atajo[] = [
  ["← ↑ → ↓", "Mover el cursor por el tablero"],
  ["Enter / Espacio", "Abrir la celda; ya abierta, revelar la respuesta"],
  ["1 – 4", "Dar los puntos al equipo con ese número y cerrar la celda"],
  ["Mayús + 1 – 4", "Restar los puntos a ese equipo y cerrar la celda"],
  ["0", "Cerrar la celda sin dar puntos (queda usada)"],
  ["Esc", "Cerrar la celda sin usarla"],
];

export default function Tablero({ d }: { d: DatosTablero }) {
  const nc = d.categorias.length;
  const nf = d.categorias[0].preguntas.length;
  const [usadas, setUsadas] = useState<Set<string>>(new Set());
  const [puntos, setPuntos] = useState<number[]>(d.equipos.map(() => 0));
  const [cur, setCur] = useState({ c: 0, f: 0 });
  const [abierta, setAbierta] = useState<{ c: number; f: number } | null>(null);
  const [resp, setResp] = useState(false);

  const q = abierta ? d.categorias[abierta.c].preguntas[abierta.f] : null;
  const abrir = (c: number, f: number) => { setCur({ c, f }); setAbierta({ c, f }); setResp(false); };
  const cerrar = (eq: number | null, signo = 1) => {
    if (!abierta || !q) return;
    if (eq !== null) setPuntos((p) => p.map((v, i) => (i === eq ? v + signo * q.valor : v)));
    setUsadas((u) => new Set(u).add(`${abierta.c}-${abierta.f}`));
    setAbierta(null);
  };

  useTeclas((ev) => {
    const k = ev.key.toLowerCase();
    if (abierta) {
      const n = numeroTecla(ev);
      if (k === "escape") setAbierta(null);
      else if (k === "enter" || k === " " || k === "r") setResp(true);
      else if (n === 0) cerrar(null);
      else if (n !== null && n <= d.equipos.length) cerrar(n - 1, ev.shiftKey ? -1 : 1);
      else return;
      ev.preventDefault();
      return;
    }
    if (k === "arrowleft") setCur((c) => ({ ...c, c: Math.max(0, c.c - 1) }));
    else if (k === "arrowright") setCur((c) => ({ ...c, c: Math.min(nc - 1, c.c + 1) }));
    else if (k === "arrowup") setCur((c) => ({ ...c, f: Math.max(0, c.f - 1) }));
    else if (k === "arrowdown") setCur((c) => ({ ...c, f: Math.min(nf - 1, c.f + 1) }));
    else if (k === "enter" || k === " ") abrir(cur.c, cur.f);
    else return;
    ev.preventDefault();
  });

  return (
    <Marco titulo={d.titulo} ejemplo={d.ejemplo} atajos={ATAJOS}>
      <div className="tab-rejilla" style={{ gridTemplateColumns: `repeat(${nc}, 1fr)`, gridTemplateRows: `auto repeat(${nf}, 1fr)` }}>
        {d.categorias.map((c, i) => <div key={i} className="tab-cat">{c.nombre}</div>)}
        {Array.from({ length: nf }, (_, f) =>
          d.categorias.map((c, ci) => {
            const usada = usadas.has(`${ci}-${f}`);
            return (
              <button key={`${ci}-${f}`} className={"tab-celda" + (usada ? " usada" : "") + (cur.c === ci && cur.f === f ? " cursor" : "")}
                onClick={() => abrir(ci, f)} aria-label={`${c.nombre}, ${c.preguntas[f].valor} puntos${usada ? ", usada" : ""}`}>
                {usada ? "·" : c.preguntas[f].valor}
              </button>
            );
          }))}
      </div>
      <Marcador equipos={d.equipos} puntos={puntos} />
      {abierta && q && (
        <div className="modal">
          <div className="modal-caja">
            <div className="meta">{d.categorias[abierta.c].nombre} · {q.valor} puntos</div>
            <div className="modal-pregunta">{q.pregunta}</div>
            <div className={"modal-respuesta" + (resp ? "" : " oculta")}>{resp ? q.respuesta : "Respuesta oculta: pulsar Enter para revelarla"}</div>
            <div className="asignar">
              <span className="etiqueta">Dar {q.valor} puntos a:</span>
              {d.equipos.map((e, i) => <button key={i} className="boton" onClick={() => cerrar(i)}>{i + 1} · {e}</button>)}
              <button className="boton sec" onClick={() => cerrar(null)}>0 · Nadie</button>
              <button className="boton sec" onClick={() => setAbierta(null)}>Esc · Cerrar</button>
            </div>
            {!resp && <div className="acciones"><button className="boton" onClick={() => setResp(true)}>Revelar respuesta</button></div>}
          </div>
        </div>
      )}
    </Marco>
  );
}
