import json
import urllib.request
import urllib.parse
# import Levenshtein
import re
# import bs4
# import nltk
from sys import stderr
from traceback import print_exc
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from lxml import etree

#global
TIME_COUNT = 0
TIME_LIST = list()


class _DeHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__text = []

    def handle_data(self, data):
        text = data.strip()
        if len(text) > 0:
            text = re.sub('[ \t\r\n]+', ' ', text)
            self.__text.append(text + ' ')

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.__text.append('\n\n')
        elif tag == 'br':
            self.__text.append('\n')

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self.__text.append('\n\n')

    def text(self):
        return ''.join(self.__text).strip()

class myTest:
    headers = dict()
    responseInfo = dict()

    def __init__(self):
        self.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36"

    def getCharSetNull(self):
        if len(self.responseInfo['Content-Type'].split('='))>1:
            return self.responseInfo['Content-Type'].split('=')[1]
        return "utf-8"

    def getCharSet(self,content_type):
        return str(content_type).split('=')[1]

    def getHtml(self,url):
        global headers
        request = urllib.request.Request(url, headers=self.headers)
        response = urllib.request.urlopen(request,data=None,timeout=15)
        html = response.read()

        self.responseInfo = response.info()
        try:
            return html.decode(str(self.getCharSetNull()))
        except UnicodeDecodeError:
            try:
                return html.decode('utf-8')
            except UnicodeDecodeError:
                return html.decode('gbk','ignore')
        # return html.decode('utf-8')

class processHTML():
    html = ""
    def setHTML(self,HTML):
        self.html = HTML
    def getHTML(self):
        return self.html

    def addCharSet(self,charSet):
        char_pattern = re.compile("(?<=<head>).*?(?=<)",re.S)
        self.html = re.sub(char_pattern,'<meta charset='+'"'+charSet+'">',self.html)

    def removeScript(self):
        script_pattern = re.compile("<script.*?</script>",re.S)
        script_pattern_single = re.compile("<script.*?/>")
        self.html = re.sub(script_pattern,'',self.html)

    def removeStyle(self):
        style_pattern = re.compile("<style.*?</style>", re.S)
        self.html = re.sub(style_pattern,'',self.html)

    def removeMeta(self):
        meta_pattern_single = re.compile("<meta.*?/>",re.S)
        meta_pattern = re.compile("<meta.*?>",re.S)
        self.html = re.sub(meta_pattern, '', self.html)
        # result = re.match(meta_pattern,self.html)
        # if result:
        #     for eachGroup in result.groups():
        #         if not "charset" in eachGroup:
        #             self.html = self.html.replace(eachGroup,'')
        # result_single = re.match(meta_pattern_single,self.html)
        # if result_single:
        #     for eachGroup in result_single.groups():
        #         if not "charset" in eachGroup:
        #             self.html = self.html.replace(eachGroup, '')

    def removeLink(self):
        link_pattern_single = re.compile("<link.*?>",re.S)
        link_pattern = re.compile("<link.*?</link>",re.S)
        self.html = re.sub(link_pattern, '', self.html)
        self.html = re.sub(link_pattern_single,'',self.html)

    def removeSelect(self):
        select_pattern_single = re.compile("<select.*?>",re.S)
        select_pattern = re.compile("<select.*?</select>",re.S)
        self.html = re.sub(select_pattern, '', self.html)
        self.html = re.sub(select_pattern_single, '', self.html)

    def removeForm(self):
        form_pattern_single = re.compile("<form.*?>",re.S)
        form_pattern = re.compile("<form.*?</form>",re.S)
        self.html = re.sub(form_pattern, '', self.html)
        self.html = re.sub(form_pattern_single, '', self.html)

    def remove_A_JavaScript(self):
        javascript_pattern_single = re.compile("<a href=\"javascript.*?>",re.S)
        javascript_pattern = re.compile("<a +href=\"javascript.*?</a>",re.S)
        self.html = re.sub(javascript_pattern, '', self.html)
        self.html = re.sub(javascript_pattern_single, '', self.html)

    def remove_Inner_JavaScript(self):
        lables = ("onmouseover","onclick","border","onload","data-original")
        for each in lables:
            self.html = re.sub(re.compile(each + '=".*?' + '"', re.S), '', self.html)
            self.html = re.sub(re.compile(each + '=\'.*?' + '\'', re.S), '', self.html)

    def removeImg(self):
        img_pattern_single = re.compile("<img.*?>",re.S)
        self.html = re.sub(img_pattern_single,'',self.html)

    def removeLastEdit(self):
        self.html = re.sub(re.compile('最后[回复|编辑|由].*?于.*?(?=<)',re.S),'',self.html)

#将html源码去除标签
def dehtml(text):
    try:
        parser = _DeHTMLParser()
        parser.feed(text)
        parser.close()
        return parser.text()
    except:
        print_exc(file=stderr)
        return text

#处理楼层回调
def floor(matchOBJ):
    return str(matchOBJ.group(0))+"\n"

def enter(matchOBJ):
    return str(matchOBJ.group(0)).replace('\n','')

def getHTML(url):
    my = myTest()
    html = str(my.getHtml(url))
    return html

# 去除了一些不必要的html便签
def getSimpleHTML(html):
    process = processHTML()
    process.setHTML(html)
    process.removeScript()
    process.removeStyle()
    process.removeLink()
    process.removeMeta()
    process.removeSelect()
    # process.removeForm()
    process.remove_A_JavaScript()
    process.remove_Inner_JavaScript()
    process.removeImg()
    process.removeLastEdit()
    process.addCharSet("utf-8")
    # print(process.html)  # 去除了一些不必要的html便签(简化完毕)
    return process.html

#去除了所有html标记(word化)
def getTextHTML(simple_html):
    # print(bs4.BeautifulSoup(html,"lxml").get_text())
    return dehtml(simple_html)

# 获取标题
def getTitle(html):
    Title = ""
    pattern = re.compile("<h1.*?</h1>",re.S)
    pattern_2 = re.compile("<h2.*?</h2>", re.S)
    pattern_3 = re.compile("<h3.*?</h3>",re.S)
    pattern_4 = re.compile("<h4.*?</h4>",re.S)
    patterns = [pattern,pattern_2,pattern_3,pattern_4]
    find = False
    for pt in patterns:
        List = re.findall(pt, str(html))
        if List:
            for eachItem in List:
                item = etree.HTML(eachItem)
                if item.text:
                    if len(item.text) > 6:
                        #print(item.text)
                        Title = item.text
                        find = True
                        break
                else:
                    if len(dehtml(eachItem))>6:
                        Title = dehtml(eachItem)
                        #print(dehtml(eachItem))
                        find = True
                        break
            if find:
                break
                #
                # for eachItem in List:
                #     eee = etree.HTML(eachItem)
                #     print(eee.text)
                #     for each in eee.xpath('//span'):
                #         print(each.text)
                #
                #     for each in eee.xpath('//a'):
                #         print(each.text)
                #
                #     for each in eee.xpath('//b'):
                #         print(each.text)
                # print(List)
    if Title!="":
        return Title
    else:
        try:
            title_pattern = re.compile('(?<=<title>).*?(?=</title>)',re.S)
            title = re.findall(title_pattern,html)
            Title = re.findall(re.compile('.*(?=[-|_])',re.S),title[0])[0]
            return Title
        except IndexError:
            return ""

def prepareTime(simple_or_text,pattern):
    global TIME_LIST,TIME_COUNT
    List = re.findall(pattern, simple_or_text)
    List.reverse()
    TIME_LIST = list(set(List))
    TIME_LIST.sort(key=List.index)
    TIME_LIST.reverse()
    TIME_COUNT = len(TIME_LIST)

def getTime(index,simple_or_text,pattern):
    if pattern is None:
        return ""
    if index<=0 or index>TIME_COUNT:
        return ""
    time_pattern = re.compile('[12][0-9][0-9][0-9]-\d+-\d+ \d+:[0-5]\d:[0-5]\d',re.S)
    # List = re.findall(pattern,simple_or_text)
    # time_list = list(set(List))
    # time_list.sort(key=List.index)
    try:
        if TIME_LIST:
            return TIME_LIST[index-1]
        else:
            return ""
    except IndexError as error:
        return ""

def checkTimeType(simple_html):
    patterns = list()
    patterns.append(re.compile('[12][0-9][0-9][0-9]/\d+/\d+ \d+:[0-5]\d:[0-5]\d',re.S)) #yyyy/MM/dd hh:mm:ss
    patterns.append(re.compile('[12][0-9][0-9][0-9]/\d+/\d+ \d+:[0-5]\d(?!:)',re.S)) #yyyy/MM/dd hh:mm
    patterns.append(re.compile('[12][0-9][0-9][0-9]-\d+-\d+ \d+:[0-5]\d(?!:)',re.S)) #yyyy-MM-dd hh:mm
    patterns.append(re.compile('[12][0-9][0-9][0-9]-\d+-\d+ \d+:[0-5]\d:[0-5]\d(?!\.)')) #yyyy-MM-dd hh:mm:ss
    patterns.append(re.compile('[12][0-9][0-9][0-9]年\d+月\d+日 \d+:[0-5]\d(?!:)'))#yyyy年MM月dd日 hh:mm
    patterns.append(re.compile('\d+-\d+ \d+:[0-5]\d(?!:)',re.S))#MM-dd hh:mm

    aim_pattern = patterns[0]
    max_count = 0
    for each in patterns:
        count = len(re.findall(each,simple_html))
        if count > max_count:
            max_count = count
            aim_pattern = each
    if max_count!=0:
        return aim_pattern
    else:
        return None

def checkTag(a,dom):
    user = "user"
    name = "name"
    auth = "auth"
    author = "author"

    aim_word = "楼主"
    not_word = "看楼主"

    hot_word = ("注册","登录","请登录","免费注册")
    try:
        if ((user in dom['class'][0].lower()) or (name in dom['class'][0].lower()) or (auth in dom['class'][0].lower()) or (
                    author in dom['class'][0].lower()) or ((aim_word in dom.get_text())and(not_word not in dom.get_text()))):
            find = True
            if not a.get_text() in hot_word:
                # print(a.get_text())
                return True
    except Exception as error:
        i = 1
        return False
    return False

#如果获取作者传入1，0。。。如果获取评论者传入从1开始的index
def getAuthor(simple_html,time_pattern,first_index,last_index):
    author = ""
    first_time = getTime(first_index,simple_html,time_pattern)
    second_time = getTime(last_index,simple_html,time_pattern)

    #开头1,0作者
    if second_time=="" and first_index>last_index:
        first_time_index = simple_html.find(first_time)
        main_simple_html = simple_html[3000:first_time_index]
    #结尾评论者
    elif second_time=="" and first_index<last_index:
        first_time_index = simple_html.find(first_time)
        main_simple_html = simple_html[first_time_index*-1:]
    #中间评论者
    else:
        first_time_index = simple_html.rfind(first_time)
        second_time_index = simple_html.rfind(second_time)
        main_simple_html = simple_html[first_time_index:second_time_index]
        # doc_html = etree.HTML(main_simple_html)
        # a_list = doc_html

    find = False
    soup_html = BeautifulSoup(main_simple_html,"html.parser")
    a_list = soup_html.find_all('a')
    for each_a in a_list:
        try:
            href = each_a['href']
            result1 = re.match(re.compile('\bu=',re.S),href)
            result2 = re.match(re.compile('\buid=',re.S),href)
            result3 = re.match(re.compile('\buid-',re.S),href)
            # if "u=" in each_a['href'] or "uid=" in each_a['href'] or "uid-" in each_a['href']:
            if result1 or result2 or result3:
                author = each_a.get_text()
                break
        except Exception:
            i = 1

        if (checkTag(each_a,each_a))or(checkTag(each_a,each_a.parent))or(checkTag(each_a,each_a.parent.parent)):
            if not each_a.get_text() in author:
                author = each_a.get_text()
                break

    author = author.replace('\r\n','').replace('\n','').replace('\t','').replace('楼主','')
    author = re.sub(re.compile(' +',re.S),' ',author)
    return author


def getEachContent(simple_or_word,time_pattern,first_index,last_index):
    first_time = getTime(first_index, simple_or_word, time_pattern)
    last_time = getTime(last_index, simple_or_word, time_pattern)

    first_str_index = simple_or_word.rfind(first_time)
    last_str_index = simple_or_word.rfind(last_time)

    if last_time!="":
        return simple_or_word[first_str_index:last_str_index]
    else:
        temp = simple_or_word[(len(simple_or_word)-first_str_index)*-1:]
        return temp
        # if temp.find('<!--'):
        #     return temp[:temp.find('<!--')]
        # else:
        #     return temp

#如果获取评论,传入从1开始的index，获取content则传入0开始的index（到1）
def getContent(simple_html,text_html,time_pattern,start_index,end_index):
    content = ""
    for i in range(start_index,end_index):
        smash_text = getEachContent(simple_html,time_pattern,i+1,i+2)
        smash_soup_html = BeautifulSoup(smash_text, "lxml")

        if "postmessage" in smash_text:
            content =  smash_soup_html.find_all(id=re.compile('postmessage'))[0].get_text()
        elif len(smash_soup_html.find_all(class_=re.compile('post_msg'))) > 0:
            content = smash_soup_html.find_all(class_=re.compile('post_msg'))[0].get_text()
        elif len(smash_soup_html.find_all(class_=re.compile('message'))) > 0:
            content = smash_soup_html.find_all(class_=re.compile('message'))[0].get_text()
        elif len(smash_soup_html.find_all(class_=re.compile('comment')))>0:
            content = smash_soup_html.find_all(class_=re.compile('comment'))[0].get_text()
        elif len(smash_soup_html.find_all(class_=re.compile('content')))>0:
            content = smash_soup_html.find_all(class_=re.compile('content'))[0].get_text()
        elif len(smash_soup_html.find_all(id=re.compile('content')))>0:
            content = smash_soup_html.find_all(id=re.compile('content'))[0].get_text()
        else:
            try:
                #TODO：遍历所有的simple标签，短于5个字的不予收录，得出最可能的回复
                List = smash_soup_html.find_all(text=re.compile('\w{5,}',re.S))
                # smash_text = getEachContent(text_html,time_pattern,i+1,i+2)#如果没有postmessage字段，解析text
                # text_pattern = re.compile('(?<=，).*。',re.S)
                # text_append = smash_text[0:smash_text.find('，')]
                # append = text_append[text_append.rfind('\n'):len(text_append)]
                # print(append+re.findall(text_pattern,smash_text)[0])
                # return append+re.findall(text_pattern,smash_text)[0]
                return ''.join(List)
            except IndexError:
                return re.sub(re.compile('\n+',re.S),'',smash_text)

    content = content.replace('\r\n','').replace('\n','').replace('\t','')
    content = re.sub(re.compile(' +',re.S),' ',content)
    content = re.sub(re.compile('[发|来]自.*',re.S),'',content)
    return content

def pureTime(time):
    try:
        # ymd_pattern = re.compile('([12][0-9][0-9][0-9][/年-])??\d+[/月-]\d+', re.S)
        # ymd = re.findall(ymd_pattern, time)[0]
        year = re.findall(re.compile('\d{4}(?=[/年-])',re.S),time)[0]
        month = re.findall(re.compile('(?<=[/年-])\d+(?=[/年-])',re.S),time)[0]
        day = re.findall(re.compile('(?<=[/年-])\d+(?= )',re.S),time)[0]
        ymd = year+"-"+month+"-"+day
        return ymd
    except Exception:
        return time

def outPut(index,url,title,time,author,content,replys_list):
    file = {"url":{},"post":{},"replys":[]}
    file["url"] = url.replace('\r\n','')
    file["post"]["author"] = author.replace('\r\n','').replace('楼主','').replace('\n','').replace('只看该作者','')
    file["post"]["content"] = content.replace('\r\n','').replace('\n','')
    file["post"]["title"] = title
    file["post"]["publish_date"] = time

    for eachReply in replys_list:
        file["replys"].append(eachReply)

    with open("result/"+str(index)+".json","w",encoding='utf-8') as json_file:
        json_file.write(str(json.dumps(file,ensure_ascii=False,indent=2)))

#main主函数
if __name__=="__main__":
    file = open('urls.txt', 'rb')
    lines = file.readlines()
    i = 1
    for eachUrl in lines:
        try:
            # url = eachUrl.decode('utf-8')
            url = 'https://tieba.baidu.com/p/5080686502?qq-pf-to=pcqq.discussion'

            print("读取url:" + url.replace('\r\n', '').replace('\n', ''))

            print("尝试下载源代码")
            sourceHTML = getHTML(url)  # 源码

            print("简化代码")
            simpleHTML = getSimpleHTML(sourceHTML)  # 精简源码
            textHTML = getTextHTML(simpleHTML)  # word化的界面

            print("获取时间格式")
            this_main_pattern = checkTimeType(simpleHTML)

            print("准备时间列表")
            prepareTime(simpleHTML,this_main_pattern)

            print("获取主要信息")
            Title = getTitle(simpleHTML)
            Time = pureTime(getTime(1, simpleHTML, this_main_pattern))
            Author = getAuthor(simpleHTML,this_main_pattern,1,0)
            Content = getContent(simpleHTML,textHTML,this_main_pattern,0,1)
            # print(Title + "\n" + Time + "\n" + Author + "\n" + Content)

            # Title=Time=Content=Author=""

            print("获取回复")
            replys_list = list()
            for index in range(1,TIME_COUNT):
                Reply_Time = pureTime(getTime(index+1, simpleHTML, this_main_pattern))
                Reply_Author = getAuthor(simpleHTML, this_main_pattern, index, index+1)
                Reply_Content = getContent(simpleHTML, textHTML, this_main_pattern, index,index+1)
                reply = {}
                reply["content"] = Reply_Content
                reply["author"] = Reply_Author
                reply["publish_date"] = Reply_Time
                replys_list.append(reply)
                # print(Time + "\n" + Author + "\n" + Content)
                #
                # print(Author)
                # print("-------------------------------------------------------------")

            print("写入文件")
            outPut(i,url,Title,Time,Author,Content,replys_list)

            print("处理完毕\n-----------------------------------------------\n")
            i = i+1
        except Exception as e:
            print(str(i)+" :"+eachUrl.decode('utf-8'))
            i = i+1
            print(e)
            print("处理完毕\n-----------------------------------------------\n")

