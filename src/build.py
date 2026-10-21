# 讀取 content/*.md，輸出 data.js（章節 + 詞庫）。新增小說：放入 .md 後重跑。
import re, json, glob, os
HERE = os.path.dirname(os.path.abspath(__file__))
# 詞性 / 雅思同義替換（人工整理，初版；其餘欄位可日後補）
EX = """desperate|a.|hopeless,despairing
magnificent|a.|splendid,grand
enormous|a.|huge,immense
bankruptcy|n.|insolvency,ruin
prominent|a.|eminent,notable
empire|n.|dominion,realm
rescue|v.|save,deliver
eliminate|v.|remove,eradicate
indifferent|a.|apathetic,unconcerned
comply|v.|obey,conform
temporary|a.|short-term,provisional
tremble|v.|shake,shiver
reputation|n.|standing,renown
arrogant|a.|haughty,conceited
yield|v.|give in,surrender
alternative|n.|option,choice
proceed|v.|go ahead,advance
efficient|a.|effective,productive
romantic|a.|passionate,amorous
heartfelt|a.|sincere,genuine
pact|n.|agreement,treaty
witness|v.|observe,see
elegant|a.|graceful,refined
maintain|v.|sustain,preserve
confine|v.|restrict,imprison
luxury|a.|lavish,opulent
detailed|a.|thorough,comprehensive
emphasize|v.|stress,highlight
shallow|a.|superficial,trivial
appearance|n.|look,façade
neutral|a.|impartial,unbiased
interfere|v.|meddle,intervene
nod|v.|bow,signal
humiliation|n.|disgrace,shame
resolve|v.|determine,decide
regain|v.|recover,retrieve
restore|v.|reinstate,renew
dignity|n.|honour,self-respect
unpredictable|a.|erratic,uncertain
annual|a.|yearly,once a year
encounter|v.|meet,come across
rival|n.|competitor,opponent
extraordinary|a.|remarkable,exceptional
courtesy|n.|politeness,civility
intense|a.|fierce,extreme
keen|a.|eager,enthusiastic
opponent|n.|adversary,rival
subtle|a.|delicate,understated
hostility|n.|animosity,enmity
fulfill|v.|accomplish,carry out
superficial|a.|shallow,cursory
calm|ad.|composedly,serenely
social|a.|communal,societal
appropriate|a.|suitable,proper
expect|v.|anticipate,await
realize|v.|recognise,grasp
assume|v.|presume,suppose
submissive|a.|obedient,compliant
discover|v.|find out,uncover
faded|a.|discoloured,bleached
radiant|a.|beaming,glowing
inquire|v.|ask,enquire
withdraw|v.|retreat,retire
contempt|n.|scorn,disdain
complex|a.|complicated,intricate
emotion|n.|feeling,sentiment
intelligence|n.|intellect,brainpower
diligence|n.|hard work,industry
charity|n.|philanthropy,benevolence
position|n.|post,role
organize|v.|arrange,coordinate
spectacular|a.|impressive,dramatic
raise|v.|collect,gather
substantial|a.|considerable,significant
admire|v.|respect,esteem
erupt|v.|break out,burst
deliberately|ad.|intentionally,purposely
leak|v.|disclose,reveal
authentic|a.|genuine,real
explode|v.|blow up,burst
plunge|v.|plummet,nosedive
severe|a.|harsh,strict
hesitate|v.|pause,waver
steady|a.|stable,constant
sincere|a.|honest,earnest
mutual|a.|reciprocal,shared
speculation|n.|conjecture,guesswork
define|v.|specify,characterise
courage|n.|bravery,valour
eloquence|n.|fluency,articulacy
suppress|v.|quell,subdue
vulnerable|a.|exposed,defenceless
abandon|v.|desert,forsake
honor|v.|keep,fulfil
gaze|v.|stare,gape
principle|n.|rule,belief
confess|v.|admit,disclose
conspiracy|n.|plot,scheme
perish|v.|die,pass away
pursue|v.|chase,seek
strategic|a.|planned,calculated
tender|a.|gentle,affectionate
transform|v.|change,convert
significance|n.|meaning,importance
moist|a.|damp,wet
comprehend|v.|understand,grasp
rigid|a.|stiff,inflexible
fragile|a.|delicate,breakable
passionate|a.|ardent,fervent
covenant|n.|pledge,promise
exquisite|a.|delicate,beautiful
contract|n.|agreement,deal
obligation|n.|duty,commitment
genuine|a.|authentic,sincere
embrace|v.|hug,hold
illuminate|v.|light up,brighten
transaction|n.|deal,exchange
conclude|v.|end,finish
splendid|a.|magnificent,glorious"""
ex = {}
for l in EX.splitlines():
    w, p, s = l.split('|'); ex[w] = (p, s.split(','))

words, chapters = {}, []
for i, f in enumerate(sorted(glob.glob(os.path.join(HERE, 'content', '*.md'))), 1):
    raw = open(f, encoding='utf-8').read().strip().split('\n')
    title = raw[0].lstrip('# ').strip()
    paras, vocab = [], []
    for para in [x for x in raw[1:] if x.strip()]:
        segs, pos = [], 0
        for m in re.finditer(r'\{([^|}]+)\|([^}]+)\}', para):
            if m.start() > pos: segs.append({'t': 'text', 'v': para[pos:m.start()]})
            en, zh = m.group(1), m.group(2)
            segs.append({'t': 'word', 'id': en, 'zh': zh})
            if en not in words:
                p, syn = ex.get(en, ('', []))
                words[en] = {'id': en, 'zh': zh, 'pos': p, 'syn': syn}
            if en not in vocab: vocab.append(en)
            pos = m.end()
        if pos < len(para): segs.append({'t': 'text', 'v': para[pos:]})
        paras.append(segs)
    chapters.append({'id': 'n1c%d' % i, 'index': i, 'title': title, 'paras': paras, 'vocab': vocab})
data = {'novels': [{'id': 'n1', 'title': '冷峻總裁的限時婚約', 'desc': '一紙一年婚約，從交易走向真愛。邊讀劇情，邊記住雅思單字。', 'chapters': chapters}], 'words': words}
open(os.path.join(HERE, 'data.js'), 'w', encoding='utf-8').write('window.DATA=' + json.dumps(data, ensure_ascii=False) + ';')
print(len(words), 'words', len(chapters), 'chapters')

# 單檔版：把資料內嵌進 index.html，輸出 dist/index.html（一個檔案即可部署/傳送）
html = open(os.path.join(HERE, 'index.html'), encoding='utf-8').read()
js = open(os.path.join(HERE, 'data.js'), encoding='utf-8').read().replace('</', '<\/')
os.makedirs(os.path.join(HERE, 'dist'), exist_ok=True)
open(os.path.join(HERE, 'dist', 'index.html'), 'w', encoding='utf-8').write(html.replace('<script src="data.js"></script>', '<script>' + js + '</script>'))
print('dist/index.html written')
