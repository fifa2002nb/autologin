# -*- coding:utf-8 -*-
import sys
import os
import logging
import time
import json
import urllib
import urllib2
from com.dtmilano.android.viewclient import ViewClient
from com.dtmilano.android.adb import adbclient

logging.basicConfig(
    level       = logging.INFO,
    format      = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt     = '[%Y-%m-%d %H:%M:%S]',
)
#adb -s 042c0bf122390a96  shell /system/bin/screencap -p /sdcard/screenshot.png && rm -rf screenshot.png && adb -s 042c0bf122390a96  pull /sdcard/screenshot.png ./ && adb -s 042c0bf122390a96  shell rm /sdcard/screenshot.png
class TaobaoLoginHandler:
    def __init__(self, deviceSNs, qrcodeUrl, qrcodeLocalFile, qrcodeRemoteFile):
        self.Headers = {
            'Content-Type'      :   'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie'            :   None,
            'User-Agent'        :   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        }
        self.deviceSNs = (None and deviceSNs) or deviceSNs
        self.qrcodeUrl =  (None and qrcodeUrl) or qrcodeUrl
        self.qrcodeLocalFile = (None and qrcodeLocalFile) or qrcodeLocalFile
        self.qrcodeRemoteFile = (None and qrcodeRemoteFile) or qrcodeRemoteFile

    def _request(self, url, data, method = 'POST'):
        if data:
            data = urllib.urlencode(data)
        if 'GET' == method:
            if data:
                url = '{}?{}'.format(url, data)
            data = None
        req = urllib2.Request(url, data, self.Headers)
        return urllib2.urlopen(req, timeout = 5)

    def get(self, url, data = None):
        return self._request(url, data, method = 'GET')

    def wget(self, url, data = None, outFile = "~/Desktop/qrcode.png"):
        try:
            res = self.get(url, data)
            data = res.read() 
            try:
                jsonData = json.loads(data)
                if jsonData :
                    if 0 != jsonData['code']:
                        logging.error(jsonData)
                    return False
            except Exception, e:
                pass

            with open(outFile, "wb") as code:     
                code.write(data)
        except Exception, e:
            logging.error(e)
            return False
        return True

    def taobaoAppLogin(self, deviceSN):
        # 0、qrcode图片push到手机上
        os.system('adb -s %s push %s %s' %(deviceSN, self.qrcodeLocalFile, self.qrcodeRemoteFile))
        logging.info("[%s] 0、pushed qrcode to %s." %(deviceSN, self.qrcodeRemoteFile))

        try:
            # 1、初始化设备，启动taobao app
            device, serialno = ViewClient.connectToDeviceOrExit(serialno = deviceSN)
            if False == device.isScreenOn():
                device.wake()
            if True == device.isLocked():
                device.unlock()
            device.startActivity(component = "com.taobao.taobao/com.taobao.tao.welcome.Welcome")
            logging.info("[%s] 1、lanuched [taobao] activity." %deviceSN)
            time.sleep(4)
            device.press('KEYCODE_BACK')
            vc = ViewClient(device, serialno)
            vc.click(x = 106, y = 1692)
            logging.info("[%s] click [taobao] shouye." %deviceSN)
            time.sleep(2)
            # 判断是否有抢红包图层，有则点击关闭
            #vc = ViewClient(device, serialno)
            #views = vc.getViewsById()
            #for k in views:
            #    if "android.view.View" == views[k]['class']:
            #        logging.info("[%s] 1、click hongbao's \"close\" button." %deviceSN)
            #        vc.click(x = 540, y = 1630)
            #        break

            # 2、点扫一扫
            vc = ViewClient(device, serialno)
            scanView = vc.findViewById(viewId = "com.taobao.taobao:id/tv_scan_text")
            if None != scanView:
                scanView.touch()
            else:
                logging.error("[%s] None == scanView" %deviceSN)
            logging.info("[%s] 2、entered scanQrcode window." %deviceSN)

            # 3、打开相册
            vc = ViewClient(device, serialno)
            albumBtn = vc.findViewById(viewId = "com.taobao.taobao:id/btn_album")
            if None != albumBtn:
                albumBtn.touch()
            else:
                logging.info("[%s] None == albumBtn" %deviceSN)
            logging.info("[%s] 3、entered album window." %deviceSN)

            # 4、进入相册文件夹
            vc = ViewClient(device, serialno)
            photosDir = vc.findViewWithText(text = "WeiXin")
            if None != photosDir:
                photosDir.touch()
            else:
                logging.info("[%s] None == photosDir" %deviceSN)
            logging.info("[%s] 4、entered photos dir." %deviceSN)

            # 5、点击图片
            vc = ViewClient(device, serialno)
            #photo = vc.findViewById(viewId = "com.google.android.apps.photos:id/list_photo_tile_view")
            photo = vc.findViewWithContentDescription(contentdescription = u"照片")
            if None != photo:
                photo.touch()
            else:
                logging.info("[%s] None == photo" %deviceSN)
            logging.info("[%s] 5、clicked the first photo." %deviceSN)

            # 6、二维码失效则返回上层
            vc = ViewClient(device, serialno)
            vc.click(x = 540, y = 1390)
            vc.sleep(2)
            #views = vc.getViewsById()
            #for k in views:
            #    logging.info(views[k])
            vc.click(x = 314, y = 1170)
            vc.sleep(2)
            #back2lastwindow = vc.findViewWithContentDescription(contentdescription = u"转到上一层级")
            #if None != back2lastwindow:
            #    back2lastwindow.touch()
            #else:
            #    logging.info("[%s] None == back2lastwindow" %deviceSN)
            #logging.info("[%s] 6、backed to the last window." %deviceSN)

            # 7、退回到首页
            #vc = ViewClient(device, serialno)
            #backBtn = vc.findViewById(viewId = "com.taobao.taobao:id/kakalib_button_nav_left")
            #if None != backBtn:
            #    backBtn.touch()
            #else:
            #    logging.info("[%s] None == backBtn" %deviceSN)
            logging.info("[%s] 7、backed to main window." %deviceSN)

            device.press('KEYCODE_BACK')
            device.press('KEYCODE_BACK')
            device.press('KEYCODE_BACK')
            device.press('KEYCODE_BACK')
            device.press('KEYCODE_BACK')
            device.press('KEYCODE_BACK')
            os.system('adb -s %s shell am force-stop com.taobao.taobao' %(deviceSN))
            logging.info("[%s] done." %deviceSN)
        except Exception, e:
            logging.error(e)
            logging.info("[%s] done with err." %deviceSN)

    def appLoginLoop(self):
        logging.info("appLoginService started.")
        while True:
            for username in self.deviceSNs:
                time.sleep(5)
                deviceSN = self.deviceSNs.get(username)
                qrcodeUrl = '%s%s' %(self.qrcodeUrl, "fastorz")
                if False == self.wget(url = qrcodeUrl, outFile = self.qrcodeLocalFile):
                    logging.info("[%s:%s] everything is ok." %(deviceSN, username))
                    continue
                else:
                    logging.info("[%s:%s] wget success." %(deviceSN, username))
                self.taobaoAppLogin(deviceSN)

    def test(self, deviceSN):
        try:
            # 1、初始化设备，启动taobao app
            device, serialno = ViewClient.connectToDeviceOrExit(serialno = deviceSN)
            if False == device.isScreenOn():
                device.wake()
            if True == device.isLocked():
                device.unlock()
            device.startActivity(component = "com.taobao.taobao/com.taobao.tao.welcome.Welcome")
            time.sleep(3)
            logging.info("[%s] 1、lanuched [taobao] activity." %deviceSN)

            vc = ViewClient(device, serialno)
            views = vc.getViewsById()
            for k in views:
                #if "true" == views[k]['clickable']: 
                    #logging.info("%s %s %s" %(views[k]['clickable'], views[k]['content-desc'], views[k]['bounds']))
                if "android.view.View" == views[k]['class']:
                    logging.info(views[k])

            logging.info("[%s] done." %deviceSN)
        except Exception, e:
            logging.error(e)
            logging.info("[%s] done with err." %deviceSN)


if __name__ == "__main__":
    deviceSNs = {"fastorz": "0828f2c10c859146"}
    qrcodeUrl = "http://127.0.0.1:8000/qrcode?username="
    #qrcodeUrl = "http://118.89.190.25:8000/qrcode?username="
    localFile = "/Users/miles/Desktop/qrcode.png"
    remoteFile = "/storage/emulated/0/tencent/MicroMsg/WeiXin/mmexport1492919707621.png"
    h = TaobaoLoginHandler(deviceSNs, qrcodeUrl, localFile, remoteFile)
    h.appLoginLoop()
