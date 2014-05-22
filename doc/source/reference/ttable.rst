Tables
`````````````````````````

A Table in SNAP is represented by the class :class:`TTable`.

TTable
========

.. class:: TTable()

.. class::            TTable(TTableContext& Context)
.. class::            TTable(const TStr& TableName, const Schema& S, TTableContext& Context)
.. class::            TTable(TSIn& SIn, TTableContext& Context)
.. class::            TTable(const TStr& TableName, const THash<TInt,TInt>& H, const TStr& Col1, const TStr& Col2, TTableContext& Context, const TBool IsStrKeys = false)
.. class::            TTable(const TStr& TableName, const THash<TInt,TFlt>& H, const TStr& Col1, const TStr& Col2, TTableContext& Context, const TBool IsStrKeys = false)

.. class::            TTable(const TTable& Table, const TIntV& RowIds)
.. class::            TTable(const TTable& Table)

*********************************************************************

Below is a list of functions supported by the :class:`TTable` class:

.. function:: AddDstNodeAttr(Attr)

Adds column to be used as the destination node attribute of the graph.

Parameters:

- *Attr*: Snap.TStr (input)

  Destination node attribute

Return value:

- None

*********************************************************************

.. function:: AddDstNodeAttr(Attrs)

Adds columns to be used as destination node attributes of the graph.

Parameters:

- *Attrs*: Snap.TStrV (input)

  Destination node attribute vector

Return value:

- None

*********************************************************************

.. function:: AddEdgeAttr(Attr)

Adds column to be used as graph edge attribute.

Parameters:

- *Attr*: Snap.TStr (input)

  Graph edge attribute

Return value:

- None

*********************************************************************

.. function:: AddEdgeAttr(Attrs)

Adds columns to be used as graph edge attributes.

Parameters:

- *Attrs*: Snap.TStrV (input)

  Graph edge attribute vector

Return value:

- None

*********************************************************************

.. function:: AddNodeAttr(Attr)

Handles the common case where source and destination both belong 
to the same "universe" of entities.

Parameters:

- *Attr*: Snap.TStr (input)

  Node attribute (both source and destination)

Return value:

- None

*********************************************************************

.. function:: AddNodeAttr(Attrs)

Handles the common case where source and destination both belong 
to the same "universe" of entities.

Parameters:

- *Attrs*: Snap.TStrV (input)

  Node attribute vector (both source and destination)

Return value:

- None

*********************************************************************

.. function:: AddSrcNodeAttr(Attr)

Adds column to be used as the source node attribute of the graph.

Parameters:

- *Attr*: Snap.TStr (input)

  Source node attribute

Return value:

- None

*********************************************************************

.. function:: AddSrcNodeAttr(Attrs)

Adds columns to be used as source node attributes of the graph.

Parameters:

- *Attrs*: Snap.TStrV (input)

  Source node attribute vector

Return value:

- None

*********************************************************************

.. function:: Aggregate(GroupByAttrs, AggOp, ValAttr, ResAttr, Ordered)

Aggregates values over one attribute after grouping with respect to a list
of attributes. Results are stored in a new attribute.

Parameters:

- *GroupByAttrs*: Snap.TStrV (input)

  Attribute vector grouping performed with respect to

- *AggOp*: Aggregation operator (input)

  Must be one of the following:

  * snap.aaSum - Sum of elements in the group
  * snap.aaCount - Number of elements in the group
  * snap.aaMin - Minimum element in the group
  * snap.aaMax - Maximum element in the group
  * snap.aaFirst - First element in the group
  * snap.aaLast - Last element in the group
  * snap.aaMean - Mean of the group
  * snap.aaMedian - Median of the group

  Note: Count is the only aggregation that can be performed over string 
  columns.

- *ValAttr*: Snap.TStr (input)

  Attribute aggregation is performed over.

  Note: This is ignored when *AggOp* is snap.aaCount

- *ResAttr*: Snap.TStr (input)

  Result attribute

- *Ordered*: Snap.TBool (input) [default: true]

  Flag specifying whether to treat grouping key as ordered 
  (true) or unordered.

Return value:

- None

*********************************************************************

.. function:: AggregateCols(AggrAttrs, AggOp, ResAttr)

For each row in the table, aggregates values over a list of attributes. 
Results are stored in a new attribute.

Parameters:

- *AggrAttrs*: Snap.TStrV (input)

  Vector of attributes aggregation is performed over for each row

- *AggOp*: Aggregation operator (input)

  Must be one of the following:

  * snap.aaSum - Sum of elements in the group
  * snap.aaCount - Number of elements in the group
  * snap.aaMin - Minimum element in the group
  * snap.aaMax - Maximum element in the group
  * snap.aaFirst - First element in the group
  * snap.aaLast - Last element in the group
  * snap.aaMean - Mean of the group
  * snap.aaMedian - Median of the group

  Note: This function only works for Int and Float columns.

- *ResAttr*: Snap.TStr (input)

  Result attribute

Return value:

- None

*********************************************************************

.. function:: BegRI()

To Be Documented

*********************************************************************

.. function:: BegRIWR()

To Be Documented

*********************************************************************

.. function:: Classify()
.. function:: ClassifyAtomic()

To Be Documented

*********************************************************************

.. function:: ColAdd(Attr1, Attr2, ResAttr)
.. function:: ColAdd(Attr1, Table, Attr2, ResAttr, AddToFirstTable)
.. function:: ColAdd(Attr1, Value, ResAttr, FloatCast)

Performs the operation Attr1 + Attr2, where Attr1 and Attr2 are 
attributes which can belong to the same or different tables. 

Could also perform Attr1 + Value, depending on the function 
prototype.

The result is stored in a new attribute.

**NOTE**: This operation does not work on String columns.

Parameters:

- *Attr1*: Snap.TStr (input)

  First operand, specifies an attribute in the table corresponding 
  to the caller.

- *Attr2*: Snap.TStr (input)

  Second operand, could specify either an attribute in the table 
  corresponding to the caller or in table *Table*, depending on 
  the function prototype.

- *Table*: Snap.TTable (input)

  Table object *Attr2* is to be looked up from.

- *ResAttr*: Snap.TStr (input) [default: ""]

  Name of result attribute. A new column with this name is 
  created to store the result. If *ResAttr* = "", the result is 
  stored instead in the column corresponding to *Attr1*, unless
  *AddToFirstTable* is passed and is false, in which case the
  column corresponding to *Attr2* is used.

- *AddToFirstTable*: Snap.TBool (input) [default: true]

  Flag specifying whether to add *ResAttr* to the table 
  corresponding to the caller (true), or to the table *Table*.

- *Value*: Snap.Flt (input)

  Second operand, for the third function prototype.

- *FloatCast*: Snap.TBool (input) [default: false]

  Casts values in Int columns to Flt values if this flag is
  true.

Return value:

- None

*********************************************************************

.. function:: ColConcat(Attr1, Attr2, Separator, ResAttr)
.. function:: ColConcat(Attr1, Table, Attr2, Separator, ResAttr, AddToFirstTable)

Concatenates two columns, separated by *Separator*. 

Result is stored in a new column.

**NOTE**: This operation only works on String columns.

Parameters:

- *Attr1*: Snap.TStr (input)

  Attribute corresponding to the first column.

- *Attr2*: Snap.TStr (input)

  Attribute corresponding to the second column. Specifies either 
  an attribute in the table corresponding to the caller or in 
  table *Table*, depending on the function prototype.

- *Table*: Snap.TTable (input)

  Table object *Attr2* is to be looked up from.

- *ResAttr*: Snap.TStr (input) [default: ""]

  Name of result attribute. A new column with this name is 
  created to store the result. If *ResAttr* = "", the result is 
  stored instead in the column corresponding to *Attr1*, unless
  *AddToFirstTable* is passed and is false, in which case the
  column corresponding to *Attr2* is used.

- *Separator*: Snap.TStr (input) [default: ""]
  
  Separator string.

- *AddToFirstTable*: Snap.TBool (input) [default: true]

  Flag specifying whether to add *ResAttr* to the table 
  corresponding to the caller (true), or to the table *Table*.

*********************************************************************

.. function:: ColConcatConst(Attr, Value, Separator, ResAttr)

Concatenates column values with the given string value, separated 
by *Separator*. 

Result is stored in a new column.

**NOTE**: This operation only works on String columns.

Parameters:

- *Attr*: Snap.TStr (input)

  Attribute corresponding to a column.

- *Value*: Snap.TStr (input)
  
  String each column value is to be concatenated with.

- *ResAttr*: Snap.TStr (input) [default: ""]

  Name of result attribute. A new column with this name is 
  created to store the result. If *ResAttr* = "", the result is 
  stored instead in the column corresponding to *Attr*.

- *Separator*: Snap.TStr (input) [default: ""]
  
  Separator string.

*********************************************************************

.. function:: ColDiv(Attr1, Attr2, ResAttr)
.. function:: ColDiv(Attr1, Table, Attr2, ResAttr, AddToFirstTable)
.. function:: ColDiv(Attr1, Value, ResAttr, FloatCast)

Performs the operation Attr1 / Attr2, where Attr1 and Attr2 are 
attributes which can belong to the same or different tables. 

Could also perform Attr1 / Value, depending on the function 
prototype.

The result is stored in a new attribute.

**NOTE**: This operation does not work on String columns.

Parameters:

- *Attr1*: Snap.TStr (input)

  First operand, specifies an attribute in the table corresponding 
  to the caller.

- *Attr2*: Snap.TStr (input)

  Second operand, could specify either an attribute in the table 
  corresponding to the caller or in table *Table*, depending on 
  the function prototype.

- *Table*: Snap.TTable (input)

  Table object *Attr2* is to be looked up from.

- *ResAttr*: Snap.TStr (input) [default: ""]

  Name of result attribute. A new column with this name is 
  created to store the result. If *ResAttr* = "", the result is 
  stored instead in the column corresponding to *Attr1*, unless
  *AddToFirstTable* is passed and is false, in which case the
  column corresponding to *Attr2* is used.

- *AddToFirstTable*: Snap.TBool (input) [default: true]

  Flag specifying whether to add *ResAttr* to the table 
  corresponding to the caller (true), or to the table *Table*.

- *Value*: Snap.Flt (input)

  Second operand, for the third function prototype.

- *FloatCast*: Snap.TBool (input) [default: false]

  Casts values in Int columns to Flt values if this flag is
  true.

Return value:

- None

*********************************************************************

.. function:: ColGenericOp

REMOVE ?

*********************************************************************

.. function:: ColMax(Attr1, Attr2, ResAttr)

Performs the operation MAX (Attr1, Attr2), where Attr1 and Attr2 
are attributes in a table.

The result is stored in a new attribute.

**NOTE**: This operation does not work on String columns.

Parameters:

- *Attr1*: Snap.TStr (input)

  First operand, specifies an attribute in the table.

- *Attr2*: Snap.TStr (input)

  Second operand, specifies an attribute in the table.

- *ResAttr*: Snap.TStr (input) [default: ""]

  Name of result attribute. A new column with this name is 
  created to store the result. If *ResAttr* = "", the result is 
  stored instead in the column corresponding to *Attr1*.

Return value:

- None

*********************************************************************

.. function:: ColMin(Attr1, Attr2, ResAttr)

Performs the operation MIN (Attr1, Attr2), where Attr1 and Attr2 
are attributes in a table.

The result is stored in a new attribute.

**NOTE**: This operation does not work on String columns.

Parameters:

- *Attr1*: Snap.TStr (input)

  First operand, specifies an attribute in the table.

- *Attr2*: Snap.TStr (input)

  Second operand, specifies an attribute in the table.

- *ResAttr*: Snap.TStr (input) [default: ""]

  Name of result attribute. A new column with this name is 
  created to store the result. If *ResAttr* = "", the result is 
  stored instead in the column corresponding to *Attr1*.

Return value:

- None

*********************************************************************

.. function:: ColMod(Attr1, Attr2, ResAttr)
.. function:: ColMod(Attr1, Table, Attr2, ResAttr, AddToFirstTable)
.. function:: ColMod(Attr1, Value, ResAttr, FloatCast)

Performs the operation Attr1 % Attr2, where Attr1 and Attr2 are 
attributes which can belong to the same or different tables. 

Could also perform Attr1 % Value, depending on the function 
prototype.

The result is stored in a new attribute.

**NOTE**: This operation does not work on String and Float columns.

Parameters:

- *Attr1*: Snap.TStr (input)

  First operand, specifies an attribute in the table corresponding 
  to the caller.

- *Attr2*: Snap.TStr (input)

  Second operand, could specify either an attribute in the table 
  corresponding to the caller or in table *Table*, depending on 
  the function prototype.

- *Table*: Snap.TTable (input)

  Table object *Attr2* is to be looked up from.

- *ResAttr*: Snap.TStr (input) [default: ""]

  Name of result attribute. A new column with this name is 
  created to store the result. If *ResAttr* = "", the result is 
  stored instead in the column corresponding to *Attr1*, unless
  *AddToFirstTable* is passed and is false, in which case the
  column corresponding to *Attr2* is used.

- *AddToFirstTable*: Snap.TBool (input) [default: true]

  Flag specifying whether to add *ResAttr* to the table 
  corresponding to the caller (true), or to the table *Table*.

- *Value*: Snap.Flt (input)

  Second operand, for the third function prototype.

- *FloatCast*: Snap.TBool (input) [default: false]

  Casts values in Int columns to Flt values if this flag is
  true.

Return value:

- None

*********************************************************************

.. function:: ColMul(Attr1, Attr2, ResAttr)
.. function:: ColMul(Attr1, Table, Attr2, ResAttr, AddToFirstTable)
.. function:: ColMul(Attr1, Value, ResAttr, FloatCast)

Performs the operation Attr1 * Attr2, where Attr1 and Attr2 are 
attributes which can belong to the same or different tables. 

Could also perform Attr1 * Value, depending on the function 
prototype.

The result is stored in a new attribute.

**NOTE**: This operation does not work on String columns.

Parameters:

- *Attr1*: Snap.TStr (input)

  First operand, specifies an attribute in the table corresponding 
  to the caller.

- *Attr2*: Snap.TStr (input)

  Second operand, could specify either an attribute in the table 
  corresponding to the caller or in table *Table*, depending on 
  the function prototype.

- *Table*: Snap.TTable (input)

  Table object *Attr2* is to be looked up from.

- *ResAttr*: Snap.TStr (input) [default: ""]

  Name of result attribute. A new column with this name is 
  created to store the result. If *ResAttr* = "", the result is 
  stored instead in the column corresponding to *Attr1*, unless
  *AddToFirstTable* is passed and is false, in which case the
  column corresponding to *Attr2* is used.

- *AddToFirstTable*: Snap.TBool (input) [default: true]

  Flag specifying whether to add *ResAttr* to the table 
  corresponding to the caller (true), or to the table *Table*.

- *Value*: Snap.Flt (input)

  Second operand, for the third function prototype.

- *FloatCast*: Snap.TBool (input) [default: false]

  Casts values in Int columns to Flt values if this flag is
  true.

Return value:

- None

*********************************************************************

.. function:: ColSub(Attr1, Attr2, ResAttr)
.. function:: ColSub(Attr1, Table, Attr2, ResAttr, AddToFirstTable)
.. function:: ColSub(Attr1, Value, ResAttr, FloatCast)

Performs the operation Attr1 - Attr2, where Attr1 and Attr2 are 
attributes which can belong to the same or different tables. 

Could also perform Attr1 - Value, depending on the function 
prototype.

The result is stored in a new attribute.

**NOTE**: This operation does not work on String columns.

Parameters:

- *Attr1*: Snap.TStr (input)

  First operand, specifies an attribute in the table corresponding 
  to the caller.

- *Attr2*: Snap.TStr (input)

  Second operand, could specify either an attribute in the table 
  corresponding to the caller or in table *Table*, depending on 
  the function prototype.

- *Table*: Snap.TTable (input)

  Table object *Attr2* is to be looked up from.

- *ResAttr*: Snap.TStr (input) [default: ""]

  Name of result attribute. A new column with this name is 
  created to store the result. If *ResAttr* = "", the result is 
  stored instead in the column corresponding to *Attr1*, unless
  *AddToFirstTable* is passed and is false, in which case the
  column corresponding to *Attr2* is used.

- *AddToFirstTable*: Snap.TBool (input) [default: true]

  Flag specifying whether to add *ResAttr* to the table 
  corresponding to the caller (true), or to the table *Table*.

- *Value*: Snap.Flt (input)

  Second operand, for the third function prototype.

- *FloatCast*: Snap.TBool (input) [default: false]

  Casts values in Int columns to Flt values if this flag is
  true.

Return value:

- None

*********************************************************************

.. function:: Count(Attr, ResAttr)

For each row of the table, counts number of rows in the table
sharing the same value as it for a given attribute.

Result is stored in a new column.

Parameters:

- *Attr*: Snap.TStr (input)

  Attribute corresponding to a column.

- *ResAttr*: Snap.TStr (input) [default: ""]

  Name of result attribute. A new column with this name is 
  created to store the result.

Return value:

- None

*********************************************************************

.. function:: Defrag()

Releases memory for deleted rows in the table.

Parameters:

- None

Return value:

- None

*********************************************************************

.. function:: EndRI()

To Be Documented

*********************************************************************

.. function:: EndRIWR()

To Be Documented

*********************************************************************

.. function:: GetColType()

To Be Documented

*********************************************************************

.. function:: GetDstCol()

Returns the name of the column representing destination nodes in 
the graph.

Return value:

  - TStr object corresponding to column name

*********************************************************************

.. function:: GetDstNodeFltAttrV()

Returns the Flt columns corresponding to attributes of the 
destination nodes.

Return value:

  - TStrV object corresponding to the attribute name vector

*********************************************************************

.. function:: GetDstNodeIntAttrV()

Returns the Int columns corresponding to attributes of the 
destination nodes.

Return value:

  - TStrV object corresponding to the attribute name vector

*********************************************************************

.. function:: GetDstNodeStrAttrV()

Returns the Str columns corresponding to attributes of the 
destination nodes.

Return value:

  - TStrV object corresponding to the attribute name vector

*********************************************************************

.. function:: GetEdgeFltAttrV()

Returns the Flt columns corresponding to edge attributes.

Return value:

  - TStrV object corresponding to the attribute name vector

*********************************************************************

.. function:: GetEdgeIntAttrV()

Returns the Int columns corresponding to edge attributes.

Return value:

  - TStrV object corresponding to the attribute name vector

*********************************************************************

.. function:: GetEdgeStrAttrV()

Returns the Str columns corresponding to edge attributes.

Return value:

  - TStrV object corresponding to the attribute name vector

*********************************************************************

.. function:: GetEdgeTable(Network, Context)

Extracts edge TTable from PNEANet.

Parameters:

-  *Network*: snap.PNEANet (input)

-  *Context*: snap.TTableContext (input)

Return value:

- snap.PTable object corresponding to edge table

*********************************************************************

.. function:: GetEdgeTablePN()

Extracts edge TTable from PNGraphMP

**NOTE**: Defined only if OpenMP present.

Parameters:

-  *Network*: snap.PNGraphMP (input)

-  *Context*: snap.TTableContext (input)

Return value:

- snap.PTable object corresponding to edge table

*********************************************************************

.. function:: GetFltNodePropertyTable(Network, Property, NodeAttrName, NodeAttrType, PropertyAttrName, Context)

Extracts node and and edge property TTables from a THash.

Parameters:

-  *Network*: snap.PNEANet (input)

-  *Property*: snap.TIntFltH (input)

-  *NodeAttrName*: snap.TStr (input)

-  *NodeAttrType*: snap.TAttrType (input)

-  *PropertyAttrName*: snap.TStr (input)

-  *Context*: snap.TTableContext (input)

Return value:

- snap.PTable object

*********************************************************************

.. function:: GetFltVal(Attr, RowIdx)

Gets the value of float attribute *Attr* at row *RowIdx*.

Parameters:

-  *Attr*: snap.TStr (input)

-  *RowIdx*: snap.TInt (input)

Return value:

- snap.TFlt

*********************************************************************

.. function:: GetFltValAtRowIdx()

To Be Documented

*********************************************************************

.. function:: GetIntVal(Attr, RowIdx)

Gets the value of integer attribute *Attr* at row *RowIdx*.

Parameters:

-  *Attr*: snap.TStr (input)

-  *RowIdx*: snap.TInt (input)

Return value:

- snap.TInt

*********************************************************************

.. function:: GetIntValAtRowIdx()

To Be Documented

*********************************************************************

.. function:: GetMP()

Returns the value of the static variable TTable::UseMP, which 
controls whether to use multi-threading.

TTable::UseMP is 1 by default (meaning algorithms are 
multi-threaded by default if the OpenMP library is present).

Parameters:

- None

Return value:

- snap.TInt

*********************************************************************

.. function:: GetMapHitsIterator()

To Be Documented

*********************************************************************

.. function:: GetMapPageRank(GraphSeq, Context, C, Eps, MaxIter)

Computes a sequence of PageRank tables for a graph sequence. 

Parameters:

- *GraphSeq*: snap.TVec<snap.PNEANet>

  Graph sequence vector

- *Context*: snap.TTableContext

- *C*: double

- *Eps*: double

- *MaxIter*: int

Returns:

- snap.TTableIterator

  Iterator over sequence of PageRank tables.

*********************************************************************

.. function:: GetNodeTable()

Extracts node TTable from PNEANet.

Parameters:

-  *Network*: snap.PNEANet (input)

-  *Context*: snap.TTableContext (input)

Return value:

- snap.PTable object corresponding to node table

*********************************************************************

.. function:: GetNumRows()

Returns total number of rows in the table. Count could include
rows which have been deleted previously.

Parameters:

- None

Return value:

- snap.TInt

*********************************************************************

.. function:: GetNumValidRows()

Returns total number of valid rows in the table.

Parameters:

- None

Return value:

- snap.TInt

*********************************************************************

.. function:: GetSchema()

Returns the schema of the table.

Parameters:

- None

Return value:

- snap.Schema

*********************************************************************

.. function:: GetSrcCol()

Returns the name of the column representing source nodes in 
the graph.

Return value:

  - TStr object corresponding to column name

*********************************************************************

.. function:: GetSrcNodeFltAttrV()

Returns the Flt columns corresponding to attributes of the 
source nodes.

Return value:

  - TStrV object corresponding to the attribute name vector

*********************************************************************

.. function:: GetSrcNodeIntAttrV()

Returns the Int columns corresponding to attributes of the 
source nodes.

Return value:

  - TStrV object corresponding to the attribute name vector

*********************************************************************

.. function:: GetSrcNodeStrAttrV()

Returns the Str columns corresponding to attributes of the 
source nodes.

Return value:

  - TStrV object corresponding to the attribute name vector

*********************************************************************

.. function:: GetStrVal(Attr, RowIdx)

Gets the value of string attribute *Attr* at row *RowIdx*.

Parameters:

-  *Attr*: snap.TStr (input)

-  *RowIdx*: snap.TInt (input)

Return value:

- snap.TStr

*********************************************************************

.. function:: Group(GroupByAttrs, GroupAttrName, Ordered)

Groups rows according to the values of *GroupByAttrs* attributes.

Result is stored in a new column.

Parameters:

-  *GroupByAttrs*: snap.TStrV (input) 

  List of attributes to group by.

-  *GroupAttrName*: snap.TStr (input) 
  
  Result attribute name.

-  *Ordered*: snap.TBool (input) [default: true] 

  Treat grouping key as an ordered pair?

Return value:

- None

*********************************************************************

.. function:: InitIds()

NO NEED?

*********************************************************************

.. function:: Intersection(Table)
.. function:: Intersection(PTable)

Returns a new table containing rows present in the current table
which are also present in *Table* or *PTable*.

Parameters:

-  *Table*: snap.TTable (input)

-  *PTable*: snap.PTable (input)

Return value:

- snap.PTable

  Table representing the intersection.

*********************************************************************

.. function:: IsNextK()

To Be Documented

*********************************************************************

.. function:: Join(Attr1, TTable, Attr2)
.. function:: Join(Attr1, PTable, Attr2)

Performs an equi-join on the current table and another table over
attributes Attr1 and Attr2.

Parameters:

-  *Table*: snap.TTable (input)

-  *PTable*: snap.PTable (input)

-  *Attr1*: snap.TStr (input)

  Attribute corresponding to current table

-  *Attr2*: snap.TStr (input)

  Attribute corresponding to the passed table

Return value:

- snap.PTable

  Joint table.

*********************************************************************

.. function:: Load(SIn, Context)

Loads table from binary.

Parameters:

-  *SIn*: snap.TSIn (input)

  Input stream object

-  *Context*: snap.TTableContext (input)

Return value:

- snap.PTable

*********************************************************************

.. function:: LoadSS(Schema, InFNm, Context, Separator, HasTitleLine)

Loads table from spread sheet (TSV, CSV, etc).

Parameters:

-  *Schema*: snap.Schema (input)

  Table schema

-  *InFNm*: snap.TStr (input)

  Input file name

-  *Context*: snap.TTableContext (input)

-  *Separator*: char (input) [default: '\\t']

  Field separator character in input file

-  *HasTitleLine*: snap.TBool (input) [default: false]

  Does input file start with a title line (names of columns)?

Return value:

- snap.PTable

*********************************************************************

.. function:: Minus(Table)
.. function:: Minus(PTable)

Returns a new table containing rows present in the current table
which are not present in another table.

Parameters:

-  *Table*: snap.TTable (input)

-  *PTable*: snap.PTable (input)

Return value:

- snap.PTable

  Table representing the 'minus'.

*********************************************************************

.. function:: New()

To Be Documented

*********************************************************************

.. function:: NextGraphIterator()

To Be Documented

*********************************************************************

.. function:: Order(OrderByAttrs, ResAttr, ResetRankFlag, Asc)

Orders the rows according to the values in *OrderByAttrs* (in lexicographic order).

Result is stored in a new attribute. Rows are ranked 0, 1, 2, and
so on.

Parameters:

-  *OrderByAttrs*: snap.TStrV (input)

  List of attributes to be ordered by

- *ResAttr*: Snap.TStr (input)

  Result attribute

- *ResetRankFlag*: Snap.TBool (input) [default: false]

- *Asc*: Snap.TBool (input) [default: true]

  Order rows in ascending lexicographic order.

Return value:

- None

*********************************************************************

.. function:: Project(ProjectAttrs)

Returns a table with only the attributes in *ProjectAttrs*.

Parameters:

-  *ProjectAttrs*: snap.TStrV (input)

  List of attributes to be projected into a new table

Return value:

- snap.PTable

*********************************************************************

.. function:: ProjectInPlace(ProjectAttrs)

Modifies the current table to keep only the attributes specified 
in *ProjectAttrs*.

Parameters:

-  *ProjectAttrs*: snap.TStrV (input)

  List of all the attributes to be retained in the current table

Return value:

- None

*********************************************************************

.. function:: ReadFltCol(Attr, Result)

Reads values of an entire float column.

Parameters:

-  *Attr*: snap.TStr (input)

  Name of float column.

-  *Result*: snap.TFltV (output)

  Output vector column values are read into.

Return value:

- None

*********************************************************************

.. function:: ReadIntCol(Attr, Result)

Reads values of an entire int column.

Parameters:

-  *Attr*: snap.TStr (input)

  Name of int column.

-  *Result*: snap.TIntV (output)

  Output vector column values are read into.

Return value:

- None

*********************************************************************

.. function:: ReadStrCol(Attr, Result)

Reads values of an entire string column.

Parameters:

-  *Attr*: snap.TStr (input)

  Name of string column.

-  *Result*: snap.TStrV (output)

  Output vector column values are read into.

Return value:

- None

*********************************************************************

.. function:: Rename()

To Be Documented

*********************************************************************

.. function:: Save(SOut)

Saves table schema and content into an output stream (in binary).

*********************************************************************

.. function:: SaveBin(OutFNm)

Saves table schema and content into a binary file.

Parameters:

-  *OutFNm*: snap.TStr (input)

  Output file name

Return value:

- None

*********************************************************************

.. function:: SaveSS(OutFNm)

Saves table schema and content into a TSV file.

Parameters:

-  *OutFNm*: snap.TStr (input)

  Output file name

Return value:

- None

*********************************************************************

.. function:: Select(Predicate, SelectedRows, Remove)

Selects rows that satisfy a given Predicate.

Parameters:

-  *Predicate*: snap.TPredicate (input)

-  *SelectedRows*: snap.TIntV (output)

  Indices of rows matching the predicate *Predicate*

-  *Remove*: snap.TBool (input) [default: true]

  Remove rows which do not match the given predicate.

Return value:

- None

*********************************************************************

.. function:: SelectAtomic(Attr1, Attr2, Cmp, SelectedRows, Remove)

Selects rows which satisfy an atomic compare operation. 

Parameters:

-  *Attr1*: snap.TStr (input)

-  *Attr2*: snap.TStr (input)

-  *Cmp*: snap.TPredComp (input)

  Atomic compare operator over *Attr1* and *Attr2*

-  *SelectedRows*: snap.TIntV (output)

  Indices of rows satisfying the compare operation.

-  *Remove*: snap.TBool (input) [default: true]

  Remove rows which do not match the given predicate.

Return value:

- None

*********************************************************************

.. function:: SelectAtomicConst()

To Be Documented

*********************************************************************

.. function:: SelectAtomicFltConst(Attr, Val, Cmp, SelectedTable)

Selects rows where the value of a float attribute satisfies an 
atomic comparison with a primitive type.

Parameters:

-  *Attr*: snap.TStr (input)

-  *Val*: snap.TPrimitive (input)

-  *Cmp*: snap.TPredComp (input)

  Atomic compare operator over *Attr* and *Val*

-  *SelectedTable*: snap.PTable (output)

  Table consisting of the selected rows.

Return value:

- None

*********************************************************************

.. function:: SelectAtomicIntConst(Attr, Val, Cmp, SelectedTable)

Selects rows where the value of an integer attribute satisfies an 
atomic comparison with a primitive type.

Parameters:

-  *Attr*: snap.TStr (input)

-  *Val*: snap.TPrimitive (input)

-  *Cmp*: snap.TPredComp (input)

  Atomic compare operator over *Attr* and *Val*

-  *SelectedTable*: snap.PTable (output)

  Table consisting of the selected rows.

Return value:

- None

*********************************************************************

.. function:: SelectAtomicStrConst(Attr, Val, Cmp, SelectedTable)

Selects rows where the value of a string attribute satisfies an 
atomic comparison with a primitive type.

Parameters:

-  *Attr*: snap.TStr (input)

-  *Val*: snap.TPrimitive (input)

-  *Cmp*: snap.TPredComp (input)

  Atomic compare operator over *Attr* and *Val*

-  *SelectedTable*: snap.PTable (output)

  Table consisting of the selected rows.

Return value:

- None

*********************************************************************

.. function:: SelectFirstNRows(N)

Modifies table in place so that it only its first *N* rows are 
retained.

Parameters:

-  *N*: snap.TInt (input)

Return value:

- None

*********************************************************************

.. function:: SelfJoin(Attr)

Performs a self-join on the table on the attribute *Attr*.

Returns a new table.

Parameters:

-  *Attr*: snap.TStr (input)

Return value:

- snap.PTable

  Joint table.

*********************************************************************

.. function:: SelfSimJoin()

To Be Documented

*********************************************************************

.. function:: SelfSimJoinPerGroup()

To Be Documented

*********************************************************************

.. function:: SetCommonNodeAttrs(SrcAttr, DstAttr, CommonAttr)

Sets the columns to be used as both source and destination node 
attributes.

Parameters:

- *SrcAttr*: Snap.TStr (input)

- *DstAttr*: Snap.TStr (input)

- *CommonAttr*: Snap.TStr (input)

Return value:

- None

*********************************************************************

.. function:: SetDstCol(Attr)

Sets the column representing destination nodes in the graph.

Parameters:

- *Attr*: Snap.TStr (input)

  Attribute specifying destination column name.

Return value:

- None

*********************************************************************

.. function:: SetMP(Value)

Sets the value of the static variable TTable::UseMP to Value.

Parameters:

- *Value*: snap.TInt

Return value:

- None

*********************************************************************

.. function:: SetSrcCol(Attr)

Sets the column representing source nodes in the graph.

Parameters:

- *Attr*: Snap.TStr (input)

  Attribute specifying source column name.

Return value:

- None

*********************************************************************

.. function:: SimJoin(Attr1, Table, Attr2, DistColAttr, SimType, Threshold)

Performs join if the distance between two rows is less than the 
specified threshold.

Parameters:

- *Attr1*: Snap.TStr (input)

  Attribute corresponding to current table

- *Table*: snap.TTable (input)

- *Attr2*: Snap.TStr (input)

  Attribute corresponding to passed table

- *DistColAttr*: Snap.TStr (input)

  Attribute representing distance between rows in new table

- *SimType*: Snap.TSimType (input)

  Distance metric

- *Threshold*: Snap.TFlt (input)

Return value:

- snap.PTable

  Joint table.

*********************************************************************

.. function:: SpliceByGroup(GroupByAttrs, Ordered)

Splices table into subtables according to the result of a
grouping statement.

Parameters:

- *GroupByAttrs*: Snap.TStrV (input)

  Attribute vector grouping performed with respect to

- *Ordered*: Snap.TBool (input) [default: true]

  Flag specifying whether to treat grouping key as ordered 
  or unordered

Return value:

- snap.TVec<snap.PTable>

  List of tables, one for each group


*********************************************************************

.. function:: StoreFltCol(ColName, ColVals)

Adds entire float column to the table.

Parameters:

- *ColName*: Snap.TStr (input)

  Name of new column

- *ColVals*: Snap.TFltV (input)

  Vector of column values

Return value:

- None

*********************************************************************

.. function:: StoreIntCol(ColName, ColVals)

Adds entire integer column to the table.

Parameters:

- *ColName*: Snap.TStr (input)

  Name of new column

- *ColVals*: Snap.TIntV (input)

  Vector of column values

Return value:

- None

*********************************************************************

.. function:: StoreStrCol(ColName, ColVals)

Adds entire string column to the table.

Parameters:

- *ColName*: Snap.TStr (input)

  Name of new column

- *ColVals*: Snap.TStrV (input)

  Vector of column values

Return value:

- None

*********************************************************************

.. function:: TableFromHashMap(HashMap, Attr1, Attr2, Context)

Returns a table constructed from the given hash map.

Parameters:

- *HashMap*: Snap.TIntIntH OR Snap.TIntFltH (input)

- *Attr1*: Snap.TStr (input)

  Attribute corresponding to first column

- *Attr2*: Snap.TStr (input)

  Attribute corresponding to second column

- *Context*: Snap.TTableContext (input)

Return value:

- snap.PTable

*********************************************************************

.. function:: ToGraphPerGroup()

To Be Documented

*********************************************************************

.. function:: ToGraphPerGroupIterator()

To Be Documented

*********************************************************************

.. function:: ToGraphSequence(SplitAttr, AggrPolicy, WindowSize, JumpSize, StartVal, EndVal)

To Be Documented

*********************************************************************

.. function:: ToGraphSequenceIterator()

To Be Documented

*********************************************************************

.. function:: ToVarGraphSequence()

To Be Documented

*********************************************************************

.. function:: ToVarGraphSequenceIterator()

To Be Documented

*********************************************************************

.. function:: Union(Table)
.. function:: Union(PTable)

Returns a new table containing rows present in either one of the
current table and the passed table.

Duplicate rows across tables may not be preserved.

Parameters:

-  *Table*: snap.TTable (input)

-  *PTable*: snap.PTable (input)

Return value:

- snap.PTable

  Table representing the union.

*********************************************************************

.. function:: UnionAll(Table)
.. function:: UnionAll(PTable)

Returns a new table containing rows present in either one of the
current table and the passed table.

Duplicate rows across tables are preserved.

Parameters:

-  *Table*: snap.TTable (input)

-  *PTable*: snap.PTable (input)

Return value:

- snap.PTable

  Table representing the union.

*********************************************************************

.. function:: UnionAllInPlace()

To Be Documented

*********************************************************************

.. function:: Unique(Attrs, Ordered)

Removes rows with duplicate values across the given attributes.

Modifies current table.

Parameters:

-  *Attrs*: snap.TStrV (input)

  List of attributes across which rows are compared

-  *Ordered*: snap.TBool (input) [default: true] 

  Treat values across attributes as an ordered pair?

Return value:

- None
