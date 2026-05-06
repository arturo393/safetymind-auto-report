# 📋 Jira Roadmap: Diagnostic Automation Suite (Revised)
*Prioridad: Entregables rápidos 3 clientes → Robustez → Escalabilidad*

## 🚀 Épica 1: MVP - Ingesta para 3 Clientes (Entrega < 2 semanas)
*Objetivo: Formulario funcional de 7 cámaras y reporte básico para piloto*
- **IM-1:** Componente subida 7 imágenes en Portal (`/portal`)
- **IM-2:** Validación client-side básica de imágenes
- **IM-3:** Integración envío imágenes a n8n inicial
- **IM-4:** Reporte HTML básico para 3 clientes

## 🤖 Épica 2: Core AI Workflow (MVP)
- **IM-5:** n8n + LangGraph básico (procesamiento secuencial 7 imágenes)
- **IM-6:** Moondream desplegado en 100.74.53.2 (config base)
- **IM-7:** Persistencia LangGraph mínima (Postgres local)

## ✅ Épica 3: HITL Básico (MVP)
- **IM-8:** Nodo n8n alertas básicas Slack/Email
- **IM-9:** Pausa n8n esperando confirmación humana vía email

## 🛡️ Épica 4: Robustez
- **IM-10:** LangGraph procesamiento paralelo imágenes
- **IM-11:** Optimización Moondream 100.74.53.2
- **IM-12:** Manejo de errores robusto ingesta/procesamiento
- **IM-13:** Feedback visual "IA Analizando..." en Portal

## 📈 Épica 5: Escalabilidad Premium
- **IM-14:** Botones "Aprobar/Rechazar" en notificaciones
- **IM-15:** Diseño Bento Grid reportes profesionales
- **IM-16:** Envío automático reportes SendGrid/SMTP
- **IM-17:** CSS optimizado impresión/PDF
- **IM-18:** Migración persistencia LangGraph a Firestore/Postgres gestionado
