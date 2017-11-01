# -*- coding: utf-8 -*-
import os.path
import time
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import torndb
import json
import api.ip2city.ipip

from tornado.options import define, options

define("port", default=10086, help="run on the given port", type=int)


def _load_ip_to_city():
    api.ip2city.ipip.IP.load("api/data/17monipdb20170909.dat")

    return api.ip2city.ipip.IP


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('111')
        # db = torndb.Connection('127.0.0.1:3306', 'zygg', 'root', 'root')
        # # 列表广告：
        # self.user_agent = self.request.headers.get('user-agent', '')
        # if 'Android' in self.user_agent:
        #     self.pt = '安卓'
        # if 'iPhone' in self.user_agent:
        #     self.pt = '苹果'
        # remote_ip = self.request.remote_ip
        # ip = 'http: // ip.taobao.com / service / getIpInfo.php?ip =%d'
        # self.time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        # self.site = db.query('select * from zyads_sitetype ')
        # # 平台
        # self.planid[0] = db.query('select planid from zyads_acls WHERE type=%s and data!=%s ', 'pt', self.pt)
        # # 日期
        # self.planid[1] = db.query('select planid from zyads_plan WHERE expire<%s', self.time)
        # # 地区
        # self.planid[2] = db.query('select planid,data from zyads_acls WHERE type='
        # city
        # ')
        #
        # self.listads = db.query(
        #     'select * from  zyads_acls inner join zyads_plan on zyads_ads.planid=zyads_plan.id where')
class InterfaceHandler(tornado.web.RequestHandler):
    def get(self):
        listads = []
        listads[0]=[]
        listads[1] = []
        listads[2] = []
        listads[3] = []
        listads[4] = []
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
            'select	zyads_plan.top,zyads_plan.expire,zyads_ads.planid,adinfo,imageurl,imageurl1,url,headline,description FROM zyads_ads inner join zyads_plan on zyads_ads.planid=zyads_plan.planid where zyads_ads.status=3 and zyads_plan.status=1 AND zyads_ads.adstypeid=13  order by zyads_plan.priceadv desc')

        for val in ads:
            if str(val['expire']) < self.time:
                continue
            if {'planid':val['planid']} in self.planid:
                continue
            val['expire'] = ''
            if val['top'] == '110':
                listads[1].append(val)
            if val['top'] == '111':
                listads[2].append(val)
            if val['top'] == '112':
                listads[3].append(val)
            if val['top'] == '113':
                listads[4].append(val)
            listads[0].append(val)
        # self.render("poem.html", html=listads)
        listads = json.dumps(listads)
        self.write(listads)


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[(r'/', IndexHandler),(r'/ads', InterfaceHandler)],
        template_path=os.path.join(os.path.dirname(__file__), "views"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
