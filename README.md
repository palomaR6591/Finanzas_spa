# Finanzas Spa · Calculadora de costos para cualquier spa

Proyecto final de **ADMI 1301 · Introducción a la Programación** (Universidad de los Andes, 2026-2).

**Finanzas Spa** es una aplicación escrita en Python que **cualquier spa** puede usar para calcular los costos y la ganancia operativa de su jornada. La app **empieza vacía**: cada spa escribe sus propios datos y obtiene su cálculo. El escenario del proyecto es ofrecerla a spas de Bogotá.

> **Aviso:** el botón *Cargar ejemplo* usa **Sunny Side Luxury Spa**, un spa **ficticio** que sirve como cliente de muestra. Sus cifras son **supuestos de simulación propuestos por el grupo**. No son datos reales de ninguna empresa, y este proyecto no incluye información de mercado real.

<p align="center"><img src="icons/logo.svg" alt="Logo de Finanzas Spa: una flor de loto cuyos pétalos suben como las barras de una gráfica" width="96"></p>

*El logo es una flor de loto (spa) cuyos pétalos van subiendo como las barras de una gráfica (finanzas). Los colores son una paleta violeta (de #6d00a1 a #cb9bde) sobre fondo crema y blanco.*

## Abrir la app

**https://jdespinosa2008.github.io/Finanzas_spa/**

### Agregarla al celular

- **Android (Chrome):** menú ⋮ → *Instalar app* o *Añadir a la pantalla de inicio*.
- **iPhone (Safari):** botón Compartir → *Añadir a pantalla de inicio*.

Después de abrirla una vez con internet, también funciona sin conexión.

## Cómo se usa

La app tiene cuatro secciones (barra inferior):

1. **Mi spa:** el spa escribe su nombre, los clientes que atiende un terapeuta por turno, los clientes por persona de recepción/apoyo, el costo de cada turno, las cabinas, de 1 a 6 tratamientos (nombre, precio, costo de insumos y porcentaje de clientes que lo piden) y cuántos clientes espera. Hay botones − / + para los números, y para agregar, duplicar o quitar tratamientos.
2. **Resultados:** terapeutas y personal de recepción necesarios, ingresos por tratamiento (gráfica circular), costos, ganancia operativa, margen y utilización. Un deslizador y botones permiten cambiar los clientes y ver el resultado al instante. Una gráfica muestra la ganancia para cada número de clientes y el **punto de equilibrio**. Se puede copiar un resumen o imprimir / guardar en PDF.
3. **Escenarios:** compara tres jornadas: baja afluencia (un tercio de la capacidad), ocupación media (dos tercios) y agenda llena.
4. **¿Y si…?:** simulador para ver qué pasaría con la ganancia si suben o bajan los precios, los insumos o los turnos del personal. No cambia los datos del spa.

Los datos se guardan **solo en el dispositivo** (no hay servidor ni cuentas). *Limpiar todo* los borra.

## Reglas del cálculo

- **Capacidad máxima** = cabinas × clientes por terapeuta. Si la demanda la supera, la app avisa que no se puede atender y **no muestra cifras financieras**.
- **Personal:** siempre se redondea hacia arriba (`clientes // capacidad`, y uno más si sobra resto).
- **Reparto de clientes:** el primer tratamiento recibe el resto; los demás reciben su porcentaje, redondeado al entero más cercano. Estos porcentajes son un **supuesto de demanda** que escribe cada spa.
- **Ganancia operativa** = ingresos − costo de personal − costo de insumos. **No incluye** arriendo, servicios públicos ni impuestos.
- **Punto de equilibrio:** el primer número de clientes desde el cual todas las jornadas, hasta la capacidad máxima, dejan ganancia operativa.

Si un dato no es válido (letras, negativos, decimales, porcentajes que suman más de 100 %, nombres repetidos…), la app lo indica y no calcula hasta corregirlo.

## ¿Cómo funciona por dentro?

- **`app.py`** contiene todo el cálculo, escrito en Python: `validar_configuracion`, `personal_necesario`, `repartir_clientes`, `calcular_jornada`, `punto_de_equilibrio`, `simular`, entre otras. Las funciones reciben los datos del spa como parámetro. Con los datos del ejemplo dan los mismos resultados que el notebook del proyecto.
- **`index.html`** es la pantalla. Solo recoge los datos y dibuja lo que devuelve Python.
- El Python se ejecuta **dentro del navegador** con [Pyodide](https://pyodide.org) (carpeta `pyodide/`, licencia MPL-2.0), así que no hay servidor y nada sale del dispositivo.
- `manifest.webmanifest`, `sw.js` e `icons/` permiten instalarla en el celular y usarla sin conexión.

Si se modifica algún archivo, cambiar el número de `VERSION` en `sw.js` para que los celulares descarguen la versión nueva.

### Probarla en el computador

```
python -m http.server 8000
```

y abrir `http://localhost:8000`. (Abrir `index.html` con doble clic no funciona, porque el navegador bloquea la carga de archivos locales.)

## Limitaciones

- Es un modelo simple de **una jornada**: no incluye arriendo, servicios, impuestos, nómina mensual ni demanda por horas.
- Supone que cada terapeuta usa una cabina y que la mezcla de tratamientos es la que escribe el spa.
- Los resultados son estimaciones para planear, no contabilidad.
- Los datos quedan en el navegador del dispositivo: si se borran los datos del navegador, hay que volver a escribirlos.

## Uso de inteligencia artificial

Se usó Claude (Anthropic) como apoyo para diseñar y generar un borrador de la aplicación. El grupo verificó los cálculos contra cuentas hechas a mano. La nota completa está en el notebook del proyecto.

## Integrantes

Matias Galeano · Emily Rojas · Paloma Restrepo · Valeria Nuncio

Profesor: Gustavo Niño · ADMI 1301 · Facultad de Administración, Universidad de los Andes.
