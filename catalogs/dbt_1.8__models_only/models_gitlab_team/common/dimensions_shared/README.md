# Shared / Conformed Dimensions 

Conformed Dimensions serve as the basis for a series of interlocking stars.

1.  A conformed dimension is a dimension that has the same meaning to every fact with which it relates to. Different subject areas share conformed dimensions.
2.  Conformed dimensions allow facts and measures to be categorized and described in the same way across multiple fact tables and/or data marts, ensuring consistent analytical reporting and reusability. Allows each subject areas to be analyzed on its own and in conjunction with related with related areas. This cross-area analysis will not work if the dimensions are slightly different in each subject area.
3.  A classic example of a conformed dimension is the [dim\_date](https://gitlab-data.gitlab.io/analytics/#!/model/model.gitlab_snowflake.dim_date) model that is used across various fact tables/Subject areas such as ARR [fct\_mrr](https://gitlab-data.gitlab.io/analytics/#!/model/model.gitlab_snowflake.fct_mrr) and Salesforce Opportunities [fct\_crm\_opportunity\_daily\_snapshot](https://gitlab-data.gitlab.io/analytics/#!/model/model.gitlab_snowflake.fct_crm_opportunity_daily_snapshot). Other examples of conformed dimensions include [dim\_crm\_account](https://gitlab-data.gitlab.io/analytics/#!/model/model.gitlab_snowflake.dim_crm_account) and [dim\_subscription](https://gitlab-data.gitlab.io/analytics/#!/model/model.gitlab_snowflake.dim_subscription).
4.  Kimball refers to the set of conformed dimensions as the conformance bus.
5.  Reuse of Common Dimensions allows for reports that combine subject areas.
