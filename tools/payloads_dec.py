"""Print Metricool payloads for one day of the December plan. Usage: payloads_dec.py SHA DAY"""
import json, sys, datetime
from plan_dec import plan, START
sha, day = sys.argv[1], int(sys.argv[2])
date = (START + datetime.timedelta(days=day)).isoformat()
RAW = f"https://raw.githubusercontent.com/desireekaidi/kirtantutorials-posts/{sha}/"
base = dict(autoPublish=True, draft=False, descendants=[], firstCommentText="", hasNotReadNotes=False, shortener=False, smartLinkData={"ids": []}, mediaAltText=[])
def later(t):
    h, m = map(int, t.split(":")); m += 30
    return f"{h + m // 60:02d}:{m % 60:02d}"
for i in plan():
    if i["date"] != date: continue
    ig = dict(base, providers=[{"network": "instagram"}], publicationDate={"dateTime": f"{date}T{i['time']}:00", "timezone": "Europe/Tirane"},
              media=[RAW + i["video"]], videoThumbnailUrl=RAW + i["cover_png"], text=i["caption"],
              instagramData={"type": "TRIAL_REEL", "isAiGenerated": False, "audioConfiguration": {"audioId": i["audio_id"]}, "shareTrialAutomatically": False})
    print("IG", f"{date}T{i['time']}:00+01:00", json.dumps(ig, ensure_ascii=False))
    for lang, t in (("en", i["time"]), ("de", later(i["time"]))):
        pin = dict(base, providers=[{"network": "pinterest"}], publicationDate={"dateTime": f"{date}T{t}:00", "timezone": "Europe/Tirane"},
                   media=[RAW + i[f"pin_{lang}"]], text=i[f"desc_{lang}"],
                   pinterestData={"boardId": i[f"board_{lang}"], "pinTitle": i[f"title_{lang}"], "pinLink": i[f"link_{lang}"], "pinNewFormat": True, "isAiGenerated": False, "isAiGeneratedPerson": False})
        print("PIN", f"{date}T{t}:00+01:00", json.dumps(pin, ensure_ascii=False))
