##############################
# Test comparison of mismatched texts
# The first text in the spreadsheet is compared
# against all the content.
#
# The first comparison is like text with the rest
# being mismatched.

MISALIGN = False

# Remove stopwords from the text
STOPWORDS = True

##############################


import warnings

from bert_score import score

import nltk

if STOPWORDS:
    from nltk.corpus import stopwords


from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    inspect,
    update,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select

# Strip out stopwords
if STOPWORDS:
    stopen = stopwords.words("english")
    stopes = stopwords.words("spanish")
    stopfr = stopwords.words("french")

warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")

# Pull down some models to tag parts of speech in Spanish, French and English
# nltk.download("averaged_perceptron_tagger")
# nltk.download("punkt")
# nltk.download('french_UD_POS_Tagger')
# nltk.download('conll2002')



def newcompare(text1, text2, language):
    return 0


# def justnouns(text, language):
#     if language=="en":
#         language=="eng"
#     elif language=="es":
#         language="spa"
#     elif language=="fr":
#         language="fra"
#     words = nltk.word_tokenize(text)
#     tagged_words = nltk.pos_tag(words, lang=language)
#     nouns = [word for word, pos in tagged_words if pos in ['NN', 'NNS']]
#     return nouns



# Compare the two text using BERTScore
def compare(text1, text2, language):

    print("Text1: ", text1)
    print("Text2: ", text2)

    if STOPWORDS:
        # Remove numbers from the text
        # text1=''.join([c for c in text1 if not c.isnumeric()])
        # text2=''.join([c for c in text2 if not c.isnumeric()])

        # print(text1, text2)
        # Strip out stopwords
        if language == "en":
            text1 = " ".join([word for word in text1.split(" ") if word not in stopen])
            text2 = " ".join([word for word in text2.split(" ") if word not in stopen])
        elif language == "es":
            text1 = " ".join([word for word in text1.split(" ") if word not in stopes])
            text2 = " ".join([word for word in text2.split(" ") if word not in stopes])
        elif language == "fr":
            text1 = " ".join([word for word in text1.split(" ") if word not in stopfr])
            text2 = " ".join([word for word in text2.split(" ") if word not in stopfr])

    print("***************")
    print("Text1: ", text1)
    print("Text2: ", text2)
    text1=text1.split("\n")
    text2=text2.split("\n")

    # Pad the shorter text with empty strings
    while len(text1) > len(text2):
        text2.append("")
    while len(text1) < len(text2):
        text1.append("")

    text1=" ".join(text1)
    text2=" ".join(text2)

    length1=len(text1)
    length2=len(text2)

    print("Length1: ", length1)
    print("Length2: ", length2)

    # text1=justnouns(text1, language)
    # text2=justnouns(text2, language)

    # Return the F1 score from the comparison
    return score(
        [text1],
        [text2],
        # model_type="allenai/led-base-16384",
        # model_type="microsoft/deberta-xlarge-mnli",
        # model_type="bert-base-multilingual-cased",
        model_type="google/mt5-small",
        # model_type="t5-large",
        rescale_with_baseline=True,
        lang=language,
    )[2].item()


# Connect to SQLITEdatabase and intialize the session
dbcon = create_engine(
    'sqlite:///websites/data/websites.db'
)
Base = declarative_base()

# Database access
metadata = MetaData()
source = Table("source", metadata, autoload=True, autoload_with=dbcon)

# Each website pair has a unique id.
# Get maximum value for the pairid value for further processing
max_pairid = dbcon.execute(
    select([source.c.pairid]).order_by(source.c.pairid.desc()).limit(1)
).fetchone()[0]

# Initialize the flag variable for MISALIGN processing
flag = False

# Iterate through all the unique pairids
for i in range(1, max_pairid + 1):
    print("\n\nPairid: ", i, "\n", "------------------")

    # Get all the rows with the same pairid
    results = dbcon.execute(
        select(
            [source.c.id, source.c.english, source.c.french, source.c.spanish]
        ).where(source.c.pairid == i)
    )

    data = results.fetchall()
    returnrows = len(data)

    # If there are two rows, iterate through
    # both rows in results
    if returnrows == 2:
        rowcounter = 1

        # For loop to iterate through the rows
        for row in data:
            # Get the english and french text
            print("Rowcounter: ", rowcounter)

            if rowcounter == 1:
                if MISALIGN:
                    if not flag:
                        print("This is the first row.")
                        frozenenglish1 = row[1]
                        frozenfrench1 = row[2]
                        frozenspanish1 = row[3]
                        flag = True

                # Retrieve the first row
                english1 = row[1]
                french1 = row[2]
                spanish1 = row[3]
            else:
                # Retrieve the second row
                english2 = row[1]
                french2 = row[2]
                spanish2 = row[3]

            # Increment the row counter
            rowcounter += 1

        if MISALIGN:
            # Test comparision- only the first comparison pair is like to like
            # Subsequent comparisons are are against disparate texts
            englishscore = compare(frozenenglish1, english2, "en")
            frenchscore = compare(frozenfrench1, french2, "fr")
            spanishscore = compare(frozenspanish1, spanish2, "es")
        else:
            # Production comparision
            englishscore = compare(english1, english2, "en")
            frenchscore = compare(french1, french2, "fr")
            spanishscore = compare(spanish1, spanish2, "es")

        # englishscore = sum([x[0].item() for x in englishscore])
        # frenchscore = sum([x[0].item() for x in frenchscore])
        # spanishscore = sum([x[0].item() for x in spanishscore])

        print("English Score: ", englishscore)
        print("French Score: ", frenchscore)
        print("Spanish Score: ", spanishscore)

        # Update the database with the scores
        stmt = (
            source.update()
            .values(
                bertscoreenglish=englishscore*englishscore,
                bertscorefrench=frenchscore*frenchscore,
                bertscorespanish=spanishscore*spanishscore
            )
            .where(source.c.pairid == i)
        )
        dbcon.execute(stmt)
