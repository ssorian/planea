// Esquemas y validación de los datos de cada juego. Lo usan construir.ts (validar antes de
// construir) y los juegos (tipos). Todos los mensajes de error van en español.

export type Juego = "encuesta" | "tarjetas" | "tablero" | "ruleta";
export const JUEGOS: Juego[] = ["encuesta", "tarjetas", "tablero", "ruleta"];

type Base = { titulo: string; ejemplo: boolean };
export type DatosEncuesta = Base & {
  equipos: [string, string];
  rondas: { pregunta: string; multiplicador: number; respuestas: { texto: string; puntos: number }[] }[];
};
export type DatosTarjetas = Base & {
  segundos: number; // 0 = sin temporizador
  preguntas: { pregunta: string; opciones: string[]; correcta: number; tema: string; explicacion: string }[];
};
export type DatosTablero = Base & {
  equipos: string[];
  categorias: { nombre: string; preguntas: { valor: number; pregunta: string; respuesta: string }[] }[];
};
export type DatosRuleta = Base & {
  modo: "nombres" | "preguntas";
  noRepetir: boolean;
  elementos: { texto: string; respuesta: string }[];
};

export type Resultado<T> = { ok: true; datos: T } | { ok: false; errores: string[] };

type Obj = Record<string, unknown>;
const esObj = (x: unknown): x is Obj => typeof x === "object" && x !== null && !Array.isArray(x);
const sub = (ruta: string, clave: string) => (ruta ? `${ruta}.${clave}` : clave);

class Validador {
  errores: string[] = [];
  err(ruta: string, msg: string) {
    this.errores.push(`${ruta || "(raíz)"}: ${msg}`);
  }
  objeto(x: unknown, ruta: string, claves: string[]): Obj | null {
    if (!esObj(x)) {
      this.err(ruta, "debe ser un objeto { ... }");
      return null;
    }
    for (const k of Object.keys(x)) {
      if (!claves.includes(k)) this.err(sub(ruta, k), `clave desconocida. Claves válidas: ${claves.join(", ")}`);
    }
    return x;
  }
  texto(o: Obj, clave: string, ruta: string, opts: { req?: boolean; max?: number } = {}): string {
    const { req = true, max = 400 } = opts;
    const r = sub(ruta, clave);
    const x = o[clave];
    if (x === undefined || x === null) {
      if (req) this.err(r, "es obligatorio (texto entre comillas)");
      return "";
    }
    if (typeof x !== "string") {
      this.err(r, "debe ser texto entre comillas");
      return "";
    }
    const t = x.trim();
    if (req && !t) this.err(r, "no puede estar vacío");
    if (t.length > max) this.err(r, `es demasiado largo (${t.length} caracteres; máximo ${max})`);
    return t;
  }
  entero(o: Obj, clave: string, ruta: string, opts: { req?: boolean; min: number; max: number; def?: number }): number {
    const r = sub(ruta, clave);
    const x = o[clave];
    if (x === undefined || x === null) {
      if (opts.req) this.err(r, "es obligatorio (número entero)");
      return opts.def ?? opts.min;
    }
    if (typeof x !== "number" || !Number.isInteger(x)) {
      this.err(r, "debe ser un número entero sin comillas");
      return opts.def ?? opts.min;
    }
    if (x < opts.min || x > opts.max) this.err(r, `debe estar entre ${opts.min} y ${opts.max} (es ${x})`);
    return x;
  }
  booleano(o: Obj, clave: string, ruta: string, def: boolean): boolean {
    const x = o[clave];
    if (x === undefined || x === null) return def;
    if (typeof x !== "boolean") {
      this.err(sub(ruta, clave), "debe ser true o false (sin comillas)");
      return def;
    }
    return x;
  }
  lista(o: Obj, clave: string, ruta: string, min: number, max: number): unknown[] {
    const r = sub(ruta, clave);
    const x = o[clave];
    if (!Array.isArray(x)) {
      this.err(r, `es obligatorio y debe ser una lista [ ... ] de ${min} a ${max} elementos`);
      return [];
    }
    if (x.length < min || x.length > max) this.err(r, `debe tener entre ${min} y ${max} elementos (tiene ${x.length})`);
    return x;
  }
  equipos(o: Obj, ruta: string, min: number, max: number, def: string[]): string[] {
    if (o.equipos === undefined) return def;
    const lista = this.lista(o, "equipos", ruta, min, max);
    const nombres = lista.map((e, i) => {
      if (typeof e !== "string" || !e.trim()) {
        this.err(`${sub(ruta, "equipos")}[${i}]`, "debe ser el nombre del equipo (texto no vacío)");
        return `Equipo ${i + 1}`;
      }
      return e.trim().slice(0, 30);
    });
    if (new Set(nombres).size !== nombres.length) this.err(sub(ruta, "equipos"), "los nombres de equipo no pueden repetirse");
    return nombres;
  }
}

function encuesta(v: Validador, x: unknown): DatosEncuesta {
  const o = v.objeto(x, "", ["ejemplo", "titulo", "equipos", "rondas"]) ?? {};
  const equipos = v.equipos(o, "", 2, 2, ["Equipo A", "Equipo B"]);
  const rondas = v.lista(o, "rondas", "", 1, 30).map((r, i) => {
    const ruta = `rondas[${i}]`;
    const ro = v.objeto(r, ruta, ["pregunta", "multiplicador", "respuestas"]) ?? {};
    const respuestas = v.lista(ro, "respuestas", ruta, 4, 8).map((a, j) => {
      const rr = `${ruta}.respuestas[${j}]`;
      const ao = v.objeto(a, rr, ["texto", "puntos"]) ?? {};
      return { texto: v.texto(ao, "texto", rr, { max: 80 }), puntos: v.entero(ao, "puntos", rr, { req: true, min: 1, max: 100 }) };
    });
    return {
      pregunta: v.texto(ro, "pregunta", ruta, { max: 200 }),
      multiplicador: v.entero(ro, "multiplicador", ruta, { min: 1, max: 3, def: 1 }),
      respuestas,
    };
  });
  return { ejemplo: v.booleano(o, "ejemplo", "", false), titulo: v.texto(o, "titulo", "", { max: 80 }), equipos: equipos as [string, string], rondas };
}

function tarjetas(v: Validador, x: unknown): DatosTarjetas {
  const o = v.objeto(x, "", ["ejemplo", "titulo", "segundos", "preguntas"]) ?? {};
  const segundos = o.segundos === undefined || o.segundos === 0 ? 0 : v.entero(o, "segundos", "", { req: true, min: 5, max: 600 });
  const preguntas = v.lista(o, "preguntas", "", 1, 50).map((p, i) => {
    const ruta = `preguntas[${i}]`;
    const po = v.objeto(p, ruta, ["pregunta", "opciones", "correcta", "tema", "explicacion"]) ?? {};
    const opciones = v.lista(po, "opciones", ruta, 2, 4).map((t, j) => {
      if (typeof t !== "string" || !t.trim()) {
        v.err(`${ruta}.opciones[${j}]`, "debe ser texto no vacío");
        return "";
      }
      if (t.trim().length > 120) v.err(`${ruta}.opciones[${j}]`, "es demasiado largo (máximo 120 caracteres)");
      return t.trim();
    });
    let correcta = 0;
    const c = po.correcta;
    if (typeof c !== "string" || !/^[A-Da-d]$/.test(c.trim())) v.err(`${ruta}.correcta`, 'es obligatorio y debe ser una letra "A", "B", "C" o "D"');
    else {
      correcta = c.trim().toUpperCase().charCodeAt(0) - 65;
      if (correcta >= opciones.length) v.err(`${ruta}.correcta`, `la letra "${c.trim().toUpperCase()}" no corresponde a ninguna de las ${opciones.length} opciones`);
    }
    return {
      pregunta: v.texto(po, "pregunta", ruta, { max: 250 }),
      opciones,
      correcta,
      tema: v.texto(po, "tema", ruta, { req: false, max: 60 }),
      explicacion: v.texto(po, "explicacion", ruta, { req: false, max: 250 }),
    };
  });
  return { ejemplo: v.booleano(o, "ejemplo", "", false), titulo: v.texto(o, "titulo", "", { max: 80 }), segundos, preguntas };
}

function tablero(v: Validador, x: unknown): DatosTablero {
  const o = v.objeto(x, "", ["ejemplo", "titulo", "equipos", "categorias"]) ?? {};
  const equipos = v.equipos(o, "", 2, 4, ["Equipo 1", "Equipo 2"]);
  const categorias = v.lista(o, "categorias", "", 2, 6).map((c, i) => {
    const ruta = `categorias[${i}]`;
    const co = v.objeto(c, ruta, ["nombre", "preguntas"]) ?? {};
    const preguntas = v.lista(co, "preguntas", ruta, 2, 6).map((p, j) => {
      const rr = `${ruta}.preguntas[${j}]`;
      const po = v.objeto(p, rr, ["valor", "pregunta", "respuesta"]) ?? {};
      return {
        valor: v.entero(po, "valor", rr, { req: true, min: 1, max: 10000 }),
        pregunta: v.texto(po, "pregunta", rr, { max: 250 }),
        respuesta: v.texto(po, "respuesta", rr, { max: 250 }),
      };
    });
    return { nombre: v.texto(co, "nombre", ruta, { max: 40 }), preguntas };
  });
  const largos = new Set(categorias.map((c) => c.preguntas.length));
  if (largos.size > 1) v.err("categorias", "todas las categorías deben tener el mismo número de preguntas (una por fila del tablero)");
  return { ejemplo: v.booleano(o, "ejemplo", "", false), titulo: v.texto(o, "titulo", "", { max: 80 }), equipos, categorias };
}

function ruleta(v: Validador, x: unknown): DatosRuleta {
  const o = v.objeto(x, "", ["ejemplo", "titulo", "modo", "noRepetir", "elementos"]) ?? {};
  let modo: "nombres" | "preguntas" = "nombres";
  if (o.modo !== undefined) {
    if (o.modo === "nombres" || o.modo === "preguntas") modo = o.modo;
    else v.err("modo", 'debe ser "nombres" o "preguntas"');
  }
  const elementos = v.lista(o, "elementos", "", 2, 60).map((e, i) => {
    const ruta = `elementos[${i}]`;
    if (typeof e === "string") {
      if (!e.trim()) v.err(ruta, "no puede estar vacío");
      if (e.trim().length > 250) v.err(ruta, "es demasiado largo (máximo 250 caracteres)");
      return { texto: e.trim(), respuesta: "" };
    }
    const eo = v.objeto(e, ruta, ["texto", "respuesta"]);
    if (!eo) return { texto: "", respuesta: "" };
    return { texto: v.texto(eo, "texto", ruta, { max: 250 }), respuesta: v.texto(eo, "respuesta", ruta, { req: false, max: 250 }) };
  });
  return {
    ejemplo: v.booleano(o, "ejemplo", "", false),
    titulo: v.texto(o, "titulo", "", { max: 80 }),
    modo,
    noRepetir: v.booleano(o, "noRepetir", "", true),
    elementos,
  };
}

export function validar(juego: "encuesta", x: unknown): Resultado<DatosEncuesta>;
export function validar(juego: "tarjetas", x: unknown): Resultado<DatosTarjetas>;
export function validar(juego: "tablero", x: unknown): Resultado<DatosTablero>;
export function validar(juego: "ruleta", x: unknown): Resultado<DatosRuleta>;
export function validar(juego: Juego, x: unknown): Resultado<unknown>;
export function validar(juego: Juego, x: unknown): Resultado<unknown> {
  const v = new Validador();
  const fn = { encuesta, tarjetas, tablero, ruleta }[juego];
  const datos = fn(v, x);
  return v.errores.length ? { ok: false, errores: v.errores } : { ok: true, datos };
}
