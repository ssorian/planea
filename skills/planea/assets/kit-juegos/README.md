# Kit de minijuegos para proyectar (React + Vite → un solo HTML)

Cuatro juegos de aula con nombres y aspecto propios. Cada juego se construye como **un único archivo HTML** que funciona con doble clic, sin internet y sin instalar nada en la computadora del aula. El kit no trae contenido curricular: las preguntas y respuestas salen de un archivo JSON que se prepara para cada sesión.

| Juego | Qué es | Ejemplo de datos |
| --- | --- | --- |
| `encuesta` | «La comunidad opina»: pregunta con respuestas ocultas que valen puntos, 3 errores, dos equipos | `ejemplos/encuesta.json` |
| `tarjetas` | «Tarjetas de colores»: quiz sin celulares; el grupo responde con tarjetas A–D | `ejemplos/tarjetas.json` |
| `tablero` | «Tablero de categorías»: categorías × valores, celdas que se atenúan al usarse | `ejemplos/tablero.json` |
| `ruleta` | «Ruleta»: sorteo de nombres o preguntas, con o sin repetición | `ejemplos/ruleta.json`, `ejemplos/ruleta-preguntas.json` |

Los archivos de `ejemplos/` tienen `"ejemplo": true`: el juego muestra la insignia «EJEMPLO · contenido ilustrativo». Son solo para probar el kit; no usarlos con el grupo.

## Requisitos
- `bun` (para construir). Las dependencias ya están en `node_modules`; si falta la carpeta, `bun install` necesita internet y permiso.
- Para **jugar**: solo un navegador (Edge, Chrome, Firefox o Chromium). En Windows, abrir el `.html` con doble clic en Edge o Chrome. Sin internet, sin sonido.
- Para **capturas** (opcional): Chromium, Chrome o Edge. Si no se detectan solos, indicar la ruta con la variable de entorno `PLANEA_NAVEGADOR`.
  - Linux/macOS: `PLANEA_NAVEGADOR=/ruta/al/navegador bun capturar.ts ...`
  - Windows (PowerShell): `$env:PLANEA_NAVEGADOR = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"`

## Construir un juego
```
bun ~/.pi/agent/skills/planea/assets/kit-juegos/construir.ts <juego> <datos.json> <salida.html>
```
- Funciona desde cualquier carpeta; `datos.json` y `salida.html` se leen y escriben relativos a la carpeta donde se ejecuta el comando. Si `salida` es una carpeta existente, el archivo se llama `<juego>.html`.
- Antes de construir valida el JSON contra el esquema del juego. Si hay errores, los lista en español con la ruta exacta (por ejemplo `rondas[1].respuestas: debe tener entre 4 y 8 elementos (tiene 3)`) y no genera el archivo.
- Compatible con Windows: solo usa rutas y archivos de Node, sin comandos de shell de Unix.
- Los textos del JSON se muestran como texto plano (no se interpreta HTML).

Ejemplo (en la carpeta del proyecto):
```
bun ~/.pi/agent/skills/planea/assets/kit-juegos/construir.ts tarjetas Recursos/fuente/anexo-05-datos.json Recursos/anexo-05-juego-tarjetas.html
```

## Captura de pantalla (vista previa para el anexo)
```
bun ~/.pi/agent/skills/planea/assets/kit-juegos/capturar.ts <juego.html> <captura.png> [--teclas "1,2,x"] [--ancho 1600] [--alto 900] [--espera ms]
```
`--teclas` simula pulsaciones antes de capturar (separadas por comas: `1`, `x`, `Enter`, `Space`, `ArrowRight`, `Shift+1`…), por ejemplo `--teclas "Enter,Enter"` en `tarjetas` para mostrar la respuesta revelada. Con la ruleta, agregar `--espera 6000` para que termine el giro. Revisar la imagen antes de usarla.

## Controles comunes
| Tecla | Acción |
| --- | --- |
| `F` | Pantalla completa |
| `H` o `?` | Ayuda con todos los atajos del juego (también se cierra con `Esc`) |

Todo se puede hacer también con ratón o pantalla táctil. Cada juego incluye su lista de atajos en la ayuda (`H`).

## Encuesta («La comunidad opina»)
```json
{
  "ejemplo": false,
  "titulo": "Texto de la barra superior",
  "equipos": ["Equipo A", "Equipo B"],
  "rondas": [
    {
      "pregunta": "Enunciado que se lee al grupo",
      "multiplicador": 1,
      "respuestas": [ { "texto": "Respuesta", "puntos": 30 } ]
    }
  ]
}
```
- `titulo` obligatorio. `equipos` opcional: exactamente 2 nombres.
- `rondas`: de 1 a 30. Cada una con `pregunta` y de **4 a 8** `respuestas`; `puntos` es entero de 1 a 100. `multiplicador` (1–3, por defecto 1) hace valer doble o triple.
- Las respuestas se muestran en el orden escrito; conviene ordenarlas de mayor a menor puntaje.

| Tecla | Acción |
| --- | --- |
| `1`–`8` | Revelar esa respuesta |
| `R` | Revelar todas |
| `X` o `0` | Marcar error (máximo 3, aparece una X grande) |
| `←` / `→` | Dar los puntos en juego al equipo izquierdo / derecho (o clic en el equipo) |
| `N` o `Enter` | Siguiente ronda; tras la última, resultado final |
| `P` | Ronda anterior |

## Tarjetas («Tarjetas de colores»)
```json
{
  "ejemplo": false,
  "titulo": "Texto de la barra superior",
  "segundos": 20,
  "preguntas": [
    {
      "pregunta": "Enunciado",
      "opciones": ["Opción A", "Opción B", "Opción C", "Opción D"],
      "correcta": "B",
      "tema": "Tema para el resumen",
      "explicacion": "Comentario opcional que se muestra al revelar"
    }
  ]
}
```
- `segundos` opcional (5–600); sin él no hay temporizador. `preguntas`: de 1 a 50, con **2 a 4** `opciones`. `correcta` es la letra `"A"`–`"D"`. `tema` y `explicacion` son opcionales.
- Cada opción lleva color, letra y figura: **A rojo triángulo, B azul círculo, C amarillo cuadrado, D verde rombo**. El grupo usa las tarjetas impresas de `../kit-recursos/ejemplos/tarjetas-colores.tsx`.
- Flujo: se lee la pregunta, el grupo levanta tarjetas, el docente revela la respuesta, cuenta las tarjetas correctas y las anota en «¿Cuántos acertaron?». En la pantalla inicial o en el resumen se escribe cuántos alumnos responden.
- El resumen final muestra el porcentaje por pregunta, marca «Reforzar» por debajo de 60 % y agrupa por `tema` para detectar qué retomar.

| Tecla | Acción |
| --- | --- |
| `Enter` / `Espacio` | Empezar; revelar la respuesta; siguiente pregunta |
| `R` | Revelar la respuesta |
| `T` | Pausar o reanudar el temporizador |
| `→` / `←` | Siguiente / anterior |
| `S` | Ir al resumen |
| `O` | En el resumen, ordenar por menor acierto |

## Tablero («Tablero de categorías»)
```json
{
  "ejemplo": false,
  "titulo": "Texto de la barra superior",
  "equipos": ["Equipo 1", "Equipo 2"],
  "categorias": [
    {
      "nombre": "Categoría",
      "preguntas": [ { "valor": 100, "pregunta": "Enunciado", "respuesta": "Respuesta" } ]
    }
  ]
}
```
- `equipos` opcional: de 2 a 4. `categorias`: de 2 a 6 columnas; cada una con de 2 a 6 `preguntas` (filas) y **todas con el mismo número**. `valor` es un entero positivo.

| Tecla | Acción |
| --- | --- |
| `←` `↑` `→` `↓` | Mover el cursor |
| `Enter` / `Espacio` | Abrir la celda; ya abierta, revelar la respuesta |
| `1`–`4` | Dar los puntos a ese equipo y cerrar (la celda queda atenuada) |
| `Mayús` + `1`–`4` | Restar los puntos a ese equipo |
| `0` | Cerrar sin dar puntos (queda usada) |
| `Esc` | Cerrar sin usar la celda |

## Ruleta
```json
{
  "ejemplo": false,
  "titulo": "Texto de la barra superior",
  "modo": "nombres",
  "noRepetir": true,
  "elementos": ["Ana", "Beto", { "texto": "¿Pregunta?", "respuesta": "Respuesta opcional" }]
}
```
- `modo`: `"nombres"` (por defecto; el sector muestra el texto) o `"preguntas"` (el sector muestra el número y el texto completo aparece al lado). `noRepetir` (por defecto `true`). `elementos`: de 2 a 60, texto simple u objeto con `texto` y `respuesta`.
- Con más de 30 elementos los sectores no llevan texto; el resultado se lee en el recuadro grande.
- El sorteo usa números aleatorios del navegador; el giro es animado y respeta la opción de movimiento reducido del sistema.

| Tecla | Acción |
| --- | --- |
| `Enter` / `Espacio` | Girar |
| `R` | Mostrar la respuesta del elemento |
| `M` | Activar o desactivar «no repetir» |
| `N` | Reiniciar (vuelven a entrar todos) |

## Diseño y límites
- Texto grande (el tamaño escala con la pantalla), alto contraste, sin sonidos y sin recursos externos: cada HTML pesa unos 250 KB porque incluye React.
- Todo el estado vive en la página: al recargar se reinicia el juego. Los puntajes no se guardan.
- Los nombres, colores y tableros son originales del kit; no usar logotipos, música ni nombres comerciales de otros juegos al nombrar o adaptar los materiales.
