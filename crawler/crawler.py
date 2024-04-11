
import phisherman
import util

process_args = util.process_args
save_csv = util.save_csv
Phisherman = phisherman.Phisherman 

def crawl():
    start, end = process_args()
    phisherman = Phisherman(start, end)
    data = phisherman.crawl()
    save_csv(data, "new.csv")


crawl()