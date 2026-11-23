// Ejemplo de estructura. Los textos son ilustrativos: en una planeación real deben
// derivarse de los PDA del proyecto, no copiarse de aquí.
import { Hoja, Encabezado, CamposAlumno, Consigna, Rubrica, Retroalimentacion, Credito, ListaCotejo } from "../componentes";

export const meta = { nombre: "ejemplo-rubrica", pagina: "letter landscape" };

export default function Recurso() {
  return (
    <>
      <Hoja>
        <Encabezado titulo="Rúbrica del guion teatral" campo="Lenguajes" grado="2.º grado" anexo="Anexo 00 (ejemplo)" />
        <CamposAlumno campos={["Equipo", "Grupo", "Fecha"]} />
        <Consigna>Revisar el guion con esta rúbrica antes del ensayo general y marcar el nivel alcanzado en cada criterio.</Consigna>
        <Rubrica
          criterios={[
            { criterio: "Adaptación del relato", pda: "ESP 6.1", descriptores: [
              "Conserva el conflicto y el sentido del relato y los transforma en escenas con una progresión clara.",
              "Conserva el conflicto y el sentido del relato y los organiza en escenas.",
              "Conserva parte del relato, pero las escenas no muestran el conflicto completo.",
              "Copia el relato narrado sin organizarlo en escenas." ] },
            { criterio: "Acotaciones de voz y cuerpo", pda: "ART 6.1", descriptores: [
              "Todas las escenas tienen acotaciones precisas de tono, ritmo y movimiento que refuerzan la emoción.",
              "Cada escena tiene acotaciones de tono y movimiento comprensibles.",
              "Algunas escenas tienen acotaciones, pero son generales.",
              "No incluye acotaciones." ] },
          ]}
        />
        <Retroalimentacion />
        <Credito>Elaboración propia con apoyo de IA.</Credito>
      </Hoja>
      <Hoja>
        <Encabezado titulo="Lista de cotejo del guion" campo="Lenguajes" grado="2.º grado" anexo="Anexo 00 (ejemplo)" />
        <ListaCotejo indicadores={[
          { texto: "Incluye encabezado de escena con lugar y momento." },
          { texto: "Escribe el nombre del personaje antes de cada diálogo." },
          { texto: "Usa paréntesis para las acotaciones." },
        ]} />
      </Hoja>
    </>
  );
}
