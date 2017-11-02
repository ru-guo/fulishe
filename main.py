# -*- coding: utf-8 -*-
import os.path
import time
import redis
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import torndb
import logging
import json
import api.ip2city.ipip

from tornado.options import define, options

define("port", default=10086, help="run on the given port", type=int)


def _load_ip_to_city():
    api.ip2city.ipip.IP.load("api/data/17monipdb20170909.dat")

    return api.ip2city.ipip.IP

logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='myapp.log',
                    filemode='w')

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')
class InterfaceHandler(tornado.web.RequestHandler):
    def get(self):
        listads = []
        listads0 = []
        listads1 = []
        listads2 = []
        listads3 = []
        listads4 = []
        # 获取时间
        self.time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        # 连接数据库
        db = torndb.Connection('127.0.0.1:3306', 'zygg', 'root', 'root')
        # 获取用户平台
        self.user_agent = self.request.headers.get('user-agent', '')
        pt = ''
        if 'Android' in self.user_agent:
            pt = '安卓'
        if 'iPhone' in self.user_agent:
            pt = '苹果'
        self.planid = db.query('select planid from zyads_acls WHERE type=%s and data!=%s ', 'pt', pt)

        # IP判断地址
        self.remote_ip = self.request.remote_ip

        self.ip2city = _load_ip_to_city()
        self.city_info = self.ip2city.find(self.remote_ip)

        if self.city_info[0] != '本机地址':

            self.planid.append(db.query("select planid from zyads_acls WHERE type='city' and data NOT LIKE '%%北京%%'"))
        # print(self.planid)

        ads = db.query(
            'select	zyads_plan.top,zyads_ads.adstypeid,zyads_plan.expire,zyads_ads.planid,zyads_ads.uid,zyads_ads.adsid,adinfo,imageurl,imageurl1,url,headline,description FROM zyads_ads inner join zyads_plan on zyads_ads.planid=zyads_plan.planid where zyads_ads.status=3 and zyads_plan.status=1 AND zyads_ads.adstypeid=13  order by zyads_plan.priceadv desc')

        for val in ads:
            # print (val['adsid'])
            if str(val['expire']) < self.time:
                continue
            if {'planid':val['planid']} in self.planid:
                continue
            val['expire'] = ''
            if val['top'] == 110:
                listads1.append(val)
            if val['top'] == 111:
                listads2.append(val)
            if val['top'] == 112:
                listads3.append(val)
            if val['top'] == 113:
                listads4.append(val)
            print (val['adsid'])
            listads0.append(val)
        # self.render("poem.html", html=listads)
        listads = [listads0,listads1,listads2,listads3,listads4]
        # self.render("poem.html", html=listads)
        # listads = json.dumps(listads)
        # self.write(listads)
        self.render("poem.html", html=listads)

class redirectHandler(tornado.web.RequestHandler):
    def get(self):
        self.name = self.get_argument('url')
        # self.remote_ip = self.request.remote_ip
        # self.user_agent = self.request.headers.get('user-agent', '')
        # self.redisname =self.name+self.remote_ip+self.user_agent
        if self.get_cookie(self.name)!='1':
            self.set_cookie(self.name, '1', expires=time.time() + 900)
            self.adsid = self.get_argument('adsid')
            self.adstypeid = self.get_argument('adstypeid')
            self.planid = self.get_argument('planid')
            self.uid = self.get_argument('uid')
            self.write(self.name)
            # self.write(self.adsid)
            db = torndb.Connection('127.0.0.1:3306', 'zygg', 'root', 'root')
            # 获取时间
            self.time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            try:
                aaa = db.query('select clicks from zyads_stats WHERE  day=%s AND adsid=%s',self.time,self.adsid)
                if aaa :
                    db.execute('update zyads_stats set clicks=clicks+1 WHERE  day=%s AND adsid=%s',self.time,self.adsid)
                else:
                    db.execute('insert into zyads_stats (clicks,adsid,day,adstypeid,planid,uid) VALUES (1,%s,%s,%s,%s,%s)',self.adsid,self.time,self.adstypeid,self.planid,self.uid)
            except Exception as e:
                logging.error(e)
        self.redirect(self.name)

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[(r'/', IndexHandler),(r'/ads', InterfaceHandler),(r'/redi', redirectHandler)],
        template_path=os.path.join(os.path.dirname(__file__), "views"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
