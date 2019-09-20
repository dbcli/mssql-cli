# coding=utf-8
import unittest
import socket
import os
from utility import random_str
from mssqltestutils import (create_mssql_cli_client,
    create_mssql_cli_options, shutdown)
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
        characters_list = charset.get_next_characters(
            charset.get_double_characters())
        self.run_charset_validation(characters_list)
    

    def test_charset_four(self):
        charset = GB18030()
        characters_list = charset.get_next_characters(
            charset.get_four_characters())
        self.run_charset_validation(characters_list)


    def test_charset_mongolian(self):
        charset = GB18030()
        characters_list = charset.get_next_characters(
            charset.get_mongolian_characters())
        self.run_charset_validation(characters_list)


    def test_charset_uyghur(self):
        charset = GB18030()
        characters_list = charset.get_next_characters(
            charset.get_uyghur_characters())
        self.run_charset_validation(characters_list)


    def test_charset_tibetian(self):
        charset = GB18030()
        characters_list = charset.get_next_characters(
            charset.get_tibetian_characters())
        self.run_charset_validation(characters_list)


    def test_charset_yi(self):
        charset = GB18030()
        characters_list = charset.get_next_characters(
            charset.get_yi_characters())
        self.run_charset_validation(characters_list)


    def test_charset_zang(self):
        charset = GB18030()
        characters_list = charset.get_next_characters(
            charset.get_zang_characters())
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
                col1_name = u'col1_{0}'.format(test_str)
                col2_name = u'col2_{0}'.format(test_str)
                table_name = u'#mssqlcli_{0}_{1}_{2}'.format(local_machine_name, random_str(), test_str)
                setup_query = u"CREATE TABLE {0} ({1} nvarchar(MAX), {2} int);"\
                    u"INSERT INTO {0} VALUES (N'value_{3}1', 1);"\
                    u"INSERT INTO {0} VALUES (N'value_{3}2', 2);"\
                    .format(table_name, col1_name, col2_name, test_str)
                
                if (not run_query(client, setup_query)):
                    assert False #should not fail

                select_query = u"SELECT {0}, {1} FROM {2};".format(col1_name, col2_name, table_name)
                for rows, columns, _, _, is_error in client.execute_query(select_query):
                    assert is_error == False
                    assert len(columns) == 2
                    assert columns[0] == col1_name
                    assert columns[1] == col2_name
                    assert len(rows) == 2
                    assert rows[0][0] == u'value_{0}1'.format(test_str)
                    assert rows[1][0] == u'value_{0}2'.format(test_str)
        finally:
            shutdown(client)


class GlobalizationMetadataTests(unittest.TestCase):

    def test_schema_metadata(self):
        characters_list = get_GB18030_characters_list()
        try:
            client1 = create_mssql_cli_client()
            test_db_name = get_random_db_name()
            query = u"CREATE DATABASE {0};".format(test_db_name)
            run_query(client1, query)

            options = create_mssql_cli_options()
            options.database = test_db_name
            client2 = create_mssql_cli_client(options=options)
            new_schemas = []
            for characters in characters_list:
                schema_name = u'mssqlcli_{0}_{1}_{2}'.format(
                    get_local_machine_name(), random_str(), characters)
                query = u'CREATE SCHEMA {0}'.format(schema_name)
                if run_query(client2, query):
                    new_schemas.append(schema_name)
                else:
                    assert False # should not fail

            completer = MssqlCompleter(smart_completion=True)
            completion_refresher.refresh_schemas(completer, client2)
            completions = completer.get_completions(
                document=Document(u'select * from ', 14, None),
                complete_event=None, smart_completion=True)
            db_schemas = set(map(lambda e: e.text, completions))
            for new_schema in new_schemas:
                assert u'"{}"'.format(new_schema) in db_schemas
        finally:
            shutdown(client2)
            run_query(client1, u'DROP DATABASE {0}'.format(test_db_name))
            shutdown(client1)


    def test_table_metadata(self):
        characters_list = get_GB18030_characters_list()
        try:
            client1 = create_mssql_cli_client()
            test_db_name = get_random_db_name()
            query = u"CREATE DATABASE {0};".format(test_db_name)
            run_query(client1, query)

            options = create_mssql_cli_options()
            options.database = test_db_name
            client2 = create_mssql_cli_client(options=options)
            new_tables = []
            for characters in characters_list:
                col1_name = u'col_{0}1'.format(characters)
                col2_name = u'col_{0}2'.format(characters)
                table_name = u'mssqlcli_{0}_{1}_{2}'.format(
                    get_local_machine_name(), random_str(), characters)
                query = u"CREATE TABLE {0} ({1} nvarchar(MAX), {2} int);".format(
                    table_name, col1_name, col2_name)
                if (run_query(client2, query)):
                    new_tables.append(table_name)

            completer = MssqlCompleter(smart_completion=True)
            completion_refresher.refresh_schemas(completer, client2)
            completion_refresher.refresh_tables(completer, client2)
            test_query = u'select * from "dbo".'
            completions = completer.get_completions(
                document=Document(test_query, len(test_query), None),
                complete_event=None, smart_completion=True)
            
            db_tables = set(map(lambda e: e.text, completions))
            assert len(db_tables) > 0
            for new_table in new_tables:
                assert u'"{}"'.format(new_table) in db_tables
        finally:
            shutdown(client2)
            run_query(client1, u'DROP DATABASE {0}'.format(test_db_name))
            shutdown(client1)


def get_local_machine_name():
    return socket.gethostname().replace('-','_').replace('.','_')


def get_random_db_name():
    return u'mssqlcli_testdb_{0}_{1}'.format(
        get_local_machine_name(), random_str())


def get_GB18030_characters_list():
    charset = GB18030()
    return charset.get_next_characters(charset.get_all_characters())


def run_query(mssqlcliclient, query):
    success = True
    try:
        for _, _, _, _, is_error in mssqlcliclient.execute_query(query):
            if is_error is True:
                success = False
                break
    except:
        success = False
    return success


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
    
    def get_all_characters(self):
        return u''.join([
            self.get_double_characters(),
            self.get_four_characters(),
            self.get_mongolian_characters(),
            self.get_uyghur_characters(),
            self.get_tibetian_characters(),
            self.get_yi_characters(),
            self.get_zang_characters()
        ])
        