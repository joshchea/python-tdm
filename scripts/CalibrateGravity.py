#-------------------------------------------------------------------------------
# Name:        Calibrate gravity model
# Purpose:     Calibrates the coefficient for the gravity model with -ve exp friction factor
#              given an average trip length, skim and P/A vectors
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
import numpy as np

def CalibrateSinglyConstrained(P, A, avg_trip_len, skim, c = -0.1, alpha = 2, max_iter = 10):
    ProdA = P
    AttrA = A
    num_zones = len(P)
    trips = np.zeros((num_zones, num_zones))
    fric_mat = np.exp(c*skim)

    for Iter in range(0, max_iter):
        for i in range(0, num_zones):
            trips[i,:] = ProdA[i]*AttrA*fric_mat[i,:]/np.maximum(0.000001, np.sum(AttrA * fric_mat[i,:]))

        model_trip_len = (trips*skim).sum() / trips.sum()
        c = c*(model_trip_len / avg_trip_len)**alpha
        fric_mat = np.exp(c*skim)

        print ('iteration: ', Iter, ' coefficient: ', c, ' average trip length (model): ', model_trip_len)

    print ('target average trip length (observed): ', avg_trip_len)
    print ('final average trip length (model): ', model_trip_len)
    print ('final logit scaling factor: ', c)
    return trips   #returns final trip matrix corresponding to calibrated coefficient
