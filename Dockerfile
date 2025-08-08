# Imagen base
FROM python:3.11-slim

# Evita que Python guarde .pyc y buffers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Dar permisos de ejecución al script de arranque
RUN sed -i 's/\r$//' start.sh
RUN chmod +x start.sh

# Puerto para Render
ENV PORT=8080

# Comando de inicio
CMD ["./start.sh"]
