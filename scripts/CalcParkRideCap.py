#-------------------------------------------------------------------------------
# Name:        Capacity constrained park and ride with logit choice
# Purpose:     Computes park and ride lot choice between OD pairs using a logit choice model and
#              using capacity constraint defined on a Zone attribute vector | change references to Visum as needed
# Author:      Chetan Joshi, Portland OR
#
# Created:     5/6/2015
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
#-------------------------------------------------------------------------------

import numpy
import VisumPy.helpers as h #only needed to pull matrices from Visum... 
import time
start = time.time()

def ComputeRouteMats(ImpPrT, ImpPuT, Zk, Pk, MainTrips, result1, result2, numiter):
    ImpPrT = ImpPrT.compress(Zk, 1)  #Compress i -> k impedance
    ImpPuT = ImpPuT.compress(Zk, 1)  #Compress k -> j impedance
    OTrips = MainTrips.sum(1)
    Ck = Pk.copy()
    Pk[:] = 1.0
    for iter in xrange(0, numiter):        
        Leg1 = numpy.zeros((len(Zk), len(Pk)))
        Leg2 = numpy.zeros((len(Pk), len(Zk)))
        for i in xrange(0, len(Zk)):
            if OTrips[i] > 0:
                Uikj = Pk * ImpPrT[i,:] * ImpPuT
                Uij = Uikj.sum(1)
                Pikj = Uikj.transpose() / Uij
                Tikj = MainTrips[i,:] * Pikj
                Leg1[i,:]+=Tikj.sum(1)
                Leg2+=Tikj  #--> this need not be computed till last iteration but is done for some testing 
        Ak = Leg1.sum(0)/Ck
        #Ak[Ak < 1] = 1
        Pk = Pk/Ak  #--> update lot attractivity ratios, there is another alternative to this, cap Ak to min 1, would be interesting to know its effect  perhaps for choice of pnr lot
        Visum.WriteToTrace('Finished iteration: '+str(iter+1))
    ExpandedLeg1 = numpy.zeros((len(Zk), len(Zk)))
    ExpandedLeg2 = numpy.zeros((len(Zk), len(Zk)))
    cnt = 0
    for k in range(0, len(Zk)):
        if Zk[k] > 0:
            ExpandedLeg1[:,k] = Leg1[:,cnt]
            ExpandedLeg2[k,:] = Leg2[cnt,:]
            cnt+=1
    if result1 <> 0:
        h.SetMatrixRaw(Visum, result1, ExpandedLeg1)  #instead of doing this ... the matrices can simply be returned 
    if result2 <> 0:
        h.SetMatrixRaw(Visum, result2, ExpandedLeg2)  #instead of doing this ... the matrices can simply be returned 
    del Leg1, Leg2, ExpandedLeg1, ExpandedLeg2
    
Visum.WriteToTrace('Started PnR calculation...')
#------------------------USAGE---------------------------------------------------------------------------------------#  
# note the references to Visum and change as needed... 
a = -0.1                   #Change this disutility coefficient as needed
w = 0.1                    #Change the weight as needed, hint: higher weight -> driving further out but less out of line, lower weight -> driving to closer lot, possibly a bit out of line
aumat = 210                #Auto impedance matrix no
trmat = 490                #Transit impedance matrix no
prmat = 2150               #Park and ride OD matrix -> i,j
prcap = "ParkCAP_Transit"  #Park ride capacity attribute name at the zone level
auleg = 2152               #Resulting auto trip leg matrix no
trleg = 2151               #Resulting transit trip leg matrix no
maxiter  = 1               #Number of iterations for balancing cap restraint - 1 = no capacity constraint, > 1 = capacity constraint with shadow pricing


ImpPrT = numpy.exp(a*h.GetMatrixRaw(Visum, aumat)) #input matix for auto leg impedance 
ImpPuT = numpy.exp(a*w*h.GetMatrixRaw(Visum, trmat).transpose()) #input matrix for transit leg impedance 
MainTrips = h.GetMatrixRaw(Visum, prmat)
Zk = numpy.array(Visum.Net.Zones.GetMultiAttValues(prcap, False))[:,1]  #vector of zones - 1 = has pnr lot, 0 = no pnr lot
Ck = numpy.array(Visum.Net.Zones.GetMultiAttValues(prcap, False))[:,1]  #parkride lot capacity vector 
Zk[Zk>0]=1 #vector of zones - 1 = has pnr lot, 0 = no pnr lot
Pk = Ck.compress(Zk) #only zones with pnr lots are kept 
ComputeRouteMats(ImpPrT, ImpPuT, Zk, Pk, MainTrips, auleg, trleg, maxiter) #call the function for pnr capacity 
Visum.WriteToTrace('Time taken: '+str(time.time()-start)+' secs')
#----------------------END OF USER INPUTS---------------------------------------------------------------------------#
    
