# Estado del proyecto

Los datos confirmados, el diseño aprobado y la numeración de anexos viven en la **carpeta de trabajo del usuario**, nunca dentro de la skill.

## Árbol de la carpeta de trabajo
```
<carpeta de trabajo>/
├─ <RAIPA y planeación modelo>        originales del usuario; solo lectura
├─ AGENTS.md                          opcional; una sola línea que apunta a planea/estado.md
├─ planea/
│  ├─ estado.md                       datos confirmados, calendario, decisiones, avance por proyecto, preguntas abiertas, siguiente paso
│  ├─ materiales.csv                  copia de assets/catalogo-materiales.csv: registro único de materiales y de números de anexo
│  ├─ diseno-<proyecto>.md            diseño aprobado de cada proyecto, con fecha de aprobación y fichas de actividad
│  └─ trabajo/                        copias de trabajo y temporales; se limpia al cerrar
├─ Recursos/
│  ├─ fuente/                         fuentes HTML e imágenes: NN-<nombre>
│  ├─ NN-<nombre>.pdf                 NN = número de anexo
│  └─ juegos/<nombre>/                juegos proyectados
└─ salida/                            la planeación DOCX producida
```

## Reglas
- Al empezar, leer `planea/estado.md` si existe y continuar desde «Siguiente paso». Si no existe, crearlo desde la [plantilla](../assets/plantilla-estado.md).
- Actualizarlo en cada dato confirmado y en cada aprobación del usuario.
- `AGENTS.md` de la carpeta, si existe, solo lleva una línea que apunta a `planea/estado.md`.
- Un número de anexo se asigna una sola vez, en `planea/materiales.csv`, y no se reutiliza.
- Guardar el diseño aprobado de cada proyecto en `planea/diseno-<proyecto>.md` con la fecha de aprobación.
- Escribir scripts auxiliares y copias temporales en `planea/trabajo/`; no tocar los originales.

## Cuestionario inicial
Un solo bloque de preguntas, solo de lo que falte en el estado:
- Escuela, CCT, turno, grado y grupo.
- Docente titular y docente en formación.
- Fechas de la jornada y días sin clase (suspensiones, Consejo Técnico Escolar).
- Minutos por sesión y sesiones por día o por campo.
- Proyectos del RAIPA que se van a planear.
- Número de estudiantes.
- Equipo del aula: proyector o pantalla, bocinas, internet, dispositivos.
- Impresión: copias y color.
- Contexto confirmado: lenguas y barreras para el aprendizaje.
- Planeación modelo y dónde se insertan las secciones.

Nunca rellenar con datos de plantillas o de documentos anteriores sin confirmar.
