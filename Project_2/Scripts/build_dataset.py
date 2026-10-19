"""Compile Charlottesville city crashes + ERA5 weather. Python 3.9+, no packages.

Usage: python3 build_dataset.py          # use bundled frozen source files
       python3 build_dataset.py --refresh # download sources, then rebuild
"""
import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parent
RAW=ROOT/'raw'
NY=ZoneInfo('America/New_York')
BASE='https://services.arcgis.com/p5v98VHDX9Atv3l7/arcgis/rest/services/Full_Crash/FeatureServer/0'
WHERE="PHYSICAL_JURIS = '104'"
START=dt.date(2017,1,1)
END=dt.date(2025,12,31)
WEATHER_PARAMS={'latitude':38.03,'longitude':-78.48,'start_date':'2016-12-01',
    'end_date':'2026-07-31','models':'era5',
    'daily':'temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,snowfall_sum,wind_speed_10m_max',
    'timezone':'America/New_York'}
FIELDS={'temperature_2m_max':'temp_max_c','temperature_2m_min':'temp_min_c',
    'temperature_2m_mean':'temp_mean_c','precipitation_sum':'precip_mm',
    'snowfall_sum':'snowfall_cm','wind_speed_10m_max':'wind_max_kmh'}

def fetch(url,params=None):
    if params: url+='?'+urllib.parse.urlencode(params)
    with urllib.request.urlopen(url,timeout=90) as response: data=json.load(response)
    if 'error' in data: raise RuntimeError(data['error'])
    return data

def save_json(path,value):
    path.write_text(json.dumps(value,indent=2),encoding='utf-8')

def save_csv(name,rows):
    if not rows: raise RuntimeError('Empty output '+name)
    with (ROOT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def refresh():
    RAW.mkdir(exist_ok=True)
    metadata=fetch(BASE,{'f':'json'})
    count=fetch(BASE+'/query',{'f':'json','where':WHERE,'returnCountOnly':'true'})['count']
    records=[]
    while len(records)<count:
        page=fetch(BASE+'/query',{'f':'json','where':WHERE,'outFields':'*',
            'returnGeometry':'false','orderByFields':'OBJECTID','resultOffset':len(records),
            'resultRecordCount':1000})
        batch=page.get('features',[])
        if not batch: raise RuntimeError('Incomplete paginated download')
        records.extend(batch)
    if len(records)!=count: raise RuntimeError('Record count changed during download')
    end_count=fetch(BASE+'/query',{'f':'json','where':WHERE,'returnCountOnly':'true'})['count']
    if end_count!=count: raise RuntimeError('Source changed during download; rerun')
    now=dt.datetime.now(dt.timezone.utc).isoformat()
    save_json(RAW/'crashes.json',{'features':records,'query_where':WHERE,'source_count':count,'retrieved_at_utc':now})
    save_json(RAW/'crash_metadata.json',metadata)
    url='https://archive-api.open-meteo.com/v1/archive?'+urllib.parse.urlencode(WEATHER_PARAMS)
    save_json(RAW/'weather.json',fetch(url))
    save_json(RAW/'weather_request.json',{'url':url,'parameters':WEATHER_PARAMS,
        'retrieved_at_utc':dt.datetime.now(dt.timezone.utc).isoformat()})

def build():
    source=json.loads((RAW/'crashes.json').read_text())
    metadata=json.loads((RAW/'crash_metadata.json').read_text())
    domains={f['name']:{str(v['code']):v['name'] for v in (f.get('domain') or {}).get('codedValues',[])}
        for f in metadata['fields']}
    domain_rows=[{'field':field,'code':code,'label':label} for field,mapping in domains.items()
        for code,label in mapping.items()]
    save_csv('source_codebook.csv',domain_rows)
    rows=[];seen={};excluded=[];duplicate_conflicts=[];time_issues=0
    for f in sorted(source['features'],key=lambda f:f['attributes']['OBJECTID']):
        a=f['attributes'];identifier=a.get('DOCUMENT_NBR')
        if str(a.get('PHYSICAL_JURIS'))!='104': raise RuntimeError('City filter violated')
        if identifier is None or a.get('CRASH_DT') is None:
            excluded.append({'object_id':a['OBJECTID'],'document_number':identifier,'reason':'missing ID or date'});continue
        key=str(identifier)
        if key in seen:
            other=seen[key]
            differing=[k for k in a if k!='OBJECTID' and a[k]!=other.get(k)]
            if differing:duplicate_conflicts.append({'document_number':key,'fields':differing})
            excluded.append({'object_id':a['OBJECTID'],'document_number':key,'reason':'duplicate document; lowest OBJECTID retained'});continue
        seen[key]=a
        # CRASH_DT is a date at local midnight, encoded as a UTC epoch instant.
        # Time of crash is a separate HHMM field; do not mistake midnight for crash time.
        local_date=dt.datetime.fromtimestamp(a['CRASH_DT']/1000,dt.timezone.utc).astimezone(NY).date()
        raw_time=a.get('CRASH_MILITARY_TM');clock=None;hour=None
        if isinstance(raw_time,(int,float)) and float(raw_time).is_integer():
            hh,mm=divmod(int(raw_time),100)
            if 0<=hh<24 and 0<=mm<60:clock=f'{hh:02d}:{mm:02d}';hour=hh
        if clock is None:time_issues+=1
        def label(field):return domains.get(field,{}).get(str(a.get(field)))
        rows.append({'crash_id':key,'source_object_id':a['OBJECTID'],'date_local':local_date.isoformat(),
            'time_local_hhmm':clock,'time_raw_hhmm':raw_time,'hour_local':hour,
            'year':local_date.year,'month':local_date.month,'weekday_mon0':local_date.weekday(),
            'is_weekend':int(local_date.weekday()>=5),'physical_jurisdiction_code':'104',
            'physical_jurisdiction':'City of Charlottesville','latitude':a.get('LAT'),'longitude':a.get('LON'),
            'street_source':a.get('ROUTE_OR_STREET_NM'),'severity_code':a.get('CRASH_SEVERITY'),
            'severity_label':label('CRASH_SEVERITY'),'persons_killed':a.get('K_PEOPLE'),
            'persons_injured':a.get('PERSONS_INJURED'),'vehicles_involved':a.get('VEH_COUNT'),
            'pedestrians_killed':a.get('PEDESTRIANS_KILLED'),'pedestrians_injured':a.get('PEDESTRIANS_INJURED'),
            'collision_type_code':a.get('COLLISION_TYPE'),'collision_type_label':label('COLLISION_TYPE'),
            'reported_weather_code':a.get('WEATHER_CONDITION'),'reported_weather_label':label('WEATHER_CONDITION'),
            'road_surface_code':a.get('ROADWAY_SURFACE_COND'),'road_surface_label':label('ROADWAY_SURFACE_COND'),
            'light_condition_code':a.get('LIGHT_CONDITION'),'light_condition_label':label('LIGHT_CONDITION'),
            'record_period_status':'complete_calendar_year' if START<=local_date<=END else 'partial_2026',
            'source_ref':'[1],[2]'})
    rows.sort(key=lambda r:(r['date_local'],r['time_local_hhmm'] or '',r['crash_id']))
    save_csv('cville_crash_incidents.csv',rows)
    if excluded:save_csv('excluded_records.csv',excluded)
    wsource=json.loads((RAW/'weather.json').read_text()); wd=wsource['daily']
    weather={}
    for i,date in enumerate(wd['time']):
        weather[date]={'date_local':date,**{alias:wd[field][i] for field,alias in FIELDS.items()},'source_ref':'[3]'}
    save_csv('cville_weather_daily.csv',list(weather.values()))
    crash_by_day=collections.defaultdict(list)
    for r in rows:crash_by_day[r['date_local']].append(r)
    panel=[];history=[];weather_misses=0
    for index in range((END-START).days+1):
        day=START+dt.timedelta(days=index);key=day.isoformat();events=crash_by_day[key]
        observed=weather.get(key,{});lag_weather=weather.get((day-dt.timedelta(days=7)).isoformat(),{})
        if not observed:weather_misses+=1
        def total(field):return sum(r[field] for r in events if r[field] is not None)
        p={'date_local':key,'year':day.year,'month':day.month,'day_of_month':day.day,
            'weekday_mon0':day.weekday(),'is_weekend':int(day.weekday()>=5),
            'day_of_year':day.timetuple().tm_yday,
            'month_sin':round(math.sin(2*math.pi*(day.month-1)/12),6),
            'month_cos':round(math.cos(2*math.pi*(day.month-1)/12),6),
            'crash_count':len(events),'injury_crash_count':sum((r['persons_injured'] or 0)>0 for r in events),
            'fatal_crash_count':sum((r['persons_killed'] or 0)>0 for r in events),
            'persons_injured':total('persons_injured'),'persons_killed':total('persons_killed'),
            'crash_count_lag1':history[-1] if len(history)>=1 else None,
            'crash_count_lag7':history[-7] if len(history)>=7 else None,
            'crash_count_lag14':history[-14] if len(history)>=14 else None,
            'crash_count_prior7_mean':round(sum(history[-7:])/7,6) if len(history)>=7 else None,
            'crash_count_prior28_mean':round(sum(history[-28:])/28,6) if len(history)>=28 else None,
            **{'observed_'+name:observed.get(name) for name in FIELDS.values()},
            **{name+'_lag7':lag_weather.get(name) for name in FIELDS.values()},
            'coverage_status':'complete_calendar_year_range; source_completeness_unverified',
            'source_ref':'[1],[2],[3]'}
        panel.append(p);history.append(len(events))
    save_csv('cville_daily_crashes_weather.csv',panel)
    annual=[{'year':int(y),'observed_crash_count':n,
        'period_status':'partial_through_July_31' if y=='2026' else 'complete_calendar_year_range'}
        for y,n in sorted(collections.Counter(str(r['year']) for r in rows).items())]
    save_csv('annual_crash_counts.csv',annual)
    modeling=[r for r in rows if START.isoformat()<=r['date_local']<=END.isoformat()]
    if sum(p['crash_count'] for p in panel)!=len(modeling):raise RuntimeError('Daily counts do not reconcile')
    if len(rows)!=len({r['crash_id'] for r in rows}):raise RuntimeError('Duplicate clean IDs')
    if len(source['features'])!=source['source_count']:raise RuntimeError('Raw count mismatch')
    quality={'city':'City of Charlottesville, Virginia','filter':WHERE,
        'source_rows':len(source['features']),'clean_incident_rows':len(rows),'excluded_rows':len(excluded),
        'duplicate_conflicts':duplicate_conflicts,'invalid_or_missing_hhmm':time_issues,
        'earliest_crash_date':rows[0]['date_local'],'latest_crash_date':rows[-1]['date_local'],
        'modeling_start':START.isoformat(),'modeling_end':END.isoformat(),'modeling_incidents':len(modeling),
        'daily_panel_rows':len(panel),'weather_source_rows':len(weather),'unmatched_weather_days':weather_misses,
        'crashes_by_year':annual,'missing_values_incident_fields':{k:sum(r[k] is None for r in rows) for k in rows[0]},
        'weather_missing_values':{k:sum(w.get(k) is None for w in weather.values()) for k in FIELDS.values()},
        'weather_grid':{k:wsource.get(k) for k in ['latitude','longitude','elevation','timezone']},
        'weather_units':wsource.get('daily_units'),'weather_model_requested':'era5',
        'reporting_completeness':'not independently verified','built_at_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
    save_json(ROOT/'quality_report.json',quality)
    save_json(ROOT/'provenance.json',{'crash_source_url':BASE,'query':WHERE,
        'crash_retrieved_at_utc':source.get('retrieved_at_utc'),
        'weather_request':json.loads((RAW/'weather_request.json').read_text()),
        'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(RAW.glob('*.json'))}})
    print(json.dumps({k:quality[k] for k in ['clean_incident_rows','modeling_incidents','daily_panel_rows',
        'excluded_rows','invalid_or_missing_hhmm','unmatched_weather_days','earliest_crash_date','latest_crash_date']},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--refresh',action='store_true');args=parser.parse_args()
    if args.refresh:refresh()
    build()
