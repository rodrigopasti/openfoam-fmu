# -*- coding: utf-8 -*-
'''
Created on 23/07/2018

@author: Walter Mazuroski
'''

from wsl_docker_runner import run_command, process_exists

def main(state):

    #if process_exists(state.pid):
    #    run_command(["taskkill", "/PID", str(state.pid), "/F"])
    #    print(f"dockerd (PID {state.pid}) finalizado com sucesso.")

    return str('finalized')
