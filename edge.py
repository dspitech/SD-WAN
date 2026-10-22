"""Educational application-level encrypted UDP overlay. NOT IPsec, IKEv2 or a production SD-WAN.
Runs in Linux containers on Windows/macOS/Linux via Docker. Port 45900/UDP on each underlay.
"""
import collections, json, os, random, socket, sys, threading, time, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen
from urllib.parse import urlsplit, parse_qs
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROLE = sys.argv[1]
KEY = bytes.fromhex(os.environ['DEMO_KEY_HEX'])
assert len(KEY) == 32
CRYPTO = AESGCM(KEY)
PORT = 45900
HTTP_PORT = 8080
LAN_LISTEN = ('10.10.0.1', '10.11.0.1')   # LAN employes, LAN invites : jamais les underlays
GUEST_IP = '10.11.0.1'
GUEST_NET = '10.11.0.'
PATHS = {
 'internet': ('172.28.10.10' if ROLE=='paris' else '172.28.10.20',
              '172.28.10.20' if ROLE=='paris' else '172.28.10.10'),
 'mpls': ('172.28.20.10' if ROLE=='paris' else '172.28.20.20',
          '172.28.20.20' if ROLE=='paris' else '172.28.20.10')}
SOCKS, METRICS, PENDING, PROBES = {}, {}, {}, {}
LOCK = threading.RLock()
POLICY = {'generation':'fallback', 'applications':{'erp':{'preferred':'mpls','max_rtt_ms':100,'max_loss_pct':20},
      'teams':{'preferred':'internet','max_rtt_ms':100,'max_loss_pct':20},
      'backup':{'preferred':'internet','max_rtt_ms':350,'max_loss_pct':60}},
      'guest_blocked':['erp','teams','backup']}
CONTROL_OK = False
CONTROL_LAST_OK = None
IMPAIR = {'internet': {'loss':0.0,'delay_ms':0}, 'mpls': {'loss':0.0,'delay_ms':0}}

def seal(obj):
    nonce=os.urandom(12)
    return b'E5A1'+nonce+CRYPTO.encrypt(nonce,json.dumps(obj,separators=(',',':')).encode(),b'MERIDIAN-LAB')

def unseal(packet):
    if not packet.startswith(b'E5A1') or len(packet)<33: raise ValueError('invalid frame')
    return json.loads(CRYPTO.decrypt(packet[4:16],packet[16:],b'MERIDIAN-LAB'))

def transmit(path,obj):
    with LOCK: conf=IMPAIR[path].copy()
    if random.random()*100<conf['loss']: return
    if conf['delay_ms']: time.sleep(conf['delay_ms']/1000.0)
    SOCKS[path].sendto(seal(obj),(PATHS[path][1],PORT))

def receive(path,sock):
    while True:
        try: data,addr=sock.recvfrom(65535)
        except OSError: break
        if addr[0] != PATHS[path][1]: continue
        try: packet=unseal(data)
        except Exception: continue
        kind=packet.get('kind')
        if kind=='probe' and ROLE=='berlin': transmit(path,{'kind':'pong','id':packet['id']})
        elif kind=='pong' and ROLE=='paris':
            with LOCK:
                sent=PROBES.pop(packet['id'],None)
                if sent:
                    ms=(time.monotonic()-sent[1])*1000
                    METRICS[path]['samples'].append((True,round(ms,2)))
                    METRICS[path]['last_ok']=time.monotonic()
        elif kind=='req' and ROLE=='berlin':
            threading.Thread(target=process_request,args=(path,packet),daemon=True).start()
        elif kind=='resp' and ROLE=='paris':
            with LOCK: item=PENDING.get(packet.get('id'))
            if item:
                item['answer']=packet
                item['event'].set()

def process_request(path,pkt):
    endpoint=pkt.get('route','erp')
    try:
        url='http://10.20.0.20:8000/'+endpoint+'?request='+pkt['id']
        with urlopen(url,timeout=4) as response: body=response.read(30000).decode()
        ans={'kind':'resp','id':pkt['id'],'code':200,'body':body,'edge':'berlin','path':path}
    except Exception as exc: ans={'kind':'resp','id':pkt['id'],'code':502,'body':str(exc),'path':path}
    transmit(path,ans)

def probe_loop():
    while True:
        started=time.monotonic()
        with LOCK:
            expired=[ident for ident,(path,ts) in PROBES.items() if started-ts>2.3]
            for ident in expired:
                path,ts=PROBES.pop(ident)
                METRICS[path]['samples'].append((False,None))
            for path in PATHS:
                ident=uuid.uuid4().hex
                PROBES[ident]=(path,time.monotonic())
                threading.Thread(target=transmit,args=(path,{'kind':'probe','id':ident}),daemon=True).start()
        time.sleep(1)

def controller_loop():
    global POLICY, CONTROL_OK, CONTROL_LAST_OK
    while True:
        try:
            with urlopen('http://172.28.30.10:9000/policy',timeout=1.5) as response:
                conf=json.load(response)
            if not isinstance(conf.get('applications'),dict): raise ValueError('policy invalid')
            with LOCK: POLICY=conf; CONTROL_OK=True; CONTROL_LAST_OK=time.time()
        except Exception:
            with LOCK: CONTROL_OK=False
        time.sleep(3)

def snapshot():
    now=time.monotonic()
    result={}
    with LOCK:
        for path,entry in METRICS.items():
            samples=list(entry['samples'])
            rtts=[s[1] for s in samples if s[0]]
            result[path]={
              'up': (now-entry['last_ok']<3.5),
              'rtt_ms': round(sum(rtts)/len(rtts),1) if rtts else None,
              'loss_pct': round(100*sum(not s[0] for s in samples)/len(samples),1) if samples else None,
              'observations':len(samples)}
        return {'role':ROLE,'generation':POLICY.get('generation'),
                'controller_reachable':CONTROL_OK,'controller_last_seen':CONTROL_LAST_OK,
                'http_listen':[f'{ip}:{HTTP_PORT}' for ip in LAN_LISTEN],
                'paths':result,'impairment_training_only':IMPAIR.copy()}

def choose(application):
    with LOCK: conf=POLICY['applications'][application].copy()
    s=snapshot()['paths']; pref=conf['preferred']
    acceptable=[p for p,v in s.items() if v['up'] and v['rtt_ms'] is not None and
                v['rtt_ms'] <= conf['max_rtt_ms'] and (v['loss_pct'] or 0)<=conf['max_loss_pct']]
    if pref in acceptable: return pref, 'preferred-and-within-sla'
    if acceptable: return acceptable[0], 'alternate-within-sla'
    available=[p for p,v in s.items() if v['up']]
    if available: return (pref if pref in available else available[0]), 'degraded-no-path-meets-sla'
    return None,'no-underlay-available'

class HttpHandler(BaseHTTPRequestHandler):
    def answer(self,code,body):
        raw=json.dumps(body,ensure_ascii=False,indent=2).encode()
        self.send_response(code); self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def is_guest(self):
        # Segment invite : ecoute sur l'adresse invite OU source dans 10.11.0.0/24
        return self.server.server_address[0]==GUEST_IP or self.client_address[0].startswith(GUEST_NET)
    def do_GET(self):
        u=urlsplit(self.path); route=u.path.strip('/')
        if route in ('status','lab/impair') and self.is_guest():
            self.answer(403,{'error':'guest-segment-policy','application':route}); return
        if route=='status': self.answer(200,snapshot()); return
        if route=='lab/impair':
            q=parse_qs(u.query)
            path=q.get('path',['internet'])[0]
            if path not in PATHS: self.answer(400,{'error':'path invalid'}); return
            try:
                loss=float(q.get('loss',['0'])[0]); delay=int(q.get('delay_ms',['0'])[0])
                if not (0<=loss<=100 and 0<=delay<=1000): raise ValueError()
                with LOCK: IMPAIR[path]={'loss':loss,'delay_ms':delay}
                self.answer(200,{'ok':True,'path':path,'impairment':IMPAIR[path]})
            except ValueError: self.answer(400,{'error':'loss 0..100, delay_ms 0..1000'})
            return
        guest=self.is_guest()
        with LOCK: blocked=set(POLICY.get('guest_blocked',[]))
        if guest and route in blocked:
            self.answer(403,{'error':'guest-segment-policy','application':route}); return
        if route=='guest': self.answer(200,{'guest':'internet-only-demo','note':'application policy, not VRF'});return
        if route=='saas':
            try:
                with urlopen('http://172.28.10.40:8000/office',timeout=4) as r: body=json.load(r)
                self.answer(200,{'breakout':'local-at-paris-edge','saas_response':body})
            except Exception as exc: self.answer(502,{'error':str(exc)})
            return
        if route not in ('erp','teams','backup'):
            self.answer(404,{'help':'/status /erp /teams /backup /saas /guest /lab/impair'});return
        path,reason=choose(route)
        if path is None: self.answer(503,{'error':reason,'paths':snapshot()['paths']});return
        ident=uuid.uuid4().hex
        item={'event':threading.Event(),'answer':None}
        with LOCK: PENDING[ident]=item
        transmit(path,{'kind':'req','id':ident,'route':route})
        got=item['event'].wait(5)
        with LOCK: PENDING.pop(ident,None)
        if not got: self.answer(504,{'error':'overlay-timeout','selected_path':path,'reason':reason});return
        self.answer(item['answer'].get('code',200),{'selected_path':path,'policy_reason':reason,
                     'request_id':ident,'remote':item['answer'].get('body')})
    def log_message(self,fmt,*args): print(f'[{ROLE}] {self.client_address[0]} {fmt%args}',flush=True)

for path,(local,remote) in PATHS.items():
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind((local,PORT)); SOCKS[path]=s
    METRICS[path]={'samples':collections.deque(maxlen=12),'last_ok':float('-inf')}
    threading.Thread(target=receive,args=(path,s),daemon=True).start()
if ROLE=='paris':
    threading.Thread(target=controller_loop,daemon=True).start()
    threading.Thread(target=probe_loop,daemon=True).start()
    servers=[ThreadingHTTPServer((ip,HTTP_PORT),HttpHandler) for ip in LAN_LISTEN]
    for srv in servers[1:]: threading.Thread(target=srv.serve_forever,daemon=True).start()
    print(f'Paris edge on TCP/{HTTP_PORT} (LAN only: {", ".join(LAN_LISTEN)}) | encrypted teaching overlay on UDP/45900',flush=True)
    servers[0].serve_forever()
else:
    print('Berlin edge on UDP/45900 ready',flush=True)
    while True: time.sleep(60)
