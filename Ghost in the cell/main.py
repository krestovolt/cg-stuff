import sys
import math
import numpy as np
import copy
from collections import deque

'''********************************************************************************'''
bomb_counter,game_tick = 0,0
factory_count = int(input())  # the number of factories
cost_matrix = np.full((factory_count,factory_count), np.inf)
path_m = None
dist_m = None
link_count = int(input())  # the number of links between factories
for i in range(link_count):
    factory_1, factory_2, distance = [int(j) for j in input().split()]
    #print(distance, file=sys.stderr)
    cost_matrix[factory_1][factory_2] = np.inf if distance == 0 else distance
    cost_matrix[factory_2][factory_1] = cost_matrix[factory_1][factory_2]
'''********************************************************************************'''
def floyd_warshall_v1(cost_mat = []):
    global factory_count
    query_set = ''
    distance_matrix = np.full((factory_count,factory_count), np.inf)
    path_matrix = np.full((factory_count,factory_count), np.inf)
    if len(cost_mat) != 0:
        print('change distance matrix', file=sys.stderr)
        #initalize path and distance matrix for next process
        for i in range(len(distance_matrix)):
            for j in range(len(distance_matrix)):
                distance_matrix[i][j] = cost_mat[i][j]
                if cost_mat[i][j] != np.inf and i != j:
                    path_matrix[i][j] = i
                else:
                    path_matrix[i][j] = -1
        #next process
        for k in range(len(cost_mat)):
            for i in range(len(cost_mat)):
                for j in range(len(cost_mat)):
                    if distance_matrix[i][k] == np.inf or distance_matrix[k][j] == np.inf:
                        continue
                    if distance_matrix[i][j] > distance_matrix[i][k] + distance_matrix[k][j]:
                        distance_matrix[i][j] = distance_matrix[i][k] + distance_matrix[k][j]
                        path_matrix[i][j] = path_matrix[k][j]

    return (distance_matrix,path_matrix)

def get_path(path_matrix,source,dest):
    path_id = deque()
    i = int(source.fid)
    j = int(dest.fid)
    path_id.appendleft(j)
    while True:
        print('J',j,'I',i,file=sys.stderr)
        j = int(path_matrix[i][j])
        if j == -1:
            return
        path_id.appendleft(j)
        if j == i:
            break
    return list(path_id)

'''********************************************************************************'''
dist_m, path_m = floyd_warshall_v1(cost_mat = copy.copy(cost_matrix))
print(cost_matrix, file=sys.stderr)
print(dist_m, file=sys.stderr)
print(path_m, file=sys.stderr)
'''********************************************************************************'''
class Factory:
    def __init__(self,fid,owner,troops,production):
        self.fid = fid
        self.owner = owner
        self.troops = troops
        self.production = production
        self.attacker = 0
        self.capacity = troops/2
        self.status = "G"
        self.request_troops = 0
        self.nearest = []
        self.bomb_candidate = None
        self.assist_to = {}
        self.assisting = "N"
    def get_status(self):
        self.status = "G" if self.troops+self.production > self.attacker\
                        else "A" if self.capacity <= 0 else "A"
        if self.status == "A":
            self.request_troops = abs(self.troops)+10
        return self.status
    def recalc_cap(self,r=0):
        self.capacity = int((self.troops+r)/2)
    def pre_calc_nearest(self,fs,cm):
        self.nearest = sorted(fs, key = lambda d: cm[self.fid][d.fid])




'''********************************************************************************'''
def broadcast_command(path,source,factory_list,troops_sent=0):
    end_point = None
    for p in range(1,len(path)):
        tp = list(filter(lambda x: x.fid == path[p],factory_list))[0]
        if tp.owner != 1:
            prev_tp = list(filter(lambda x: x.fid == path[p-1],factory_list))[0]
            if tp.fid in prev_tp.assist_to:
                prev_tp.assist_to[tp.fid] += source.capacity if troops_sent==0 else troops_sent
            else:
                prev_tp.assist_to[tp.fid] = source.capacity if troops_sent==0 else troops_sent
            break
        elif tp.owner == 1:
            tp.assisting = 'Y'
            prev_tp = list(filter(lambda x: x.fid == path[p-1],factory_list))[0]
            if tp.fid in prev_tp.assist_to:
                prev_tp.assist_to[tp.fid] += source.capacity if troops_sent==0 else troops_sent
            else:
                prev_tp.assist_to[tp.fid] = source.capacity if troops_sent==0 else troops_sent




def nearest_factory(source,bomb_target,all_f):
    query,counter,flag,flag_help = '',0,0,0
    source_status = source.get_status()

    for f in source.nearest:
        if counter < len(source.nearest):
            if (f.status == 'R' and f.owner == 1 and f.troops >= 10):
                query += 'INC '+str(f.fid)+';'
            if f.owner == 1 and f.get_status() == 'A' and source_status != 'A' and f.production != 0 and flag_help != 1:
                path_f = get_path(path_m,source,f)
                f.request_troops -= source.capacity
                source.troops -= source.capacity
                source.recalc_cap()
                f.recalc_cap(r=source.capacity)
                f.status = 'R'
                broadcast_command(path_f,source,all_f)
                flag_help += 1
            elif f.owner != 1 and f.production > 0 and source_status != 'A' and flag != 3:
                sent_troops = 0
                flag += 1
                path_f = None
                if bomb_target != None and flag==1:
                    sent_troops = source.capacity*2
                    path_f = get_path(path_m,source,f)
                elif source.troops - (source.capacity*3) - source.attacker > 0 and f.production >= 2:
                    sent_troops = source.capacity*3
                    path_f = get_path(path_m,source,f)
                elif source.troops - (source.capacity*2) - source.attacker > 0 and f.production >= 2:
                    sent_troops = source.capacity*2
                    path_f = get_path(path_m,source,f)
                elif source.capacity > 1:
                    sent_troops = source.capacity
                    path_f = get_path(path_m,source,f)
                if sent_troops > 0:
                    if bomb_target != None and bomb_target.fid != source.fid:
                        source.troops -= sent_troops
                        source.recalc_cap()
                        broadcast_command(path_f,source,all_f,troops_sent = sent_troops)
                        #query += 'MOVE '+str(source.fid)+' '+str(bomb_target.fid)+' '+str(sent_troops)+';'
                    else:
                        broadcast_command(path_f,source,all_f,troops_sent = sent_troops)
                else:
                    query += 'WAIT;'
                    counter = len(source.nearest)
            elif source_status == 'A':
                query += 'WAIT;'
                counter = len(source.nearest)
        counter += 1
    if len(source.assist_to) != 0:
        for dest_id,amount in source.assist_to.items():
            query += 'MOVE '+str(source.fid)+' '+str(int(dest_id))+' '+str(int(amount))+';'
        source.assist_to.clear()
    if source.troops - 10 > source.attacker * 1.5:
        source.troops -= 10
        query += 'INC '+str(source.fid)+';'

    return query

'''********************************************************************************'''
prev_bomb_target,bomb_timestamp = None,0
while True:
    entity_count = int(input())  # the number of entities (e.g. factories and troops)
    my_troops_movement = {}
    all_f = []
    mf = []

    other_f = []
    command = ''

    for i in range(entity_count):
        entity_id, entity_type, ag1, ag2, ag3, ag4, ag5 = input().split()
        entity_id = int(entity_id)

        ag1 = int(ag1)
        ag2 = int(ag2)
        ag3 = int(ag3)
        ag4 = int(ag4)
        ag5 = int(ag5)

        if entity_type == "FACTORY" and ag1 == 1:
            print(entity_id,file=sys.stderr)
            mf.append(Factory(entity_id,ag1,ag2,ag3))
        elif entity_type == "FACTORY" and ag1 != 1:
            other_f.append(Factory(entity_id,ag1,ag2,ag3))
        elif entity_type == "TROOP" and ag1 != 1 and len(mf)!=0:
            targeted = list(filter(lambda f:f.fid == ag3, mf))
            if len(targeted)!=0:
                targeted[0].attacker += ag4
                targeted[0].troops -= ag4
        elif entity_type == "TROOP" and ag1 == 1 and len(other_f)!=0:
            targeted = list(filter(lambda f:f.fid == ag3, other_f))
            if len(targeted)!=0:
                targeted[0].attacker += ag4
                targeted[0].troops -= ag4

    all_f = copy.deepcopy(mf) + copy.deepcopy(other_f)
    #calculate nearest factory for other factory

    #core process
    for row in range(len(other_f)):
        other_f[row].pre_calc_nearest(all_f,dist_m)
    for row in range(len(mf)):
        mf[row].pre_calc_nearest(all_f,dist_m)
        filtered_enemy_factory = list(filter(lambda f:f.owner == -1 and f.troops>10 and f.production >= 2, other_f))
        if len(filtered_enemy_factory) != 0:
            filtered_enemy_factory = copy.copy(sorted(filtered_enemy_factory, key = lambda s: s.troops, reverse = True)[0])
            mf[row].bomb_candidate = filtered_enemy_factory
    for row in range(len(mf)):
        mf[row].recalc_cap()
        print(mf[row].fid,mf[row].attacker, file=sys.stderr)
        command += nearest_factory(mf[row],prev_bomb_target,other_f+mf)
        if bomb_counter < 2 and mf[row].bomb_candidate != None and (prev_bomb_target==None or prev_bomb_target.fid != mf[row].bomb_candidate.fid):
            #BOMB source destination
            prev_bomb_target = copy.copy(mf[row].bomb_candidate)
            command += 'BOMB '+str(mf[row].fid)+' '+str(mf[row].bomb_candidate.fid)+';'
            bomb_counter += 1
            bomb_timestamp = game_tick

    command += 'MSG meerkat'
    print(bomb_counter, file=sys.stderr)
    print(command)
    if bomb_timestamp != 0 and game_tick - bomb_timestamp == 60:
        prev_bomb_target = None
    game_tick += 1
