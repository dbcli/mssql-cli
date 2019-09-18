# coding=utf-8
import unittest
import socket
from utility import random_str
from mssqltestutils import create_mssql_cli_client, shutdown
from mssqlcli.mssqlcompleter import MssqlCompleter
import mssqlcli.completion_refresher as completion_refresher
from prompt_toolkit.document import Document


"""
All tests require a live connection to test server.
Make modifications to mssqlutils.create_mssql_cli_client()
to use a different server and database.
Please Note: These tests cannot be run offline.
"""


class GlobalizationResultSetTests(unittest.TestCase):
    
    def test_charset_double(self):
        charset = GB18030()
        characters_list = (charset.
            get_next_characters(charset.get_double_characters()))
        self.run_charset_validation(characters_list)
    

    def test_charset_four(self):
        charset = GB18030()
        characters_list = (charset.
            get_next_characters(charset.get_four_characters()))
        self.run_charset_validation(characters_list)


    def test_charset_mongolian(self):
        charset = GB18030()
        characters_list = (charset.
            get_next_characters(charset.get_mongolian_characters()))
        self.run_charset_validation(characters_list)


    def test_charset_uyghur(self):
        charset = GB18030()
        characters_list = (charset.
            get_next_characters(charset.get_uyghur_characters()))
        self.run_charset_validation(characters_list)


    def test_charset_tibetian(self):
        charset = GB18030()
        characters_list = (charset.
            get_next_characters(charset.get_tibetian_characters()))
        self.run_charset_validation(characters_list)


    def test_charset_yi(self):
        charset = GB18030()
        characters_list = (charset.
            get_next_characters(charset.get_yi_characters()))
        self.run_charset_validation(characters_list)


    def test_charset_zang(self):
        charset = GB18030()
        characters_list = (charset.
            get_next_characters(charset.get_zang_characters()))
        self.run_charset_validation(characters_list)

    
    def run_charset_validation(self, characters_list):
        """
            Verify the column names and string values in rows returned by
            select statement are properly encoded as unicode.
        """
        local_machine_name = socket.gethostname().replace('-','_').replace('.','_')
        try:
            client = create_mssql_cli_client()

            # Each characters in characters_list is a string with max length 50
            # Each time in the for loop, the string used for 'create table' and 'insert into' statement
            # that are executed by client.execute_query().
            # We validates the query results are the same value we inserted and
            # they are properly unicode encoded.
            for characters in characters_list:
                test_str = characters
                col1_name = u'col_{0}1'.format(test_str)
                col2_name = u'col_{0}2'.format(test_str)
                table_name = u'#mssqlcli_{0}_{1}_{2}'.format(local_machine_name, random_str(), test_str)
                setup_query = u"CREATE TABLE {0} ({1} nvarchar(MAX), {2} int);"\
                    u"INSERT INTO {0} VALUES (N'value_{3}1', 1);"\
                    u"INSERT INTO {0} VALUES (N'value_{3}2', 2);"\
                    .format(table_name, col1_name, col2_name, test_str)
                
                for rows, columns, status, statement, is_error in client.execute_query(setup_query):
                    assert is_error == False

                select_query = u"SELECT {0}, {1} FROM {2};".format(col1_name, col2_name, table_name)
                for rows, columns, status, statement, is_error in client.execute_query(select_query):
                    assert is_error == False
                    assert len(rows) == 2
                    assert rows[0][0] == u'value_{0}1'.format(test_str)
                    assert rows[1][0] == u'value_{0}2'.format(test_str)
        finally:
            shutdown(client)


class GlobalizationMetadataTests(unittest.TestCase):

    def test_schema_metadata_double(self):
        charset = GB18030()
        characters_list = (charset.
            get_next_characters(charset.get_double_characters()))
        self.run_schema_metadata_validation(characters_list)


    def run_schema_metadata_validation(self, characters_list):
        client = create_mssql_cli_client()
        completer = MssqlCompleter(smart_completion=True)
        new_schemas = []
        try:
            for characters in characters_list:
                schema_name = (u'mssqlcli_{0}_{1}_{2}'.
                    format(get_local_machine_name(), random_str(), characters))
                query = u'CREATE SCHEMA {0}'.format(schema_name)
                for _, _, _, _, is_error in client.execute_query(query):
                    assert is_error is False
                    new_schemas.append(schema_name)
            completion_refresher.refresh_schemas(completer, client)
            completions = (completer.
                get_completions(document=Document(u'select * from ', 14, None),
                complete_event=None, smart_completion=True))
            db_schemas = set(map(lambda e: e.text, completions))
            for new_schema in new_schemas:
                assert u'"{}"'.format(new_schema) in db_schemas
        finally:
            for new_schema in new_schemas:
                try:
                    query = u'DROP SCHEMA IF EXISTS {0}'.format(new_schema)
                    for _, _, _, _, _ in client.execute_query(query):
                        pass
                except:
                    pass
            shutdown(client)


def get_local_machine_name():
    return socket.gethostname().replace('-','_').replace('.','_')


class GB18030(object):

    def get_double_characters(self):
        return (
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
        )
            

    def get_four_characters(self):
        return (
            u'㐀㐁㐂㐃㐄㐅㐆㐇㐈㐉㐊㐋㐌㐍㐎㐏㐐㐑㐒㐓㐔㐕㐖㐗㐘㐙㐚㐛㐜㐝㐞㐟㐠㐡㐢㐣㐤㐥㐦㐧㐨㐩㐪㐫㐬㐭㐮㐯㐰㐱㐲㐳㐴㐵㐶㐷㐸㐹'
            u'㐺㐻㐼㐽㐾㐿㑀㑁㑂㑃㑄㑅㑆㑈㑉㑊㑋㑌㑍㑎㑏㑐㑑㑒㑓㑔㑕㑖㑗㑘㑙㑚㑛㑜㑝㑞㑟㑠㑡㑢㑣㑤㑥㑦㑧㑨㑩㑪㑫㑬㑭㑮㑯㑰㑱㑲㑴㑵'
            u'㑶㑷㑸㑹㑺㑻㑼㑽㑾㑿㒀㒁㒂㒃㒄㒅㒆㒇㒈㒉㒊㒋㒌㒍㒎㒏㒐㒑㒒㒓㒔㒕㒖㒗㒘㒙㒚㒛㒜㒝㒞㒟㒠㒡㒢㒣㒤㒥㒦㒧㒨㒩㒪㒫㒬㒭㒮㒯'
            u'㒰㒱㒲㒳㒴㒵㒶㒷㒸㒹㒺㒻㒼㒽㒾㒿㓀㓁㓂㓃㓄㓅㓆㓇㓈㓉㓊㓋㓌㓍㓎㓏㓐㓑㓒㓓㓔㓕㓖㓗㓘㓙㓚㓛㓜㓝㓞㓟㓠㓡㓢㓣㓤㓥㓦㓧㓨㓩'
            u'㓪㓫㓬㓭㓮㓯㓰㓱㓲㓳㓴㓵㓶㓷㓸㓹㓺㓻㓼㓽㓾㓿㔀㔁㔂㔃㔄㔅㔆㔇㔈㔉㔊㔋㔌㔍㔎㔏㔐㔑㔒㔓㔔㔕㔖㔗㔘㔙㔚㔛㔜㔝㔞㔟㔠㔡㔢㔣'
            u'㔤㔥㔦㔧㔨㔩㔪㔫㔬㔭㔮㔯㔰㔱㔲㔳㔴㔵㔶㔷㔸㔹㔺㔻㔼㔽㔾㔿㕀㕁㕂㕃㕄㕅㕆㕇㕈㕉㕊㕋㕌㕍㕎㕏㕐㕑㕒㕓㕔㕕㕖㕗㕘㕙㕚㕛㕜㕝'
        )


    def get_mongolian_characters(self):
        return (
            u'᠐᠑᠒᠓᠔᠕᠖᠗᠘᠙ᠠᠡᠢᠣᠤᠥᠦᠧᠨᠩᠪᠫᠬᠭᠮᠯᠰᠱᠲᠳᠴᠵᠶᠷᠸᠹᠺᠻᠼᠽᠾᠿᡀᡁᡂᡃᡄᡅᡆᡇᡈᡉᡊᡋᡌᡍᡎᡏᡐᡑᡒᡓᡔᡕᡖᡗᡘᡙᡚᡛᡜᡝᡞᡟᡠᡡᡢᡣᡤᡥᡦᡧᡨᡩᡪᡫᡬᡭᡮᡯᡰᡱᡲᡳᡴᡵᡶᡷᢀᢁᢂᢃᢄᢅᢆᢇᢈᢉᢊᢋᢌᢍᢎᢏᢐᢑᢒᢓᢔᢕᢖᢗᢘᢙᢚᢛᢜᢝᢞᢟᢠᢡᢢᢣᢤᢥᢦᢧᢨᢩ'
        )


    def get_uyghur_characters(self):
        return (
            u'ﺏﺐﺑﺒﺓﺔﺕﺖﺗﺘﺙﺚﺛﺜﺝﺞﺟﺠﺡﺢﺣﺤﺥﺦﺧﺨﺩﺪﺫﺬﺭﺮﺯﺰﺱﺲﺳﺴﺵﺶﺷﺸﺹﺺﺻﺼﺽﺾﺿﻀﻁﻂﻃﻄﻅﻆﻇﻈﻉﻊﻋﻌﻍﻎﻏﻐﻑﻒﻓﻔﻕﻖﻗﻘﻙﻚﻛﻜﻝﻞﻟﻠﻡﻢﻣﻤﻥﻦﻧﻨﻩﻪﻫﻬﻭﻮﻯﻰﻱ'
            u'ﮀﮁﮂﮃﮄﮅﮆﮇﮈﮉﮊﮋﮌﮍﮎﮏﮐﮑﮒﮓﮔﮕﮖﮗﮘﮙﮚﮛﮜﮝﮞﮟﮠﮡﮢﮣﮤﮥﮦﮧﮨﮩﮪﮫﮬﮭﮮﮯﮰﮱﯚﯛﯜﯝﯞﯟﯠﯡﯢﯣﯤﯥﯦﯧﯨﯩﯪﯫﯬﯭﯮﯯﯰﯱﯲﯳﯴﯵﯶﯷﯸﯹﯺﯻﯼﯽﯾﯿﺄﺅﺆﺇﺈﺉﺊﺋﺌﺍﺎ'
            u'ڡڢڣڤڥڦڧڨکڪګڬڭڮگڰڱڲڳڴڵڶڷڸڹںڻڼڽھڿۀہۂۃۄۅۆۇۈۉۊۋیۍێۏېۑפֿﭏﭐﭑﭒﭓﭔﭕﭖﭗﭘﭙﭚﭛﭜﭝﭞﭟﭠﭡﭢﭣﭤﭥﭦﭧﭨﭩﭪﭫﭬﭭﭮﭯﭰﭱﭲﭳﭴﭵﭶﭷﭸﭹﭺﭻﭼﭽﭾﭿ'
            u'بةتثجحخدذرزسشصضٻټٽپٿڀځڂڃڄڅچڇڈډڊڋڌڍڎڏڐڑڒړڔڕږڗژڙښڛڜڝڞڟڠ'
        )


    def get_tibetian_characters(self):
        return u'ༀཀཁགགྷངཅཆཇཉཊཋཌཌྷཎཏཐདདྷནཔཕབབྷམཙཚཛཛྷཝཞཟའཡརལཤཥསཧཨཀྵཪྈྉྊྋ'


    def get_yi_characters(self):
        return (
            u'ꀀꀁꀂꀃꀄꀅꀆꀇꀈꀉꀊꀋꀌꀍꀎꀏꀐꀑꀒꀓꀔꀕꀖꀗꀘꀙꀚꀛꀜꀝꀞꀟꀠꀡꀢꀣꀤꀥꀦꀧꀨꀩꀪꀫꀬꀭꀮꀯꀰꀱꀲꀳꀴꀵꀶꀷꀸꀹꀺꀻꀼꀽꀾꀿꁀꁁꁂꁃꁄꁅꁆꁇꁈꁉꁊꁋꁌꁍꁎꁏꁐꁑꁒꁓꁔꁕꁖ'
            u'ꁗꁘꁙꁚꁛꁜꁝꁞꁟꁠꁡꁢꁣꁤꁥꁦꁧꁨꁩꁪꁫꁬꁭꁮꁯꁰꁱꁲꁳꁴꁵꁶꁷꁸꁹꁺꁻꁼꁽꁾꁿꂀꂁꂂꂃꂄꂅꂆꂇꂈꂉꂊꂋꂌꂍꂎꂏꂐꂑꂒꂓꂔꂕꂖꂗꂘꂙꂚꂛꂜꂝꂞꂟꂠꂡꂢꂣꂤꂥꂦꂧꂨꂩꂪꂫꂬꂭ'
            u'ꂮꂯꂰꂱꂲꂳꂴꂵꂶꂷꂸꂹꂺꂻꂼꂽꂾꂿꃀꃁꃂꃃꃄꃅꃆꃇꃈꃉꃊꃋꃌꃍꃎꃏꃐꃑꃒꃓꃔꃕꃖꃗꃘꃙꃚꃛꃜꃝꃞꃟꃠꃡꃢꃣꃤꃥꃦꃧꃨꃩꃪꃫꃬꃭꃮꃯꃰꃱꃲꃳꃴꃵꃶꃷꃸꃹꃺꃻꃼꃽꃾꃿꄀꄁꄂꄃꄄ'
            u'ꄅꄆꄇꄈꄉꄊꄋꄌꄍꄎꄏꄐꄑꄒꄓꄔꄕꄖꄗꄘꄙꄚꄛꄜꄝꄞꄟꄠꄡꄢꄣꄤꄥꄦꄧꄨꄩꄪꄫꄬꄭꄮꄯꄰꄱꄲꄳꄴꄵꄶꄷꄸꄹꄺꄻꄼꄽꄾꄿꅀꅁꅂꅃꅄꅅꅆꅇꅈꅉꅊꅋꅌꅍꅎꅏꅐꅑꅒꅓꅔꅕꅖꅗꅘꅙꅚꅛ'
            u'ꅜꅝꅞꅟꅠꅡꅢꅣꅤꅥꅦꅧꅨꅩꅪꅫꅬꅭꅮꅯꅰꅱꅲꅳꅴꅵꅶꅷꅸꅹꅺꅻꅼꅽꅾꅿꆀꆁꆂꆃꆄꆅꆆꆇꆈꆉꆊꆋꆌꆍꆎꆏꆐꆑꆒꆓꆔꆕꆖꆗꆘꆙꆚꆛꆜꆝꆞꆟꆠꆡꆢꆣꆤꆥꆦꆧꆨꆩꆪꆫꆬꆭꆮꆯꆰꆱꆲ'
            u'ꆳꆴꆵꆶꆷꆸꆹꆺꆻꆼꆽꆾꆿꇀꇁꇂꇃꇄꇅꇆꇇꇈꇉꇊꇋꇌꇍꇎꇏꇐꇑꇒꇓꇔꇕꇖꇗꇘꇙꇚꇛꇜꇝꇞꇟꇠꇡꇢꇣꇤꇥꇦꇧꇨꇩꇪꇫꇬꇭꇮꇯꇰꇱꇲꇳꇴꇵꇶꇷꇸꇹꇺꇻꇼꇽꇾꇿꈀꈁꈂꈃꈄꈅꈆꈇꈈꈉ'
        )


    def get_zang_characters(self):
        return (
            u'ꃙꃚꃛꃜꃝꃞꃟꃠꃡꃢꃣꃤꃥꃦꃧꃨꃩꃪꃫꃬꃭꃮꃯꃰꃱꃲꃳꃴꃵꃶꃷꃸꃹꃺꃻꃼꃽꃾꃿꄀꄁꄂꄃꄄꄅꄆꄇꄈꄉꄊꄋꄌꄍꄎꄏꄐꄑꄒꄓꄔꄕꄖꄗꄘꄙꄚꄛꄜꄝꄞꄟꄠꄡꄢꄣꄤꄥꄦꄧꄨꄩꄪꄫꄬꄭꄮꄯ'
            u'ꄰꄱꄲꄳꄴꄵꄶꄷꄸꄹꄺꄻꄼꄽꄾꄿꅀꅁꅂꅃꅄꅅꅆꅇꅈꅉꅊꅋꅌꅍꅎꅏꅐꅑꅒꅓꅔꅕꅖꅗꅘꅙꅚꅛꅜꅝꅞꅟꅠꅡꅢꅣꅤꅥꅦꅧꅨꅩꅪꅫꅬꅭꅮꅯꅰꅱꅲꅳꅴꅵꅶꅷꅸꅹꅺꅻꅼꅽꅾꅿꆀꆁꆂꆃꆄꆅꆆ'
            u'ꆇꆈꆉꆊꆋꆌꆍꆎꆏꆐꆑꆒꆓꆔꆕꆖꆗꆘꆙꆚꆛꆜꆝꆞꆟꆠꆡꆢꆣꆤꆥꆦꆧꆨꆩꆪꆫꆬꆭꆮꆯꆰꆱꆲꆳꆴꆵꆶꆷꆸꆹꆺꆻꆼꆽꆾꆿꇀꇁꇂꇃꇄꇅꇆꇇꇈꇉꇊꇋꇌꇍꇎꇏꇐꇑꇒꇓꇔꇕꇖꇗꇘꇙꇚꇛꇜꇝ'
            u'ꇞꇟꇠꇡꇢꇣꇤꇥꇦꇧꇨꇩꇪꇫꇬꇭꇮꇯꇰꇱꇲꇳꇴꇵꇶꇷꇸꇹꇺꇻꇼꇽꇾꇿꈀꈁꈂꈃꈄꈅꈆꈇꈈꈉꈊꈋꈌꈍꈎꈏꈐꈑꈒꈓꈔꈕꈖꈗꈘꈙꈚꈛꈜꈝꈞꈟꈠꈡꈢꈣꈤꈥꈦꈧꈨꈩꈪꈫꈬꈭꈮꈯꈰꈱꈲꈳꈴ'
            u'ꈵꈶꈷꈸꈹꈺꈻꈼꈽꈾꈿꉀꉁꉂꉃꉄꉅꉆꉇꉈꉉꉊꉋꉌꉍꉎꉏꉐꉑꉒꉓꉔꉕꉖꉗꉘꉙꉚꉛꉜꉝꉞꉟꉠꉡꉢꉣꉤ'
        )


    def get_next_characters(self, all_characters, count=50):
        """
        Takes 50 characters (by default) at a time from all_characters and
        yield them as a string until all_characters becomes empty.
        """
        while(len(all_characters) > 0):
            next_characters_length = min(len(all_characters), count)
            next_characters = all_characters[0:next_characters_length]
            all_characters = all_characters[next_characters_length:]
            yield next_characters