// pmmnet.i
// Templates for SNAP TMMNet
//

%extend TMMNet {
        TModeNetI BegModeNetI() {
          return TModeNetI($self->BegModeNetI());
        }
        TModeNetI EndModeNetI() {
          return TModeNetI($self->EndModeNetI());
        }
        TModeNetI GetModeNetI(const int &NId) {
          return TModeNetI($self->GetModeNetI(NId));
        }

  
        TCrossNetI BegCrossNetI() {
          return TCrossNetI ($self->BegCrossNetI());
        }
        TCrossNetI EndCrossNetI() {
          return TCrossNetI ($self->EndCrossNetI());
        }
        TCrossNetI GetCrossNetI(const int &CId) {
          return TCrossNetI ($self->GetCrossNetI(CId));
        }
  
};



// Basic TMMNets
%template(PMMNet) TPt< TMMNet >;