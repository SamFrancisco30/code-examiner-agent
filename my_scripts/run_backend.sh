SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "${SCRIPT_DIR}/../backend" || exit
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 
