import { createRoot } from "react-dom/client";
import "./estilos.css";
import Encuesta from "./juegos/Encuesta";
import Tarjetas from "./juegos/Tarjetas";
import Tablero from "./juegos/Tablero";
import Ruleta from "./juegos/Ruleta";

// Los inyecta construir.ts en el momento del build.
declare const __JUEGO__: string;
declare const __DATOS__: any;

const juegos: Record<string, (p: { d: any }) => JSX.Element> = { encuesta: Encuesta, tarjetas: Tarjetas, tablero: Tablero, ruleta: Ruleta };
const Juego = juegos[__JUEGO__];
createRoot(document.getElementById("raiz")!).render(<Juego d={__DATOS__} />);
