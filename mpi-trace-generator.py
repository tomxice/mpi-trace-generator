
# An MPI Trace Generator written in Python3.
# Currently, only blocking point-to-point communication (Send/Recv) are supported.
# To use this generator, you should specify the following information:
# 1. How many MPI processes are there (N).
# 2. Specify a communication patter for each process (i==i) or each process group (i%2==1), including
# 2.1 The time of starting a send, in microseconds, e.g., 43510
# 2.2 The message size, in bytes, e.g., 16384
# 2.3 The duration of communication, in microseconds, e.g., 10000
# 2.4 The destination process ID. It can be a number or a expression of current sender (i), e.g., 23, i+1, (i+1)%N.
# * You may have already noticed that you only need to provide information of senders. 
# * For receivers, their information will be automatically derivated from senders.
# ** NOTICE!!! All fields in step 2 should be given as strings.
# 3. Give a list of processes, and their traces will be logged into files.
#    (Two file for each process, send and receive, respectively)
import random

class trace:
    def __init__(self,tp,src,dest,size,start,end):
        self.tp, self.src, self.dest, self.size, self.start, self.end = tp,src,dest,size,start,end
    def __str__(self):
        return "%s %d %d %d %d %d" % (self.tp, self.src, self.dest, self.size, self.start, self.end)
    
class TRG:
    def __init__(self):
        self.N = 0;
        self.patterns=[]
        self.trace=None
    def set_size(self, N):
        self.N = N
    def add_pattern(self,  pattern):
        self.patterns.append(pattern)
    def build(self):
        self.trace=[[] for _ in range(self.N)]
        for pattern in self.patterns:
            amI, dest, st, dur, msgsz = pattern
            senders=[i for i in range(0, self.N) if eval(amI)]
            for i in senders:
                receiver=eval(dest)
                for t in eval(st):
                    sz=eval(msgsz)
                    dr=eval(dur)
                    #print(i,receiver,sz,t,dr)
                    self.trace[i].append(trace('S',i,receiver,sz,t,t+dr))
                    self.trace[receiver].append(trace('R',i,receiver,sz,t,t+dr))
        for i in range(self.N):
            self.trace[i] = sorted(self.trace[i], key=lambda tr: tr.start)
    def log(self, procs):
        for p in procs:
            with open("send.%d"%p,'w') as fs, open("recv.%d"%p,'w') as fr:
                fs.write("TYPE SRC DEST SIZE(Byte) START(us) END(us)\n")
                fr.write("TYPE SRC DEST SIZE(Byte) START(us) END(us)\n")
                for tc in self.trace[p]:
                    if tc.tp == 'S':
                        fs.write(str(tc))
                        fs.write('\n')
                    elif tc.tp == 'R':
                        fr.write(str(tc))
                        fr.write('\n')

# Example 1, odd-even send-recv, with constant interval, constant size and constant duration
def run_example_one():
    # Specify the parameters in this section
    g=TRG()
    # Number of process
    g.set_size(4)
    # Communication pattern
    # processes filter, destination expression, start time, duration, message size
    g.add_pattern(["i%2==0", "i+1", "range(0,100,10)", "20", "64"])
    # generate traces
    g.build()
    # output all or some of them
    g.log(range(4))

# Example 2, all processes send to random destinations with random time and random size
def run_example_two():
    g=TRG()
    N=4
    g.set_size(N)
    g.add_pattern(["i==i", # all processes will evaluate this expression to be true
                  "random.randint(0,self.N-1)", # random destination 
                  "[random.randint(0,2000) for _ in range(random.randint(10,20))]", # random times communication at random time
                  "random.randint(10,500)", # random duration
                  "random.randint(8,1024)"]) # random size
    g.build()
    g.log(range(N))

#run_example_one()
run_example_two()
