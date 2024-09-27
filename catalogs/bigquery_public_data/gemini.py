

PROMPT = '''
Return a list of categories and subcategories which best represent these BigQuery TABLES.
Each table must be associated with a subcategory.

'''

import vertexai
from vertexai.generative_models import GenerationConfig, GenerativeModel, Part, HarmCategory, HarmBlockThreshold, SafetySetting

vertexai.init(location="europe-west1")

model = GenerativeModel("gemini-1.5-pro-002")

safety_config = [
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=HarmBlockThreshold.OFF,
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=HarmBlockThreshold.OFF,
    ),
]




# response_schema = {
#   "title": "Categorized Tables",
#   "description": "Schema for tables organized into categories and subcategories.",
#   "type": "object",
#   "properties": {
#     "categories": {
#       "type": "array",
#       "items": {
#         "type": "object",
#         "properties": {
#           "name": {
#             "type": "string",
#             "description": "Name of the category",
#           },
#           "subcategories": {
#             "type": "array",
#             "items": {
#               "type": "object",
#               "properties": {
#                 "name": {
#                   "type": "string",
#                   "description": "Name of the subcategory",
#                 },
#                 "tables": {
#                   "type": "array",
#                   "items": {
#                     "type": "string",
#                   }
#                 }
#               },
#               "required": ["name", "tables"]
#             }
#           }
#         },
#         "required": ["name", "subcategories"]
#       }
#     }
#   },
#   "required": ["categories"]
# }


response_schema = {
  "title": "Categorized Tables",
  "description": "Schema for BigQuery tables organized into categories and subcategories.",
  "type": "object",
  "properties": {
    "categories": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "Name of the category",
          },
          "subcategories": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "name": {
                  "type": "string",
                  "description": "Name of the subcategory",
                },
                "description": {
                  "type": "string",
                  "description": "Description of the subcategory",
                },                
              },
              "required": ["name", "description"]
            }
          }
        },
        "required": ["name", "subcategories"]
      }
    }
  },
  "required": ["categories"]
}


xml = open('catalog.xml').read()
prompt = PROMPT + xml

response = model.generate_content(
    prompt, 
    safety_settings=safety_config, 
    generation_config=GenerationConfig(
        response_mime_type="application/json", response_schema=response_schema
    ),
)
print(response.text)
with open('categories.json', 'w') as f:
    f.write(response.text)

