"""Deterministic, corpus-bounded overlap and explicitly heuristic review."""
import re, hashlib
from datetime import datetime,timezone

def tokens(text):return [(m.group().lower(),m.start(),m.end()) for m in re.finditer(r"\b[\w]+(?:['’][\w]+)?\b",text)]
def eligible_text(text,exclude_quotes=True,exclude_references=True):
 chars=list(text)
 if exclude_references:
  match=re.search(r'(?im)^\s*(references|bibliography|works cited)\s*$',text)
  if match:chars[match.start():]=[' ']*(len(text)-match.start())
 if exclude_quotes:
  for match in re.finditer(r'"[^"\n]*"|“[^”\n]*”',text):chars[match.start():match.end()]=[' ']*(match.end()-match.start())
 return ''.join(chars)
def analyze(paper,sources,exclude_quotes=True,exclude_references=True,window=8):
 eligible=eligible_text(paper,exclude_quotes,exclude_references);pt=tokens(eligible);index={}
 for source in sources:
  st=tokens(source['text'])
  for i in range(len(st)-window+1):
   key=tuple(x[0] for x in st[i:i+window]);index.setdefault(key,[])
   if len(index[key])<10:index[key].append((source['name'],st[i][1],st[i+window-1][2]))
 covered=set();hits=[]
 for i in range(len(pt)-window+1):
  start,end=pt[i][1],pt[i+window-1][2]
  if paper[start:end]!=eligible[start:end]:continue
  key=tuple(x[0] for x in pt[i:i+window])
  if key in index:
   covered.update(range(i,i+window));start,end=pt[i][1],pt[i+window-1][2]
   for name,ss,se in index[key]:hits.append({'source':name,'paper_start':start,'paper_end':end,'source_start':ss,'source_end':se,'passage':paper[start:end]})
 # Merge overlapping matches in the same source; percentage uses union, never sum.
 merged=[]
 for hit in sorted(hits,key=lambda x:(x['source'],x['paper_start'])):
  if merged and merged[-1]['source']==hit['source'] and hit['paper_start']<=merged[-1]['paper_end']:
   merged[-1]['paper_end']=max(merged[-1]['paper_end'],hit['paper_end']);merged[-1]['passage']=paper[merged[-1]['paper_start']:merged[-1]['paper_end']]
  else:merged.append(dict(hit))
 findings=[]
 for i,paragraph in enumerate(re.split(r'\n\s*\n',eligible),1):
  words=tokens(paragraph)
  if len(words)>180:findings.append({'category':'Writing','priority':'Medium','location':f'Paragraph {i}','passage':paragraph.strip()[:500],'concern':'Long paragraph may obscure the argument.','next_step':'Review topic sentences and consider splitting at a change in idea.','origin':'Heuristic'})
  if re.search(r'\b(proves?|always|never|100%|guarantees?)\b',paragraph,re.I):findings.append({'category':'Claim support','priority':'High','location':f'Paragraph {i}','passage':paragraph.strip()[:500],'concern':'Absolute claim needs careful qualification and evidence.','next_step':'Check the scope, limitations and supporting source.','origin':'Heuristic'})
  if len(words)>5 and re.search(r'\b(studies|research shows|research demonstrates|evidence suggests)\b',paragraph,re.I) and not re.search(r'\(.*?\d{4}.*?\)|\[\d+\]',paragraph):findings.append({'category':'Citation','priority':'High','location':f'Paragraph {i}','passage':paragraph.strip()[:500],'concern':'Research claim lacks a recognized author-year or numeric citation pattern.','next_step':'Verify whether attribution is needed; citation styles may differ.','origin':'Heuristic'})
 return {'created_at':datetime.now(timezone.utc).isoformat(),'paper_sha256':hashlib.sha256(paper.encode()).hexdigest(),'corpus':[{'name':s['name'],'sha256':hashlib.sha256(s['text'].encode()).hexdigest()} for s in sources],'overlap':{'percentage':round(100*len(covered)/len(pt),2) if pt and sources else None,'matched_tokens':len(covered),'eligible_tokens':len(pt),'source_count':len(sources),'method':f'Union of eligible word tokens in exact normalized {window}-word sequences','exclude_quotes':exclude_quotes,'exclude_references':exclude_references,'matches':merged},'findings':findings,'citation_verification':'Not performed: reference existence and claim support require independent source verification.','ai_authorship':'Not assessed. No AI-authorship percentage is produced.','limitations':['Only supplied sources are compared; no internet-wide search.','Exact sequence matching misses paraphrases and translations.','Quotation/reference exclusions use simple patterns; inspect extracted text.','Overlap does not establish plagiarism or originality.','Heuristic writing flags may be false positives.']}
