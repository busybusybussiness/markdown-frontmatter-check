import subprocess,sys,os
HERE=os.path.dirname(os.path.abspath(__file__))
SCRIPT=os.path.join(HERE,'..','check_frontmatter.py')
REQ='title:string,date:date,tags:list'
def run(glob_):
    r=subprocess.run([sys.executable,SCRIPT,glob_,REQ],capture_output=True,text=True)
    return r.returncode,r.stdout
fails=0
def expect(name,cond):
    global fails
    print(('PASS ' if cond else 'FAIL ')+name)
    if not cond: fails+=1
fx=os.path.join(HERE,'..','fixtures')
rc,out=run(os.path.join(fx,'good','*.md')); expect('good fixtures exit 0',rc==0)
rc,out=run(os.path.join(fx,'bad','no_fm.md')); expect('no frontmatter exit 1',rc==1 and 'missing frontmatter' in out)
rc,out=run(os.path.join(fx,'bad','unclosed.md')); expect('unclosed exit 1',rc==1 and 'not closed' in out)
rc,out=run(os.path.join(fx,'bad','missing_key.md')); expect('missing tags key reported',rc==1 and "missing required key 'date'" in out or "missing required key 'tags'" in out)
rc,out=run(os.path.join(fx,'bad','bad_date.md')); expect('impossible date 2026-02-30 rejected',rc==1 and 'not a real calendar date' in out)
rc,out=run(os.path.join(fx,'bad','empty_list.md')); expect('empty list rejected',rc==1 and 'non-empty list' in out)
rc,out=run(os.path.join(fx,'bad','empty_title.md')); expect('empty title rejected',rc==1 and 'must not be empty' in out)
rc,out=run(os.path.join(fx,'bad','*.md')); expect('whole bad dir exit 1',rc==1)
rc,out=run(os.path.join(fx,'nothing','*.md')); expect('no match exit 2',rc==2)
r=subprocess.run([sys.executable,SCRIPT,os.path.join(fx,'good','*.md'),'title:banana'],capture_output=True,text=True)
expect('unknown type exit 2',r.returncode==2)
print('FAILURES:',fails)
sys.exit(1 if fails else 0)
