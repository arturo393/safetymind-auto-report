# Guía del Usuario: Generador de Reportes SafetyMind

Esta guía está diseñada para que cualquier persona en el equipo pueda generar reportes profesionales (Kickoff, Progreso y Cierre) sin necesidad de programar ni usar herramientas especiales.

## 1. Requisitos
- Tener Python instalado en tu computadora (o acceso a la red del servidor Ubuntu).
- Una conexión estable a la red corporativa (para acceder a Jira).

## 2. Cómo Iniciar el Programa
Hemos creado un portal web interno para simplificar el proceso.

### Opción A (Desde el Terminal - Fácil)
1. Abre tu terminal o consola.
2. Escribe el siguiente comando y presiona `Enter`:
   ```bash
   streamlit run src/app.py
   ```
3. Se abrirá automáticamente una pestaña en tu navegador (Chrome/Safari) con el título **SafetyMind: Report Generator**.

### Opción B (Icono de Escritorio)
Puedes pedir al administrador de sistemas que te cree un icono en el escritorio que ejecute este comando por ti.

## 3. Guía Paso a Paso en la Web
1. **Selecciona Proyecto**: Elige de la lista (ej. `GMF`).
2. **Tipo de Reporte**: Marca `Kickoff`, `Progress` o `Final`.
3. **Generar**: Haz clic en el botón cohete 🚀 **Generar Reporte**.
4. **Descargar**: Una vez listo, aparecerá un botón azul para **Descargar PDF**.

---

### 🧠 Inteligencia Artificial (Ollama)
Si el servidor Ubuntu (`192.168.1.149`) está activo, el sistema te sugerirá automáticamente un **Resumen Ejecutivo** basado en lo que encuentre en Jira. Puedes aceptarlo o editarlo manualmente en el archivo `config/projects.yaml`.

---

© 2026 SafetyMind Inc. - Documentación de Proyectos Estándar PMBOK/PRINCE2.
