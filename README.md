# python-tdm
Python modules for typical travel demand modeling calculations
<p class=MsoNormal>Contributors: Chetan Joshi, Portland OR</p>

<p class=MsoNormal>Requires: Python with standard modules and numpy</p>

<p class=MsoNormal>Tested With: Data from DVRPC and Waterloo demand models</p>

<p class=MsoNormal>License: The MIT License (MIT)</p>

<p class=MsoNormal>License URI: https://opensource.org/licenses/MIT</p>

<p class=MsoNormal>Description: These are some python scripts that can be used
as modules for performing typicaly calculations in a travel demand model. The
expected usage is to put the py file in the site packages or other directory
and then to use the import command in python to load the functions in the
modules. The documentation for usage of each of the functions is shown in the
python scripts and it should also show up in the help as you type the function.</p>

<p class=MsoNormal>Distribution functions:</p>

<p class=MsoNormal>a) CalcFratar : Calculates a Fratar/IPF on a seed matrix
given row and column (P and A) totals</p>

<p class=MsoNormal>b) CalcSinglyConstrained : Calculates a singly constrained
trip distribution for given P/A vectors and a friction factor matrix</p>

<p class=MsoNormal>c) CalcDoublyConstrained : Calculates a doubly constrained
trip distribution for given P/A vectors and a friction factor matrix (P and A
should be balanced before usage, if not then A is scaled to P)</p>

<p class=MsoNormal>d) CalcMultiFratar : Applies fratar model to given set of
trip matrices with multiple target production vectors and one attraction vector</p>

<p class=MsoNormal>e) CalcMultiDistribute : Applies gravity model to a given
set of friction matrices with multiple production vectors and one target
attraction vector</p>

<p class=MsoNormal>Choice functions:</p>

<p class=MsoNormal>a) CalcMultinomialChoice : Calculates a multinomial choice
model probability given a dictionary of mode utilities </p>

<p class=MsoNormal>b) CalcPivotPoint : Calculates pivot point choice
probability given base utilities, current utilities and base proabilities</p>

<p class=MsoNormal>c) CalcNestedChoice : Calculates n-level nested mode choice
probabilities given dictionary with tree definition, matrix references and
number of zones</p>

<p class=MsoNormal>d) CalcNestedChoiceFlat : Calculate nested choice on
flat array so it can be used for stuff like microsim ABM etc. usage is same as c) 
but inputs are flat arrays instead of square matrices and length of vector/s instead of 
number of zones</p>

<p class=MsoNormal>Have fun!</p>

