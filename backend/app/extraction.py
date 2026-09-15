import re
from .nlp import NLP
from .llm import get_llm_provider
PATTERNS=[('Phone',r'\b(?:\+91[- ]?)?[6-9]\d{9}\b'),('Vehicle',r'\b[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{4}\b'),('Account',r'\b\d{9,18}\b')]
KNOWN_PEOPLE=['Rohan Mehta','Vikram Shah','Ayesha Khan']; KNOWN_ORGS=['Orion Logistics']; KNOWN_LOCATIONS=['Eastern Freight Warehouse','Sector 18, Noida','Cafe Meridian, Noida']
def slug(v): return re.sub(r'[^a-z0-9]+','-',v.lower()).strip('-')
def entity(label,kind,confidence): return {'id':f'{kind.lower()}:{slug(label)}','label':label,'type':kind,'confidence':confidence}
def extract(text):
    entities=[]
    for kind,pattern in PATTERNS: entities += [entity(m.group(),kind,.96) for m in re.finditer(pattern,text,re.I)]
    for kind,values in [('Person',KNOWN_PEOPLE),('Organization',KNOWN_ORGS),('Location',KNOWN_LOCATIONS)]: entities += [entity(v,kind,.9) for v in values if v.lower() in text.lower()]
    for ent in NLP(text).ents:
        kind={'PERSON':'Person','ORG':'Organization','GPE':'Location','LOC':'Location'}.get(ent.label_)
        if kind and len(ent.text.strip())>2: entities.append(entity(ent.text.strip(),kind,.7))
    llm=get_llm_provider().extract(text)
    if llm:
        for item in llm.get('entities',[]):
            if item.get('label') and item.get('type') in {'Person','Phone','Vehicle','Location','Account','Organization','Event'}: entities.append(entity(item['label'],item['type'],float(item.get('confidence',.7))))
    entities=list({e['id']:e for e in entities}.values()); by_label={e['label'].lower():e for e in entities}; relations=[]
    people=[e for e in entities if e['type']=='Person']; targets=[e for e in entities if e['type'] in {'Phone','Vehicle','Location'}]
    if len(people)>1: relations.append({'source':people[0]['id'],'target':people[1]['id'],'type':'ASSOCIATED_WITH','confidence':.65})
    for p in people:
        for target in targets: relations.append({'source':p['id'],'target':target['id'],'type':'MENTIONED_WITH','confidence':.55})
    if llm:
        for r in llm.get('relationships',[]):
            a=by_label.get(str(r.get('source_label','')).lower()); b=by_label.get(str(r.get('target_label','')).lower())
            if a and b and a['id']!=b['id']: relations.append({'source':a['id'],'target':b['id'],'type':str(r.get('type','RELATED_TO')).upper()[:40],'confidence':float(r.get('confidence',.7))})
    return {'entities':entities,'relationships':list({(r['source'],r['target'],r['type']):r for r in relations}.values()),'engine':'Gemini + spaCy + deterministic rules' if llm else 'spaCy + deterministic rules','llmUsed':bool(llm)}
