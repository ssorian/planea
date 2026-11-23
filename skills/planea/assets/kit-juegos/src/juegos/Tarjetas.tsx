import { useEffect, useRef, useState } from "react";
import { Forma, Marco, OPCIONES, useTeclas, type Atajo } from "../comun";
import type { DatosTarjetas } from "../esquemas";

const ATAJOS: Atajo[] = [
  ["Enter / Espacio", "Empezar; revelar la respuesta; pasar a la siguiente pregunta"],
  ["R", "Revelar la respuesta correcta"],
  ["T", "Pausar o reanudar el temporizador"],
  ["→", "Siguiente pregunta (la última lleva al resumen)"],
  ["←", "Pregunta anterior"],
  ["S", "Ir al resumen final"],
  ["O", "En el resumen: ordenar por menor acierto"],
];

const UMBRAL = 60; // % de acierto por debajo del cual se sugiere reforzar

export default function Tarjetas({ d }: { d: DatosTarjetas }) {
  const n = d.preguntas.length;
  const [fase, setFase] = useState<"intro" | "juego" | "fin">("intro");
  const [i, setI] = useState(0);
  const [reveladas, setReveladas] = useState<boolean[]>(() => d.preguntas.map(() => false));
  const [aciertos, setAciertos] = useState<(number | null)[]>(() => d.preguntas.map(() => null));
  const [total, setTotal] = useState<number | null>(null);
  const [resta, setResta] = useState(d.segundos);
  const [corre, setCorre] = useState(false);
  const [ordenar, setOrdenar] = useState(false);
  const campo = useRef<HTMLInputElement>(null);

  const p = d.preguntas[i];
  const revelada = reveladas[i];

  // El temporizador arranca solo en cada pregunta que aún no se ha revelado.
  useEffect(() => {
    if (fase !== "juego" || !d.segundos || reveladas[i]) { setCorre(false); return; }
    setResta(d.segundos);
    setCorre(true);
  }, [fase, i]);
  useEffect(() => {
    if (!corre) return;
    const t = setInterval(() => setResta((s) => (s > 0 ? s - 1 : 0)), 1000);
    return () => clearInterval(t);
  }, [corre]);
  useEffect(() => { if (resta === 0) setCorre(false); }, [resta]);
  useEffect(() => { if (revelada && fase === "juego") campo.current?.focus(); }, [revelada, i, fase]);

  const revelar = () => { setReveladas((l) => l.map((v, j) => v || j === i)); setCorre(false); };
  const siguiente = () => { if (i < n - 1) setI(i + 1); else setFase("fin"); };
  const anterior = () => { if (fase === "fin") setFase("juego"); else if (i > 0) setI(i - 1); };

  useTeclas((ev) => {
    const k = ev.key.toLowerCase();
    if (fase === "intro") {
      if (k === "enter" || k === " ") { setFase("juego"); ev.preventDefault(); }
      return;
    }
    if (fase === "fin") {
      if (k === "o") setOrdenar((o) => !o);
      else if (k === "arrowleft" || k === "p") anterior();
      return;
    }
    if (k === "enter" || k === " ") { if (revelada) siguiente(); else revelar(); }
    else if (k === "r") revelar();
    else if (k === "t" && d.segundos && !revelada) setCorre((c) => (resta > 0 ? !c : false));
    else if (k === "arrowright") siguiente();
    else if (k === "arrowleft") anterior();
    else if (k === "s") setFase("fin");
    else return;
    ev.preventDefault();
  });

  const campoTotal = (
    <label className="tar-anota">
      Alumnos que responden:
      <input className="campo" type="number" min={1} max={99} value={total ?? ""} onChange={(e) => setTotal(e.target.value === "" ? null : Math.max(1, Number(e.target.value)))} />
    </label>
  );

  if (fase === "intro") {
    return (
      <Marco titulo={d.titulo} ejemplo={d.ejemplo} atajos={ATAJOS}>
        <div className="centro">
          <h2>Tarjetas de colores</h2>
          <p>Cada alumno tiene sus tarjetas <b>A, B, C y D</b>. Se lee la pregunta; al contar tres, todos levantan a la vez la tarjeta de su respuesta.</p>
          <p>{n} pregunta{n === 1 ? "" : "s"}{d.segundos ? ` · ${d.segundos} segundos por pregunta` : " · sin temporizador"}</p>
          {campoTotal}
          <p className="nota">Escribir el total ayuda a calcular el porcentaje de acierto en el resumen final.</p>
          <div className="acciones"><button className="boton" onClick={() => setFase("juego")}>Empezar (Enter)</button></div>
        </div>
      </Marco>
    );
  }

  if (fase === "fin") {
    const filas = d.preguntas.map((q, j) => {
      const a = aciertos[j];
      const pct = a !== null && total ? Math.min(100, Math.round((a / total) * 100)) : null;
      return { j, q, a, pct };
    });
    const orden = ordenar ? [...filas].sort((x, y) => (x.pct ?? 101) - (y.pct ?? 101)) : filas;
    const temas = new Map<string, { a: number; t: number }>();
    for (const f of filas) {
      if (!f.q.tema || f.a === null || !total) continue;
      const x = temas.get(f.q.tema) ?? { a: 0, t: 0 };
      temas.set(f.q.tema, { a: x.a + Math.min(f.a, total), t: x.t + total });
    }
    const porTema = [...temas.entries()].map(([t, v]) => ({ t, pct: Math.round((v.a / v.t) * 100) }));
    const debiles = porTema.filter((x) => x.pct < UMBRAL);
    return (
      <Marco titulo={d.titulo} ejemplo={d.ejemplo} atajos={ATAJOS}>
        <div className="tar-cab">
          <h2 style={{ margin: 0, fontSize: "2.2rem", color: "var(--acento-osc)" }}>Resumen: ¿qué reforzar?</h2>
          <div style={{ marginLeft: "auto" }}>{campoTotal}</div>
          <button className="boton sec" onClick={() => setOrdenar((o) => !o)}>{ordenar ? "Orden original (O)" : "Menor acierto primero (O)"}</button>
        </div>
        <div className="temas">
          {!total ? <span>Escribir el total de alumnos para calcular porcentajes.</span>
            : porTema.length === 0 ? <span>Sin temas con datos. Anotar los aciertos y usar el campo «tema» en las preguntas.</span>
            : <><b>Temas a reforzar (menos de {UMBRAL} %):</b>{debiles.length ? debiles.map((x) => <span key={x.t} className="chip">{x.t} · {x.pct} %</span>) : <span className="chip ok">Ninguno por debajo de {UMBRAL} %</span>}</>}
        </div>
        <div className="resumen">
          <table>
            <thead><tr><th>#</th><th>Pregunta</th><th>Tema</th><th>Acertaron</th><th>Porcentaje</th><th></th></tr></thead>
            <tbody>
              {orden.map(({ j, q, a, pct }) => (
                <tr key={j}>
                  <td>{j + 1}</td>
                  <td>{q.pregunta}</td>
                  <td>{q.tema}</td>
                  <td>{a === null ? "—" : total ? `${a} de ${total}` : a}</td>
                  <td>{pct === null ? "—" : <><span className="barra-pct"><i style={{ width: pct + "%" }} /></span>{pct} %</>}</td>
                  <td>{pct !== null && pct < UMBRAL && <span className="reforzar">Reforzar</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="acciones"><button className="boton sec" onClick={anterior}>Volver a las preguntas (←)</button></div>
      </Marco>
    );
  }

  return (
    <Marco titulo={d.titulo} ejemplo={d.ejemplo} atajos={ATAJOS}>
      <div className="tar-cab">
        <span className="cuenta">Pregunta {i + 1} de {n}</span>
        {p.tema && <span className="etiqueta">{p.tema}</span>}
        {d.segundos > 0 && !revelada && <div className={"tar-tiempo" + (resta === 0 ? " fin" : "")} role="timer">{resta === 0 ? "¡Tiempo!" : resta}</div>}
      </div>
      <div className="tar-pregunta">{p.pregunta}</div>
      <div className="tar-opciones">
        {p.opciones.map((t, j) => {
          const o = OPCIONES[j];
          const cls = "tar-op" + (revelada ? (j === p.correcta ? " correcta" : " apagada") : "");
          return (
            <div key={j} className={cls} style={{ borderColor: o.color }}>
              <div className="ficha" style={{ background: o.color, color: o.texto }} title={o.nombre}>
                <Forma i={j} tam="2.6rem" />{o.letra}
              </div>
              <div className="txt">{t}</div>
              {revelada && j === p.correcta && <span className="marca">✓ Correcta</span>}
            </div>
          );
        })}
      </div>
      {revelada ? (
        <>
          {p.explicacion && <div className="tar-expl">{p.explicacion}</div>}
          <label className="tar-anota">
            ¿Cuántos acertaron?
            <input ref={campo} className="campo" type="number" min={0} max={99} value={aciertos[i] ?? ""}
              onChange={(e) => setAciertos((l) => l.map((v, j) => (j === i ? (e.target.value === "" ? null : Math.max(0, Number(e.target.value))) : v)))}
              onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); siguiente(); } else if (e.key === "Escape") (e.target as HTMLInputElement).blur(); }} />
            {total ? `de ${total}` : ""}
            <button className="boton" onClick={siguiente}>{i < n - 1 ? "Siguiente (Enter)" : "Ver resumen (Enter)"}</button>
          </label>
        </>
      ) : (
        <div className="acciones">
          {i > 0 && <button className="boton sec" onClick={anterior}>← Anterior</button>}
          <button className="boton" onClick={revelar}>Revelar respuesta (Enter)</button>
        </div>
      )}
    </Marco>
  );
}
