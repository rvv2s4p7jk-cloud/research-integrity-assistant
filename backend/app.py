from pathlib import Path
import io,zipfile,os
from fastapi import FastAPI,UploadFile,File,HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from backend.review import analyze
from backend import llm
app=FastAPI(title='Research Integrity Review Assistant',version='1.0.0')
class Source(BaseModel):
 name:str=Field(min_length=1,max_length=150)
 text:str=Field(min_length=1,max_length=60000)
class ReviewInput(BaseModel):
 paper:str=Field(min_length=20,max_length=60000)
 sources:list[Source]=Field(default_factory=list,max_length=8)
 context:str=Field(default='',max_length=5000)
 exclude_quotes:bool=True
 exclude_references:bool=True
 consent:bool=False
 def bounded(self):
  if len(self.paper)+sum(len(s.text) for s in self.sources)+len(self.context)>150000:raise HTTPException(413,'Combined review text exceeds 150,000 characters; review one chapter at a time')
@app.get('/api/config')
def config():return {'provider':'OpenAI','configured':bool(os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_MODEL')),'model':os.getenv('OPENAI_MODEL'),'max_characters':60000,'max_sources':8}
@app.post('/api/review')
def local(body:ReviewInput):
 body.bounded();return analyze(body.paper,[s.model_dump() for s in body.sources],body.exclude_quotes,body.exclude_references)
@app.post('/api/llm-review')
async def model(body:ReviewInput):
 body.bounded()
 try:return await llm.review(body.paper,[s.model_dump() for s in body.sources],body.context,body.consent)
 except ValueError as e:raise HTTPException(400,str(e))
@app.post('/api/extract')
async def extract(file:UploadFile=File(...)):
 raw=await file.read(5*1024*1024+1)
 if len(raw)>5*1024*1024:raise HTTPException(413,'Maximum upload is 5 MB')
 suffix=Path(file.filename or '').suffix.lower()
 try:
  if suffix in ['.txt','.md']:text=raw.decode('utf-8-sig')
  elif suffix=='.pdf':
   from pypdf import PdfReader
   reader=PdfReader(io.BytesIO(raw))
   if len(reader.pages)>100:raise ValueError('Maximum 100 pages')
   text='\n\n'.join(page.extract_text() or '' for page in reader.pages)
  elif suffix=='.docx':
   from xml.etree import ElementTree
   with zipfile.ZipFile(io.BytesIO(raw)) as z:
    info=z.getinfo('word/document.xml')
    if info.file_size>10*1024*1024:raise ValueError('Document XML too large')
    xml=ElementTree.fromstring(z.read('word/document.xml'))
   ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
   text='\n\n'.join(''.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in xml.findall('.//w:p',ns))
  else:raise HTTPException(415,'Use TXT, MD, PDF or DOCX')
 except HTTPException:raise
 except Exception:raise HTTPException(422,'Could not extract this document. Try a text export; scanned PDFs need OCR externally.')
 if not text.strip():raise HTTPException(422,'No readable text found. Scanned documents need OCR externally.')
 if len(text)>60000:raise HTTPException(413,'Extracted text exceeds 60,000 characters; upload one chapter at a time')
 return {'text':text,'filename':file.filename,'warning':'Inspect extracted text for missing tables, equations, footnotes and reading-order errors.'}
app.mount('/',StaticFiles(directory=Path(__file__).resolve().parents[1]/'frontend',html=True),name='ui')
