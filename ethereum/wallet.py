import threading
import os
import time
import random
import codecs
import requests
import json
from ecdsa import SigningKey, SECP256k1
import sha3
import traceback

# maxPage = pow(2,256) / 128
maxPage = 904625697166532776746648320380374280100293470930272690489102837043110636675


def getRandPage():
    # print ("random.randint(1,",maxPage,")=",random.randint(1, maxPage))
    return random.randint(1, maxPage)


def getPage(pageNum):
    keyList = []
    addrList = []
    addrStr = ""
    num = (pageNum - 1) * 50 + 1
    try:
        for i in range(num, num + 50):
            key = hex(i)[2:]
            if len(key) < 64: key = "0" * (64 - len(key)) + key
            priv = codecs.decode(key, 'hex_codec')
            pub = SigningKey.from_string(priv, curve=SECP256k1).get_verifying_key().to_string()
            addr = "0x" + sha3.keccak_256(pub).hexdigest()[24:]
            print("priv=", priv, "pub=", pub, "addr=", addr)
            keyList.append(key)
            addrList.append(addr)
            if len(addrStr): addrStr = addrStr + ","
            addrStr = addrStr + addr
    except:
        traceback.print_exc()
        pass
    '''
    print('-----------------------------keyList-----------------------------')
    for i in keyList:
        print('i=',i)
    '''
    return [keyList, addrList, addrStr]


def getBalances(addrStr):
    # threadLock.acquire()
    balances = ""
    try:
        # print (addrStr)
        # print ("request=https://etherchain.org/api/account/multiple/%s" % addrStr)
        # r = requests.get(url='https://etherchain.org/api/account/multiple/%s' % addrStr, timeout=5)
        r = requests.get(
            url='https://api.etherscan.io/api?module=account&action=balancemulti&address=%s&tag=latest&apikey=B8E33U1NG6AUBN3SFKBCN5KVGMEUK64NME' % addrStr,
            timeout=5)
        balances = r.text
        print("balances = r.text=", balances)
    except:
        traceback.print_stack()
        return
    try:
        balances = json.loads(balances)
        print('json.loads(balances)=', balances)
        print("balances['status']=", balances['status'])
        if int(balances['status']) != 1: raise Exception("API Busy")
        balances = balances['result']
    except:
        # print ("balances = r.text=",balances,file=sys.stderr)
        # print ("balances['status']=",balances['status'],file=sys.stderr)
        traceback.print_exc()
    #    threadLock.release()
    return balances


getCount = 0
page = 1
fp_found = open("found.txt", "a+")
fp_fund = open("fund.txt", "a+")

try:
    start_page_file = open("start_page.txt", "r+")
    page = int(list(start_page_file)[-1])
except:
    start_page_file = open("start_page.txt", "x+")


# threadLock = threading.Lock()

def getWallet():
    global getCount
    global page
    # balance_int=0
    while True:
        page = getRandPage()
        pageRet = getPage(page)
        getCount = getCount + len(pageRet[1])

        try:
            # threadLock.acquire()
            balancesRet = getBalances(pageRet[2])
            # threadLock.release()
            for balance in balancesRet:
                key = ""
                for i in range(0, len(pageRet[1])):
                    if balance['account'] == pageRet[1][i]:
                        key = pageRet[0][i]
                        break
                if key == "": continue
                # balance_int=int(balance['balance'])/1000000000000000000
                # fp_found.write(f'{balance_int: .15f}' + " " + key + " " + balance['account'] + "\n")
                if int(balance['balance']) > 0:
                    # fp_fund.write(f'{balance_int: .15f}' + " " + key + " " + balance['account'] + "\n")
                    fp_fund.write(balance['balance'] + " " + key + " " + balance['account'] + "\n")
                # print (f'{balance_int: .15f}', key, balance['account'])
                print(balance['balance'], key, balance['account'])
                # https://mkaz.blog/code/python-string-format-cookbook/
            fp_found.flush()
            fp_fund.flush()
        except:
            traceback.print_exc()
            continue
        # page = page + 1
        start_page_file.seek(0)
        start_page_file.write(str(page) + "\n")
        start_page_file.flush()
        start_page_file.truncate()
        clearScreen()
        print(getCount)
        # time.sleep(5)


def clearScreen():
    os.system('clear')


def main():
    threads = []
    for i in range(1):
        threads.append(threading.Thread(target=getWallet, args=()))
    for t in threads:
        time.sleep(1.0)
        t.start()
        # print ("threading.active_count()=",threading.active_count())
    for t in threads:
        t.join()


if __name__ == '__main__':
    main()
