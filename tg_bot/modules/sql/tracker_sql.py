import threading
from sqlalchemy import Column, String
from tg_bot.modules.sql import BASE, SESSION

class Tracker(BASE):
    __tablename__ = "tracker"
    tracked_chat_id = Column(String(255), primary_key=True)
    log_group_id = Column(String(255), nullable=False)

    def __init__(self, tracked_chat_id, log_group_id):
        self.tracked_chat_id = str(tracked_chat_id)
        self.log_group_id = str(log_group_id)

Tracker.__table__.create(checkfirst=True)

TRACK_LOCK = threading.RLock()

def add_track(tracked_chat_id, log_group_id):
    with TRACK_LOCK:
        track = SESSION.query(Tracker).get(str(tracked_chat_id))
        if not track:
            track = Tracker(str(tracked_chat_id), str(log_group_id))
        else:
            track.log_group_id = str(log_group_id)
        SESSION.add(track)
        SESSION.commit()

def remove_track(tracked_chat_id):
    with TRACK_LOCK:
        track = SESSION.query(Tracker).get(str(tracked_chat_id))
        if track:
            SESSION.delete(track)
            SESSION.commit()
            return True
        return False

def get_log_group(tracked_chat_id):
    try:
        track = SESSION.query(Tracker).get(str(tracked_chat_id))
        if track:
            return track.log_group_id
        return None
    finally:
        SESSION.close()
