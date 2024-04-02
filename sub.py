import subprocess
import os
import resource
def set_limit_resource(language,time_limit,memory_limit):
    memory_limit*=1048576
    if(language==True):
        time_limit*=5
        memory_limit*=5
    def setlimits():
        resource.setrlimit(resource.RLIMIT_CPU, (time_limit, time_limit))
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
    return setlimits()

os.chdir('src')
er=open('error.txt','w+')
rc=open('return_code.txt','w+')
def py(time_limit,memory_limit):
    a=subprocess.run('python3 code.py <input.txt>output.txt',shell=True,stderr=er,preexec_fn=set_limit_resource(True,time_limit,memory_limit),text=True)
    rc.write(str(a.returncode))
    rc.close()
    er.close()
def cpp(time_limit,memory_limit):
    a=subprocess.run('g++ code.cpp -o cpp.out',shell=True,stderr=er,text=True)
    rc.write(str(a.returncode))
    if(a.returncode==0):
        a=subprocess.run('./cpp.out <input.txt>output.txt',shell=True,stderr=er,preexec_fn=set_limit_resource(False,time_limit,memory_limit),text=True)
        rc.write(str(a.returncode))
    rc.close()
    er.close()

def c(time_limit,memory_limit):
    a=subprocess.run('gcc code.c -o c.out',shell=True,stderr=er,text=True)
    rc.write(str(a.returncode))
    if(a.returncode==0):
        a=subprocess.run('./c.out <input.txt>output.txt',shell=True,stderr=er,preexec_fn=set_limit_resource(False,time_limit,memory_limit),text=True)
        rc.write(str(a.returncode))
    rc.close()
    er.close()