#!/usr/bin/env python
import subprocess
import sys
import text_predict
from libshorttext.analyzer import *

def call(cmd):
  subprocess.call(cmd, shell=True)

def fold(num):
  call("rm test* train*")
  for i in range(1, len(sys.argv)):
    cmd = "python converter.py " + sys.argv[i] + " " + str(num)
    print cmd
    call(cmd)

def main():
  outfile = open('final', 'w', 1)
  acc = []
  cmd = "./libshorttext/text-train.py train -f -P 3 -F 0 -N 1 -L 2"
  #cmd = './text-train.py train -f'
  #cmd = "./text-train.py train -f -P 3 -F 0 -N 1 -L 2 -A train_feats"
  #cmd = "./text-train.py train -f -A train_feats"
  outfile.write(cmd+'\n')
  confusion_table = None
  for m in range(10):
    fold(m)
    call(cmd)
    #acc.append(text_predict.main([0, "testfile", "train.model", "out1", "-f", "-A", "test_feats"]))
    acc.append(text_predict.main([0, "testfile", "train.model", "out1", "-f"]))
    outfile.write('fold ' + str(m) + ' acc ' + str(acc[m])+'\n')
    
    analyzer = Analyzer('train.model')
    insts = InstanceSet('out1')
    confusion_table = analyzer.get_confusion_table(insts, confusion_table)
  outfile.write('average: ' + str(float(sum(acc) / len(acc))) + '\n')
  analyzer.draw_confusion_table(insts, confusion_table, outfile)
  
def crossall():
  outfile = open('results', 'w', 1)
  cmd = "./text-train.py train -f -P "
  for i in range(8):
    cmd2 = cmd + str(i) + " -F "
    for j in range(4):
      cmd3 = cmd2 + str(j) + " -N "
      for k in range(2):
        cmd4 = cmd3 + str(k) + " -L "
        for l in range(4):
          name = "train"
          outfile.write(str(i) + str(j) + str(k) + str(l)+'\n')
          cmd5 = cmd4 + str(l) + " " + name + ".model"
          outfile.write(cmd5+'\n')
          acc = []
          for m in range(3):
            fold(m)
            call(cmd5)
            print cmd5
            acc.append(text_predict.main([0, "testfile", name + ".model", "out", "-f", "-a", "0"]))
          outfile.write(str(float(sum(acc)/len(acc)))+'\n')
          outfile.flush()
  outfile.close()

if __name__ == '__main__':
  main()
