import json
from datetime import datetime
from traceback import format_exc
import requests
import pandas as pd

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
        try:
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
        except IndexError:
            print(sport)
            continue
        except KeyError:
            print(sport)
            continue
    df_output = pd.DataFrame(output)
    return df_output
 
if __name__ == '__main__':
  df_output = parse_resp_by_sport(sport_code=443)
  df_mlb = df_output[df_output['sport']=='美國職棒']
  df_mlb['name_away'] = df_mlb['team_away'].apply(lambda x: x[1])
  df_mlb['name_home'] = df_mlb['team_home'].apply(lambda x: x[1])
  df_mlb = df_mlb.drop(['team_away', 'team_home'], axis=1)
  df_mlb = df_mlb[['idx', 'sport', 'name_away', 'odd_away', 'odd_home', 'name_home', 'etl_dttm']]
  df_mlb.to_csv('mlb_odds.csv', encoding='utf-8-sig')
