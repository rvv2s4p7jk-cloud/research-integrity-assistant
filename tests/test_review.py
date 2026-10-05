import json,io,zipfile
import pytest,httpx
from fastapi.testclient import TestClient
from backend.review import analyze
from backend import llm
from backend.app import app
PAPER='alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu'
def test_overlap_union_not_double_counted():
 r=analyze(PAPER,[{'name':'a','text':PAPER},{'name':'b','text':PAPER}])
 assert r['overlap']['percentage']==100 and r['overlap']['matched_tokens']==12
 assert len(r['overlap']['matches'])==2
def test_quote_and_references_exclusion():
 r=analyze('original writing remains here\n"'+PAPER+'"\nReferences\n'+PAPER,[{'name':'a','text':PAPER}])
 assert r['overlap']['percentage']==0 and r['overlap']['eligible_tokens']==4
 r=analyze('"'+PAPER+'"',[{'name':'a','text':PAPER}],exclude_quotes=False)
 assert r['overlap']['percentage']==100
def test_no_corpus_is_not_originality():
 r=analyze(PAPER,[])
 assert r['overlap']['percentage'] is None and 'Not assessed' in r['ai_authorship']
def test_paraphrase_limitation_and_flags():
 r=analyze('Research shows that our method always guarantees perfect results across all settings.',[{'name':'a','text':'An unrelated article about data'}])
 assert r['overlap']['percentage']==0
 assert {'Citation','Claim support'}<=set(f['category'] for f in r['findings'])
def test_grounded_offsets():
 r=analyze('Intro. '+PAPER+' Ending.',[{'name':'source','text':PAPER}])
 for m in r['overlap']['matches']:assert ('Intro. '+PAPER+' Ending.')[m['paper_start']:m['paper_end']]==m['passage']
@pytest.fixture
def client():return TestClient(app)
def test_uploads_and_empty_pdf(client):
 r=client.post('/api/extract',files={'file':('chapter.txt',b'Hello research paper','text/plain')})
 assert r.status_code==200 and r.json()['text']=='Hello research paper'
 assert client.post('/api/extract',files={'file':('x.exe',b'fake')}).status_code==415
 assert client.post('/api/extract',files={'file':('x.pdf',b'broken')}).status_code==422
 assert client.post('/api/extract',files={'file':('x.txt',b' ')}).status_code==422
 assert client.post('/api/extract',files={'file':('x.txt',b'a'*60001)}).status_code==413
def test_docx_extraction(client):
 out=io.BytesIO()
 with zipfile.ZipFile(out,'w') as z:z.writestr('word/document.xml','<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Test paper text</w:t></w:r></w:p></w:body></w:document>')
 assert client.post('/api/extract',files={'file':('test.docx',out.getvalue())}).json()['text']=='Test paper text'
def test_consent_and_missing_key(client,monkeypatch):
 monkeypatch.delenv('OPENAI_API_KEY',raising=False)
 assert client.post('/api/llm-review',json={'paper':PAPER}).status_code==400
 r=client.post('/api/llm-review',json={'paper':PAPER,'consent':True})
 assert 'Configure' in r.json()['detail']
 assert client.get('/api/config').json()['configured'] is False
def test_limits_and_ui(client):
 assert client.post('/api/review',json={'paper':'too short'}).status_code==422
 assert client.post('/api/review',json={'paper':PAPER,'sources':[{'name':'s','text':'a'*60000}]*3}).status_code==413
 assert client.get('/').status_code==200
 assert client.post('/api/review',json={'paper':PAPER}).status_code==200
def mock_client(monkeypatch,output,status=200):
 monkeypatch.setenv('OPENAI_API_KEY','test-key-not-real');monkeypatch.setenv('OPENAI_MODEL','test-model')
 class Fake:
  def __init__(self,**kw):pass
  async def __aenter__(self):return self
  async def __aexit__(self,*a):pass
  async def post(self,url,headers,json):
   assert url=='https://api.openai.com/v1/responses' and json['store'] is False
   assert json['model']=='test-model'
   return httpx.Response(status,json={'output':[{'type':'message','content':[{'type':'output_text','text':output}]}]},request=httpx.Request('POST',url))
 monkeypatch.setattr(llm.httpx,'AsyncClient',Fake)
def test_model_response_grounding(client,monkeypatch):
 f={'category':'Writing','priority':'Low','location':'Paragraph 1','passage':'alpha beta','concern':'Improve connection','next_step':'Explain transition'}
 mock_client(monkeypatch,json.dumps({'summary':'Review these suggestions','findings':[f,f|{'passage':'fabricated quotation'}]}))
 r=client.post('/api/llm-review',json={'paper':PAPER,'consent':True})
 assert r.status_code==200 and len(r.json()['findings'])==1 and r.json()['rejected_ungrounded_findings']==1
@pytest.mark.parametrize('output,status',[('not json',200),('{}',401)])
def test_provider_failures_are_safe(client,monkeypatch,output,status):
 mock_client(monkeypatch,output,status)
 r=client.post('/api/llm-review',json={'paper':PAPER,'consent':True})
 assert r.status_code==400 and 'test-key-not-real' not in r.text

def test_matching_cannot_bridge_excluded_quote():
 paper='alpha beta gamma delta "quoted words" epsilon zeta eta theta'
 result=analyze(paper,[{'name':'s','text':'alpha beta gamma delta epsilon zeta eta theta'}])
 assert result['overlap']['matched_tokens']==0
