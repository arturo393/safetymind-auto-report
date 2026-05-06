# 🔄 Jira ↔ Reality Sync Status
*Actualizado: 2026-04-29*

## 📊 Resumen Ejecutivo
- **Proyecto Jira:** DAS (Diagnostic Automation Suite)
- **Tablero:** DAS board (ID: 763)
- **Estado general:** 23 issues creadas, 0 completadas
- **Brecha crítica:** El código actual no refleja el roadmap de DAS

---

## 🚀 Épica 1: MVP - Ingesta para 3 Clientes
*Objetivo: Formulario 7 cámaras y reporte básico*

| Issue | Título | Jira Status | Realidad | Ubicación |
|-------|--------|-------------|----------|-----------|
| DAS-6 | Componente subida 7 imágenes en Portal | ⚪ To Do | ❌ **No existe** | `frontend/portal/src/` |
| DAS-7 | Validación client-side básica de imágenes | ⚪ To Do | ❌ **No existe** | - |
| DAS-8 | Integración envío imágenes a n8n inicial | ⚪ To Do | ❌ **No existe** (ni n8n config) | `backend/go-api/` |
| DAS-9 | Reporte HTML básico para 3 clientes | ⚪ To Do | ⚠️ **Parcial** (HTML genérico en Go API) | `backend/go-api/main.go:337-360` |

**Estado real:** El portal (`frontend/portal/`) solo tiene UI base (button, card, input). No hay componente de upload múltiple. El backend genera reportes HTML/PDF pero no para diagnósticos de cámaras.

---

## 🤖 Épica 2: Core AI Workflow (MVP)
*Flujo básico: n8n + LangGraph + Moondream*

| Issue | Título | Jira Status | Realidad | Ubicación |
|-------|--------|-------------|----------|-----------|
| DAS-10 | n8n + LangGraph básico | ⚪ To Do | ❌ **No existe** | - |
| DAS-11 | Moondream en 100.74.53.2 | ⚪ To Do | ❌ **No verificado** | - |
| DAS-12 | Persistencia LangGraph mínima | ⚪ To Do | ❌ **No existe** | - |

**Estado real:** El backend usa Ollama (Llama3) para AI summary (`main.go:302-335`), no Moondream. No hay n8n ni LangGraph.

---

## ✅ Épica 3: HITL Básico (MVP)
*Validación humana asistida*

| Issue | Título | Jira Status | Realidad | Ubicación |
|-------|--------|-------------|----------|-----------|
| DAS-13 | Nodo n8n alertas Slack/Email | ⚪ To Do | ❌ **No existe** | - |
| DAS-14 | Pausa n8n esperando confirmación | ⚪ To Do | ❌ **No existe** | - |

**Estado real:** No hay integración con Slack ni sistema de pausa humana.

---

## 🛡️ Épica 4: Robustez
*Mejoras de robustez y errores*

| Issue | Título | Jira Status | Realidad | Ubicación |
|-------|--------|-------------|----------|-----------|
| DAS-15 | LangGraph procesamiento paralelo | ⚪ To Do | ❌ **No existe** | - |
| DAS-16 | Optimización Moondream | ⚪ To Do | ❌ **No verificado** | - |
| DAS-17 | Manejo de errores robusto | ⚪ To Do | ⚠️ **Básico** (Gin recovery) | `backend/go-api/main.go:63` |
| DAS-22 | Feedback visual "IA Analizando..." | ⚪ To Do | ❌ **No existe** | `frontend/portal/src/` |

**Estado real:** Manejo de errores básico con Gin. No hay feedback visual de IA.

---

## 📈 Épica 5: Escalabilidad Premium
*Producto final premium*

| Issue | Título | Jira Status | Realidad | Ubicación |
|-------|--------|-------------|----------|-----------|
| DAS-18 | Diseño Bento Grid reportes | ⚪ To Do | ❌ **No existe** | `templates/*.html` |
| DAS-19 | Envío automático SendGrid/SMTP | ⚪ To Do | ❌ **No existe** | - |
| DAS-20 | CSS optimizado impresión/PDF | ⚪ To Do | ❌ **No existe** | - |
| DAS-21 | Migración persistencia LangGraph | ⚪ To Do | ❌ **No existe** | - |
| DAS-23 | Botones Aprobar/Rechazar | ⚪ To Do | ❌ **No existe** | - |

**Estado real:** Reportes actuales son HTML genérico (`main.go:337-360`). No hay Bento Grid ni envío de correos.

---

## 🗂️ Infraestructura Actual vs DAS

| Componente | Estado Actual | Requerido por DAS |
|-----------|--------------|-------------------|
| **Portal** (Next.js :8501) | ✅ Funcional (UI base) | ❌ Falta upload 7 cámaras |
| **API** (Go/Gin :8080) | ✅ Funcional (reportes) | ❌ Falta integración n8n |
| **n8n** | ❌ No instalado | ✅ Requerido para MVP |
| **LangGraph** | ❌ No existe | ✅ Requerido para MVP |
| **Moondream** | ❌ No verificado en 100.74.53.2 | ✅ Requerido para MVP |
| **Ollama** | ✅ En 100.74.53.2 (:11434) | ⚠️ Migrar a Moondream |
| **Postgres** | ❌ No configurado | ✅ Para persistencia |

---

## 🎯 Próximos Pasos Recomendados

### Semana 1-2: MVP Ingesta (DAS-1)
1. **DAS-6:** Crear componente `CameraUpload.tsx` en `frontend/portal/src/components/`
2. **DAS-7:** Validar imágenes (tipo, tamaño) en client-side
3. **DAS-8:** Endpoint en Go API para recibir imágenes y disparar n8n webhook
4. **DAS-9:** Template HTML específico para diagnósticos de 7 cámaras

### Semana 3-4: Core AI (DAS-2)
1. **DAS-11:** Verificar Moondream en 100.74.53.2
2. **DAS-10:** Configurar n8n + LangGraph workflow básico
3. **DAS-12:** Postgres local para checkpoints de LangGraph

---

## 📝 Notas de Sincronización
- Las issues DAS-1 a DAS-23 están en el tablero pero **no reflejan el código actual**
- El código actual (`jira-automation/`) es para reportes de Jira tradicionales, no diagnósticos de cámaras
- Se recomienda crear un nuevo directorio `diagnostic-automation/` o adaptar `jira-automation/` para el flujo DAS
- El servidor 100.74.53.2 tiene Ollama pero necesita Moondream para visión artificial

---
*Generado automáticamente basado en código actual y proyecto DAS en Jira*
