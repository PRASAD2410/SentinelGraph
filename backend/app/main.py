import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[2]/'.env')
import networkx as nx
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .extraction import extract
from .neo_store import NeoStore
from .file_reader import read_upload
from .llm import get_llm_provider

app=FastAPI(title='SentinelGraph API',version='0.2.0')
app.add_middleware(CORSMiddleware,allow_origins=[os.getenv('FRONTEND_ORIGIN','http://localhost:5173')],allow_methods=['*'],allow_headers=['*'])
# Start every local session with an empty case. Findings are created only from
# the reports and documents the investigator submits in that session.
nodes={}; edges=[]; reports=[]; neo=NeoStore()
class Ingest(BaseModel): text:str=Field(min_length=15); title:str='Investigator submitted report'; date:str|None=None
class Question(BaseModel): question:str=Field(min_length=2,max_length=1000)
def graph():
 g=nx.Graph(); g.add_nodes_from(nodes); g.add_edges_from((e['source'],e['target']) for e in edges); return g
def analytics():
 g=graph()
 if not g:return []
 degree=nx.degree_centrality(g); between=nx.betweenness_centrality(g); pagerank=nx.pagerank(g)
 return sorted([{'id':i,'label':nodes[i]['label'],'type':nodes[i]['type'],'degree':round(degree.get(i,0),3),'betweenness':round(between.get(i,0),3),'pagerank':round(pagerank.get(i,0),3)} for i in g.nodes],key=lambda x:(x['pagerank'],x['degree']),reverse=True)
def evidence(a,b): return sorted({e['reportId'] for e in edges if {e['source'],e['target']}=={a,b}})
def leads():
 g=graph(); out=[]; bridges=nx.betweenness_centrality(g)
 for node in g.nodes:
  links=list(g.neighbors(node)); kinds={nodes[n]['type'] for n in links}; names=', '.join(nodes[n]['label'] for n in links[:4]); sources=sorted({rid for n in links for rid in evidence(node,n)})
  if len(links)>=3: out.append({'severity':'high','title':f"Cross-domain linkage: {nodes[node]['label']}",'entity':nodes[node]['label'],'reason':f"Reported alongside {len(links)} linked entities ({names}) across {len(kinds)} categories. Sources: {', '.join(sources) or 'review pending'}.",'rule':'Entity links across three or more records/categories','sources':sources})
  if bridges.get(node,0)>=.12: out.append({'severity':'medium','title':f"Potential network bridge: {nodes[node]['label']}",'entity':nodes[node]['label'],'reason':'Connects otherwise separate parts of the reported network. Review underlying source context before any action.','rule':'High betweenness centrality','sources':sources})
 for a,b in g.edges:
  common=list(nx.common_neighbors(g,a,b))
  if common:
   shared=nodes[common[0]]['label']; sources=sorted(set(evidence(a,common[0])+evidence(b,common[0])))
   out.append({'severity':'medium','title':f"Shared reported association: {nodes[a]['label']} and {nodes[b]['label']}",'entity':f"{nodes[a]['label']} ↔ {nodes[b]['label']}",'reason':f"Both are linked to {shared}. Validate whether this is a meaningful connection or incidental overlap. Sources: {', '.join(sources)}.",'rule':'Common-neighbor pattern','sources':sources})
 return out[:12]
def process(text,title,source,date=None):
 result=extract(text); report_id=f'USR-{len(reports)+1:03d}'; date=date or datetime.now().date().isoformat(); reports.append({'id':report_id,'date':date,'title':title,'text':text,'source':source})
 for e in result['entities']: nodes.setdefault(e['id'],{'id':e['id'],'label':e['label'],'type':e['type'],'risk':30})
 for r in result['relationships']:
  if r['source'] in nodes and r['target'] in nodes: edges.append({**r,'label':r['type'],'reportId':report_id})
 neo.add_extraction(result['entities'],result['relationships'],report_id)
 return {'reportId':report_id,**result,'message':'Findings are investigative leads for human review; they do not establish criminality.'}
@app.on_event('startup')
def startup(): neo.seed(nodes,edges)
@app.get('/health')
def health(): return {'status':'ok','mode':'neo4j+memory' if neo.available else 'demo-memory','geminiEnabled':get_llm_provider().available}
@app.get('/api/overview')
def overview(): return {'nodes':len(nodes),'edges':len(edges),'reports':len(reports),'leads':len(leads()),'topEntities':analytics()[:5],'geminiEnabled':get_llm_provider().available}
@app.get('/api/network')
def network(): return {'nodes':list(nodes.values()),'edges':edges}
@app.get('/api/timeline')
def timeline(): return sorted(reports,key=lambda x:x['date'])
@app.get('/api/analytics')
def get_analytics(): return analytics()
@app.get('/api/leads')
def get_leads(): return leads()
@app.delete('/api/workspace')
def clear_workspace():
 # The local MVP is intentionally session-based; clearing starts a fresh case.
 nodes.clear(); edges.clear(); reports.clear()
 return {'message':'Workspace cleared. Start a new case by uploading a source record.'}
@app.post('/api/ingest')
def ingest(payload:Ingest): return process(payload.text,payload.title,'Investigator submitted',payload.date)
@app.post('/api/upload')
async def upload(file:UploadFile=File(...)):
 content=await file.read()
 if len(content)>10*1024*1024: raise HTTPException(413,'Maximum file size is 10 MB.')
 try: text=read_upload(file.filename or 'upload.txt',content)
 except ValueError as e: raise HTTPException(415,str(e))
 except Exception: raise HTTPException(422,'The file could not be read. Try a text-based PDF, DOCX, TXT, CSV, or XLSX file.')
 if len(text.strip())<15: raise HTTPException(422,'No usable text was found in this file.')
 return process(text,f'Uploaded: {file.filename}','Uploaded file')
@app.post('/api/assistant')
def assistant(payload:Question):
 provider=get_llm_provider(); context={'entities':analytics()[:12],'leads':leads()[:8],'reports':[{'id':r['id'],'title':r['title'],'date':r['date']} for r in reports[-12:]]}
 if provider.available:
  answer=provider.generate(f'''You are SentinelGraph's cautious investigation assistant. Answer only from this case context. Be concise, cite report IDs when available, identify uncertainty, and never claim guilt or advise enforcement action. Use “reported”, “possible lead”, and “requires verification”.\nCASE CONTEXT:{context}\nQUESTION:{payload.question}''') or 'Gemini is temporarily unavailable. Please try again.'
 else: answer=f'Gemini is not configured. This workspace contains {len(nodes)} entities, {len(edges)} reported relationships, and {len(reports)} source records. Add GEMINI_API_KEY to .env to enable contextual chat.'
 return {'answer':answer,'disclaimer':'This response summarizes reported data and potential leads only. It is not proof of criminality.'}
