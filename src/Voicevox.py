import datetime as dt
from enum import auto, Enum
import json
from queue import Queue
import requests as rq
from threading import Thread
from typing import Dict, Optional
import ulid

from src.db.Models.Preference import Preference
from src.db.Database import Session

class Vvox_status(Enum):
    Accepted = auto()
    Queried = auto()
    Synthesized = auto()

class Vvox_req:
    def __init__(self, uid: str, sid: str, dt: dt.datetime, text: str) -> None:
        self.user_id = uid
        self.server_id = sid
        self.created_at = dt
        self.text = text
        self.preference:Preference = Session.query(Preference)\
                                            .filter(Preference.user_id == uid,
                                                    Preference.server_id == sid)\
                                            .first()
        if self.preference is None:
            p = Preference()
            p.user_id = uid
            p.server_id = sid
            Session.add(p)
            Session.commit()
            self.preference = p
    
        self.status = Vvox_status.Accepted
    
    def audio_query(self) -> Dict:
        headers = {"accept":"application/json"}
        speaker = self.preference.speaker
        res = rq.post(
                f"http://127.0.0.1:50021/audio_query?text={self.text}&speaker={speaker}",
                headers=headers
            )
        self.query = res.json()
        self.set_preferences()
        # print(self.query)
        self.status = Vvox_status.Queried

    def set_preferences(self):
        self.query["speedScale"] = self.preference.speed
        self.query["pitchScale"] = self.preference.pitch
        self.query["intonationScale"] = self.preference.intonation
        self.query["volumeScale"] = self.preference.volume
        self.query["postPhonemeLength"] = 0.2

    def synthesis(self):
        headers = {
            "accept":"audio/wav",
            "Content-Type":"application/json"
        }
        speaker = self.preference.speaker
        res = rq.post(
                f"http://127.0.0.1:50021/synthesis?speaker={speaker}",
                data=json.dumps(self.query),
                headers=headers
            )
        
        self.tmp_file_name = "tmp/" + ulid.new().str + ".wav"
        with open(self.tmp_file_name, mode="bx") as f:
             f.write(res.content)

        self.status = Vvox_status.Synthesized


def test():
    text = "テストメッセージ"
    d = dt.datetime.now()
    v = Vvox_req(0, 0, d, text)
    v.audio_query()
    v.synthesis()

if __name__ == "__main__":
    test()