import requests
from dotenv import load_dotenv
from os import environ
import re
load_dotenv()


def getBeatmapInfo(beatmapId, mods=[]):
    info = dict()
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + environ["OSU_TOKEN"]
    }
    payload = {
        "mods": mods,
        "ruleset": "osu"
    }
    infoRes = requests.get(
        environ["BASE_URL"] + f"/beatmaps/{beatmapId}", headers=headers).json()
    attributeRes = requests.post(
        environ["BASE_URL"] + f"/beatmaps/{beatmapId}/attributes", headers=headers, json=payload).json()["attributes"]

    hpMod = 1
    csMod = 1
    bpmMod = 1
    if "HR" in mods:
        hpMod *= 1.4
        csMod *= 1.3
    if "EZ" in mods:
        hpMod *= 0.5
        csMod *= 0.5
    if "DT" in mods:
        bpmMod *= 1.5
    if "HT" in mods:
        bpmMod *= 0.75

    info["id"] = infoRes["id"]
    info["mapset_id"] = infoRes["beatmapset"]["id"]
    info["cover_url"] = infoRes["beatmapset"]["covers"]["cover"]
    info["artist"] = infoRes["beatmapset"]["artist"].replace("\"", "'")
    info["title"] = infoRes["beatmapset"]["title"].replace("\"", "'")
    info["diff_name"] = infoRes["version"]
    info["star_rating"] = round(attributeRes["star_rating"], 1)
    info["ar"] = round(attributeRes["approach_rate"], 1)
    info["od"] = round(attributeRes["overall_difficulty"], 1)
    info["hp"] = round(min(infoRes["drain"] * hpMod, 10), 1)
    info["cs"] = round(min(infoRes["cs"] * csMod, 10), 1)
    info["bpm"] = round(infoRes["bpm"] * bpmMod, 1)
    info["length"] = f"{int((infoRes['total_length'] / bpmMod) / 60)}:{round((infoRes['total_length'] / bpmMod) % 60):02d}"
    info["mods"] = mods
    info["url"] = f"https://osu.ppy.sh/beatmapsets/{info['mapset_id']}#osu/{info['id']}"

    return info


def parseURL(url):
    return re.findall(r'\d+', url)[-1]


def parseMods(mods):
    res = []
    if re.search(r'hr', mods.lower()):
        res.append('HR')
    if re.search(r'hd', mods.lower()):
        res.append('HD')
    if re.search(r'dt', mods.lower()):
        res.append('DT')
    if re.search(r'ez', mods.lower()):
        res.append('EZ')

    return res


def generate_pool(urls):
    modCounter = {}
    pool = list(filter(None, (line.rstrip() for line in urls)))
    with open("pool.txt", "w+") as output:
        output.write(
            "Mod\tCover\tSong Name\tDifficulty\tStar Rating\tLength\tBPM\tCS\tHP\tAR\tOD\tBeatmap ID\n")
        for beatmap in pool:
            beatmapId = re.findall(r'\d+', beatmap)[-1]
            mod = beatmap[:2].upper()
            if modCounter.get(mod) == None:
                modCounter[mod] = 0
            modCounter[mod] += 1
            mods = []
            if mod != "FM" and mod != "NM" and mod != "TB":
                mods.append(mod)
            info = getBeatmapInfo(beatmapId, mods)

            t = '\t'
            fBanner = f"=IMAGE(\"{info['cover_url']}\")"
            fTitle = f"=HYPERLINK(\"https://osu.ppy.sh/beatmaps/{beatmapId}\", \"{info['artist']} - {info['title']}\")"
            fMod = f"{mod}{modCounter[mod]}"
            print(f"Processed: {fMod}")
            output.write(fMod + t
                         + fBanner + t
                         + fTitle + t
                         + info['diff_name'] + t
                         + str(info['star_rating']) + t
                         + str(info['length']) + t
                         + str(info['bpm']) + t
                         + str(info['cs']) + t + str(info['hp']) + t +
                         str(info['ar']) + t + str(info['od']) + t
                         + beatmapId
                         + '\n')
