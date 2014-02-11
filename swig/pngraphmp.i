// pngraph.i
// Templates for SNAP TNGraphMP, PNGraphMP

%extend TNGraphMP {
        TNGraphMPNodeI BegNI() {
                return TNGraphMPNodeI($self->BegNI());
        }
        TNGraphMPNodeI EndNI() {
                return TNGraphMPNodeI($self->EndNI());
        }
        TNGraphMPNodeI GetNI(const int &NId) {
                return TNGraphMPNodeI($self->GetNI(NId));
        }
        TNGraphMPEdgeI BegEI() {
                return TNGraphMPEdgeI($self->BegEI());
        }
        TNGraphMPEdgeI EndEI() {
                return TNGraphMPEdgeI($self->EndEI());
        }
};

%pythoncode %{
# redefine TNGraphMPEdgeI.GetId to return a pair of nodes rather than -1
def GetId(self):
    return (self.GetSrcNId(), self.GetDstNId())

TNGraphMPEdgeI.GetId = GetId
%}


// Basic Undirected Graphs

%template(PrintGraphStatTable_PNGraphMP) PrintGraphStatTable<PNGraphMP>;

//%template(MxSccSz_PNGraphMP) TSnap::GetMxScc<PNGraphMP>;
//%template(MxWccSz_PNGraphMP) TSnap::GetMxWccSz<PNGraphMP>;
// End Basic Directed Graphs

// Basic PNGraphMPs
%template(PNGraphMP) TPt< TNGraphMP >;
