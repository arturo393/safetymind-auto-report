# Configuración del Servidor Ubuntu (Ollama AI)

Esta guía explica cómo configurar el "cerebro" (Ollama) en tu servidor Ubuntu (`arturo@192.168.1.149`) para que el generador de reportes pueda usar inteligencia artificial local.

## 1. Instalación de Ollama
Ejecuta esto en tu servidor Ubuntu:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## 2. Configuración de Acceso Externo (Crucial)
Por defecto, Ollama solo escucha internamente. Debemos configurarlo para que el portal web de los usuarios pueda conectarse.

1. Abre el archivo de configuración del servicio:
   ```bash
   sudo systemctl edit ollama.service
   ```
2. Agrega estas líneas al final:
   ```ini
   [Service]
   Environment="OLLAMA_HOST=0.0.0.0"
   ```
3. Guarda y reinicia el servicio:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart ollama
   ```

## 3. Descarga del Modelo
Recomendamos `llama3` o `mistral` por su excelente capacidad de resumen ejecutivo:
```bash
ollama run llama3
```

## 4. Verificar Cortafuegos (UFW)
Asegúrate de que el puerto `11434` esté abierto:
```bash
sudo ufw allow 11434
```

---
Una vez hecho esto, cualquier usuario en la red local podrá usar la IA para sus reportes.
