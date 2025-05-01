SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "${SCRIPT_DIR}/../backend" || exit
docker-compose up -d || exit
source venv/bin/activate
cd ".."
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000