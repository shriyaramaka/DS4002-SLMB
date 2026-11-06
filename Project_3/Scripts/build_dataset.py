"""Build a licensed bird identification dataset from iNaturalist public API.
Run from any directory: python Scripts/build_dataset.py
Uses a Virginia-clipped bounding box, not an official county definition.
One photo per observation; metadata-balanced observer-grouped splits; exact deduplication.
API calls are paced; existing responses/images are cached. No credentials required.
"""
from pathlib import Path
import argparse,csv,hashlib,json,time,random,datetime,urllib.request,urllib.parse
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
BASE='https://api.inaturalist.org/v1/'
LICENSES={'cc0':'https://creativecommons.org/publicdomain/zero/1.0/','cc-by':'https://creativecommons.org/licenses/by/4.0/','cc-by-sa':'https://creativecommons.org/licenses/by-sa/4.0/'}
# Fix the study area and observation-date cutoff for a reproducible snapshot.
FILTER={'taxon_id':3,'place_id':7,'swlat':36.54,'swlng':-83.68,'nelat':37.95,'nelng':-79.65,'quality_grade':'research','captive':'false','photos':'true','photo_license':','.join(LICENSES),'d2':'2026-11-05'}
# Retain the twelve species selected during the initial regional coverage audit.
IDS=[12727,9744,4956,9100,9083,17008,11901,12942,145310,8021,3454,144814]
# Preserve original API responses so a rerun does not silently change labels.
def fetch(url,path):
 if path.exists():return json.loads(path.read_text())
 for attempt in range(3):
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'DS4002-SouthwestVirginiaBirds-Pilot/0.1'})
   with urllib.request.urlopen(req,timeout=35) as r:data=json.load(r)
   path.write_text(json.dumps(data));time.sleep(1.1);return data
  except Exception:
   if attempt==2:raise
   time.sleep(2**attempt)
def table(path,rows):
 if not rows:return
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# Validate media before including a record in the final analysis table.
def download(row):
 path=ROOT/row['image_path'];path.parent.mkdir(exist_ok=True,parents=True)
 try:
  if not path.exists():
   req=urllib.request.Request(row['image_url'],headers={'User-Agent':'DS4002-Birds-Pilot/0.1'})
   with urllib.request.urlopen(req,timeout=30) as r:path.write_bytes(r.read())
  with Image.open(path) as im:im.verify()
  with Image.open(path) as im:row.update(width=im.width,height=im.height)
  row.update(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),download_status='ok')
 except Exception as e:row.update(width='',height='',sha256='',download_status=type(e).__name__)
 return row
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--per-species',type=int,default=60);args=parser.parse_args()
 raw=ROOT/'Data/raw';raw.mkdir(parents=True,exist_ok=True)
 url=BASE+'observations/species_counts?'+urllib.parse.urlencode(dict(FILTER,per_page=100))
 counts=fetch(url,raw/'species_counts.json')
 audit=[{'taxon_id':r['taxon']['id'],'scientific_name':r['taxon']['name'],'common_name':r['taxon'].get('preferred_common_name',''),'matching_observations':r['count'],'rank':r['taxon']['rank']} for r in counts['results']]
 table(ROOT/'Data/species_availability.csv',audit)
 rows=[];species=[]
 for taxon_id in IDS:
  params=dict(FILTER,taxon_id=taxon_id,per_page=200,order_by='id',order='desc')
  data=fetch(BASE+'observations?'+urllib.parse.urlencode(params),raw/f'observations_{taxon_id}_200.json')
  candidates=[]
  for o in data['results']:
   t=o.get('taxon',{})
   if t.get('rank')!='species' or t.get('id')!=taxon_id:continue
   if o.get('geoprivacy') in ('obscured','private') or o.get('taxon_geoprivacy') in ('obscured','private') or o.get('obscured'):continue
   photos=[p for p in o.get('photos',[]) if p.get('license_code') in LICENSES]
   if not photos:continue
   p=photos[0];user=o['user']['id'];n=int(hashlib.sha256(f'4002:{user}'.encode()).hexdigest(),16)%100
   date=o.get('observed_on') or ''
   candidates.append({'observation_id':o['id'],'photo_id':p['id'],'taxon_id':taxon_id,'scientific_name':t['name'],'common_name':t.get('preferred_common_name',''),'observed_on':date,'month':date[5:7] if len(date)>=7 else '', 'observer_id':user,'place_guess':o.get('place_guess',''),'quality_grade':o['quality_grade'],'photo_license':p['license_code'],'license_url':LICENSES[p['license_code']],'attribution':p.get('attribution',''),'observation_url':o.get('uri',f"https://www.inaturalist.org/observations/{o['id']}"),'photo_url':f"https://www.inaturalist.org/photos/{p['id']}",'image_url':p['url'].replace('/square.','/medium.'),'image_path':f"Data/images/{taxon_id}/{p['id']}.jpg",'provisional_split':'train' if n<70 else 'validation' if n<85 else 'test'})
  # Round-robin observers instead of letting prolific photographers dominate.
  from collections import defaultdict
  buckets=defaultdict(list)
  random.Random(4002+taxon_id).shuffle(candidates)
  for row in candidates:buckets[row['observer_id']].append(row)
  users=sorted(buckets);random.Random(4002+taxon_id).shuffle(users)
  chosen=[]
  for round_index in range(8):
   for user in users:
    if round_index<len(buckets[user]) and len(chosen)<args.per_species:chosen.append(buckets[user][round_index])
  rows+=chosen
  species.append({'taxon_id':taxon_id,'common_name':chosen[0]['common_name'] if chosen else '', 'api_matching_observations':data['total_results'],'eligible_in_latest_200':len(candidates),'selected':len(chosen)})
  print('Selected',taxon_id,len(chosen),'from',len(buckets),'observers',flush=True)
 with ThreadPoolExecutor(max_workers=4) as pool:
  downloaded=[]
  for i,r in enumerate(pool.map(download,rows),1):
   downloaded.append(r)
   if i%50==0:print('Downloaded/checked',i,'of',len(rows),flush=True)
  rows=downloaded
 # Keep one copy of each successfully decoded image byte sequence.
 seen=set();final=[]
 for r in rows:
  if r['download_status']!='ok':continue
  if r['sha256'] in seen:continue
  seen.add(r['sha256']);final.append(r)
 # Assign observer groups using metadata only, never model performance.
 import numpy as np
 users=sorted({r['observer_id'] for r in final}); taxa=sorted({r['taxon_id'] for r in final})
 matrix=np.array([[sum(r['observer_id']==u and r['taxon_id']==t for r in final) for t in taxa] for u in users])
 totals=matrix.sum(axis=0);rng=np.random.default_rng(4002);best=None
 for trial in range(5000):
  assignments=rng.choice(3,size=len(users),p=[.6,.2,.2])
  counts=np.array([matrix[assignments==k].sum(axis=0) for k in range(3)])
  loss=((counts/totals-np.array([.6,.2,.2])[:,None])**2).sum()+100*(counts<3).sum()
  if best is None or loss<best[0]:best=(loss,assignments.copy())
 mapping={u:['train','validation','test'][int(k)] for u,k in zip(users,best[1])}
 for r in final:r['split']=mapping[r['observer_id']];r.pop('provisional_split',None)
 for r in rows:
  r.pop('provisional_split',None);r.setdefault('split','')
 table(ROOT/'Data/download_manifest.csv',rows);table(ROOT/'Data/bird_images.csv',final);table(ROOT/'Data/selected_species.csv',species)
 summary={'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'filters':FILTER,'selected_taxon_ids':IDS,'rows_selected':len(rows),'usable_unique_images':len(final),'download_failures':sum(r['download_status']!='ok' for r in rows),'exact_duplicates_removed':sum(r['download_status']=='ok' for r in rows)-len(final),'observers':len({r['observer_id'] for r in final}),'species':len(set(r['taxon_id'] for r in final)),'split_counts':{s:sum(r['split']==s for r in final) for s in ['train','validation','test']}}
 (ROOT/'Output/build_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
