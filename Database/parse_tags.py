import pandas as pd

# 1) Load the CSV
df_tags = pd.read_csv("tags_parsed.csv")

# 2) Inspect the DataFrame
print("DataFrame head:")
print(df_tags.head())

# If 'Tag URL' is the column containing "/tags/..." strings:
# 3) Extract the substring after "/tags/"
df_tags["tag_name"] = df_tags["Tag URL"].str.replace("/tags/", "", regex=False)

# Now df_tags looks like:
#   Tag URL        | tag_name
#   /tags/artifacts| artifacts
#   /tags/treasure | treasure
#   /tags/tokens   | tokens
#   ...            | ...

# 4) Get a list of all tags
list_of_tags = df_tags["tag_name"].tolist()

print("\nList of parsed tag names:")
print(list_of_tags)

# 5) Optional: if you just need the unique tags as a set
unique_tags = set(list_of_tags)

print("\nNumber of unique tags:", len(unique_tags))
