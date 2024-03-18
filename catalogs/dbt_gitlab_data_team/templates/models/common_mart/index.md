Marts are a combination of dimensions and facts that are joined together and used by business entities for insights and analytics. They are often grouped by business units such as marketing, finance, product, and sales. When a model is in this directory, it communicates to business stakeholders that the data is cleanly modelled and is ready for querying.

Below are some guidelines to follow when building marts:

1.  Following the naming convention for fact and dimension tables, all marts should start with the prefix `mart_`.
2.  Marts should not be built on top of other marts and should be built using FCT and DIM tables.

