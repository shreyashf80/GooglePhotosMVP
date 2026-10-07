from datetime import datetime
from pathlib import Path
import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.data import PHOTOS
from app.search import parse
from app.tags import normalize

client=TestClient(app)

def search(query='cafe in Goa',**state):
    response=client.post('/api/search',json={'query':query,**state})
    assert response.status_code==200,response.text
    return response.json()

def hint(response,facet,label):
    return next(v['filter'] for row in response['hints'] if row['facet']==facet for v in row['values'] if v['label'].lower()==label.lower())

def test_hero_and_restoration():
    broad=search()
    assert broad['n_results']==12
    assert {r['facet'] for r in broad['hints']}=={'when','who','also'}
    feb=hint(broad,'when','February 2024')
    narrowed=search(filters=[feb])
    assert narrowed['n_results']==4
    assert 'd01' in [p['id'] for p in narrowed['results']]
    assert narrowed['hints']==[]
    assert search(filters=[])['n_results']==12

@pytest.mark.parametrize('facet,label,count',[('who','Rahul',5),('also','Outdoor Seating',6),('also','Coffee',8)])
def test_refinements(facet,label,count):
    filt=hint(search(),facet,label)
    refined=search(filters=[filt])
    assert refined['n_results']==count
    assert not any(v['filter'].get('value')==filt.get('value') for row in refined['hints'] for v in row['values'])
    assert search(filters=[])['n_results']==12

def test_combination():
    b=search();n=search(filters=[hint(b,'when','February 2024'),hint(b,'who','Rahul')])
    assert n['n_results']==2
    assert 'd01' in [p['id'] for p in n['results']]

@pytest.mark.parametrize('query,label,count',[('cafe in Goa 2025','2024',12),('cafe in Goa February 2025','Nov 2024',4)])
def test_nearest(query,label,count):
    miss=search(query)
    assert miss['n_results']==0
    nearest=miss['drop'][0]
    assert nearest['kind']=='nearest'
    assert nearest['action']['with']['label']==label
    recovered=search(query,concept_overrides=[nearest['action']['with']])
    assert recovered['n_results']==count
    removed=search(query,removed_concept_ids=[nearest['action']['concept_id']],concept_overrides=[nearest['action']['with']])
    assert removed['n_results']==12

def test_drop_unknown_and_concept_remove():
    miss=search('cafe in Goa snowy')
    drop=next(d for d in miss['drop'] if d['action'].get('concept_id')=='snowy')
    assert drop['count']==12
    assert search('cafe in Goa snowy',removed_concept_ids=['snowy'])['n_results']==12
    requested=search(want_drop=True)
    assert all(d['count']>12 for d in requested['drop'])

def test_removed_filter_options():
    f=hint(search(),'when','February 2024')
    response=search(filters=[f],want_drop=True)
    drop=next(d for d in response['drop'] if d['action']['type']=='remove_filter')
    assert drop['action']['index']==0
    assert drop['count']==12

def test_hint_bounds_and_common_exclusion():
    b=search()
    assert len(b['hints'])<=3
    assert all(len(row['values'])<=4 for row in b['hints'])
    assert not any(v['label'].lower() in {'friends','cafe','goa'} for row in b['hints'] for v in row['values'])
    assert [v['count'] for r in b['hints'] if r['facet']=='when' for v in r['values']]==[4,4,4]

def test_time_parsing_aliases_stopwords():
    assert search('café in Goa')['n_results']==12
    assert search('coffee shop in Goa')['n_results']==12
    assert search('medicine')['n_results']==4
    assert search('medication')['n_results']==4
    assert search('cafe in Goa feb')['n_results']==4
    assert len(parse('rahul feb 2024'))==2
    assert search('my photos in the')['message']=='Type something you remember about the photo.'
    assert search('my photos in the')['n_results']==0
    assert normalize('Christmas Trees')=='christmas tree'
    assert normalize('glass')=='glass'

def test_hints_off():
    assert search(hints_on=False)['n_results']==12
    assert search(hints_on=False)['hints']==[]
    assert search('cafe Goa 2025',hints_on=False)['drop']==[]

def test_gallery_detail_pagination_errors():
    assert client.get('/api/health').json()=={'ok':True}
    first=client.get('/api/photos?limit=5').json()
    second=client.get('/api/photos',params={'limit':5,'cursor':first['next_cursor']}).json()
    assert not set(p['id'] for p in first['items']) & set(p['id'] for p in second['items'])
    assert client.get('/api/photos/d01').json()['people_names']==['rahul']
    assert client.get('/api/photos/nope').status_code==404
    assert client.get('/api/photos?cursor=nope').status_code==400
    assert client.post('/api/search',json={'query':'cafe','filters':[{'facet':'when','level':'month','label':'bad','start':'bad','end':'bad'}]}).status_code==422

def test_fixture_and_assets():
    root=Path(__file__).resolve().parents[2]
    assert len(PHOTOS)==24 and len({p['id'] for p in PHOTOS})==24
    for p in PHOTOS:
        datetime.fromisoformat(p['taken_at'])
        assert (root/'frontend/public'/p['image_path'].lstrip('/')).read_bytes().startswith(b'\xff\xd8')


def test_phrase_hint_components_are_not_repeated():
    also=next(row for row in search()['hints'] if row['facet']=='also')
    labels={v['label'] for v in also['values']}
    assert 'Outdoor Seating' in labels
    assert not labels & {'Outdoor','Seating'}
    assert 'Pastry' in labels
