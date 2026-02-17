FROM python:3.11-slim

WORKDIR /app

# Instala dependencias Python (Render usa requirements-render.txt com playwright)
COPY requirements-render.txt .
RUN pip install --no-cache-dir -r requirements-render.txt

# Instala Chromium + dependencias de sistema para Playwright
RUN playwright install --with-deps chromium

# Copia codigo do app
COPY . .

# Porta dinamica (Render define via $PORT)
EXPOSE 8501

CMD streamlit run Sistema_Pedagogico.py \
    --server.port=${PORT:-8501} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false
