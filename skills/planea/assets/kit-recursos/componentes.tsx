import type { ReactNode } from "react";

// Componentes reutilizables para recursos imprimibles. Todo el texto entra por props:
// el kit no inventa contenidos, criterios ni respuestas.

export function Hoja({ children }: { children: ReactNode }) {
  return <section className="hoja">{children}</section>;
}

export function Encabezado({ titulo, campo, grado, anexo }: { titulo: string; campo?: string; grado?: string; anexo?: string }) {
  return (
    <header className="encabezado">
      <h1>{titulo}</h1>
      <div className="meta">
        {anexo && <div>{anexo}</div>}
        {campo && <div>{campo}</div>}
        {grado && <div>{grado}</div>}
      </div>
    </header>
  );
}

export function CamposAlumno({ campos = ["Nombre", "Grupo", "Fecha"] }: { campos?: string[] }) {
  return (
    <div className="campos-alumno">
      {campos.map((c) => <div key={c}>{c}:</div>)}
    </div>
  );
}

export function Consigna({ children }: { children: ReactNode }) {
  return <p className="consigna">{children}</p>;
}

export function Credito({ children }: { children: ReactNode }) {
  return <p className="credito">{children}</p>;
}

export type CriterioRubrica = { criterio: string; pda?: string; descriptores: string[] };

export function Rubrica({ niveles = ["Destacado", "Satisfactorio", "En proceso", "Requiere apoyo"], criterios, puntajes }: { niveles?: string[]; criterios: CriterioRubrica[]; puntajes?: number[] }) {
  for (const c of criterios) {
    if (c.descriptores.length !== niveles.length) throw new Error(`Criterio "${c.criterio}": ${c.descriptores.length} descriptores para ${niveles.length} niveles`);
  }
  if (puntajes && puntajes.length !== niveles.length) throw new Error("puntajes debe tener un valor por nivel");
  return (
    <table>
      <thead>
        <tr>
          <th style={{ width: "22%" }}>Criterio</th>
          {niveles.map((n, i) => <th key={n}>{n}{puntajes ? ` (${puntajes[i]})` : ""}</th>)}
        </tr>
      </thead>
      <tbody>
        {criterios.map((c) => (
          <tr key={c.criterio}>
            <td className="criterio">{c.criterio}{c.pda && <span className="pda">{c.pda}</span>}</td>
            {c.descriptores.map((d, i) => <td key={i}>{d}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function ListaCotejo({ indicadores, columnas = ["Sí", "No"] }: { indicadores: { texto: string; pda?: string }[]; columnas?: string[] }) {
  return (
    <table>
      <thead>
        <tr><th style={{ width: "6%" }}>#</th><th>Indicador</th>{columnas.map((c) => <th key={c} className="casilla">{c}</th>)}<th style={{ width: "26%" }}>Observaciones</th></tr>
      </thead>
      <tbody>
        {indicadores.map((ind, i) => (
          <tr key={i}>
            <td>{i + 1}</td>
            <td>{ind.texto}{ind.pda && <span className="pda">{ind.pda}</span>}</td>
            {columnas.map((c) => <td key={c} className="casilla"></td>)}
            <td></td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function EscalaEstimativa({ conductas, valores = ["Siempre", "Casi siempre", "A veces", "Nunca"] }: { conductas: string[]; valores?: string[] }) {
  return (
    <table>
      <thead><tr><th>Conducta</th>{valores.map((v) => <th key={v} className="casilla">{v}</th>)}</tr></thead>
      <tbody>{conductas.map((c) => <tr key={c}><td>{c}</td>{valores.map((v) => <td key={v} className="casilla"></td>)}</tr>)}</tbody>
    </table>
  );
}

export type Reactivo =
  | { tipo: "opcion"; base: string; opciones: string[]; correcta: number; bloom?: string }
  | { tipo: "abierta"; base: string; renglones?: number; criterio: string; bloom?: string }
  | { tipo: "relacion"; base: string; izquierda: string[]; derecha: string[]; clave: string; bloom?: string };

const LETRAS = "abcdefgh";

export function Examen({ reactivos }: { reactivos: Reactivo[] }) {
  return (
    <div>
      {reactivos.map((r, i) => (
        <div className="reactivo" key={i}>
          <div className="base"><strong>{i + 1}.</strong> {r.base}</div>
          {r.tipo === "opcion" && (
            <ul className="opciones">{r.opciones.map((o, j) => <li key={j}>{LETRAS[j]}) {o}</li>)}</ul>
          )}
          {r.tipo === "abierta" && (
            <div className="renglones">{Array.from({ length: r.renglones ?? 3 }, (_, j) => <div key={j}></div>)}</div>
          )}
          {r.tipo === "relacion" && (
            <table><tbody>{r.izquierda.map((iz, j) => (
              <tr key={j}><td style={{ width: "8%" }}>(  )</td><td>{iz}</td><td>{LETRAS[j]}) {r.derecha[j] ?? ""}</td></tr>
            ))}</tbody></table>
          )}
        </div>
      ))}
    </div>
  );
}

// Clave para el docente: se renderiza en un archivo separado del examen del alumnado.
export function ClaveExamen({ reactivos }: { reactivos: Reactivo[] }) {
  return (
    <table>
      <thead><tr><th>#</th><th>Respuesta o criterio</th><th>Nivel de Bloom</th></tr></thead>
      <tbody>{reactivos.map((r, i) => (
        <tr key={i}>
          <td>{i + 1}</td>
          <td>{r.tipo === "opcion" ? `${LETRAS[r.correcta]}) ${r.opciones[r.correcta]}` : r.tipo === "abierta" ? r.criterio : r.clave}</td>
          <td>{r.bloom ?? ""}</td>
        </tr>
      ))}</tbody>
    </table>
  );
}

export function Retroalimentacion({ etiqueta = "Retroalimentación" }: { etiqueta?: string }) {
  return <div className="retro">{etiqueta}:</div>;
}

export function Figura({ src, pie }: { src: string; pie?: string }) {
  return <figure><img src={src} alt={pie ?? ""} />{pie && <figcaption>{pie}</figcaption>}</figure>;
}
