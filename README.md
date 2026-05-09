# Farm RPG — Prototipo

Proyecto de práctica para un juego tipo **farm RPG**: ritmo relajado, gestión de recursos y acciones con temporizadores en tiempo real (cultivo, y a futuro cocina, minería, fundición, investigaciones y exploración).

---

## Idea del proyecto

### Visión general

Construir una experiencia **single-player** y **local** donde el jugador progresa en bucles de:

- Plantar → esperar (tiempo real) → cosechar → ganancias simples (oro/inventario).
- Más adelante, encadenar **cadena de materiales**: minería → fundición → cocina/recetas → investigaciones que desbloquean mejor contenido.

### Principios de diseño

| Enfoque | Descripción |
|--------|--------------|
| **Ritmo** | Relajado, estilo farm RPG; sin presión tipo acción rápida. |
| **Tiempo** | Los temporizadores siguen la hora real del sistema; más adelante se persiste el estado para que el avance siga con la aplicación cerrada. |
| **Economía inicial** | Simple (vender/consolidar ganancias); crafting y loops más ricos llegan después. |
| **Energía/stamina** | No en los sistemas núcleo al inicio; reservado para exploración cuando exista ese módulo. |
| **Plataforma objetivo UI** | **Web** con [Flet](https://flet.dev/). |

### Alcance próximo vs. más adelante

**Prioridad cercana**

- MVP: solo cultivos, varias parcelas, persistencia local (SQLite) y mismo motor de tiempo que ya usa `TimedAction`.

**Roadmap medio plazo**

- Minería (siguiente interés después del farming).
- Fundición y cocina.
- Investigación/desbloqueos.
- Exploración (posible stamina aquí).

**Futuro opcional**

- Multijugador u online (después de consolidar MVP local).

---

## Stack técnico

| Componente | Uso actual |
|-----------|-------------|
| **Python 3** | Lenguaje del proyecto |
| **[Flet](https://flet.dev/)** | Interfaz; punto de entrada `main.py`. |
| **Flask** | Esqueleto en `backend/app.py` pensado como API/backend; sin rutas funcionales definidas en el estado actual del repo. |

---

## Estructura del repositorio

```
Flask + Flet/
├── README.md                 # Este archivo
├── Ideas                     # Notas del autor
├── main.py                   # Aplicación Flet (UI de demostración)
└── backend/
    ├── __init__.py
    ├── app.py                # Flask (preparación futura / API)
    ├── timed_action.py       # Temporizador reutilizable
    └── cropsystem/
        ├── __init__.py
        └── crops.py          # Lógica de cultivo
```

---

## Cómo ejecutar la UI local

Desde la raíz del proyecto (donde está `main.py`):

```powershell
pip install flet
python main.py
```

Para modo web de Flet, consulta la documentación oficial (`flet run --web` o equivalente según tu versión instalada).

---

## Documentación del código

### `backend/timed_action.py` — `TimedAction`

Pieza central para cualquier acción con **duración fija** usando la hora del sistema (`datetime.now()`).

Úsala igual para parcelas virtuales independientes o para cocina/fundición cuando implementes esos sistemas.

| API | Comportamiento |
|-----|----------------|
| `start(when=None) -> bool` | Inicia el temporizador. Si ya hay uno en curso, no cambia estado y devuelve `False`. |
| `cancel()` | Limpia estado sin completar la acción. |
| `is_idle` | No hay sesión temporal activa. |
| `is_active(now=None)` | Corriendo y aún no cumple duración. |
| `is_ready(now=None)` | Ya transcurrieron los segundos requeridos desde `started_at`. |
| `time_remaining_seconds(now=None)` | Segundos hasta completar (`0` si idle o ya listo). |
| `progress_ratio(now=None)` | Progreso `0..1` (útil para barras UI). |
| `finish_if_ready(now=None) -> bool` | Si está listo, resetea estado y devuelve `True` (momento para aplicar recompensa). |

**Tests:** cualquier método con `now` opcional admite fecha inyectada para simular tiempo sin esperar segundos reales.

**Ejemplo mínimo (minería ficticia)**

```python
from backend.timed_action import TimedAction

mining = TimedAction(duration_seconds=15.0)
mining.start()
# más tarde, en pantalla:
sec = mining.time_remaining_seconds()
if mining.finish_if_ready():
    aplicar_drop_de_mineral()
```

---

### `backend/cropsystem/crops.py` — `Crop`

Representa **un cultivo** con tiempo de crecimiento y una recompensa (en el ejemplo numérica; puedes cambiarla a objeto “ítem” más adelante).

Internamente delega todo el tiempo en `_growth: TimedAction`.

| API | Descripción |
|-----|--------------|
| `plant()` | Siembra si la parcela lógica estaba idle. |
| `is_idle`, `is_growing` | Estado útil para la UI sin tocar `_growth`. |
| `is_ready()` | Listo para cosechar sin consumir estado. |
| `harvest()` | Si está listo, limpia y devuelve `reward`; si no, `None`. |
| `time_remaining()` | Segundos restantes durante el crecimiento. |

Constructor: `Crop(nombre, grow_seconds, reward)`.

---

### `main.py`

Construye la página Flet actual:

- Un cultivo de trigo (`Crop("Trigo", 5, 10)`): botones Plantar / Cosechar y textos de estado.
- Una demostración de **cocina** con un `TimedAction` de 8 s separado para mostrar reutilización del temporizador.
- Un hilo que cada segundo actualiza textos mediante `refresh_labels()` y `page.update()`.

La luego en el proyecto cabe extraer esa UI a carpetas tipo `ui/` dejando en `backend/` solo reglas de juego.

---

### `backend/app.py` (Flask)

Contenedor mínimo de Flask. Actualmente:

- Intenta importar desde `cropsystem.crops` rutas relativas típicas de ejecutar dentro de `backend/`.
- No define aún rutas REST ni el símbolo `wheat`; conviene completar rutas (`/`) y ejecutar Flask con el PYTHONPATH correcto cuando quieras conectar cliente Flet ⇄ servidor.

---

## Convenciones sugeridas (evolución)

1. **`domain`** (o mantener `backend/`): datos y reglas puras (`Crop`, `TimedAction`, futuro inventario).
2. **`services`**: casos de uso (`plantar_en_parcela`, `cosechar`).
3. **`infra`**: SQLite, archivo de guardado.
4. **`ui`**: solo Flet llamando a servicios.

Esto facilita repetir el patrón `TimedAction` en minería, horno y crafting sin duplicar lógica de temporizadores.

---

## Estado del proyecto (resumen)

- Temporización unificada y reutilizable: **hecha** (`TimedAction`).
- Ciclo cultivos básico en código: **hecho** (`Crop` + ejemplo en UI).
- Multiples parcelas, inventario persistente y despliegue web pulido: **pendiente**.
- API Flask integrada al juego: **pendiente**.

---

## Licencia y autoría

Define licencia y créditos aquí cuando lo desees.
