import socket
import threading
import select


default_version = 5

class Proxy:
    def __init__(self):
        self.username = "default"
        self.password = "default"

    def istek_isle(self, con):
        version,mmethod = con.recv(2)
        methots = self.mevcut_metod(mmethod, con)

        if 2 not in set(methots):
            con.close()
            return

        con.sendall(bytes([default_version, 2]))

        if not self.onayla(con):
            print("authentication error")
            return
        version, komut, blabla, adresturu = con.recv(4)
        if adresturu == 1:
            adres = socket.inet_ntoa(con.recv(4))
        elif adresturu == 3:
            dlen = con.recv(1)[0]
            adres = con.recv(dlen)
            adres = socket.gethostbyname(adres)
        port = int.from_bytes(con.recv(2), "big", signed=False)

        try:
            if komut == 1:
                bag = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                bag.connect((adres, port))
                bad = bag.getsockname()
                print(f"Baglanildi: {adres} -> {port}")
            else:
                con.close()

            addr = int.from_bytes(socket.inet_aton(bad[0]), "big", signed=False)
            port = bad[1]
            rep = b"".join([default_version.to_bytes(1,"big"), int(0).to_bytes(1,"big"), int(0).to_bytes(1,"big"), int(1).to_bytes(1,"big"), addr.to_bytes(4,"big"), port.to_bytes(2,"big")])
        except:
            rep = self.reply_error(adresturu, 5)
        con.sendall(rep)
        if rep[1] == 0 and komut == 1:
            self.degisim(con, bag)
        con.close()

    def degisim(self, con, bag):
        while True:
            r,w,e = select.select([con, bag], [], [])
            if con in r:
                veri = con.recv(4096)
                print(f"[ --> ] {veri}")
                if bag.send(veri) <= 0:
                    break

            if bag in r:
                veri = bag.recv(4096)
                print(f"[ <-- ] {veri}")
                if con.send(veri) <= 0:
                    break



    def repy_error(self, adresturu, hatano):
        return b"".join([default_version.to_bytes(1,"big"), hatano.to_bytes(1,"big"), int(0).to_bytes(1,"big"), adresturu.to_bytes(1,"big"), int(0).to_bytes(1,"big"), int(0).to_bytes(1,"big")])




    def onayla(self,con):
        version = con.recv(1)
        ulen = ord(con.recv(1))
        uname = con.recv(ulen).decode("utf-8")
        plen = ord(con.recv(1))
        password = con.recv(plen).decode("utf-8")
        if uname == self.username and password == self.password:
            cevap = bytes([ord(version), 0])
            con.sendall(cevap)
            return True
        cevap = bytes([ord(version), 0xff])
        con.sendall(cevap)
        con.close()
        return False



    def mevcut_metod(self,mmethot,con):
        metodlar = []
        for i in range(mmethot):
            metodlar.append(ord(con.recv(1)))
        return metodlar

    def run(self,host,port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host,port))
        s.listen()
        print(f"Server calisiyor: {host}:{port}")
        while True:
            con,addr = s.accept()
            print(f"[i] New connection from ip:{addr[0]} port: {addr[1]}")
            t = threading.Thread(target=self.istek_isle, args=(con, ))
            t.start()


if __name__ == "__main__":
    proxy = Proxy()
    proxy.run("127.0.0.1",8888)
