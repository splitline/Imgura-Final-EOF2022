import os
import os.path
import secrets
import json
import requests
import shutil
import asyncio

from datetime import timezone, datetime, timedelta

from checker import check_all

os.chdir('/manager/')

# ========= CONSTANTS =========

chal_id = int(os.getenv("CHALLENGE_ID", 1))
chal_token = os.getenv("CHALLENGE_TOKEN", "")
ctfd_host = os.getenv('CTFD_HOST', 'http://127.0.0.1:4000')

# ==============================

round_id = datetime.now(tz=timezone(timedelta(hours=+8))
                        ).strftime('%Y%m%d-%H-%M')
if not os.path.exists(f"rounds/{round_id}/"):
    os.mkdir(f"rounds/{round_id}/", )

teams = json.load(open("/manager/teams.json"))
all_team_id = list(map(int, teams.keys()))
total_score = json.load(open("/manager/score.json"))


def generate_flag():
    return "EOF{%s}" % secrets.token_hex(32)


def service_check(team_ids):
    urls = map(
        lambda port: f"http://127.0.0.1:{30000+port}",
        team_ids
    )
    res = asyncio.run(check_all(urls))
    ret = {"passed": [], "failed": []}
    for team_id, status in zip(team_ids, res):
        if status:
            ret["passed"].append(team_id)
        else:
            ret["failed"].append(team_id)
    return ret


if __name__ == "__main__":
    print(f"Updating {round_id}...")

    is_attacking = False
    scoreboard_data = {}
    service_check_queue = list(all_team_id)

    # initialize data
    for team_id in all_team_id:
        scoreboard_data[team_id] = {
            "id": team_id,
            "name": teams[str(team_id)]["name"],
            'attack': [],
            'defense': True,
            'alive': None,
            "score": {
                "attack": total_score[str(team_id)]["attack"],
                "defense": total_score[str(team_id)]["defense"]
            }
        }

    # check attack / defense
    for team_id in all_team_id:
        team_file = 'teams/team-%s.json' % team_id
        shutil.copy(team_file, 'rounds/%s/team-%s.json' % (round_id, team_id))
        data = json.load(open(team_file))

        scoreboard_data[team_id]['attack'] = list(data['attacked'])
        scoreboard_data[team_id]['score']['attack'] += round(
            len(data['attacked']) * 0.6)
        print(f"Team {team_id} attacked: {data['attacked']}")

        for victim_id in data['attacked']:
            is_attacking = True
            scoreboard_data[victim_id]['defense'] = False

        if (datetime.now()-datetime.fromtimestamp(data['lastPatch']/1000)).seconds < 60*5:
            print(
                f"Team {team_id} updated WAF in this 5 mins, can't get dfs pts")
            scoreboard_data[team_id]['defense'] = False
            if team_id in service_check_queue:
                service_check_queue.remove(team_id)

        elif (datetime.now()-datetime.fromtimestamp(data['lastRestart']/1000)).seconds < 60*5:
            print(f"Team {team_id} restarted in this 5 mins, can't get dfs pts")
            scoreboard_data[team_id]['defense'] = False
            if team_id in service_check_queue:
                service_check_queue.remove(team_id)

        data['attacked'] = []
        open(team_file, 'w').write(json.dumps(data, indent=4))

    if not is_attacking:
        print("No one got attacked.")
        for team_id in all_team_id:
            scoreboard_data[team_id]['defense'] = False

        service_check_queue = []

    # check service
    result = service_check(list(service_check_queue))
    print("Service check result:", result)

    for team_id in result['passed']:
        scoreboard_data[team_id]['alive'] = True

    for team_id in result['failed']:
        scoreboard_data[team_id]['defense'] = False
        scoreboard_data[team_id]['alive'] = False

    # update defense points
    for team_id, data in scoreboard_data.items():
        if data['defense']:
            data['score']['defense'] += 7

    # generate new flag
    for team_id in all_team_id:
        flag_file = '/service/files/flag_%s' % team_id
        open(flag_file, 'w').write(generate_flag())

    with open("public/scoreboard.json", 'w') as f:
        json.dump({
            "round": round_id,
            "teams": scoreboard_data
        }, f, indent=4)

    with open('/manager/score.json', 'w') as f:
        json.dump({
            str(team_id): {
                "attack": data["score"]["attack"],
                "defense": data["score"]["defense"]
            } for team_id, data in scoreboard_data.items()
        }, f, indent=4)
    
    shutil.copy('/manager/public/scoreboard.json', 'rounds/%s/scoreboard.json' % (round_id))
    shutil.copy('/manager/score.json', 'rounds/%s/score.json' % (round_id))

    submit = {
        "id": chal_id,
        "token": chal_token,
        "attacks": {
            team_id: round(len(data['attack']) * 0.6) for team_id, data in scoreboard_data.items()
        },
        "defenses": [
            team_id for team_id, data in scoreboard_data.items() if data['defense']
        ]
    }
    print("Submitting:", submit)
    api_endpoint = f"{ctfd_host}/plugins/awd/api/update"
    res = requests.post(api_endpoint, json=submit, verify=False).json()
    if res['success']:
        print("[+] Update successful")
    else:
        print('[x] Update failed:', res['message'])
