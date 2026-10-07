# Indicator definitions shared by the scenario input builder and the golden build.
# order, published label, GSS variable, response codes counted, response wording as printed in the compendium
INDICATORS = [
    ("Very happy", "happy", [1], "very happy"),
    ("Own health is excellent", "health", [1], "excellent"),
    ("Favours the death penalty for persons convicted of murder", "cappun", [1], "favor"),
    ("Favours a police permit before a person can buy a gun", "gunlaw", [1], "favor"),
    ("A great deal of confidence in the people running television", "contv", [1], "a great deal"),
    ("Abortion should be possible if the woman wants it for any reason", "abany", [1], "yes"),
    ("Too little is being spent on welfare", "natfare", [1], "too little"),
    ("Too little is being spent on improving and protecting the environment", "natenvir", [1], "too little"),
    ("Too little is being spent on parks and recreation", "natpark", [1], "too little"),
    ("Pretty well satisfied with present financial situation", "satfin", [1], "pretty well satisfied"),
    ("Afraid to walk alone at night within a mile of home", "fear", [1], "yes"),
    ("Liberal", "polviews", [1, 2, 3], "extremely liberal, liberal or slightly liberal"),
    ("Democrat, including independents close to the Democrats", "partyid", [0, 1, 2], "strong democrat, not very strong democrat, or independent close to democrat"),
    ("No religious preference", "relig", [4], "none"),
    ("A great deal of confidence in the people running the press", "conpress", [1], "a great deal"),
    ("A great deal of confidence in the people running medicine", "conmedic", [1], "a great deal"),
    ("Moderate, middle of the road", "polviews", [4], "moderate, middle of the road"),
    ("Identifies with the lower class", "class", [1], "lower class"),
    ("Strongly agrees that America is a better country than most other countries", "ambetter", [1], "strongly agree"),
    ("A good idea for older people to share a home with their grown children", "aged", [1], "a good idea"),
]
FIRST_YEAR, BASE_YEAR, EDITION_YEAR = 1987, 2014, 2024
