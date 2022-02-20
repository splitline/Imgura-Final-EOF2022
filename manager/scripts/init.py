import secrets
import json
import os


def generate_flag():
    return "EOF{%s}" % secrets.token_hex(32)


if __name__ == "__main__":
    print("Initializing teams...")
    TEAMS = list(map(int, json.load(open("/manager/teams.json")).keys()))
    score_json = {}
    for team_id in TEAMS:
        score_json[str(team_id)] = {
            "attack": 0,
            "defense": 0
        }
        team_file = "/manager/teams/team-%s.json" % team_id
        json.dump({
            "id": team_id,
            "lastRestart": 0,
            "lastPatch": 0,
            "attacked": []
        }, open(team_file, 'w'), indent=4)

        flag_file = '/service/files/flag_%s' % team_id
        open(flag_file, 'w').write(generate_flag())
        
        waf_file = '/service/files/waf_%s.php' % team_id
        if os.path.exists(waf_file) == False:
            waf_file = '/service/files/waf_%s.php' % team_id
            open(waf_file, 'w').write("<?php // Your WAF goes here")

        port = 30000+int(team_id)
        os.system(f"/manager/start.sh {team_id} {port}")

    if os.path.exists("/manager/score.json") == False:
        open("/manager/score.json", 'w').write(json.dumps(score_json, indent=4))

