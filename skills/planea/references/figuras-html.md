# Figuras con HTML y React

Crear figuras (animales, plantas, vehículos, objetos, personas, edificios, diagramas) directamente en el recurso, como apoyo visual. Son vectoriales: se imprimen nítidas a cualquier tamaño, el texto sigue siendo texto y se corrigen en la fuente.

## 1. Elegir la técnica
| Necesidad | Técnica |
| --- | --- |
| Ícono pequeño junto a un texto (categoría, instrucción, material) | Ícono de una biblioteca libre (§5) |
| Figura simple o mediana: animal, planta, auto, casa, objeto | **SVG en línea** compuesto con formas básicas (§2) |
| Diagrama científico o matemático: partes de una planta, fuerzas, figuras geométricas, plano | SVG con medidas, ejes y etiquetas exactas (§4) |
| Muchas figuras parecidas: tarjetas, fichas de juego, variantes de color o tamaño | Componente React que recibe propiedades y genera el SVG (§3) |
| Formas muy simples: círculos, insignias, flechas, marcos | CSS (`border-radius`, `clip-path`) |
| Escena detallada, realista o con mucha textura | No dibujar a mano: generar una ilustración ([diseño de recursos](diseno-recursos.md)) o usar un material existente con licencia |

## 2. Construir con formas básicas
Descomponer la figura en primitivas y ordenarlas de atrás hacia adelante:
1. **Silueta:** 2–5 formas grandes (`ellipse`, `circle`, `rect` con `rx`, `path`) que ya hagan reconocible la figura.
   - Gato = cuerpo (elipse) + cabeza (círculo) + orejas (2 triángulos) + cola (curva).
   - Árbol = tronco (rectángulo) + copa (3 círculos superpuestos).
   - Auto = carrocería (rectángulo redondeado) + cabina (trapecio) + 2 ruedas (círculos con un círculo interior).
2. **Rasgos:** ojos, ventanas, hojas, pétalos; repetir piezas con `<use>` o rotaciones (`transform="rotate(…)"`) para simetrías (flores, ruedas, estrellas).
3. **Detalle mínimo:** solo lo que ayuda a reconocer o a explicar. Menos es más legible.

Reglas de dibujo:
- `viewBox` cuadrado o proporcional (`0 0 200 200`), y medidas en ese sistema; el tamaño final lo da el CSS.
- Contorno uniforme (2–4 unidades, `stroke-linejoin="round"`, `stroke-linecap="round"`) y 2–4 colores planos de la paleta del proyecto.
- Agrupar partes con `<g id="cabeza">` para moverlas o animarlas juntas.
- Curvas con `path` (`Q`, `C`, `A`) en lugar de muchos puntos.
- Sin degradados complejos, filtros ni sombras difusas: se imprimen mal.

Ejemplo mínimo (solo para mostrar la composición):
```html
<svg viewBox="0 0 200 140" width="60mm" role="img" aria-label="Auto">
  <rect x="20" y="60" width="160" height="45" rx="14" fill="#2f6fdb" stroke="#1d1d2b" stroke-width="3"/>
  <path d="M55 60 L75 30 H135 L155 60 Z" fill="#9cc3ff" stroke="#1d1d2b" stroke-width="3"/>
  <circle cx="60" cy="108" r="18" fill="#1d1d2b"/><circle cx="60" cy="108" r="7" fill="#fff"/>
  <circle cx="145" cy="108" r="18" fill="#1d1d2b"/><circle cx="145" cy="108" r="7" fill="#fff"/>
</svg>
```

## 3. Componentes React para figuras repetidas
Usar React solo cuando la figura se repite con variaciones. El componente:
- recibe propiedades con sentido didáctico (`color`, `tamano`, `etiqueta`, `cantidad`, `estado`), no ajustes arbitrarios;
- devuelve un `<svg>` con `viewBox` fijo y `role="img"` + `aria-label`;
- vive en `Recursos/fuente/` junto al recurso, no en la skill.

Usos típicos: tarjetas de memorama (la misma silueta con distinta etiqueta), fichas de conteo y fracciones (N manzanas, pizza dividida en N partes), personajes por categoría de un juego, señales de ruta en un tablero.

## 4. Figuras didácticas exactas
Cuando la figura enseña algo, la exactitud manda sobre la estética:
- **Ciencias:** partes y proporciones correctas (planta: raíz, tallo, hoja, flor; célula; ciclo del agua), etiquetas con líneas guía que no crucen otras figuras, y la fuente consultada.
- **Matemáticas:** medidas reales a escala dentro del `viewBox` (1 unidad = 1 mm o 1 cm declarado), ángulos y lados marcados, cotas con flechas, cuadrícula si ayuda.
- **Física:** vectores con flecha y magnitud proporcional, puntos de aplicación, unidades.
- **Geografía e historia:** mapas solo de fuentes con licencia; no inventar fronteras ni ubicaciones.

Verificar cifras, nombres y proporciones antes de usar la figura. Una figura bonita pero errónea es peor que ninguna.

## 5. Bibliotecas de íconos y emoji con licencia libre
Usar el SVG descargado o copiado dentro del recurso (sin cargarlo de internet al imprimir) y respetar la licencia. Para dar acabado a un recurso con estos íconos, ver [calidad visual](calidad-visual.md).

| Biblioteca | Contenido | Licencia (verificada) | Atribución |
| --- | --- | --- | --- |
| Lucide | Íconos de línea | ISC (unos pocos íconos derivados de Feather son MIT) | Conservar el aviso de copyright y de licencia al redistribuir los archivos |
| Tabler Icons | Íconos de línea | MIT | Conservar el aviso de copyright y de licencia |
| Phosphor Icons | Íconos en varios grosores | MIT | Conservar el aviso de copyright y de licencia |
| Microsoft Fluent Emoji | Emoji planos y 3D (animales, plantas, objetos) | MIT | Conservar el aviso de copyright y de licencia |
| Noto Emoji (Google) | Emoji de colores | Fuentes: SIL OFL 1.1; herramientas y la mayoría de las imágenes: Apache 2.0; banderas: dominio público o exentas | Apache 2.0: conservar licencia y avisos; OFL: conservar su aviso si se redistribuye la fuente |
| OpenMoji | Emoji de estilo uniforme | CC BY-SA 4.0 | Obligatoria («All emojis designed by OpenMoji – the open-source emoji and icon project. License: CC BY-SA 4.0») e indicar los cambios; derivados con la misma licencia |
| Twemoji | Emoji de colores | Gráficos: CC BY 4.0; código: MIT (proyecto mantenido en `jdecked/twemoji`) | Obligatoria para los gráficos; basta una mención en créditos o «Acerca de» |

Verificado el 23/11/2026 en las páginas oficiales: [Lucide](https://lucide.dev/license), [Tabler](https://github.com/tabler/tabler-icons/blob/main/LICENSE), [Phosphor](https://github.com/phosphor-icons/core/blob/main/LICENSE), [Fluent Emoji](https://github.com/microsoft/fluentui-emoji/blob/main/LICENSE), [Noto Emoji](https://github.com/googlefonts/noto-emoji#license), [OpenMoji](https://openmoji.org/faq/) y [Twemoji](https://github.com/jdecked/twemoji#license). Las licencias MIT, ISC y Apache no piden mención visible en una hoja impresa, pero sí conservar su aviso al redistribuir los archivos; por eso se recomienda una línea de créditos al pie del recurso.

- Iconify reúne muchas colecciones; revisar la licencia de cada colección antes de usarla.
- Comprobar la licencia vigente en la página oficial al usarla; registrar la atribución en las fuentes de la planeación.
- No mezclar estilos de íconos en un mismo recurso; ajustar color y grosor a la paleta del proyecto.

## 6. Estilo y coherencia
- Seguir el [estilo visual](estilos-visuales.md) del proyecto: el arcade de personajes pide contornos gruesos y sombras duras; el gamificado amable, formas redondeadas sin contorno; las tarjetas temáticas, figuras sobrias.
- Las figuras de un proyecto comparten grosor de línea, paleta, nivel de detalle y proporción.
- Personajes propios del tema (una gota, un átomo, una semilla), nunca mascotas de marcas o personajes con derechos.

## 7. Accesibilidad e impresión
- `role="img"` y `aria-label` (o `<title>`) en cada SVG; si es decorativa, `aria-hidden="true"`.
- Distinguibles en blanco y negro: contorno, forma o patrón (`<pattern>` de rayas o puntos), no solo color.
- Tamaño mínimo para que se reconozca impresa: 15 mm para íconos, 40 mm para figuras con detalle, mayor en láminas.
- Revisar la figura en la vista previa del PDF, a tamaño real, antes de darla por buena.
