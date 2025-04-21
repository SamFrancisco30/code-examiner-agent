SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "${SCRIPT_DIR}/../frontend" || exit
pnpm install
pnpm run dev
