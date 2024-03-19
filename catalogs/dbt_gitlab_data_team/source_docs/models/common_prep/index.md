# Common Prep: Layer of transformation on top of Source Models

The Common Prep Schema has 6 primary use cases at this time. The use cases are as follows:

1.  Generate Surrogate Keys used in the Common Schema.
2.  Clean Source System data such as the conversion of data types and replacing `NULL` values.
3.  Apply business process logic that is needed before combining with other data in the Common Schema.
4.  Bring in Foreign Keys/Identifier fields from other models that are useful for joins in dimensions and facts in the Common Schema.
5.  Unioning data coming from multiple sources before loading into tables in the Common Schema.
6.  Breakup big data sources into smaller pieces so models can build and run in the data warehouse.

In order to keep the `COMMON_PREP` schema streamlined and without unnecessary redundancies, we need to have guidelines and preferences for developing models in the Common Prep Schema. As Developers work through the use cases mentioned above, they should take into consideration the below guidelines when developing models in the `COMMON_PREP` schema. The `COMMON_PREP` schema is optional and it is not a requirement that every lineage have a model built in the `COMMON_PREP` schema. However, the `COMMON_PREP` schema is useful to resolve the above mentioned use cases while keeping the data model DRY (Do not repeat yourself) and maintaining a SSOT for business entity use cases.

1.  Prefer to have one Prep Model per dimensional entity in the `COMMON` schema. For example, prefer to only have `prep_charge` and NOT a `prep_charge` and `prep_recurring_charge`. The 2nd `prep_recurring_charge` is a filtered down and aggregated version of `prep_charge`. In this case, `prep_recurring_charge` should instead be built as either a `FACT`, `MART`, or `REPORT` downstream in the lineage of `prep_charge`. Doing this will streamline the lineages, keep code DRY, and prevent extra layers and redundancy in the `COMMON_PREP` schema. Multiple Prep models in this case results in the Developer having to update code in both Prep models.
    
2.  Prefer to keep the Prep model at the lowest grain of the dimensional entity it is representing in the `COMMON_PREP` schema. This allows it to be the SSOT Prep model for the lineage where additional dimensional and reporting models can be built downstream from it either in a `DIM`, `FACT`, `MART`, `MAPPING`, `BDG` or `REPORT` table. Pre-aggregating data in the `COMMON_PREP` schema renders the Prep model not useful to build models in the `COMMON` schema that would be at a lower grain.
    
3.  Prefer to not filter records out of the Prep Model in the `COMMON_PREP` schema. This allows it to be the SSOT Prep model for the lineage where additional dimensional and reporting models can be built downstream from it either in a `DIM`, `FACT`, `MART`, `MAPPING`, `BDG` or `REPORT` table. Prefer to start filtering out data in the `COMMON` schema and subsequent downstream models. Filtering out data in the `COMMON_PREP` schema renders the Prep model not useful to build models in the `COMMON` schema that would require the data that was filtered out too early in the `COMMON_PREP` schema.
    
4.  Prefer to not make a model in the `COMMON_PREP` schema that is only for the sake of following the same pattern of having Prep models. For example, if a dimension table is built in the `COMMON` schema and is only built by doing a `SELECT *` from the table in the `COMMON_PREP` schema, then it may be the case that the Prep model is not needed and we can build that model directly in the `COMMON` schema.