"""
utc 8
待解
"""

from datetime import datetime
from traceback import format_exc
import os

import requests
import pandas as pd


def send_msg_to_LINE(msg):
    """
    """
    # LINE Notify 權杖
    try:
        token = os.environ["LINE_API_TOKEN"]
    except KeyError:
        raise ValueError('The ENV LINE_API_TOKEN does not exist!')

    # HTTP 標頭參數與資料
    headers = {"Authorization": "Bearer " + token}
    data = {'message': msg}

    # 以 requests 發送 POST 請求
    resp = requests.post(
        url="https://notify-api.line.me/api/notify",
        headers=headers,
        data=data)

    return resp.text


def parse_resp_by_sport(sport_code=443):
    """
    - 棒球 443
    - 籃球 442
    - 足球 441; 會多1個欄位: 和局
    """
    resp = requests.get(f'https://blob.sportslottery.com.tw/apidata/Pre/ListBySport/{sport_code}.json')
    etl_dttm = datetime.now().strftime(r'%Y-%m-%d %H:%M:%S')
    data = resp.json()
    output = []
    for game_dict in data:
        idx = game_dict['id']
        sport = game_dict['ln'][0]
        team_away = game_dict['atn']
        team_home = game_dict['htn']
        odd_info = game_dict['ms'][0]['cs'][0]
        odd_away = odd_info[0]['o']
        odd_home = odd_info[1]['o']
        output.append({
            'idx': idx,
            'sport': sport,
            'team_away': team_away,
            'team_home': team_home,
            'odd_away': odd_away,
            'odd_home': odd_home,
            'etl_dttm': etl_dttm
        })
    df_output = pd.DataFrame(output)
    return df_output


def main():
    try:
        # crawler
        df_output = parse_resp_by_sport(sport_code=443)
        df_output['name_away'] = df_output['team_away'].apply(lambda x: x[1])
        df_output['name_home'] = df_output['team_home'].apply(lambda x: x[1])
        df_output = df_output.drop(['team_away', 'team_home'], axis=1)
        df_output_new = df_output[['idx', 'sport', 'name_away', 'odd_away', 'odd_home', 'name_home', 'etl_dttm']]
        df_output_new.to_csv(f'twsl_baseball_odds_new.csv', encoding='utf-8-sig', index=False)

        # produce file
        df_base = pd.read_csv('twsl_baseball_odds_base.csv', encoding='utf-8-sig')
        df_output_done_all = pd.concat([df_base, df_output_new])
        assert (df_base.shape[0] + df_output_new.shape[0]) == df_output_done_all.shape[0]
        df_base.to_csv(f'twsl_baseball_odds_backup.csv', encoding='utf-8-sig', index=False)
        df_output_done_all.to_csv(f'twsl_baseball_odds_base.csv', encoding='utf-8-sig', index=False)

        msg = f"""爬取台灣運彩賠率資料成功: \n
            原資料量:{df_base.shape[0]},\n
            新資料量:{df_output_new.shape[0]},\n
            總資料量: {df_output_done_all.shape[0]}"""
        send_msg_to_LINE(msg)
    except Exception:
        msg = f'爬取台灣運彩賠率資料失敗: {format_exc()}'
        send_msg_to_LINE(msg)


if __name__ == '__main__':
    main()
