from datetime import datetime, timedelta

# Mock curfew time (for demo purposes)
CURFEW_START = datetime.now().replace(second=0, microsecond=0) # active attedance window demo

# This makes the curfew end 10 minutes ago
# CURFEW_START = datetime.now() - timedelta(minutes=40) 

CURFEW_WINDOW_MINUTES = 30


def is_within_curfew():
    now = datetime.now()
    return CURFEW_START <= now <= CURFEW_START + timedelta(minutes=CURFEW_WINDOW_MINUTES)


def is_curfew_over():
    now = datetime.now()
    return now > CURFEW_START + timedelta(minutes=CURFEW_WINDOW_MINUTES)