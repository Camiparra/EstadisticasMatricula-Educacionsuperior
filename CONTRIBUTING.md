# Reglas para la integración del trabajo

Este documento lo administra el **Integrante 1** (responsable del repositorio)
y aplica a los cuatro integrantes del equipo. Su objetivo es que el trabajo de
cada dimensión se pueda integrar a `main` sin romper el de los demás.

---

## 1. Regla de oro

**Nadie hace `push` directo a `main`.** Todo cambio entra por Pull Request
(PR), sin excepción, incluido el Integrante 1.

`main` debe estar siempre en un estado funcional: si alguien la descarga o
Render la despliega en cualquier momento, la aplicación debe correr sin
errores.

---

## 2. Configuración de la rama `main`

El Integrante 1 configura en GitHub (`Settings → Branches → Branch protection rules`):

- Rama por defecto: `main`.
- **Require a pull request before merging** (bloquea el push directo).
- **Require approvals: 1** — como mínimo el Integrante 1 debe aprobar.
- **Require conversation resolution before merging.**
- Opcional pero recomendado: **Require status checks to pass** si el equipo
  agrega en el futuro un workflow de CI que corra la app o valide sintaxis.

---

## 3. Convención de ramas

Una rama por dimensión, ya definidas en la guía del proyecto:

| Rama | Integrante | Contenido |
|---|---|---|
| `feature/dimension-poblacional` | 1 | Tablero + rutas de la dimensión poblacional |
| `feature/dimension-territorial` | 2 | Tablero + rutas de la dimensión territorial |
| `feature/dimension-temporal` | 3 | Tablero + rutas de la dimensión temporal |
| `feature/dimension-multivariada` | 4 | Tablero + rutas de la dimensión relacional/multivariada |

Reglas adicionales:

- Nunca se trabaja directo sobre `main`.
- Antes de crear la rama, actualizar `main` localmente: `git checkout main && git pull origin main`.
- Si una rama tarda varios días, traer los cambios de `main` periódicamente
  (`git merge main` dentro de la rama de trabajo) para evitar conflictos
  grandes al final.
- No se crean ramas adicionales sin avisar al equipo (para no perder la
  trazabilidad de quién hizo qué).

---

## 4. Convención de commits

Formato: `tipo: descripción corta en minúsculas`

| Tipo | Cuándo usarlo |
|---|---|
| `feat` | Nueva funcionalidad (ruta, gráfico, indicador, filtro) |
| `fix` | Corrección de un error |
| `style` | Cambios visuales (CSS, Bootstrap, layout) sin lógica nueva |
| `docs` | Cambios en README, CONTRIBUTING, informe u otra documentación |
| `chore` | Tareas de mantenimiento (dependencias, estructura de carpetas) |

Ejemplos:

```
feat: agregar grafico de barras por categoria en dimension poblacional
fix: corregir filtro de territorio que no se aplicaba
docs: agregar interpretacion de indicadores poblacionales
```

Cada integrante debe tener **mínimo tres commits identificables** en su
dimensión (requisito de la guía). Commits vacíos, gigantes ("subida final") o
sin mensaje descriptivo no cuentan como evidencia válida.

---

## 5. Flujo obligatorio de trabajo

1. `git checkout main && git pull origin main`
2. `git checkout -b feature/dimension-<tu-dimension>`
3. Desarrollar el tablero correspondiente.
4. Commits descriptivos y frecuentes (no un solo commit al final).
5. `git push origin feature/dimension-<tu-dimension>`
6. Abrir un Pull Request hacia `main` usando la plantilla de `.github/PULL_REQUEST_TEMPLATE.md`.
7. Solicitar revisión al Integrante 1 (asignarlo como *reviewer* en GitHub).
8. Aplicar las correcciones solicitadas, si las hay.
9. Obtener la aprobación.
10. El Integrante 1 fusiona el PR (`Squash and merge` o `Merge commit`, a
    elección del equipo, pero siempre igual para todos).

---

## 6. Checklist antes de abrir un Pull Request

Quien abre el PR debe poder marcar todo esto:

- [ ] Probé la app localmente (`python app.py`) y mi ruta/dimensión carga sin errores.
- [ ] No rompí ninguna otra ruta ya existente.
- [ ] No subí archivos innecesarios (entornos virtuales, `__pycache__`, `.env`).
- [ ] Mis commits siguen la convención de la sección 4.
- [ ] La descripción del PR explica qué se hizo y qué falta (si aplica).
- [ ] Si mi cambio afecta `config.py` (nombres de columnas), avisé al equipo,
      porque impacta las otras tres dimensiones.

---

## 7. Criterios de revisión (Integrante 1)

Al revisar un PR, el Integrante 1 valida:

1. **Que corra**: clona/actualiza la rama y ejecuta la app localmente.
2. **Que no rompa nada más**: navega las otras rutas ya integradas en `main`.
3. **Que cumpla el requisito mínimo de la dimensión**: 3 indicadores, 3
   visualizaciones, 2 filtros interactivos, interpretación, conocimientos
   evidentes, limitación y decisión sustentada (ver guía del proyecto).
4. **Que los commits sean identificables** y coherentes con el trabajo mostrado.

Si algo falla, el Integrante 1 **solicita cambios directamente en el PR**
(comentarios en líneas específicas o comentario general), no corrige el
código de los demás. Quien abrió el PR hace los ajustes y vuelve a pedir
revisión.

Tiempo esperado de respuesta a una solicitud de revisión: 24 horas hábiles,
para no bloquear al resto del equipo cerca de la fecha de entrega.

---

## 8. Resolución de conflictos de integración

- Si `main` avanzó mientras trabajabas en tu rama, trae los cambios antes de
  pedir revisión: `git checkout feature/tu-rama && git merge main`.
- Los conflictos se resuelven en la propia rama de quien abrió el PR, no en
  `main`.
- Si el conflicto involucra `config.py` u otro archivo compartido (por
  ejemplo `app.py`, `templates/base.html`), avisar al equipo antes de
  resolverlo unilateralmente: puede afectar el trabajo de otra dimensión.

---

## 9. Qué hacer si un PR no cumple los requisitos

1. El Integrante 1 dejar comentarios puntuales señalando qué falta.
2. Quien abrió el PR corrige en la misma rama y hace push (el PR se
   actualiza solo, no hay que abrir uno nuevo).
3. Se vuelve a solicitar revisión.
4. Solo se fusiona cuando el checklist de la sección 6 se cumple por
   completo.

---

## 10. Verificación final antes de la entrega

Antes de la fecha de evaluación, el Integrante 1 confirma sobre `main`:

- [ ] Las 4 dimensiones están fusionadas y funcionan juntas.
- [ ] Todos los integrantes tienen commits identificables en el historial.
- [ ] La versión publicada en Render corresponde a la última versión de `main`.
- [ ] El repositorio es público y los 4 integrantes figuran como colaboradores.
