# Local Dimensions

Local dimensions serve as the basis for analyzing one star.

1.  These dimensions have not been conformed across multiple subject areas and they cannot be shared by a series of interlocking stars in the same way that a conformed dimension could.
2.  These local dimensions can be useful if we do not want to store the attributes on the single fact table as degenerate dimensions. In that case, we can promote those dimensional attributes to a stand-alone, local dimension table.
3.  An example is [dim\_instances](https://gitlab-data.gitlab.io/analytics/#!/model/model.gitlab_snowflake.dim_instances) that contains statistical data for instances from Service ping and is specifically used in Product Usage models like [mart\_monthly\_product\_usage](https://gitlab-data.gitlab.io/analytics/#!/model/model.gitlab_snowflake.mart_monthly_product_usage).