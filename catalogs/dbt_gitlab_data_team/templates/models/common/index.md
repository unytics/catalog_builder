
The Common schema is where all of the facts and dimensions that compose the Enterprise Dimensional Model are stored. The Common schema contains a variety of different types of dimensions and facts that create multiple star schemas. The models in this schema are robust and provide the basis for analyzing GitLab’s businesses processes. The `Common Mart` schema contains materializations of the star schemas stored in the `Common` schema that provide the Analyst and BI Developer with easy to use and query data marts. What follows is a summary of the different types of facts and dimensions that are available in the Common Schema.

## Conformed Dimensions

Conformed Dimensions serve as the basis for a series of interlocking stars.

1.  A conformed dimension is a dimension that has the same meaning to every fact with which it relates to. Different subject areas share conformed dimensions.
2.  Conformed dimensions allow facts and measures to be categorized and described in the same way across multiple fact tables and/or data marts, ensuring consistent analytical reporting and reusability. Allows each subject areas to be analyzed on its own and in conjunction with related with related areas. This cross-area analysis will not work if the dimensions are slightly different in each subject area.
3.  A classic example of a conformed dimension is the [dim\_date](https://gitlab-data.gitlab.io/analytics/#!/model/model.gitlab_snowflake.dim_date) model that is used across various fact tables/Subject areas such as ARR [fct\_mrr](https://gitlab-data.gitlab.io/analytics/#!/model/model.gitlab_snowflake.fct_mrr) and Salesforce Opportunities [fct\_crm\_opportunity\_daily\_snapshot](https://gitlab-data.gitlab.io/analytics/#!/model/model.gitlab_snowflake.fct_crm_opportunity_daily_snapshot). Other examples of conformed dimensions include [dim\_crm\_account](https://gitlab-data.gitlab.io/analytics/#!/model/model.gitlab_snowflake.dim_crm_account) and [dim\_subscription](https://gitlab-data.gitlab.io/analytics/#!/model/model.gitlab_snowflake.dim_subscription).
4.  Kimball refers to the set of conformed dimensions as the conformance bus.
5.  Reuse of Common Dimensions allows for reports that combine subject areas.

## Local Dimensions

Local dimensions serve as the basis for analyzing one star.

1.  These dimensions have not been conformed across multiple subject areas and they cannot be shared by a series of interlocking stars in the same way that a conformed dimension could.
2.  These local dimensions can be useful if we do not want to store the attributes on the single fact table as degenerate dimensions. In that case, we can promote those dimensional attributes to a stand-alone, local dimension table.
3.  An example is [dim\_instances](https://gitlab-data.gitlab.io/analytics/#!/model/model.gitlab_snowflake.dim_instances) that contains statistical data for instances from Service ping and is specifically used in Product Usage models like [mart\_monthly\_product\_usage](https://gitlab-data.gitlab.io/analytics/#!/model/model.gitlab_snowflake.mart_monthly_product_usage).

## Atomic Facts

Facts are the things being measured in a process. The terms `measurement` or `metric` are often used instead of fact to describe what is happening in the model. The Atomic Facts are modeled at the lowest level of the process they are measuring. They do not filter out any data and include all the rows that have been generated from the process the Atomic Fact table is describing. The documentation for the models would include details about the fact table being an atomic one or a derived one.

## Derived Facts

Derived Facts are built on top of the Atomic Facts. The Derived Fact directly references the Atomic Fact thereby creating an auditable, traceable lineage. The documentation for the models would include details about the fact table being an atomic one or a derived one. There are several use cases for building a Derived Fact table:

1.  Filter a large, Atomic Fact table into smaller pieces that provide for an enhanced querying and analysis experience for Data Analytics Professionals. For example, we may have a large event table and one Business Analytics team may only need to query 10% of that data on a regular basis. Creating a Derived Fact table that essentially describes a sub-process within the larger business process the event table is measuring provides for an optimized querying experience.
2.  Precompute and aggregate commonly used aggregations of data. This is particular useful with semi-additive and non-additive measurements. For example, semi-additive metrics such as ratios cannot be summed across different aggregation grains and it is necessary to recompute the ratio at each grain. In this case, creating a Derived Fact would help insure that all Analysts and BI Developers get the same answer for the ratio analysis. Another example is with measures that are semi-additive balances such as ARR, Retention, or a Balance Sheet account balance. In those cases, creating Derived Facts that precompute answers at the required grains would help insure that all Analysts and BI Developers get the same answer for the analyses.
3.  Create `Drill Across Facts` that connect two or more facts together through Conformed Dimensions and store as a Derived Fact table. In this process, separate select statements are issued to each fact in the project and includes the Conformed Dimensions the facts have in Common. The results are combined using a Full Outer Join on the Conformed Dimensions included in the select statement results.

## Bridge Tables

Bridge(bdg\_) tables should reside in the `common` schema. These tables act as intermediate tables to resolve many-to-many relationships between two tables.