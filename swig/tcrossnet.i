// tcrossnet.i
// Templates for SNAP TCrossNet, PNEANet
//

%extend TCrossNet {
        TCrossNetEdgeI BegEI() {
          return TCrossNetEdgeI($self->BegEI());
        }
        TCrossNetEdgeI EndEI() {
          return TCrossNetEdgeI($self->EndEI());
        }
  
        TCrossNetAIntI BegNAIntI(const TStr& attr) {
          return TCrossNetAIntI($self->BegNAIntI(attr));
        }
        TCrossNetAIntI EndNAIntI(const TStr& attr) {
          return TCrossNetAIntI($self->EndNAIntI(attr));
        }
  
        TCrossNetAStrI BegNAStrI(const TStr& attr) {
          return TCrossNetAStrI($self->BegNAStrI(attr));
        }
        TCrossNetAStrI EndNAStrI(const TStr& attr) {
          return TCrossNetAStrI($self->EndNAStrI(attr));
        }
  
        TCrossNetAFltI BegNAFltI(const TStr& attr) {
          return TCrossNetAFltI($self->BegNAFltI(attr));
        }
        TCrossNetAFltI EndNAFltI(const TStr& attr) {
          return TCrossNetAFltI($self->EndNAFltI(attr));
        }
  
        TCrossNetAIntI BegEAIntI(const TStr& attr) {
          return TCrossNetAIntI($self->BegEAIntI(attr));
        }
        TCrossNetAIntI EndEAIntI(const TStr& attr) {
          return TCrossNetAIntI($self->EndEAIntI(attr));
        }
        
        TCrossNetAStrI BegEAStrI(const TStr& attr) {
          return TCrossNetAStrI($self->BegEAStrI(attr));
        }
        TCrossNetAStrI EndEAStrI(const TStr& attr) {
          return TCrossNetAStrI($self->EndEAStrI(attr));
        }
        
        TCrossNetAFltI BegEAFltI(const TStr& attr) {
          return TCrossNetAFltI($self->BegEAFltI(attr));
        }
        TCrossNetAFltI EndEAFltI(const TStr& attr) {
          return TCrossNetAFltI($self->EndEAFltI(attr));
        }
  
};

