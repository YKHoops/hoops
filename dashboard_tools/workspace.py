"""Allow the prepared refresh tools to use the complete local evidence workspace."""
import os
from pathlib import Path
ROOT=Path(os.environ.get('YK_DASHBOARD_WORKSPACE',Path(__file__).resolve().parents[1])).expanduser().resolve()
