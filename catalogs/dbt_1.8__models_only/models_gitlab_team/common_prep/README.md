# Common Prep: Layer of transformation on top of Source Models

The Common Prep Schema has 6 primary use cases at this time. The use cases are as follows:

1.  Generate Surrogate Keys used in the Common Schema.
2.  Clean Source System data such as the conversion of data types and replacing `NULL` values.
3.  Apply business process logic that is needed before combining with other data in the Common Schema.
4.  Bring in Foreign Keys/Identifier fields from other models that are useful for joins in dimensions and facts in the Common Schema.
5.  Unioning data coming from multiple sources before loading into tables in the Common Schema.
6.  Breakup big data sources into smaller pieces so models can build and run in the data warehouse.
