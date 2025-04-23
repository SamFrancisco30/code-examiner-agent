SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "${SCRIPT_DIR}/../backend" || exit
docker-compose up -d || exit
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 
