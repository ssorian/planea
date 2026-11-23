# Recursos: React → PDF

## Elegir cómo producir cada recurso
| Recurso | Producción |
| --- | --- |
| Material existente adecuado (video, lámina oficial, interactivo) | Usarlo según [materiales existentes](materiales-existentes.md) |
| Texto exacto: fichas, hojas de trabajo, rúbricas, listas, exámenes, tarjetas, guías de entrevista, organizadores | Kit React → PDF |
| Ilustración, escena, personaje, portada o portadilla | `openai_image`, y el resultado se inserta en el recurso con `Figura` si lleva texto |
| Juego (diseño, impreso o proyectado) | [juegos didácticos](juegos-didacticos.md) |
| Lectura extensa | Kit React → PDF con texto maquetado, nunca como imagen |

No generar con `openai_image` imágenes que contengan mucho texto: las letras salen con errores. El texto va en el kit y la ilustración en la imagen.

## Flujo
1. Seguir [el README del kit](../assets/kit-recursos/README.md) para crear el `.tsx` y renderizar con `--png`.
2. Guardar la fuente `.tsx` en `Recursos/fuente/` del proyecto y el PDF en `Recursos/`, con nombre estable `anexo-NN-nombre`.
3. Abrir los PNG de vista previa y revisar página por página:
   - texto completo, sin cortes ni desbordes;
   - ortografía, cifras, unidades y respuestas;
   - legibilidad al imprimir (cuerpo de texto de 10 pt o más) y contraste;
   - número de páginas esperado.
4. Usar el PNG de la primera página como vista previa en ANEXOS.
5. Al corregir, editar el `.tsx` y volver a renderizar; no editar el PDF.

## Estilo
- Sobrio y apto para adolescentes: pocos colores, mucho espacio libre y jerarquía clara.
- Ciencias y matemáticas: centrado en datos, diagramas y relaciones; sin adornos.
- Ilustraciones de `openai_image`: animadas y minimalistas. Pasar literalmente los prompts del usuario; si no hay prompt, proponerlo y pedir autorización para elaborarlo.
- Identificar el material original como «Elaboración propia con apoyo de IA». Lo adaptado lleva «Adaptado de…» con su fuente.
- Accesibilidad: no transmitir información solo con color; usar letras, iconos o patrones.
