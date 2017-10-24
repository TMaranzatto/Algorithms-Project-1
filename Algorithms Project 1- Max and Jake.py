import random
import statistics
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
import linecache
import time
import itertools
from scipy.optimize import linear_sum_assignment
import re
import os
import glob

def my_shuffle(array):
    random.shuffle(array)
    return(array)

def resourceAllocation(a, r, kValue, eqClasses,  initialAllocations, seed):
    myFile = open('new.txt', 'w+')
    myFile.write('Agents: ' + str(a) + ' Resources: ' + str(r) + ' K Value: ' + str(kValue) + ' Eq. Classes: ' + str(eqClasses) + '\n') #JM made data representation the same as Selena's
    random.seed(seed)
    agentResources = [random.sample(range(r), eqClasses*kValue) for j in range(a)]
    if initialAllocations == 0:
        for resource in agentResources:
            myFile.write(str(resource)[1: -1] + ' ' + '\n')
        myFile.close()


def merge(a,b):
    c = []
    while len(a) != 0 and len(b) != 0:
        if a[0] < b[0]:
            c.append(a[0])
            a.remove(a[0])
        else:
            c.append(b[0])
            b.remove(b[0])
    if len(a) == 0:
        c += b
    else:
        c += a
    return c

def mergesort(x):
    if len(x) == 0 or len(x) == 1:
        return x
    else:
        middle = len(x)/2
        a = mergesort(x[:middle])
        b = mergesort(x[middle:])
        return merge(a,b)

def reversemergesort(x):
    return mergesort(x)[::-1]

def sortLine(string, order):
    string = string.split(',')
    for item in string:
        if item == '' or item == ' ':
            string.remove(item)
    if order == 0:
        mergesort(string)
    elif order == 1:
        reversemergesort(string)
    
    return ",".join(map(str,string))


def sortResources(preferenceFile, sortorder):
    #we will sort each line of the file in numeric order
    myFile = open(preferenceFile, 'r')
    newFile = open('ordered.txt', 'w+')
    for line in myFile:
        newline = sortLine(line, sortorder)
        newFile.write(newline)
        
    with open(preferenceFile, 'w+') as output, open('ordered', 'r') as input:
        while True:
            data = input.read(100000)
            if data == '':  # end of file reached
                break
            output.write(data)
    
def chunks(l, n):
     for i in range(0, len(l), n):
        yield l[i:i + n]

def RicaFileMaker(preferenceFile):
    myFile = open(preferenceFile, 'r')
    first = myFile.readline()
    firstitems  = first.split(' ')
    preferenceClasses = firstitems[-1]
    a = firstitems[1]
    r = firstitems[3]
    k = firstitems[6]
    assignedObjects = []
    unassignedAgents = []
    
    eqLevels = [{} for x in range(int(k) - 1)]
    agentLocations = [{} for x in range(int(a))]

    currentAgent = 0
    
    for line in myFile:
        x = line.replace(' \n' , '')
        items = x.split(' ')
        
        currentItem = 0
        for item in items[:]:
            if item == '' or item == None or item == '  ':
                items.remove(item)
            items[currentItem] = item.replace(',' , '')
            currentItem += 1
        
        items = list(map(int, items))

        itemChunks = chunks(items, int(k))
        currentChunk = 0
        for chunk in itemChunks:
            tempLocation = agentLocations[currentAgent]
            tempLocation[currentChunk] = chunk
            for item in chunk:
                tempDict = eqLevels[currentChunk]
                if item in tempDict:
                    tempDict[item].append(currentAgent)
                else:
                    tempDict[item] = [currentAgent]
            currentChunk += 1
                    
        unassignedAgents.append(str(currentAgent))
        currentAgent += 1

    return(eqLevels, agentLocations, currentAgent, assignedObjects, unassignedAgents)

def RICA(preferenceFile):
    assignments = open('Assignments.txt', 'w+')
    data = RicaFileMaker(preferenceFile)
    
    eqLevels = data[0]
    agentLocations = data[1]
    assignedObjects = data[3]
    unassignedAgents = data[4]
    
    resourceNumbers = [i for i in range(data[2])]

    curLevel = 0
    for eqClasses in eqLevels:
        while len(eqClasses) != 0:
            minLength = min(map(len, eqClasses.values()))
            for key in eqClasses:
                if len(eqClasses[key]) == minLength:
                    randObject = key
                    break
                
            randAgent = random.choice(eqClasses[randObject])
            assignments.write('Resource ' + str(randObject) + ': ' + str(randAgent) + '\n')
            assignedObjects.append(randObject)
            unassignedAgents.remove(str(randAgent))
            randAgentLocations = agentLocations[randAgent]
            for level in eqLevels:
                try:
                    level.pop(randObject)
                except:
                    continue
            for key in randAgentLocations:
                currentLevel = eqLevels[key]
                for value in randAgentLocations[key]:
                    try:
                        currentLevel[value].remove(randAgent)
                        if(len(currentLevel[value]) == 0):
                            currentLevel.pop(value)
                    except:
                        continue
                
            curLevel += 1
            
    assignedObjectsSet = set(assignedObjects)
    unassignedObjects = [x for x in resourceNumbers if x not in assignedObjectsSet]
    random.shuffle(unassignedObjects)
    random.shuffle(unassignedAgents)
    remainingAssignments = zip(unassignedObjects, unassignedAgents)
    for pair in remainingAssignments:
        assignments.write('Resource ' + str(pair[0]) + ': ' + str(pair[1]) + '\n')


def paretoChecker():
    preferences = open('new.txt', 'r')
    preferences = preferences.read().splitlines()
    preferences.pop(0)
    paretoSwaps = 0
    baseAgent = 0
    
    assignments = open('Assignments.txt', 'r')
    assignments = assignments.read().splitlines()
    for line in preferences:
        x = line.replace('Resource ', '')
        x = line.replace(',', '')
        preference  = x.split(' ')
        preference.pop()
        preference = list(map(int, preference))
        y = linecache.getline('new.txt', baseAgent + 2)
        basePreference  = y.split(' ')
        basePreference.pop()
        basePreference = list(map(int, preference))     
        for lines in assignments:
            agent = int(lines.split(':')[1].strip(' '))
            resource = int(lines.split(':')[0].strip('Resource '))
            if resource not in preference and agent != baseAgent:   
                #comparison
                if resource in basePreference:
                    paretoSwaps += 1
                    break
        baseAgent += 1
    paretoSwaps = paretoSwaps / 2

    return paretoSwaps

def envyChecker():
    preferences = open('new.txt', 'r')
    preferences = preferences.read().splitlines()
    preferences.pop(0)
    envyValue = 0
    baseAgent = 0
    
    assignments = open('Assignments.txt', 'r')
    assignments = assignments.read().splitlines()
    for line in preferences:
        x = line.replace('Resource ', '')
        x = line.replace(',', '')
        preference = x.split(' ')
        preference.pop()
        preference = list(map(int, preference))
        for lines in assignments:
            agent = int(lines.split(':')[1].strip(' '))
            resource = int(lines.split(':')[0].strip('Resource '))
            if agent == baseAgent:
                if resource not in preference:
                    for item in preference:
                            if item in [int(x.split(':')[0].strip('Resource ')) for x in assignments]:
                                envyValue += 1
                                break
        baseAgent += 1
    return envyValue

def timeGraph(maxAgents, maxResources, kValue, eqClasses, resolution,  runs, initAll):
    times = []
    agents = [(int(maxAgents / resolution * x)) for x in range(resolution)]
    divisions = int(maxAgents / resolution)
    resourceDivisions = maxResources / resolution
    for z in range(runs):
        times1 = []
        for x in range(resolution):
            resourceAllocation(int(maxAgents / resolution * x), int(maxResources / resolution * x), kValue, eqClasses, initAll, random.randint(0, 100000))
            sortResources("C:\\Users\\Jake From State Farm\\Desktop\\new.txt", 1)
            start_time = time.clock()
            RICA("C:\\Users\\Jake From State Farm\\Desktop\\new.txt")
            times1.append(time.clock() - start_time)
            times.append(times1)
            
    data = np.array(times)
    averageTimes = np.average(data, axis = 0)
    standardDeviations = np.std(data, axis = 0)
    #plt.scatter(agents, averageTimes, s=10, alpha = 0.5)
    plt.errorbar(agents, averageTimes, yerr = standardDeviations, fmt = 'o')
    plt.xlabel('Agents')
    plt.ylabel('Runtimes (s)')
    plt.title('Runtimes for ' + 'RICA' + ': k =' + str(kValue))
    plt.show()
    #graph times
            
def paretoGraph(maxAgents, maxResources, kValue, eqClasses, resolution, runs, initAll):
    paretos = []
    agents = [(int(maxAgents / resolution * x)) for x in range(resolution)]
    divisions = int(maxAgents / resolution)
    resourceDivisions = maxResources / resolution
    for z in range(runs):
        print(z)
        paretos1 = []
        for x in range(1, resolution + 1):
            resourceAllocation(int(maxAgents / resolution * x), int(maxResources / resolution * x), kValue, eqClasses, initAll, random.randint(0, 100000))
            RICA("C:\\Users\\Jake From State Farm\\Desktop\\new.txt")
            paretos1.append(paretoChecker())
            paretos.append(paretos1)
    
    data = np.array(paretos)
    averageParetos = np.average(data, axis = 0)
    standardDeviations = np.std(data, axis = 0)
    #plt.scatter(agents, averageTimes, s=10, alpha = 0.5)
    plt.errorbar(agents, averageParetos, yerr = standardDeviations, fmt = 'o')
    plt.xlabel('Agents')
    plt.ylabel('Pareto-Swaps')
    plt.title('Pareto-Swaps for ' + 'RICA' + ': k =' + str(kValue))
    plt.show()
    #graph


def envyGraph(maxAgents, maxResources, kValue, eqClasses, resolution, runs, initAll):
    envys = []
    agents = [(int(maxAgents / resolution * x)) for x in range(resolution)]
    divisions = int(maxAgents / resolution)
    resourceDivisions = maxResources / resolution
    for z in range(runs):
        print(z)
        envys1 = []
        for x in range(1, resolution + 1):
            resourceAllocation(int(maxAgents / resolution * x), int(maxResources / resolution * x), kValue, eqClasses, initAll, random.randint(0, 100000))
            RICA("C:\\Users\\Jake From State Farm\\Desktop\\new.txt")
            envys1.append(envyChecker())
            envys.append(envys1)
            
    data = np.array(envys)
    averageEnvys = np.average(data, axis = 0)
    standardDeviations = np.std(data, axis = 0)
    #plt.scatter(agents, averageTimes, s=10, alpha = 0.5)
    plt.errorbar(agents, averageEnvys, yerr = standardDeviations, fmt = 'o')
    plt.xlabel('Agents')
    plt.ylabel('Envious Agents')
    plt.title('Envious Agents for ' + 'RICA' + ': k =' + str(kValue))
    plt.show()

timeGraph(100,100, 5, 1, 10, 1, 0)
