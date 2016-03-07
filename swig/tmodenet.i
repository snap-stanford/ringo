// pneanet.i
// Templates for SNAP TModeNet, PNEANet
//

/*
  Instantiates templates from SNAP for inclusion in RINGO.
  Note in Vim, this replaces SNAP Template headers:
 
 :%s#^template.*<class PGraph> \S* \([^(]*\).*#%template(\1) TSnap::\1<PNEANet>;#gc
 :%s#^///.*\n:##g
*/

%extend TModeNet {
        TModeNetNodeI BegMMNI() {
          return TModeNetNodeI($self->BegMMNI());
        }
        TModeNetNodeI EndMMNI() {
          return TModeNetNodeI($self->EndMMNI());
        }
        TModeNetNodeI GetMMNI(const int &NId) {
          return TModeNetNodeI($self->GetMMNI(NId));
        }

  
        TModeNetEdgeI BegEI() {
          return TModeNetEdgeI($self->BegEI());
        }
        TModeNetEdgeI EndEI() {
          return TModeNetEdgeI($self->EndEI());
        }
  
/*        TModeNetAIntI BegNAIntI(const TStr& attr) {
          return TModeNetAIntI($self->BegNAIntI(attr));
        }
        TModeNetAIntI EndNAIntI(const TStr& attr) {
          return TModeNetAIntI($self->EndNAIntI(attr));
        }
  
        TModeNetAStrI BegNAStrI(const TStr& attr) {
          return TModeNetAStrI($self->BegNAStrI(attr));
        }
        TModeNetAStrI EndNAStrI(const TStr& attr) {
          return TModeNetAStrI($self->EndNAStrI(attr));
        }
  
        TModeNetAFltI BegNAFltI(const TStr& attr) {
          return TModeNetAFltI($self->BegNAFltI(attr));
        }
        TModeNetAFltI EndNAFltI(const TStr& attr) {
          return TModeNetAFltI($self->EndNAFltI(attr));
        }
  
        TModeNetAIntI BegEAIntI(const TStr& attr) {
          return TModeNetAIntI($self->BegEAIntI(attr));
        }
        TModeNetAIntI EndEAIntI(const TStr& attr) {
          return TModeNetAIntI($self->EndEAIntI(attr));
        }
        
        TModeNetAStrI BegEAStrI(const TStr& attr) {
          return TModeNetAStrI($self->BegEAStrI(attr));
        }
        TModeNetAStrI EndEAStrI(const TStr& attr) {
          return TModeNetAStrI($self->EndEAStrI(attr));
        }
        
        TModeNetAFltI BegEAFltI(const TStr& attr) {
          return TModeNetAFltI($self->BegEAFltI(attr));
        }
        TModeNetAFltI EndEAFltI(const TStr& attr) {
          return TModeNetAFltI($self->EndEAFltI(attr));
        }
  */
};
