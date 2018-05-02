#this script replicates the balmprod.mac macro in EMME2, multiple productions are balanced against one attraction with their 
#own friction factor matrices. [Chetan Joshi, Portland OR October 2010]
import numpy
import VisumPy.helpers as h

Skim = h.GetMatrixRaw(Visum,3) #Specify 1st friction matrix
Prod1 = numpy.array(Visum.Net.Zones.GetMultiAttValues("Production(DestinationChoiceEst)"))[:,1]  #First production demand strata/vector
Attr =  numpy.array(Visum.Net.Zones.GetMultiAttValues("Attraction(DestinationChoiceEst)"))[:,1]   #Attraction demand strata/vector 
Trips1 = numpy.zeros((len(Prod1),len(Prod1)))

ProdA = Prod1
AttrA = Attr
alpha = 2
adjC = -0.01
TargetAvgTripLen = 10.5

fricMat1 = numpy.exp(adjC*Skim)
for Iter in range(0,50):
    
    for i in range(0,len(Prod1)):
        Trips1[i,:] = ProdA[i]*AttrA*fricMat1[i,:]/max(0.000001, sum(AttrA * fricMat1[i, :]))

    ComputedProductions = Trips1.sum(1)
    ComputedProductions[ComputedProductions==0]=1
    OrigFac = (Prod1/ComputedProductions)
    ProdA = OrigFac*ProdA

    ComputedAttractions = Trips1.sum(0) 
    ComputedAttractions[ComputedAttractions==0]=1
    DestFac = (Attr/ComputedAttractions)
    AttrA = DestFac*AttrA

    ComputedTripLen = (Trips1*Skim).sum()/ Trips1.sum()
    adjC = adjC*(ComputedTripLen / TargetAvgTripLen)**alpha
    fricMat1 = numpy.exp(adjC*Skim)
    if abs(ComputedTripLen - TargetAvgTripLen) <= 0.01:
        break;
    else:
        Visum.WriteToTrace('Coefficient: '+str(adjC))
        Visum.WriteToTrace('Average Trip Length: '+str(ComputedTripLen))

Visum.WriteToTrace('Average Trip Length: '+str(ComputedTripLen))
Visum.WriteToTrace('Coefficient: '+str(adjC))
h.SetMatrixRaw(Visum,2011,Trips1)   #Key numbers of matrices where results will be stored in VISUM




            
        
    
