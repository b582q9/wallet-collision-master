import threading
import os
import time
import random
import requests
import json
from bit import Key
from bit.format import bytes_to_wif
import traceback

# maxPage = int(pow(2, 256) / 128)
maxPage = 904625697166532776746648320380374280100293470930272690489102837043110636675
middle = int(maxPage / 2)


def getRandPage():
    return random.randint(1, maxPage)


def getPage(pageNum):
    keyList = []
    addrList = []
    addrStr1 = ""
    addrStr2 = ""
    num = (pageNum - 1) * 128 + 1
    try:
        for i in range(num, num + 128):
            key1 = Key.from_int(i)
            wif = bytes_to_wif(key1.to_bytes(), compressed=False)
            key2 = Key(wif)
            keyList.append(wif)
            addrList.append(key2.address)
            addrList.append(key1.address)
            if len(addrStr1): addrStr1 = addrStr1 + "|"
            addrStr1 = addrStr1 + key2.address
            if len(addrStr2): addrStr2 = addrStr2 + "|"
            addrStr2 = addrStr2 + key1.address
    except:
        pass
    return [keyList, addrList, addrStr1, addrStr2]


'''
def getPage(pageNum):
    try:
        r = requests.get(url='https://keys.lol/bitcoin/%d' % pageNum, headers={'User-agent': 'Mozilla/5.0'}, timeout=5)
        # r = requests.get(url='https://keys.lol/bitcoin/1',headers={'User-agent': 'Mozilla/5.0'}, timeout=5)
        # r = requests.get(url='https://www.opennet.ru/', timeout=5)
        print('https://keys.lol/bitcoin/%d' % pageNum)
        print('requests=', r)
        r = r.content
        print("r=", r)
    except:
        return []
    keys = r.split("how-this-works!/")
    addrs = r.split("blockchain.com/btc/address/")
    keyList = []
    addrList = []
    addrStr1 = ""
    addrStr2 = ""
    for i in range(1, len(keys)):
        key = keys[i].split("\"")[0]
        keyList.append(key)
    for i in range(1, len(addrs)):
        addr = addrs[i].split("\"")[0]
        addrList.append(addr)
        if i % 2 == 1:
            if len(addrStr1): addrStr1 = addrStr1 + "|"
            addrStr1 = addrStr1 + addr
        else:
            if len(addrStr2): addrStr2 = addrStr2 + "|"
            addrStr2 = addrStr2 + addr
    return [keyList, addrList, addrStr1, addrStr2]
'''


def getBalances(addrStr):
    balances = "security"
    while True:
        if "security" not in balances: break
        secAddr = balances.split("effects address ")
        if len(secAddr) >= 2:
            secAddr = secAddr[1].split(".")[0]
            addrStr = addrStr.replace(secAddr + "|", "")
            addrStr = addrStr.replace("|" + secAddr, "")
        try:
            r = requests.get(url='http://blockchain.info/multiaddr?active=%s' % addrStr, timeout=5)
            # print ("requests=", r.text)
            balances = r.text
        except:
            return
    try:
        balances = json.loads(balances)
        balances = balances['addresses']
    except:
        print(balances)
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


def getWallet():
    global getCount
    global page
    while page <= middle:
        # page = getRandPage()
        print("page=", page)
        pageRet = getPage(page)

        try:
            balancesRet = getBalances(pageRet[2])
            for balance in balancesRet:
                getCount = getCount + 1
                if balance['final_balance'] <= 0 and balance['total_sent'] <= 0: continue
                key = ""
                isCompress = 0
                for i in range(0, len(pageRet[1])):
                    if balance['address'] == pageRet[1][i]:
                        key = pageRet[0][int(i / 2)]
                        if i % 2 == 1: isCompress = 1
                        break
                if key == "": continue
                fp_found.write(str(isCompress) + " " + str(balance['final_balance']) + " " + str(
                    balance['total_sent']) + " " + key + " " + balance['address'] + "\n")
                if balance['final_balance'] > 0:
                    fp_fund.write(str(isCompress) + " " + str(balance['final_balance']) + " " + str(
                        balance['total_sent']) + " " + key + " " + balance['address'] + "\n")
                print(isCompress, balance['final_balance'], balance['total_sent'], key, balance['address'])

            balancesRet = getBalances(pageRet[3])
            for balance in balancesRet:
                getCount = getCount + 1
                if balance['final_balance'] <= 0 and balance['total_sent'] <= 0: continue
                key = ""
                isCompress = 1
                for i in range(0, len(pageRet[1])):
                    if balance['address'] == pageRet[1][i]:
                        key = pageRet[0][int(i / 2)]
                        if i % 2 == 1: isCompress = 1
                        break
                if key == "": continue
                fp_found.write(str(isCompress) + " " + str(balance['final_balance']) + " " + str(
                    balance['total_sent']) + " " + key + " " + balance['address'] + "\n")
                if balance['final_balance'] > 0:
                    fp_fund.write(str(isCompress) + " " + str(balance['final_balance']) + " " + str(
                        balance['total_sent']) + " " + key + " " + balance['address'] + "\n")
                print(isCompress, balance['final_balance'], balance['total_sent'], key, balance['address'])
            fp_found.flush()
            fp_fund.flush()
        except:
            traceback.print_exc()
            continue
        page = page + 1
        start_page_file.seek(0)
        start_page_file.write(str(page) + "\n")
        start_page_file.flush()
        start_page_file.truncate()
        clearScreen()
        print(getCount)
        time.sleep(10)


def clearScreen():
    os.system('clear')


def main():
    threads = []
    for i in range(1):
        threads.append(threading.Thread(target=getWallet, args=()))
    for t in threads:
        time.sleep(1.0)
        t.start()
    for t in threads:
        t.join()


if __name__ == '__main__':
    main()
