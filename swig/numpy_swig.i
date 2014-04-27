%{
    #define SWIG_FILE_WITH_INIT
    #include "numpy.h"
%}

%include "numpy.i"

%init %{
    import_array();
%}

%apply (int* ARGOUT_ARRAY1, int DIM1) {(int* IntNumpyVec, int n)}
%apply (float* ARGOUT_ARRAY1, int DIM1) {(float* FltNumpyVec, int n)}
%include "numpy.h"
