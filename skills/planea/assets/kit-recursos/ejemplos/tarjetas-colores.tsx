// Hoja imprimible con las tarjetas A–D para los juegos «Tarjetas de colores» (quiz sin celulares).
// Cada tarjeta lleva color + letra + figura, así se distingue aunque se imprima en blanco y negro
// o el alumno no distinga colores. Imprimir una hoja por alumno (o por pareja) y recortar.
// Los colores y figuras coinciden con los del juego digital (assets/kit-juegos).
import { Hoja, Encabezado, Consigna, Credito } from "../componentes";

export const meta = { nombre: "tarjetas-colores", pagina: "letter" };

const TARJETAS = [
  { letra: "A", color: "#c8372d", tinta: "#ffffff", nombre: "Rojo · triángulo", forma: <polygon points="50,10 94,88 6,88" /> },
  { letra: "B", color: "#1f5fae", tinta: "#ffffff", nombre: "Azul · círculo", forma: <circle cx="50" cy="50" r="42" /> },
  { letra: "C", color: "#f2b800", tinta: "#14202b", nombre: "Amarillo · cuadrado", forma: <rect x="12" y="12" width="76" height="76" /> },
  { letra: "D", color: "#2a7d4f", tinta: "#ffffff", nombre: "Verde · rombo", forma: <polygon points="50,6 92,50 50,94 8,50" /> },
];

const css = `
.tarjetas { width: calc(100% - 1px); display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
.corte { border: 0.4mm dashed #52606d; padding: 3mm; }
.tarjeta { height: 90mm; border-radius: 5mm; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1mm; }
.tarjeta svg { width: 34mm; height: 34mm; fill: currentColor; }
.tarjeta .letra { font-size: 100pt; font-weight: 800; line-height: 1; }
.tarjeta .nombre { font-size: 10pt; font-weight: 700; letter-spacing: 0.03em; }
`;

export default function Recurso() {
  return (
    <Hoja>
      <style>{css}</style>
      <Encabezado titulo="Tarjetas de respuesta A, B, C y D" campo="Juego «Tarjetas de colores»" anexo="Anexo 00 (ejemplo)" />
      <Consigna>Recortar por las líneas punteadas. Al contar tres, levantar la tarjeta de la respuesta elegida.</Consigna>
      <div className="tarjetas">
        {TARJETAS.map((t) => (
          <div className="corte" key={t.letra}>
            <div className="tarjeta" style={{ background: t.color, color: t.tinta }}>
              <svg viewBox="0 0 100 100" aria-hidden="true">{t.forma}</svg>
              <div className="letra">{t.letra}</div>
              <div className="nombre">{t.nombre}</div>
            </div>
          </div>
        ))}
      </div>
      <Credito>Elaboración propia con apoyo de IA.</Credito>
    </Hoja>
  );
}
