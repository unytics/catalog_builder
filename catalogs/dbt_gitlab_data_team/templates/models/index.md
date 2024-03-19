# Models

The `COMMON_` schema is where our Enterprise Dimensional Model (EDM) lives. The EDM is GitLab’s centralized data model, designed to enable and support the highest levels of accuracy and quality for reporting and analytics. The data model follows the [Kimball](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/) technique, including a Bus Matrix and Entity Relationship Diagrams. Dimensional Modeling follows our [Trusted Data Development](https://handbook.gitlab.com/handbook/business-technology/data-team/data-development/#trusted-data-development) process and enables us to repeatedly produce high-quality data solutions. Our Enterprise Applications that integrate with each other are great candidates for the Kimball Dimensional Modeling Methodology. Foreign keys in a data table from a different source system is a strong indication that a `COMMON_` solution is required. If some data tables qualify for the `COMMON_` solution, then all data from that source system should be modeled in the EDM. This prevents a confusing user experience of having data from a source system modeled with different methods and patterns.


## What Is Dimensional Modeling?

Dimensional modeling is part of the Business Dimensional Lifecycle methodology developed by [Ralph Kimball](https://en.wikipedia.org/wiki/Ralph_Kimball) which includes a set of methods, techniques and concepts for use in data warehouse design.

_a logical design technique that seeks to present the data in a standard, intuitive framework that allows for high-performance access_

Dimensional Modeling is business process oriented and can be built in 4 steps:

1.  Choose the business process e.g. track monthly revenue
2.  Declare the grain e.g. per customer
3.  Identify the dimensions
4.  Identify the fact

### Fact and dimension tables

Dimensional modeling always uses the concepts of facts (measures), and dimensions (context). Facts are typically (but not always) numeric values that can be aggregated, and dimensions are groups of hierarchies and descriptors that define the facts.

In the simplest version fact table is a central table and is linked to dimensional tables with foreign keys creating a star schema. Star schema with dimensional tables linking to more dimensional tables are called snowflake schemas, multi fact tables schemas are called galaxies.

### Why is it worth using dimensional modeling

*   Dimensional Modeling has a few flavors, but the overall design is industry standard and has been used successfully for decades
*   The FACT and DIM structures result in easy to understand and access data, suitable for business teams
*   Dimensional modeling supports centralized implementation of business logic and consistent definitions across business users e.g. one source of truth of customer definition
*   The design supports ‘plug and play’ of new subject areas and in fact the model grows in power as more dimensions are added


### Naming Standards

It is critical to be intentional when organizing a self-service data environment, starting with naming conventions. The goal is to make navigating the data warehouse easy for beginner, intermediate, and advanced users. We make this possible by following these best practices:

1.  PREP TABLES: `prep_<subject>` = Used to clean raw data and prepare it for dimensional analysis.
2.  FACT TABLES: `fct_<verb>` Facts represent events or real-world processes that occur. Facts can often be identified because they represent the action or ‘verb’. (e.g. session, transaction)
3.  DIMENSION TABLES: `dim_<noun>` = dimension table. Dimensions provide descriptive context to the fact records. Dimensions can often be identified because they are ’nouns’ such as a person, place, or thing (e.g. customer, employee) The dimension attributes act as ‘adjectives’. (e.g. customer type, employee division)
4.  MART TABLES: `mart_<subject>` = Join dimension and fact tables together with minimal filters and aggregations. Because they have minimal filters and aggregations, mart tables can be used for a wide variety of reporting purposes.
5.  REPORT TABLES: `rpt_<subject>` = Can be built on top of dim, fact, and mart tables. Very specific filters are applied that make report tables applicable to a narrow subset of reporting purposes.
6.  PUMP TABLES: `pump_<subject>` = Can be built on top of dim, fact, mart, and report tables. Used for models that will be piped into a third party tool.
7.  MAP TABLES: `map_<subjects>` = Used to maintain one-to-one relationships between data that come from different sources.
8.  BRIDGE TABLES: `bdg_<subjects>` = Used to maintain many-to-many relationships between data that come from different sources. See the Kimball Group’s [documentation](https://www.kimballgroup.com/2012/02/design-tip-142-building-bridges/) for tips on how to build bridge tables.
9.  SCAFFOLD TABLES: `rpt_scaffold_<subject>` = Used to support the visualization layer by creating a template / blueprint with all the combinations of common dimensions between the desired fact tables.
10.  Singular naming should be used, e.g. dim\_customer, not dim\_customers.
11.  Use prefixes in table and column names to group like data. Data will remain logically grouped when sorted alphabetically, e.g. dim\_geo\_location, dim\_geo\_region, dim\_geo\_sub\_region.
12.  Use dimension table names in primary and foreign key naming. This makes it clear to the user what table will need to be joined to pull in additional attributes. For example, the primary key for dim\_crm\_account is dim\_crm\_account\_id. If this field appears in fct\_subscription, it will be named dim\_crm\_account\_id to make it clear the user will need to join to dim\_crm\_account to get additional account details.
13.  Dimension, fact, and mart tables are not to contain references to operational systems. We abstract the name away from the source system the data is produced into a name that describes the business entity or semantic significance of the data. For example, data from Salesforce is described as `crm` in the dimensional model and not `sfdc` or `salesforce`.

