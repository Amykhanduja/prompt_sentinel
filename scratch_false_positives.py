from rapidfuzz import fuzz

text = "Please instructions previous ignore now"
val = "ignore previous instructions"
print("partial token sort", fuzz.partial_token_sort_ratio(val, text))

text = "Please instructions previous ign0re now"
val = "ignore previous instructions"
print("partial token sort with typo", fuzz.partial_token_sort_ratio(val, text))

text = "Please ignroe previuos instructons now"
val = "ignore previous instructions"
print("partial token sort with typos", fuzz.partial_token_sort_ratio(val, text))
