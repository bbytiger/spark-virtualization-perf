import os

def get_data():
   testfile = "airbnb.csv"
   datadir = "/data/"
   currdir = os.path.dirname(os.path.abspath(__file__)) 
   f = open(currdir + datadir + testfile, "r")
   data = f.read()
   return data

if __name__ == "__main__":
    get_data()
