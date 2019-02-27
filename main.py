# coding=utf-8
from gevent import monkey
monkey.patch_all()
import const as ct
from log import getLogger
from ctrader import CTrader
from cthread import CThread
from data_manager import DataManager
log = getLogger(__name__)
def main():
    threadList = []
    dm = DataManager(ct.DB_INFO)
    log.info("init succeed")
    threadList.append(CThread(dm.run, 1))
    threadList.append(CThread(dm.update, 1800))
    threadList.append(CThread(dm.scrawler, 3600))

    ctrader = CTrader(ct.DB_INFO)
    threadList.append(CThread(ctrader.buy_new_stock, 3600))

    for thread in threadList:
        thread.start()

    for thread in threadList:
        thread.join()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.error(e)
