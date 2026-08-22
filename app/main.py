import sys
from pathlib import Path
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QFont
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QLineEdit,QListWidget,QListWidgetItem,QStackedWidget,QFrame,QComboBox,QSpinBox,QFormLayout,QMessageBox,QDialog,QDialogButtonBox,QSplitter)
from app.config import APP_NAME,APP_VERSION,DATA_VERSION,SOURCES
from app import database as db
from app.recommendations import analyze
from app.maintenance import backup_database, data_status

STYLE='''
QMainWindow,QDialog{background:#0C111B;color:#F3F4F6} QWidget{font-family:"Malgun Gothic","Segoe UI";font-size:13px;color:#F3F4F6} QLabel{color:#F3F4F6;background:transparent} QFrame#panel{background:#141C28;border:1px solid #26384B;border-radius:8px} QPushButton{background:#1A3343;border:1px solid #36546A;border-radius:6px;padding:9px 13px;color:#F3F4F6;font-weight:600} QPushButton:hover{background:#24485C;border-color:#D9B76E} QPushButton#gold{background:#A8823C;color:#10151C;border:1px solid #E5C879} QLineEdit,QComboBox,QSpinBox{background:#101925;border:1px solid #365064;border-radius:5px;padding:8px;color:#F3F4F6;selection-background-color:#A8823C;selection-color:#10151C} QComboBox QAbstractItemView{background:#101925;color:#F3F4F6;selection-background-color:#284357} QListWidget{background:#101925;border:1px solid #2B4154;border-radius:6px;padding:4px;color:#F3F4F6} QListWidget::item{padding:9px;border-bottom:1px solid #203142;color:#F3F4F6} QListWidget::item:selected{background:#284357;color:#F0D79A} QLabel#title{font-size:28px;font-weight:700;color:#F0D79A} QLabel#subtitle{color:#B7C2D2;font-size:14px} QLabel#section{font-size:20px;font-weight:700;color:#F0D79A} QLabel#badge{background:#24384A;border-radius:4px;padding:4px;color:#E6F0F7}'''

def card():
    f=QFrame();f.setObjectName('panel');return f
def label(text, obj=None):
    x=QLabel(text); x.setWordWrap(True)
    if obj:x.setObjectName(obj)
    return x

class AccountDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle('내 계정 등록'); self.setMinimumWidth(400)
        form=QFormLayout(self);self.name=QLineEdit();self.uid=QLineEdit();self.region=QComboBox();self.region.addItems(['Global','Korea','Japan','Asia'])
        self.star=QSpinBox();self.star.setRange(1,999);self.world=QSpinBox();self.world.setRange(1,99);self.story=QLineEdit()
        form.addRow('계정 이름 *',self.name);form.addRow('UID (선택)',self.uid);form.addRow('지역',self.region);form.addRow('별의 서 레벨',self.star);form.addRow('월드 레벨',self.world);form.addRow('스토리 진행',self.story)
        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel);buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject);form.addRow(buttons)
    def values(self):return (self.name.text().strip(),self.uid.text().strip(),self.region.currentText(),self.star.value(),self.world.value(),self.story.text().strip())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__();self.setWindowTitle(APP_NAME);self.resize(1360,850);self.setMinimumSize(760,540);self.current_account=None
        root=QWidget();self.setCentralWidget(root);layout=QHBoxLayout(root);layout.setContentsMargins(0,0,0,0);layout.setSpacing(0)
        nav=QFrame();nav.setFixedWidth(225);nav.setStyleSheet('background:#101824;border-right:1px solid #26384B');n=QVBoxLayout(nav);n.setContentsMargins(16,24,16,18)
        n.addWidget(label('7DS ORIGIN','title'));n.addWidget(label('COMPANION GUIDE','subtitle'));n.addSpacing(28)
        self.stack=QStackedWidget(); pages=[('홈',self.home_page()),('캐릭터 DB',self.characters_page()),('통합 검색',self.search_page()),('내 계정',self.accounts_page()),('성장 추천',self.recommend_page()),('데이터 · 정보',self.info_page())]
        for i,(name,page) in enumerate(pages):
            b=QPushButton(name);b.setFlat(True);b.setStyleSheet('text-align:left;padding:11px');b.clicked.connect(lambda _,v=i:self.stack.setCurrentIndex(v));n.addWidget(b);self.stack.addWidget(page)
        n.addStretch();n.addWidget(label(f'데이터 Ver {DATA_VERSION}\n팬 프로젝트 · 비공식','subtitle'));layout.addWidget(nav);layout.addWidget(self.stack,1)
    def center_on_screen(self):
        screen=self.screen() or QApplication.primaryScreen()
        if not screen:return
        area=screen.availableGeometry()
        target_width=min(self.width(),max(self.minimumWidth(),area.width()-40))
        target_height=min(self.height(),max(self.minimumHeight(),area.height()-40))
        self.resize(target_width,target_height)
        frame=self.frameGeometry();frame.moveCenter(area.center());self.move(frame.topLeft())
    def page_base(self,title,sub):
        w=QWidget();l=QVBoxLayout(w);l.setContentsMargins(30,26,30,26);l.setSpacing(14);l.addWidget(label(title,'title'));l.addWidget(label(sub,'subtitle'));return w,l
    def home_page(self):
        w,l=self.page_base('일곱 개의 대죄 Origin 완전 공략','Britannia Complete Strategy Database · 내 계정에 맞춘 오프라인 우선 공략 도구')
        hero=card();h=QVBoxLayout(hero);h.addWidget(label('지금 무엇을 해야 할까요?','section'));h.addWidget(label('캐릭터·무기·재료를 즉시 찾고, 등록한 보유 영웅으로 다음 성장 목표와 3인 파티를 계산하세요. UID 자동 동기화는 공식 공개 API가 확인되지 않아 제공하지 않습니다.'))
        row=QHBoxLayout();
        for t,idx in [('내 계정 시작하기',3),('데이터베이스 둘러보기',1),('최신 패치 확인',5)]:
            b=QPushButton(t);b.setObjectName('gold' if idx==3 else '');b.clicked.connect(lambda _,x=idx:self.stack.setCurrentIndex(x));row.addWidget(b)
        h.addLayout(row);l.addWidget(hero);l.addWidget(label('현재 내장 데이터','section'))
        grid=QHBoxLayout()
        for a,b in [('캐릭터','25명'),('무기','5개 검증 항목'),('아이템','4개 핵심 항목'),('게임 버전',f'Ver {DATA_VERSION}')]:
            c=card();cl=QVBoxLayout(c);cl.addWidget(label(a,'subtitle'));cl.addWidget(label(b,'section'));grid.addWidget(c)
        l.addLayout(grid);l.addStretch();return w
    def characters_page(self):
        w,l=self.page_base('캐릭터 데이터베이스','현재 공개 데이터베이스 기준 플레이어블 영웅. 선택하면 빌드 메모와 계정 등록을 할 수 있습니다.')
        self.char_filter=QLineEdit();self.char_filter.setPlaceholderText('캐릭터 검색…');self.char_filter.textChanged.connect(self.refresh_characters);l.addWidget(self.char_filter)
        split=QSplitter();self.char_list=QListWidget();self.char_list.currentItemChanged.connect(self.show_character);self.char_detail=card();split.addWidget(self.char_list);split.addWidget(self.char_detail);split.setSizes([430,720]);l.addWidget(split,1);self.refresh_characters();return w
    def refresh_characters(self):
        q=self.char_filter.text().lower() if hasattr(self,'char_filter') else '' ;self.char_list.clear()
        for r in db.characters():
            if q and q not in r['name_ko'].lower() and q not in r['name_en'].lower():continue
            it=QListWidgetItem(f"[{r['rarity']}]  {r['name_ko']}  ·  {r['element']} · {r['role']}");it.setData(Qt.UserRole,r['id']);self.char_list.addItem(it)
        if self.char_list.count():self.char_list.setCurrentRow(0)
    def show_character(self,current,_):
        if not current:return
        r=db.character(current.data(Qt.UserRole)); old=self.char_detail.layout()
        if old:
            while old.count():
                item=old.takeAt(0); item.widget() and item.widget().deleteLater()
            old.deleteLater()
        l=QVBoxLayout(self.char_detail);l.setContentsMargins(28,24,28,24);l.addWidget(label(r['name_ko'],'title'));l.addWidget(label(f"{r['name_en']} · {r['rarity']} · {r['element']} · {r['role']}",'subtitle'))
        l.addWidget(label('무기/역할','section'));l.addWidget(label(f"주 무기 타입: {r['weapon_type']}\n가능 역할: {r['roles']}"))
        l.addWidget(label('공략 메모','section'));l.addWidget(label(r['guide']))
        l.addWidget(label('데이터 신뢰도','section'));l.addWidget(label('● 커뮤니티 DB 검증 · 출처 URL이 데이터에 기록되어 있습니다. 수치·스킬은 업데이트 탭에서 최신 공개 DB와 대조하세요.','badge'))
        b=QPushButton('선택 계정에 보유 캐릭터로 추가');b.clicked.connect(lambda: self.add_current_character(r['id']));l.addWidget(b);l.addStretch()
    def add_current_character(self,cid):
        if not self.current_account: QMessageBox.information(self,'계정 선택 필요','먼저 내 계정 탭에서 계정을 등록하고 선택해 주세요.');return
        db.set_owned(self.current_account,cid);QMessageBox.information(self,'등록 완료','보유 캐릭터에 추가했습니다. 성장 추천에서 결과를 확인하세요.');self.refresh_accounts()
    def search_page(self):
        w,l=self.page_base('통합 검색','캐릭터, 무기, 아이템을 이름으로 검색합니다. 인터넷 없이 내장 데이터가 작동합니다.')
        row=QHBoxLayout();self.search_input=QLineEdit();self.search_input.setPlaceholderText('예: 데리엘리, 영혼의 탐식, 유령구피');self.search_kind=QComboBox();self.search_kind.addItems(['all','characters','weapons','items']);b=QPushButton('검색');b.clicked.connect(self.do_search);self.search_input.returnPressed.connect(self.do_search);row.addWidget(self.search_input,1);row.addWidget(self.search_kind);row.addWidget(b);l.addLayout(row);self.search_results=QListWidget();l.addWidget(self.search_results,1);return w
    def do_search(self):
        self.search_results.clear();q=self.search_input.text().strip()
        for typ,name,_,desc in db.search(q,self.search_kind.currentText()):self.search_results.addItem(f'[{typ}]  {name}\n    {desc}')
        if not self.search_results.count():self.search_results.addItem('일치 항목이 없습니다. 최신 데이터가 필요하면 데이터 · 정보에서 출처를 확인하세요.')
    def accounts_page(self):
        w,l=self.page_base('내 계정','비밀번호나 로그인 토큰을 요구하지 않습니다. 사용자가 직접 등록한 데이터만 이 PC에 저장됩니다.')
        row=QHBoxLayout();b=QPushButton('새 계정 등록');b.setObjectName('gold');b.clicked.connect(self.new_account);d=QPushButton('선택 계정 삭제');d.clicked.connect(self.delete_account);row.addWidget(b);row.addWidget(d);row.addStretch();l.addLayout(row)
        split=QSplitter();self.account_list=QListWidget();self.account_list.currentItemChanged.connect(self.select_account);self.owned_list=QListWidget();self.owned_list.itemDoubleClicked.connect(self.remove_owned);split.addWidget(self.account_list);right=card();rl=QVBoxLayout(right);rl.addWidget(label('보유 캐릭터','section'));rl.addWidget(label('캐릭터 DB에서 영웅을 추가하세요. 더블 클릭하면 제거됩니다.','subtitle'));rl.addWidget(self.owned_list);split.addWidget(right);split.setSizes([410,730]);l.addWidget(split,1);self.refresh_accounts();return w
    def refresh_accounts(self):
        if not hasattr(self,'account_list'):return
        keep=self.current_account;self.account_list.clear()
        for r in db.account_list():
            it=QListWidgetItem(f"{r['name']}  ·  {r['region']}  ·  별의 서 {r['star_book']}");it.setData(Qt.UserRole,r['id']);self.account_list.addItem(it)
            if r['id']==keep:self.account_list.setCurrentItem(it)
        if self.account_list.count() and not self.account_list.currentItem():self.account_list.setCurrentRow(0)
        self.load_owned()
    def new_account(self):
        dlg=AccountDialog(self)
        if dlg.exec():
            vals=dlg.values()
            if not vals[0]:QMessageBox.warning(self,'입력 필요','계정 이름을 입력해 주세요.');return
            try:db.create_account(*vals);self.refresh_accounts()
            except Exception as e:QMessageBox.warning(self,'저장 실패',str(e))
    def select_account(self,item,_):
        self.current_account=item.data(Qt.UserRole) if item else None;self.load_owned()
    def load_owned(self):
        if not hasattr(self,'owned_list'):return
        self.owned_list.clear()
        if self.current_account:
            for r in db.owned(self.current_account):self.owned_list.addItem(QListWidgetItem(f"[{r['rarity']}] {r['name_ko']} · Lv.{r['level']} · {r['weapon_name'] or '무기 미등록'}"))
    def remove_owned(self,item):
        name=item.text().split('] ')[-1].split(' ·')[0]
        for r in db.owned(self.current_account):
            if r['name_ko']==name:db.remove_owned(self.current_account,r['id']);break
        self.load_owned()
    def delete_account(self):
        if not self.current_account:return
        if QMessageBox.question(self,'계정 삭제','선택한 계정과 로컬 보유 데이터가 삭제됩니다. 계속할까요?')==QMessageBox.Yes:
            db.delete_account(self.current_account);self.current_account=None;self.refresh_accounts()
    def recommend_page(self):
        w,l=self.page_base('성장 추천','등록된 계정의 보유 영웅, 레벨, 무기 등록 여부와 역할 균형을 기반으로 계산합니다.')
        b=QPushButton('선택 계정 분석 실행');b.setObjectName('gold');b.clicked.connect(self.run_analysis);l.addWidget(b);self.analysis=card();l.addWidget(self.analysis);l.addStretch();self.run_analysis();return w
    def run_analysis(self):
        if not hasattr(self,'analysis'):return
        old=self.analysis.layout()
        if old:
            while old.count():
                i=old.takeAt(0);i.widget() and i.widget().deleteLater()
            old.deleteLater()
        a=analyze(self.current_account) if self.current_account else {"score":0,"headline":"계정을 선택해 주세요","body":"내 계정 탭에서 계정을 만든 뒤 보유 캐릭터를 추가하세요.","team":[],"tasks":[]}
        l=QVBoxLayout(self.analysis);l.setContentsMargins(26,22,26,22);l.addWidget(label(a['headline'],'section'));l.addWidget(label(a['body']));l.addWidget(label(f"계정 준비도: {a['score']}/100",'badge'))
        if a['team']:l.addWidget(label('추천 3인 파티','section'));l.addWidget(label('  ·  '.join(f"{h['name_ko']} ({h['role']})" for h in a['team'])))
        l.addWidget(label('다음 행동','section'))
        for t in a['tasks']:l.addWidget(label('• '+t))
    def info_page(self):
        w,l=self.page_base('데이터 · 정보','데이터 상태와 업데이트 출처를 확인합니다.')
        p=card();pl=QVBoxLayout(p);pl.addWidget(label(f'내장 게임 데이터: Ver {DATA_VERSION}','section'));pl.addWidget(label('마지막 검증: 앱 설치 시점의 소스 매니페스트 · 캐릭터 25명 / 핵심 무기 및 아이템 데이터 포함'))
        status=data_status(); validation='정상' if not status['validation'] else ' / '.join(status['validation'])
        pl.addWidget(label(f"DB 검사: {validation} · 캐릭터 {status['counts']['characters']} · 무기 {status['counts']['weapons']} · 아이템 {status['counts']['items']}",'badge'))
        backup=QPushButton('내 계정 데이터 백업');backup.clicked.connect(self.backup_data);pl.addWidget(backup)
        pl.addWidget(label('출처','section'));official=QPushButton('Netmarble 공식 사이트 열기');official.clicked.connect(lambda:QDesktopServices.openUrl(QUrl(SOURCES['official'])));community=QPushButton('7DS Origin 공개 DB 열기');community.clicked.connect(lambda:QDesktopServices.openUrl(QUrl(SOURCES['community_db'])));pl.addWidget(official);pl.addWidget(community);pl.addWidget(label('이 앱은 비공식 팬 프로젝트입니다. 게임 데이터와 이미지의 권리는 각 권리자에게 있습니다. 공개 API가 확인되지 않은 UID 자동 동기화는 제공하지 않습니다.','subtitle'));l.addWidget(p);l.addStretch();return w
    def backup_data(self):
        try: QMessageBox.information(self,'백업 완료',f'백업 파일을 만들었습니다.\n{backup_database()}')
        except Exception as exc: QMessageBox.warning(self,'백업 실패',str(exc))

def main():
    db.initialize();app=QApplication(sys.argv);app.setApplicationName(APP_NAME);app.setStyleSheet(STYLE);font=QFont('Malgun Gothic',10);app.setFont(font);win=MainWindow();win.center_on_screen();win.show();return app.exec()
if __name__=='__main__':raise SystemExit(main())

