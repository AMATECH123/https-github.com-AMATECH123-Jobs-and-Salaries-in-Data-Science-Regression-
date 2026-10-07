# Indicator definitions shared by the scenario input builder and the golden build.
# order, published label, GSS variable, response codes counted, response wording as printed in the compendium
INDICATORS = [
    ("Very happy", "happy", [1], "very happy"),
    ("Most people can be trusted", "trust", [1], "most people can be trusted"),
    ("Favours the death penalty for persons convicted of murder", "cappun", [1], "favor"),
    ("Favours a police permit before a person can buy a gun", "gunlaw", [1], "favor"),
    ("Use of marijuana should be made legal", "grass", [1], "should be legal"),
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
    ("A person with an incurable disease has the right to end their own life", "suicide1", [1], "yes"),
    ("The Bible is the actual word of God", "bible", [1], "word of god"),
    ("People get ahead by their own hard work", "getahead", [1], "hard work most important"),
    ("A good idea for older people to share a home with their grown children", "aged", [1], "a good idea"),
]
FIRST_YEAR, BASE_YEAR, EDITION_YEAR = 1987, 2014, 2024
