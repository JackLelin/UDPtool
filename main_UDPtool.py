from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot                            

from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from ui import *
import socket, socketserver, threading

class ThreadingUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        current_thread = threading.current_thread()
        # print("{}: client: {}, wrote: {}".format(current_thread.name, self.client_address, data))
        self.server.bridge.udpReceived.emit(data.hex(' '))

class ThreadingUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

class ServerQtBridge(QObject):
    udpReceived = pyqtSignal(str)


class Win_Main(QMainWindow):
    def __init__(self):
        super().__init__()

# ui 的设置
        # self.ui = uic.loadUi('main.ui', self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

# 配置部分 action
        self.ui.pushButtonAddFormat.clicked.connect(self.bottonActionConvertingString)
        self.ui.pushButtonSend.clicked.connect(self.bottonActionSendMsg)
        self.ui.pushButtonConnectServ.clicked.connect(self.bottonActionConnectServ)
        self.ui.pushButtonDisconnectServ.clicked.connect(self.bottonActionCloseServ)
        self.ui.listWidgetHistory.itemDoubleClicked.connect(self.listDoubleClicked)
        self.ui.pushButtonClearTX.clicked.connect(self.bottonActionClearTXBox)
        self.ui.pushButtonClearRX.clicked.connect(self.bottonActionClearRXBox)
        self.ui.pushButtonHex2String.clicked.connect(self.bottonActionHex2String)
        self.ui.pushButtonString2Hex.clicked.connect(self.bottonActionString2SHex)

# private variables
        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recServer = None

    def FormatMessage(self, Message: bytes):
        Head = b'\xeb\x90\xeb\x90'
        Len = (2 + len(Message)).to_bytes(2,'big')
        Checksum = sum(Len+Message).to_bytes(2,'big')
        return(Head + Len + Message + Checksum)

    def String2Bytes(self, hex_string):
        try:
            hex_bytes = bytes.fromhex(hex_string)
        except:
            msg = QMessageBox()
            msg.setWindowTitle('输入的内容无法转换')
            msg.setText('请输入16进制数不要加逗号不要加\\和x，如\"0f 1a de ad\"')
            msg.exec()
            return None
        else:
            return hex_bytes

# define action
    def bottonActionConvertingString(self):
        message= self.ui.plainTextRawMsg.toPlainText()
        # print(message)
        message = self.String2Bytes(message)
        if message == None:
            return
        message = self.FormatMessage(message)
        # print(message)
        self.ui.plainTextFormMsg.setPlainText(message.hex(' '))

    def bottonActionSendMsg(self):
        message = self.ui.plainTextTX.toPlainText()
        if message == '' or message ==  ' ':
            return
        message = self.String2Bytes(message)
        if message == None:
            return 
        UDP_IP_ADDRESS = self.ui.lineEditIPAddrRemote.text()
        UDP_PORT_NO = self.ui.lineEditPortRemote.text()
        # print(UDP_IP_ADDRESS,UDP_PORT_NO)
        self.ui.listWidgetHistory.insertItem(0, message.hex(' '))
        try:
            self.clientSock.sendto(message , (UDP_IP_ADDRESS, int(UDP_PORT_NO)))
        except:
            msg = QMessageBox()
            msg.setWindowTitle('发送失败')
            msg.setText('发送失败，检查IP和端口')
            msg.exec()

    def bottonActionConnectServ(self):
        UDP_HOST_IP = self.ui.lineEditIPAddrLocal.text()
        try:
            UDP_HOST_PORT = int(self.ui.lineEditPortLocal.text())
            self.UDP_HOST_PORT = UDP_HOST_PORT
        except:
            msg = QMessageBox()
            msg.setWindowTitle('检查端口号转换失败')
            msg.setText('检查端口号是否输入正确')
            msg.exec()
            return
        print(UDP_HOST_IP,UDP_HOST_PORT)
        try:
            self.recServer = ThreadingUDPServer((UDP_HOST_IP, UDP_HOST_PORT), ThreadingUDPHandler)
        except:
            msg = QMessageBox()
            msg.setWindowTitle('接收服务器失败')
            msg.setText('端口可能已经被占用, IP可能错误')
            msg.exec()
            return
        else:
            server_thread = threading.Thread(target=self.recServer.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            self.recServer.bridge = ServerQtBridge()
            self.recServer.bridge.udpReceived.connect(self.updateRXTextBox)
            
            self.ui.pushButtonConnectServ.setEnabled(False)
            print("Server started at {} port {}".format(UDP_HOST_IP, UDP_HOST_PORT))
    def bottonActionCloseServ(self):        
        try:
            self.recServer.shutdown()
            self.recServer.server_close()
        except:
            msg = QMessageBox()
            msg.setWindowTitle('断开监听失败')
            msg.setText('断开对端口%d的监听失败'%self.UDP_HOST_PORT)
            msg.exec()
        else:
            self.ui.pushButtonConnectServ.setEnabled(True)
            msg = QMessageBox()
            msg.setWindowTitle('断开监听成功')
            msg.setText('成功断开对端口%d的监听'%self.UDP_HOST_PORT)
            msg.exec()

    def listDoubleClicked(self, item):
        self.ui.plainTextTX.setPlainText(item.text())

    @pyqtSlot(str)
    def updateRXTextBox(self, message):
        oldmessage = self.ui.plainTextRX.toPlainText()
        newmessage = oldmessage + '\n' + message if oldmessage != '' else message
        self.ui.plainTextRX.setPlainText(newmessage)

    def bottonActionClearRXBox(self):
        self.ui.plainTextRX.setPlainText('')

    def bottonActionClearTXBox(self):
        self.ui.plainTextTX.setPlainText('')

    def bottonActionHex2String(self):
        message = self.ui.plainTextHex.toPlainText()
        message = self.String2Bytes(message)
        if message == None:
            return 
        try:
            message = message.decode("ascii")
        except:
            msg = QMessageBox()
            msg.setWindowTitle('转换失败')
            msg.setText('转化为ascii字符串失败，注意不要有超过7F的字节')
            msg.exec()
        else:
            self.ui.plainTextString.setPlainText(message)

    def bottonActionString2SHex(self):
        message = self.ui.plainTextString.toPlainText()
        try:
            message = message.encode('ascii')
        except:
            msg = QMessageBox()
            msg.setWindowTitle('转换失败')
            msg.setText('转化失败，只能转换ascii字符串')
            msg.exec()          
        else:
            self.ui.plainTextHex.setPlainText(message.hex(' ')) 

app = QApplication([])
wm = Win_Main()
wm.show()
app.exec_()


