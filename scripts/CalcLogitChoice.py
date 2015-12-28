#----------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Name:        CalcLogitChoice
# Purpose:     Utilities for various calculations of different types of choice models.
#               a) CalcMultinomialChoice : Calculates a multinomial choice model probability given a dictionary of mode utilities 
#               b) CalcPivotPoint : Calculates pivot point choice probability given base utilities, current utilities and base proabilities
#               c) CalcNestedChoice : Calculates n-level nested mode choice probabilities given dictionary with tree definition, matrix references and number of zones
#               d) TODO: CalcNestedChoiceFlat : Calculate nested choice on flat array so it can be used for stuff like microsim ABM etc... e) can in general be easily modified for this 
#              **All input vectors are expected to be numpy arrays  
#               
# Author:      Chetan Joshi, Portland OR
# Dependencies:numpy [www.numpy.org], math, time 
# Created:     5/14/2015
#              
# Copyright:   (c) Chetan Joshi 2015
# Licence:     Permission is hereby granted, free of charge, to any person obtaining a copy
#              of this software and associated documentation files (the "Software"), to deal
#              in the Software without restriction, including without limitation the rights
#              to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#              copies of the Software, and to permit persons to whom the Software is
#              furnished to do so, subject to the following conditions:
#
#              The above copyright notice and this permission notice shall be included in all
#              copies or substantial portions of the Software.
#
#              THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#              IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#              FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#              AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#              LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#              OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#              SOFTWARE.
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------#
import numpy
import time
import math
#from memory_profiler import profile


def CalcMultinomialChoice(Utils, getLogSumAccess = 0):
    '''Utils = Dictionary of utility matrices for each mode
       ex. Utils = {'auto':mat1, 'transit':mat2, 'bike':mat3, 'walk':mat4}
       getLogSumAccess (optional, accessibility log sum) 0=no, <>0=yes
    '''
    Probs = {}
    eU = {}
    eU_total = numpy.zeros(Utils[Utils.keys()[0]].shape)
    for key in Utils.keys():
        eU[key] = numpy.exp(Utils[key])
        eU_total+=eU[key]
    if getLogSumAccess <> 0:
        lnSumAccess = numpy.log(eU_total)
        
    eU_total[eU_total == 0] = 0.0001
    
    for key in eU.keys():
        Probs[key] = eU[key]/eU_total
    del eU, eU_total, Utils
    
    if getLogSumAccess == 0:
        return Probs
    else:
        return Probs, lnSumAccess

def CalcPivotPoint(BaseUtils, Utils, Po):
    '''
       BaseUtils = Base utility matrices in a dictionary
       ex. BaseUtils = {'auto':mat1, 'transit':mat2, 'bike':mat3, 'walk':mat4}
       
       Utils = Updated utility matrices in a dictionary
       ex. Utils = {'auto':mat1, 'transit':mat2, 'bike':mat3, 'walk':mat4}
       
       Po = Base probabilities in a dictionary
       ex. Po = {'auto':mat1, 'transit':mat2, 'bike':mat3, 'walk':mat4}  
    '''
    Probs = {}
    PeU = {}
    PeU_total = numpy.zeros(Utils[Utils.keys()[0]].shape)
    for key in Utils.keys():
        PeU[key] = Po[key]*numpy.exp(Utils[key])
        PeU_total+=PeU[key]
    PeU_total[PeU_total == 0] = 0.0001

    for key in PeU.keys():
        Probs[key] = PeU[key]/PeU_total

    del PeU, PeU_total, Utils
    return Probs

#@profile
def CalcNestedChoice(TreeDefn, MatRefs, numZn, getLogSumAccess = 0):
    '''
    #TreeDefn = {(0,'ROOT'):[1.0,['AU', 'TR', 'AC']],
    #            (1,'AU'):[0.992,['CD', 'CP']],
    #            (1,'TR'):[0.992,['TB', 'TP']],
    #            (1,'AC'):[0.992,['BK', 'WK']]}
    #
    #Key-> (Level ID, Level Code): Values-> (LogSum Parameter enters as: 1/lambda, SubLevel IDs)
    #       ROOT should always be ID = 0 and Code = 'ROOT'                            
    #                             ROOT
    #                            / |  \
    #                           /  |   \
    #	                       /   |    \
    #	                     AU    TR    AC(logsum parameter)
    #	                    /\     /\     /\ 
    #	                  CD CP  TB TP  BK WK         
    #             		              
    #MatRefs = {'ROOT': 1.0, 'AU':0, 'TR':0, 'AC':0,
    #           'CD':Ucd), 'CP':Ucp),
    #           'TB':Utb), 'TP':Utp),
    #           'BK':Ubk), 'WK':Uwk)} Stores utilities in dict of matrices, base level utilities are pre-specified!!
    #
    #numZn = number of zones
    #
    #getLogSumAccess (optional, accessibility log sum) 0=no, <>0=yes
    ''' 
    #ProbMats = {'ROOT': 1.0, 'AU':0, 'TR':0, 'AC':0, 'CD':0, 'CP':0, 'TB':0, 'TP':0, 'BK':0, 'WK':0}   #Stores probabilities at each level
    #TripMat = GetMatrixRaw(Visum, tripmatno) #--> Input trip distribution matrix
    #numZn = Visum.Net.Zones.Count
    ProbMats = dict(zip(MatRefs.keys(), numpy.zeros(len(MatRefs.keys()))))
    ProbMats['ROOT'] = 1.0
    #Utility calculator going up...
    #print 'Getting logsums and utilities...'
    for key in sorted(TreeDefn.keys(), reverse= True):
        #print key, TreeDefn[key]
        sumExp = numpy.zeros((numZn,numZn))   
        sublevelmat_codes = TreeDefn[key][1]  #produces --> ex. ['WB', 'WX', 'DX']

        for code in sublevelmat_codes:
            #print ([code, TreeDefn[key][0]])
            MatRefs[code] = MatRefs[code]/TreeDefn[key][0]  #---> scale the utility
            sumExp+=numpy.exp(MatRefs[code])
        lnSum = sumExp.copy() #Maybe there is a better way of doing the next 4 steps in 1 shot
        lnSum[sumExp == 0] = 0.000000001 
        lnSum = numpy.log(lnSum)
        lnSum[sumExp == 0] = -999
        MatRefs[key[1]] = TreeDefn[key][0]*lnSum #---> Get ln sum of sublevel

    #Probability going down...
    #print 'Getting probabilities...'
    for key in sorted(TreeDefn.keys()):
        #print key, TreeDefn[key]
        eU_total = numpy.zeros((numZn,numZn))
        sublevelmat_codes = TreeDefn[key][1] #1st set--> ROOT : AU, TR
        for code in sublevelmat_codes:
            #print ([code, TreeDefn[key][0]])
            eU_total+=numpy.exp(MatRefs[code])
            
        eU_total[eU_total == 0] = 0.0001  #Avoid divide by 0 error
##        for code in sublevelmat_codes:
##            ProbMats[code] = ProbMats[key[1]]*numpy.exp(MatRefs[code])/eU_total
        nSublevels = len(sublevelmat_codes)
        cumProb = 0 
        for i in xrange(nSublevels - 1):
            code = sublevelmat_codes[i]
            temp = numpy.exp(MatRefs[code])/eU_total
            ProbMats[code] = ProbMats[key[1]]*temp
            cumProb+=temp
        code = sublevelmat_codes[i+1]
        ProbMats[code] = ProbMats[key[1]]*(1.0-cumProb) 
        
    if getLogSumAccess == 0:
        return ProbMats
    else:
        return ProbMats, MatRefs['ROOT']


def CalcNestedChoiceFlat(TreeDefn, MatRefs, vecLen, getLogSumAccess = 0):
    '''
    #TreeDefn = {(0,'ROOT'):[1.0,['AU', 'TR', 'AC']],
    #            (1,'AU'):[0.992,['CD', 'CP']],
    #            (1,'TR'):[0.992,['TB', 'TP']],
    #            (1,'AC'):[0.992,['BK', 'WK']]}
    #
    #Key-> (Level ID, Level Code): Values-> (LogSum Parameter enters as: 1/lambda, SubLevel IDs)
    #       ROOT should always be ID = 0 and Code = 'ROOT'                            
    #                             ROOT
    #                            / |  \
    #                           /  |   \
    #	                       /   |    \
    #	                     AU    TR    AC(logsum parameter)
    #	                    /\     /\     /\ 
    #	                  CD CP  TB TP  BK WK         
    #             		              
    #MatRefs = {'ROOT': 1.0, 'AU':0, 'TR':0, 'AC':0,
    #           'CD':Ucd), 'CP':Ucp),
    #           'TB':Utb), 'TP':Utp),
    #           'BK':Ubk), 'WK':Uwk)} Stores utilities in dict of vectors, base level utilities are pre-specified!!
    #
    #vecLen = number of od pairs being evaluated 
    #
    #getLogSumAccess (optional, accessibility log sum) 0=no, <>0=yes
    ''' 
    #ProbMats = {'ROOT': 1.0, 'AU':0, 'TR':0, 'AC':0, 'CD':0, 'CP':0, 'TB':0, 'TP':0, 'BK':0, 'WK':0}   #Stores probabilities at each level
    #TripMat = GetMatrixRaw(Visum, tripmatno) #--> Input trip distribution matrix
    #numZn = Visum.Net.Zones.Count
    ProbMats = dict(zip(MatRefs.keys(), numpy.zeros(len(MatRefs.keys()))))
    ProbMats['ROOT'] = 1.0
    #Utility calculator going up...
    #print 'Getting logsums and utilities...'
    for key in sorted(TreeDefn.keys(), reverse= True):
        #print key, TreeDefn[key]
        sumExp = numpy.zeros(vecLen)   
        sublevelmat_codes = TreeDefn[key][1]  #produces --> ex. ['WB', 'WX', 'DX']

        for code in sublevelmat_codes:
            #print ([code, TreeDefn[key][0]])
            MatRefs[code] = MatRefs[code]/TreeDefn[key][0]  #---> scale the utility
            sumExp+=numpy.exp(MatRefs[code])
        lnSum = sumExp.copy() #Maybe there is a better way of doing the next 4 steps in 1 shot
        lnSum[sumExp == 0] = 0.000000001 
        lnSum = numpy.log(lnSum)
        lnSum[sumExp == 0] = -999
        MatRefs[key[1]] = TreeDefn[key][0]*lnSum #---> Get ln sum of sublevel

    #Probability going down...
    #print 'Getting probabilities...'
    for key in sorted(TreeDefn.keys()):
        #print key, TreeDefn[key]
        eU_total = numpy.zeros(vecLen)
        sublevelmat_codes = TreeDefn[key][1] #1st set--> ROOT : AU, TR
        for code in sublevelmat_codes:
            #print ([code, TreeDefn[key][0]])
            eU_total+=numpy.exp(MatRefs[code])
            
        eU_total[eU_total == 0] = 0.0001  #Avoid divide by 0 error
##        for code in sublevelmat_codes:
##            ProbMats[code] = ProbMats[key[1]]*numpy.exp(MatRefs[code])/eU_total
        nSublevels = len(sublevelmat_codes)
        cumProb = 0 
        for i in xrange(nSublevels - 1):
            code = sublevelmat_codes[i]
            temp = numpy.exp(MatRefs[code])/eU_total
            ProbMats[code] = ProbMats[key[1]]*temp
            cumProb+=temp
        code = sublevelmat_codes[i+1]
        ProbMats[code] = ProbMats[key[1]]*(1.0-cumProb) 
        
    if getLogSumAccess == 0:
        return ProbMats
    else:
        return ProbMats, MatRefs['ROOT']

#some generic utilities for reading and writing numpy arrays to disk..

def GetMatrix(fn, numZn):
    return numpy.fromfile(fn).reshape((numZn, numZn))

def GetMatrixFlat(fn):
    return numpy.fromfile(fn)

def PushMatrix(fn, mat):
    mat.tofile(fn)

## DEMO---->
##def runNested():
##    PMats = CalcNestedChoice(TreeDefn, MatRefs, numZn)
##    for key in PMats.keys():
##        if key <> 'ROOT':
##            mat = PMats[key]
##            print key, mat.sum(), mat[3398, 3397]
##            PushMatrix(fn+str(key)+".np", mat)
##    del PMats
##
###@profile
##def runMultiNomial():
##    Utils = {'da':da, 'wb':wb, 'wx':wx}
##    PMats = CalcMultinomialChoice(Utils)
##    del PMats
##    
##    
##start = time.time()    
##print 'Calculating nested choice...'
##numZn = 3399 
##fn = r"C:\DevResearch\Visum_Utils\Test Matrices\\"
##da = GetMatrix(fn+"801.np", numZn)
##wb = GetMatrix(fn+"803.np", numZn)
##wx = GetMatrix(fn+"802.np", numZn)
##
##TreeDefn = {(0,'ROOT'):[1.0,['AU', 'TR']], (1,'TR'):[0.75,['WB', 'WX']]}
##MatRefs = {'ROOT': 1.0, 'AU':da , 'TR':0, 'WB':wb, 'WX':wx} #Stores utilities, base level utilities are pre-specified
###Utils = {'da':da, 'wb':wb, 'wx':wx}
###ProbMats = {'ROOT': 1.0, 'AU':0, 'TR':0, 'WB':0, 'WX':0}    #Stores probabilities at each level
##print 'Matrices loaded and calculation initialized...'
###PMats = CalcMultinomialChoice(Utils)  
##runNested()
##print 'Calculation completed.'
##print 'Time taken(secs): ', time.time()-start   
    
    