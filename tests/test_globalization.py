# coding=utf-8
import socket
import pytest
from prompt_toolkit.document import Document
from utility import random_str
from mssqltestutils import (
    create_mssql_cli_client,
    create_mssql_cli_options,
    create_test_db,
    clean_up_test_db,
    shutdown
)
from mssqlcli.mssqlcompleter import MssqlCompleter
import mssqlcli.completion_refresher as completion_refresher


# All tests require a live connection to test server.
# Make modifications to mssqlutils.create_mssql_cli_client()
# to use a different server and database.
# Please Note: These tests cannot be run offline.


class GlobalizationTests:
    @staticmethod
    def run_query(mssqlcliclient, query):
        success = True
        for _, _, status, _, is_error in mssqlcliclient.execute_query(query):
            if is_error is True:
                raise AssertionError(status)
        return success

    @staticmethod
    def get_next_characters(all_characters, count=50):
        """
        Takes 50 characters (by default) at a time from all_characters and
        yield them as a string until all_characters becomes empty.
        """
        while len(all_characters) > 0:
            next_characters_length = min(len(all_characters), count)
            next_characters = all_characters[0:next_characters_length]
            all_characters = all_characters[next_characters_length:]
            yield next_characters

    charset_dict = {
        'double': (
            u'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
            u'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
            u'０１２３４５６７８９'
            u'ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとど'
            u'なにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをん'
            u'ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニ'
            u'ヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶ'
            u'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρστυφχψω'
            u'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя'
            u'āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜüêɑńňǹɡ'
            u'ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦㄧㄨㄩ'
            u'啊阿埃挨哎唉哀皑癌蔼矮艾碍爱隘薄雹保堡饱宝抱报暴豹鲍爆杯碑悲病并玻菠播拨钵波博勃搏铂箔伯帛场尝常长偿肠厂敞畅唱倡超抄'
            u'钞朝础储矗搐触处揣川穿椽传船喘串疮怠耽担丹单郸掸胆旦氮但惮淡诞弹丁盯叮钉顶鼎锭定订丢东冬董懂动贰发罚筏伐乏阀法珐藩'
            u'丂丄丅丆丏丒丗丟丠両丣並丩丮丯丱侤侫侭侰侱侲侳侴侶侷侸侹侺侻侼侽傽傾傿僀僁僂僃僄僅僆僇僈僉僊僋僌凘凙凚凜凞凟凢凣凥処'
            u'凧凨凩凪凬凮匑匒匓匔匘匛匜匞匟匢匤匥匧匨匩匫咢咥咮咰咲咵咶咷咹咺咼咾哃哅哊哋嘆嘇嘊嘋嘍嘐嘑嘒嘓嘔嘕嘖嘗嘙嘚嘜園圓圔圕'
            u'獲獳獴獵獶獷獸獹獺獻獼獽獿玀玁玂珸珹珺珻珼珽現珿琀琁琂琄琇琈琋琌瑻瑼瑽瑿璂璄璅璆璈璉璊璌璍璏璑璒瓳瓵瓸瓹瓺瓻瓼瓽瓾甀'
            u'甁甂甃甅甆甇疈疉疊疌疍疎疐疓疕疘疛疜疞疢疦疧癅癆癇癈癉癊癋癎癏癐癑癒癓癕癗癘盄盇盉盋盌盓盕盙盚盜盝盞盠盡盢監睝睞睟睠'
            u'〡〢〣〤〥〦〧〨〩'
        ),
        'four': (
            u'㐀㐁㐂㐃㐄㐅㐆㐇㐈㐉㐊㐋㐌㐍㐎㐏㐐㐑㐒㐓㐔㐕㐖㐗㐘㐙㐚㐛㐜㐝㐞㐟㐠㐡㐢㐣㐤㐥㐦㐧㐨㐩㐪㐫㐬㐭㐮㐯㐰㐱㐲㐳㐴㐵㐶㐷㐸㐹'
            u'㐺㐻㐼㐽㐾㐿㑀㑁㑂㑃㑄㑅㑆㑈㑉㑊㑋㑌㑍㑎㑏㑐㑑㑒㑓㑔㑕㑖㑗㑘㑙㑚㑛㑜㑝㑞㑟㑠㑡㑢㑣㑤㑥㑦㑧㑨㑩㑪㑫㑬㑭㑮㑯㑰㑱㑲㑴㑵'
            u'㑶㑷㑸㑹㑺㑻㑼㑽㑾㑿㒀㒁㒂㒃㒄㒅㒆㒇㒈㒉㒊㒋㒌㒍㒎㒏㒐㒑㒒㒓㒔㒕㒖㒗㒘㒙㒚㒛㒜㒝㒞㒟㒠㒡㒢㒣㒤㒥㒦㒧㒨㒩㒪㒫㒬㒭㒮㒯'
            u'㒰㒱㒲㒳㒴㒵㒶㒷㒸㒹㒺㒻㒼㒽㒾㒿㓀㓁㓂㓃㓄㓅㓆㓇㓈㓉㓊㓋㓌㓍㓎㓏㓐㓑㓒㓓㓔㓕㓖㓗㓘㓙㓚㓛㓜㓝㓞㓟㓠㓡㓢㓣㓤㓥㓦㓧㓨㓩'
            u'㓪㓫㓬㓭㓮㓯㓰㓱㓲㓳㓴㓵㓶㓷㓸㓹㓺㓻㓼㓽㓾㓿㔀㔁㔂㔃㔄㔅㔆㔇㔈㔉㔊㔋㔌㔍㔎㔏㔐㔑㔒㔓㔔㔕㔖㔗㔘㔙㔚㔛㔜㔝㔞㔟㔠㔡㔢㔣'
            u'㔤㔥㔦㔧㔨㔩㔪㔫㔬㔭㔮㔯㔰㔱㔲㔳㔴㔵㔶㔷㔸㔹㔺㔻㔼㔽㔾㔿㕀㕁㕂㕃㕄㕅㕆㕇㕈㕉㕊㕋㕌㕍㕎㕏㕐㕑㕒㕓㕔㕕㕖㕗㕘㕙㕚㕛㕜㕝'
        ),
        'mongolian': (
            u'᠐᠑᠒᠓᠔᠕᠖᠗᠘᠙ᠠᠡᠢᠣᠤᠥᠦᠧᠨᠩᠪᠫᠬᠭᠮᠯᠰᠱᠲᠳᠴᠵᠶᠷᠸᠹᠺᠻᠼᠽᠾᠿᡀᡁᡂᡃᡄᡅᡆᡇᡈᡉᡊᡋᡌᡍᡎᡏᡐᡑᡒᡓᡔᡕᡖᡗᡘᡙᡚᡛᡜᡝᡞᡟᡠᡡᡢᡣᡤᡥᡦᡧᡨᡩᡪ'
            u'ᡫᡬᡭᡮᡯᡰᡱᡲᡳᡴᡵᡶᡷᢀᢁᢂᢃᢄᢅᢆᢇᢈᢉᢊᢋᢌᢍᢎᢏᢐᢑᢒᢓᢔᢕᢖᢗᢘᢙᢚᢛᢜᢝᢞᢟᢠᢡᢢᢣᢤᢥᢦᢧᢨᢩ'
        ),
        'uyghur': (
            u'ﺏﺐﺑﺒﺓﺔﺕﺖﺗﺘﺙﺚﺛﺜﺝﺞﺟﺠﺡﺢﺣﺤﺥﺦﺧﺨﺩﺪﺫﺬﺭﺮﺯﺰﺱﺲﺳﺴﺵﺶﺷﺸﺹﺺﺻﺼﺽﺾﺿﻀﻁﻂﻃﻄﻅﻆﻇﻈﻉﻊﻋﻌﻍﻎﻏﻐﻑﻒﻓﻔﻕﻖﻗﻘﻙﻚﻛﻜﻝﻞﻟﻠﻡ'
            u'ﻢﻣﻤﻥﻦﻧﻨﻩﻪﻫﻬﻭﻮﻯﻰﻱﮀﮁﮂﮃﮄﮅﮆﮇﮈﮉﮊﮋﮌﮍﮎﮏﮐﮑﮒﮓﮔﮕﮖﮗﮘﮙﮚﮛﮜﮝﮞﮟﮠﮡﮢﮣﮤﮥﮦﮧﮨﮩﮪﮫﮬﮭﮮﮯﮰﮱﯚﯛﯜﯝﯞﯟﯠﯡﯢ'
            u'ﯣﯤﯥﯦﯧﯨﯩﯪﯫﯬﯭﯮﯯﯰﯱﯲﯳﯴﯵﯶﯷﯸﯹﯺﯻﯼﯽﯾﯿﺄﺅﺆﺇﺈﺉﺊﺋﺌﺍﺎڡڢڣڤڥڦڧڨکڪګڬڭڮگڰڱڲڳڴڵڶڷڸڹںڻڼ'
            u'ڽھڿۀہۂۃۄۅۆۇۈۉۊۋیۍێۏېۑפֿﭏﭐﭑﭒﭓﭔﭕﭖﭗﭘﭙﭚﭛﭜﭝﭞﭟﭠﭡﭢﭣﭤﭥﭦﭧﭨﭩﭪﭫﭬﭭﭮﭯﭰﭱﭲﭳﭴﭵﭶﭷﭸﭹﭺﭻﭼﭽﭾﭿ'
            u'بةتثجحخدذرزسشصضٻټٽپٿڀځڂڃڄڅچڇڈډڊڋڌڍڎڏڐڑڒړڔڕږڗژڙښڛڜڝڞڟڠ'
        ),
        'tibetian': u'ༀཀཁགགྷངཅཆཇཉཊཋཌཌྷཎཏཐདདྷནཔཕབབྷམཙཚཛཛྷཝཞཟའཡརལཤཥསཧཨཀྵཪྈྉྊྋ',
        'yi': (
            u'ꀀꀁꀂꀃꀄꀅꀆꀇꀈꀉꀊꀋꀌꀍꀎꀏꀐꀑꀒꀓꀔꀕꀖꀗꀘꀙꀚꀛꀜꀝꀞꀟꀠꀡꀢꀣꀤꀥꀦꀧꀨꀩꀪꀫꀬꀭꀮꀯꀰꀱꀲꀳꀴꀵꀶꀷꀸꀹꀺꀻꀼꀽꀾꀿꁀꁁꁂꁃꁄꁅꁆꁇꁈꁉꁊꁋꁌꁍꁎꁏꁐꁑꁒꁓꁔ'
            u'ꁕꁖꁗꁘꁙꁚꁛꁜꁝꁞꁟꁠꁡꁢꁣꁤꁥꁦꁧꁨꁩꁪꁫꁬꁭꁮꁯꁰꁱꁲꁳꁴꁵꁶꁷꁸꁹꁺꁻꁼꁽꁾꁿꂀꂁꂂꂃꂄꂅꂆꂇꂈꂉꂊꂋꂌꂍꂎꂏꂐꂑꂒꂓꂔꂕꂖꂗꂘꂙꂚꂛꂜꂝꂞꂟꂠꂡꂢꂣꂤꂥꂦꂧꂨꂩ'
            u'ꂪꂫꂬꂭꂮꂯꂰꂱꂲꂳꂴꂵꂶꂷꂸꂹꂺꂻꂼꂽꂾꂿꃀꃁꃂꃃꃄꃅꃆꃇꃈꃉꃊꃋꃌꃍꃎꃏꃐꃑꃒꃓꃔꃕꃖꃗꃘꃙꃚꃛꃜꃝꃞꃟꃠꃡꃢꃣꃤꃥꃦꃧꃨꃩꃪꃫꃬꃭꃮꃯꃰꃱꃲꃳꃴꃵꃶꃷꃸꃹꃺꃻꃼꃽꃾ'
            u'ꃿꄀꄁꄂꄃꄄꄅꄆꄇꄈꄉꄊꄋꄌꄍꄎꄏꄐꄑꄒꄓꄔꄕꄖꄗꄘꄙꄚꄛꄜꄝꄞꄟꄠꄡꄢꄣꄤꄥꄦꄧꄨꄩꄪꄫꄬꄭꄮꄯꄰꄱꄲꄳꄴꄵꄶꄷꄸꄹꄺꄻꄼꄽꄾꄿꅀꅁꅂꅃꅄꅅꅆꅇꅈꅉꅊꅋꅌꅍꅎꅏꅐꅑꅒꅓ'
            u'ꅔꅕꅖꅗꅘꅙꅚꅛꅜꅝꅞꅟꅠꅡꅢꅣꅤꅥꅦꅧꅨꅩꅪꅫꅬꅭꅮꅯꅰꅱꅲꅳꅴꅵꅶꅷꅸꅹꅺꅻꅼꅽꅾꅿꆀꆁꆂꆃꆄꆅꆆꆇꆈꆉꆊꆋꆌꆍꆎꆏꆐꆑꆒꆓꆔꆕꆖꆗꆘꆙꆚꆛꆜꆝꆞꆟꆠꆡꆢꆣꆤꆥꆦꆧꆨ'
            u'ꆩꆪꆫꆬꆭꆮꆯꆰꆱꆲꆳꆴꆵꆶꆷꆸꆹꆺꆻꆼꆽꆾꆿꇀꇁꇂꇃꇄꇅꇆꇇꇈꇉꇊꇋꇌꇍꇎꇏꇐꇑꇒꇓꇔꇕꇖꇗꇘꇙꇚꇛꇜꇝꇞꇟꇠꇡꇢꇣꇤꇥꇦꇧꇨꇩꇪꇫꇬꇭꇮꇯꇰꇱꇲꇳꇴꇵꇶꇷꇸꇹꇺꇻꇼ'
            u'ꇽꇾꇿꈀꈁꈂꈃꈄꈅꈆꈇꈈꈉ'
        ),
        'zang': (
            u'ꃙꃚꃛꃜꃝꃞꃟꃠꃡꃢꃣꃤꃥꃦꃧꃨꃩꃪꃫꃬꃭꃮꃯꃰꃱꃲꃳꃴꃵꃶꃷꃸꃹꃺꃻꃼꃽꃾꃿꄀꄁꄂꄃꄄꄅꄆꄇꄈꄉꄊꄋꄌꄍꄎꄏꄐꄑꄒꄓꄔꄕꄖꄗꄘꄙꄚꄛꄜꄝꄞꄟꄠꄡꄢꄣꄤꄥꄦꄧꄨꄩꄪꄫꄬꄭ'
            u'ꄮꄯꄰꄱꄲꄳꄴꄵꄶꄷꄸꄹꄺꄻꄼꄽꄾꄿꅀꅁꅂꅃꅄꅅꅆꅇꅈꅉꅊꅋꅌꅍꅎꅏꅐꅑꅒꅓꅔꅕꅖꅗꅘꅙꅚꅛꅜꅝꅞꅟꅠꅡꅢꅣꅤꅥꅦꅧꅨꅩꅪꅫꅬꅭꅮꅯꅰꅱꅲꅳꅴꅵꅶꅷꅸꅹꅺꅻꅼꅽꅾꅿꆀꆁꆂ'
            u'ꆃꆄꆅꆆꆇꆈꆉꆊꆋꆌꆍꆎꆏꆐꆑꆒꆓꆔꆕꆖꆗꆘꆙꆚꆛꆜꆝꆞꆟꆠꆡꆢꆣꆤꆥꆦꆧꆨꆩꆪꆫꆬꆭꆮꆯꆰꆱꆲꆳꆴꆵꆶꆷꆸꆹꆺꆻꆼꆽꆾꆿꇀꇁꇂꇃꇄꇅꇆꇇꇈꇉꇊꇋꇌꇍꇎꇏꇐꇑꇒꇓꇔꇕꇖꇗ'
            u'ꇘꇙꇚꇛꇜꇝꇞꇟꇠꇡꇢꇣꇤꇥꇦꇧꇨꇩꇪꇫꇬꇭꇮꇯꇰꇱꇲꇳꇴꇵꇶꇷꇸꇹꇺꇻꇼꇽꇾꇿꈀꈁꈂꈃꈄꈅꈆꈇꈈꈉꈊꈋꈌꈍꈎꈏꈐꈑꈒꈓꈔꈕꈖꈗꈘꈙꈚꈛꈜꈝꈞꈟꈠꈡꈢꈣꈤꈥꈦꈧꈨꈩꈪꈫꈬ'
            u'ꈭꈮꈯꈰꈱꈲꈳꈴꈵꈶꈷꈸꈹꈺꈻꈼꈽꈾꈿꉀꉁꉂꉃꉄꉅꉆꉇꉈꉉꉊꉋꉌꉍꉎꉏꉐꉑꉒꉓꉔꉕꉖꉗꉘꉙꉚꉛꉜꉝꉞꉟꉠꉡꉢꉣꉤ'
        )
    }


class TestGlobalizationResultSet(GlobalizationTests):
    def test_charset_double(self):
        self.run_charset_validation('double')

    def test_charset_four(self):
        self.run_charset_validation('four')

    def test_charset_mongolian(self):
        self.run_charset_validation('mongolian')

    def test_charset_uyghur(self):
        self.run_charset_validation('uyghur')

    def test_charset_tibetian(self):
        self.run_charset_validation('tibetian')

    def test_charset_yi(self):
        self.run_charset_validation('yi')

    def test_charset_zang(self):
        self.run_charset_validation('zang')

    def run_charset_validation(self, charset):
        """
            Verify the column names and string values in rows returned by
            select statement are properly encoded as unicode.
        """
        local_machine_name = socket.gethostname().replace('-', '_').replace('.', '_')
        try:
            client = create_mssql_cli_client()

            # Each characters in charset is a string with max length 50
            # Each time in the for loop, the string used for 'create table' and
            # 'insert into' statement that are executed by client.execute_query().
            # We validates the query results are the same value we inserted and
            # they are properly unicode encoded.
            for characters in self.get_next_characters(charset):
                test_str = characters
                col1_name = u'col1_{0}'.format(test_str)
                col2_name = u'col2_{0}'.format(test_str)
                table_name = u'#mssqlcli_{0}_{1}_{2}'.format(local_machine_name,
                                                             random_str(), test_str)
                setup_query = u"CREATE TABLE {0} ({1} nvarchar(MAX), {2} int);"\
                    u"INSERT INTO {0} VALUES (N'value_{3}1', 1);"\
                    u"INSERT INTO {0} VALUES (N'value_{3}2', 2);"\
                    .format(table_name, col1_name, col2_name, test_str)

                if not self.run_query(client, setup_query):
                    assert False #should not fail

                select_query = u"SELECT {0}, {1} FROM {2};".format(col1_name, col2_name, table_name)
                for rows, columns, _, _, is_error in client.execute_query(select_query):
                    assert not is_error
                    assert len(columns) == 2
                    assert columns[0] == col1_name
                    assert columns[1] == col2_name
                    assert len(rows) == 2
                    assert rows[0][0] == u'value_{0}1'.format(test_str)
                    assert rows[1][0] == u'value_{0}2'.format(test_str)
        finally:
            shutdown(client)

@pytest.mark.unstable
class TestGlobalizationMetadata(GlobalizationTests):
    @staticmethod
    @pytest.fixture(scope="class")
    def test_db():
        db = create_test_db()
        yield db
        clean_up_test_db(db)

    def test_schema_metadata_double(self, test_db):
        self.run_schema_metadata_validation('double', test_db)

    def test_schema_metadata_four(self, test_db):
        self.run_schema_metadata_validation('four', test_db)

    def test_schema_metadata_mongolian(self, test_db):
        self.run_schema_metadata_validation('mongolian', test_db)

    def test_schema_metadata_uyghur(self, test_db):
        self.run_schema_metadata_validation('uyghur', test_db)

    def test_schema_metadata_tibetian(self, test_db):
        self.run_schema_metadata_validation('tibetian', test_db)

    def test_schema_metadata_yi(self, test_db):
        self.run_schema_metadata_validation('yi', test_db)

    def test_schema_metadata_zang(self, test_db):
        self.run_schema_metadata_validation('zang', test_db)

    def test_table_metadata_double(self, test_db):
        self.run_schema_metadata_validation('double', test_db)

    def test_table_metadata_four(self, test_db):
        self.run_schema_metadata_validation('four', test_db)

    def test_table_metadata_mongolian(self, test_db):
        self.run_schema_metadata_validation('mongolian', test_db)

    def test_table_metadata_uyghur(self, test_db):
        self.run_schema_metadata_validation('uyghur', test_db)

    def test_table_metadata_tibetian(self, test_db):
        self.run_schema_metadata_validation('tibetian', test_db)

    def test_table_metadata_yi(self, test_db):
        self.run_schema_metadata_validation('yi', test_db)

    def test_table_metadata_zang(self, test_db):
        self.run_schema_metadata_validation('zang', test_db)

    def run_schema_metadata_validation(self, charset, test_db):
        try:
            # setup db
            test_db_name = test_db
            client = self.create_mssqlcliclient(test_db_name)
            new_schemas = []

            for characters in self.get_next_characters(self.charset_dict[charset]):
                schema_name = u'mssqlcli_{0}_{1}_{2}'.format(
                    self.get_local_machine_name(), random_str(), characters)
                query = u'CREATE SCHEMA {0}'.format(schema_name)
                if self.run_query(client, query):
                    new_schemas.append(schema_name)
                else:
                    assert False # should not fail

            completer = MssqlCompleter(smart_completion=True)
            completion_refresher.refresh_schemas(completer, client)
            completions = completer.get_completions(
                document=Document(u'select * from ', 14, None),
                complete_event=None, smart_completion=True)
            db_schemas = set(map(lambda e: e.text, completions))
            for new_schema in new_schemas:
                assert u'"{}"'.format(new_schema) in db_schemas
        finally:
            shutdown(client)

    @staticmethod
    def create_mssqlcliclient(database_name=None):
        options = create_mssql_cli_options()
        if database_name is not None:
            options.database = database_name
        return create_mssql_cli_client(options=options)

    @staticmethod
    def get_local_machine_name():
        return socket.gethostname().replace('-', '_').replace('.', '_')
