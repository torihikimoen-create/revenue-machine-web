import os
import sys
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from scripts.trial_tracker import get_active_trial_count

try:
    count = get_active_trial_count()
    print(f"CURRENT_ACTIVE_TRIALS_COUNT: {count}")
except Exception as e:
    print(f"ERROR_FETCHING_STATS: {e}")
