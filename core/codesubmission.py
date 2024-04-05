from .models import Containers
import time
import os
import subprocess
import shutil

def swap_input(container_name, test_id, cust):
    dest=f"containers/{test_id}/{container_name}/input.txt"
    with open(dest, 'w') as inp:
        inp.write(cust)
    

def swap_code(container_name,code,language,time_limit,memory_limit, test_id):
    dest=f"containers/{test_id}/{container_name}/sub.py"
    path=""
    with open(dest,'a') as sub:
        if(language=="pyth"):
            path="code.py"
            sub.write(f'\npy({time_limit},{memory_limit})')
        elif(language=="c++"):
            path="code.cpp"
            sub.write(f'cpp({time_limit},{memory_limit})')
        else:
            path="code.c"
            sub.write(f'c({time_limit},{memory_limit})')
    dest=f"containers/{test_id}/{container_name}/{path}"
    with open(dest,'w+') as op:
        op.write(code)

def execute(container_name):
    command=f"docker exec {container_name} python3 src/sub.py"
    a=subprocess.run(command,shell=True,text=True)

def get_returnCode(container_name, tid):
    returnCode=0
    path = os.path.join(os.getcwd(), f'containers/{tid}/{container_name}/return_code.txt')
    with open(path, 'r') as ret:
        returnCode=ret.read()
    returnCode=returnCode.strip()
    returnCode=int(returnCode)
    return returnCode

def get_Error(container_name, tid):
    error=""
    path = os.path.join(os.getcwd(), f'containers/{tid}/{container_name}/error.txt')

    with open(path,'r') as err:
        error=err.read()
    return error

def get_Output(container_name, tid):
    path = os.path.join(os.getcwd(), f'containers/{tid}/{container_name}/output.txt')
    op=""
    with open(path) as file_1:
        op=file_1.read()
    return op

def find_container():
    container=0
    while(len(list(Containers.objects.filter(status=False)))==0):
        time.sleep(5)
    container=list(Containers.objects.filter(status=False))[0]
    container.status=True
    container.save()
    return container

def get_sub(container_name, tid):
    origin="sub.py"
    dest=f"containers/{tid}/{container_name}/sub.py"
    shutil.copyfile(origin,dest)

def returnContainer(container):
    container.status=False
    container.save()

def run_code(code, language, tid, qid, custInp):
    container=find_container()
    get_sub(container.container_name, tid)
    swap_code(container.container_name, code, language, 1, 512, tid)
    swap_input(container.container_name, tid, custInp)
    execute(container.container_name)
    rcode=get_returnCode(container.container_name, tid)
    er = get_Error(container.container_name, tid)
    op = get_Output(container.container_name, tid)
    returnContainer(container)
    return {'returnCode': rcode, 'error': er, 'output': op}