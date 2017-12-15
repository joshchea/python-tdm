#----------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Name:        MatEstimateGradient
# Purpose:     OD-matrix estimation with least squares formulation, solution method is with gradient method. See Spiess 1990
#              **All input vectors are expected to be numpy arrays, some data exchange steps use methods from Visum for which this 
#              script was prototyped. User should replace that with appropriately.  
#               
# Author:      Chetan Joshi, Portland OR
# Dependencies:numpy [http://www.numpy.org], scipy [https://www.scipy.org/], time 
# Created:     12/14/2017
#              
# Copyright:   (c) Chetan Joshi 2017
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
import numpy as np
import scipy.sparse
import VisumPy.helpers as VPH
import csv
import time
#Least squares matrix estimation with gradient method - Chetan Joshi, Klaus Noekel 

#------------User input -----------------------------------------------------------------#
matno = 41            # seed mat and also where result is stored
countAttrID = "AddVal1" 
wtAttrID = "AddVal2"
wtOD = 42
flowmatfile = r"C:\Projects\KA_Work\LSODME\FlowMatrix.mtx"
#----------------------------------------------------------------------------------------#

#Matrix estimation function: takes flow prportion matrix, OD seed, Count and returns adjusted matrix: Chetan Joshi, updated by Klaus Noekel
def EstimateMatrix(FlowProp, FlowPropT, OD_Flows, Ca, Wt, iter=25):
    #Va = numpy.sum(OD_Flows[:,numpy.newaxis] * FlowProp, axis=0)
    #Wt[Wt < 1] = 1
    Va = FlowPropT.dot(OD_Flows)
    Visum.WriteToTrace('Length of Va' + str(len(Va)))
    Visum.WriteToTrace('Length of Ca' + str(len(Ca)))
    Z = sum((Va-Ca)**2)
    Visum.WriteToTrace('Starting Z =' + str(Z))
    #print 'Starting Z =', Z

    for i in range(1, iter):
        t1 = time.time()
#        Grad = numpy.sum(FlowProp*(Va - Ca), axis=1) # sum over a in A
        Grad = FlowProp.dot((Va - Ca)*Wt) 
#        Va_prime = numpy.sum( -OD_Flows[:,numpy.newaxis] * Grad[:,numpy.newaxis] * FlowProp, axis=0)
        Va_prime = FlowPropT.dot(-OD_Flows * Grad)
        lambda_opt = sum((Ca - Va)*Va_prime)/sum(Va_prime*Va_prime) 
        if Grad.max()> 0:
            lambda_opt = min(lambda_opt, 1/Grad.max())
        OD_Flows = OD_Flows*(1 - lambda_opt*Grad) #variant - 1.1
        OD_Flows[OD_Flows<0]=0 #remove very small -0.0 values from matrix if any...
        Va = FlowPropT.dot(OD_Flows)
        Z = sum((Va-Ca)**2)
        t2 = time.time()
        if  Z < 1:
            break;
        else:
            Visum.WriteToTrace(str(i) + ': Z =' + str(Z), True)
            #Visum.WriteToTrace( 'Z =', Z, ' time = ', t2-t1

    Visum.WriteToTrace('Final Z =' + str(Z), True)
    #print 'Final Z =', Z
    return OD_Flows

def readFlowMat(nODs, nLinks, filename):
    t1 = time.time()
    with open(filename, "rb") as f:
        reader = csv.reader(f, delimiter='\t')
        for i in xrange(0, 12):
            reader.next()
        i = []
        j = []
        data = []
        for row in reader: #each row = CountIndex \t ODIndex \t proportion
            if row[0] == "": continue
            if row[0].startswith("*"): continue
            if row[0].startswith("0"): continue
            i.append(long(row[1])-1)
            j.append(long(row[0])-1)
            data.append(float(row[2]))        
    
    ix = j[-1] + 1
    z = max(i)
    for k in xrange(len(Sparse_OD)):
        # j-> link
        i.append(long(k)) #index of od pair
        j.append(long(ix))#index of link
        data.append(1.0)
        ix+=1
        
    FlowProp = scipy.sparse.csr_matrix((data, (i,j)), shape=(len(Sparse_OD), nLinks+nODs), dtype='d')
    #Visum.WriteToTrace([[k, z, i[-1],j[-1]], [len(i), len(j)]])
    t2 = time.time()
    Visum.WriteToTrace("read flow mat: " + str(t2-t1) , True)

    return FlowProp

#--------------------------------------------------------------------------------------------------------
Ca = np.array(VPH.GetMulti(Visum.Net.Links, countAttrID, True))
Wt = np.array(VPH.GetMulti(Visum.Net.Links, wtAttrID, True))
AssignedOD = VPH.GetMatrixRaw(Visum, matno).flatten() #Get the flattened seed matrix
WeightOD = VPH.GetMatrixRaw(Visum, wtOD).flatten()   #Get the flattened weight matrix
SparseWeightOD = WeightOD.compress(AssignedOD > 0).copy()
Sparse_OD = AssignedOD.compress(AssignedOD > 0).copy() #Get only cells > 0 to reduce array size
nLinks = Visum.Net.Links.CountActive # Get the number of active links based on filter - will be extended to turns if turns are used
#OD_constraint_block = numpy.identity(len(Sparse_OD)) 
Ca = np.append(Ca, Sparse_OD) #Extend the count array  to include delta with the existing OD matrix on the least squares formulation             
#Wt = np.append(Wt, np.ones(len(Sparse_OD))) #Extend the weight array for weight matrix using default of 1.0, should be changed to
Wt = np.append(Wt, SparseWeightOD) #Extend the weight array for weight matrix using default of 1.0, weight matrix values should be varied for testing 

FlowProp = readFlowMat(len(Sparse_OD), nLinks, flowmatfile)
FlowPropT = scipy.sparse.csc_matrix(FlowProp.T)

Visum.WriteToTrace(FlowPropT.shape)
Visum.WriteToTrace(FlowProp.shape)

NewODFlows = EstimateMatrix(FlowProp, FlowPropT, Sparse_OD, Ca, Wt, iter=25)

#Set back result to Visum...
AssignedOD[AssignedOD>0] = NewODFlows
nZones = Visum.Net.Zones.Count
VPH.SetMatrixRaw(Visum, matno, AssignedOD.reshape((nZones,nZones)))
Visum.WriteToTrace("results stored" , True)
del FlowProp
del FlowPropT
