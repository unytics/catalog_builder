# Facts Sales & Marketing

## Atomic Facts

Facts are the things being measured in a process. The terms `measurement` or `metric` are often used instead of fact to describe what is happening in the model. The Atomic Facts are modeled at the lowest level of the process they are measuring. They do not filter out any data and include all the rows that have been generated from the process the Atomic Fact table is describing. The documentation for the models would include details about the fact table being an atomic one or a derived one.

## Derived Facts

Derived Facts are built on top of the Atomic Facts. The Derived Fact directly references the Atomic Fact thereby creating an auditable, traceable lineage. The documentation for the models would include details about the fact table being an atomic one or a derived one. There are several use cases for building a Derived Fact table:

1.  Filter a large, Atomic Fact table into smaller pieces that provide for an enhanced querying and analysis experience for Data Analytics Professionals. For example, we may have a large event table and one Business Analytics team may only need to query 10% of that data on a regular basis. Creating a Derived Fact table that essentially describes a sub-process within the larger business process the event table is measuring provides for an optimized querying experience.
2.  Precompute and aggregate commonly used aggregations of data. This is particular useful with semi-additive and non-additive measurements. For example, semi-additive metrics such as ratios cannot be summed across different aggregation grains and it is necessary to recompute the ratio at each grain. In this case, creating a Derived Fact would help insure that all Analysts and BI Developers get the same answer for the ratio analysis. Another example is with measures that are semi-additive balances such as ARR, Retention, or a Balance Sheet account balance. In those cases, creating Derived Facts that precompute answers at the required grains would help insure that all Analysts and BI Developers get the same answer for the analyses.
3.  Create `Drill Across Facts` that connect two or more facts together through Conformed Dimensions and store as a Derived Fact table. In this process, separate select statements are issued to each fact in the project and includes the Conformed Dimensions the facts have in Common. The results are combined using a Full Outer Join on the Conformed Dimensions included in the select statement results.

