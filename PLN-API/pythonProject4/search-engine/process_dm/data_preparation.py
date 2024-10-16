import string
import re

from spellchecker import SpellChecker
import contractions as contractions
import nltk
from nltk import word_tokenize, WordNetLemmatizer, PorterStemmer
from nltk.corpus import stopwords, wordnet


class DataPreparation:
    def __init__(self) -> None:
        self.pipeline = [
            self.lower_case,
            self.expand_contractions,
            self.remove_spaces_tabs,
            self.remove_url,
            self.remove_punct,
            self.remove_single_char,
            self.remove_html,
            self.remove_stopwords,
            # other functions...
        ]
        pass

    # REFERENCE: https://medium.com/bitgrit-data-science-publication/nlp-snippets-in-python-90ac29ffaea0#4cba

    def lower_case(self, text: str) -> str:
        return text.lower()

    def remove_spaces_tabs(self, text: str) -> str:
        return " ".join(text.split())

    def remove_punct(self, text: str) -> str:
        translator = str.maketrans("", "", string.punctuation)
        return text.translate(translator)

    def remove_single_char(self, text: str) -> str:
        return re.sub(r"\b[a-zA-Z]\b", "", text)

    def remove_html(self, text: str) -> str:
        html = re.compile(r"<.*?>")
        return html.sub(r"", text)

    def remove_url(self, text: str) -> str:
        url = re.compile(r"https?://\S+|www\.\S+")
        return url.sub(r"", text)

    def remove_stopwords(self, text: str) -> str:
        stop_words = set(stopwords.words("english"))
        stop_words.update(["time"])  # add custom stopwords
        stop_words -= {"no", "not"}  # remove custom stopwords
        word_tokens = word_tokenize(text)
        filtered_sentence = [w for w in word_tokens if not w in stop_words]
        return " ".join(filtered_sentence)

    def expand_contractions(self, text: str) -> str:
        return contractions.fix(text)

    def lemmatize_text_custom(self, text: str, lemmatizer) -> str:
        wordnet_map = {
            "J": wordnet.ADJ,
            "N": wordnet.NOUN,
            "V": wordnet.VERB,
            "R": wordnet.ADV,
        }

        w_pos_tags = nltk.pos_tag(text.split())
        lemmatized_output = " ".join(
            [lemmatizer.lemmatize(w, wordnet_map.get(pos[0], wordnet.NOUN)) for w, pos in w_pos_tags])
        return lemmatized_output

    #lemmatizer = WordNetLemmatizer()
    #lemmatize_text_custom("Lemmatizing removes the affixes of a sentence", lemmatizer)

    def stem_text_custom(self, text: str, stemmer) -> str:
        word_tokens = word_tokenize(text)
        stemmed_output = " ".join([stemmer.stem(w) for w in word_tokens])
        return stemmed_output

    #stemmer = PorterStemmer()
    #stem_text_custom("Stemming removes the affixes of a sentence", stemmer)

    def correct_spelling(self, text: str) -> str:
        spell = SpellChecker()
        corrected_text = []
        misspelled_words = spell.unknown(text.split())
        for word in text.split():
            if word in misspelled_words:
                # if correction is none return the original word
                if spell.correction(word) is not None:
                    corrected_text.append(spell.correction(word))
                else:
                    corrected_text.append(word)
            else:
                corrected_text.append(word)
        return " ".join(corrected_text)

    #correct_spelling("spellling is a big probllem")



    def prepare(self, text, pipeline, lemmatizer=None, stemmer=None):
        tokens = text
        for transform in pipeline:
            # if lemmatize or stem function pass in, perform transformation
            if transform.__name__ == "lemmatize_text_custom":
                tokens = transform(tokens, lemmatizer)
            elif transform.__name__ == "stem_text_custom":
                tokens = transform(tokens, stemmer)
            else:
                tokens = transform(tokens)
        return tokens


    def prepareAll(self, documents):
        processed_documents = []
        for document in documents:
            processed_document = self.prepare(document, self.pipeline)
            processed_documents.append(processed_document)
        return processed_documents



