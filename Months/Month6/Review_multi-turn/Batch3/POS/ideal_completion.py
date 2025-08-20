import nltk  
import sklearn  
import sklearn_crfsuite  
from sklearn_crfsuite import metrics  
from sklearn.model_selection import KFold  
import pandas as pd
import numpy as np
from collections import defaultdict

nltk.download('brown')  
nltk.download('universal_tagset')  

from nltk.corpus import brown  

def word2features(sent, i):  
    word, _ = sent[i]  
    if isinstance(word, tuple):  
        word = word[0]  
    features = {  
        'bias': 1.0,  
        'word.lower()': word.lower(),  
        'word[-3:]': word[-3:],  
        'word[-2:]': word[-2:],  
        'word[:3]': word[:3],  
        'word[:2]': word[:2],  
        'word.isupper()': word.isupper(),  
        'word.istitle()': word.istitle(),  
        'word.isdigit()': word.isdigit(),  
    }  
    if i > 0:  
        prev_word, _ = sent[i - 1]  
        if isinstance(prev_word, tuple):  
            prev_word = prev_word[0]  
        features.update({  
            '-1:word.lower()': prev_word.lower(),  
            '-1:word.istitle()': prev_word.istitle(),  
            '-1:word.isupper()': prev_word.isupper(),  
        })  
    else:  
        features['BOS'] = True  

    if i < len(sent) - 1:  
        next_word, _ = sent[i + 1]  
        if isinstance(next_word, tuple):  
            next_word = next_word[0]  
        features.update({  
            '+1:word.lower()': next_word.lower(),  
            '+1:word.istitle()': next_word.istitle(),  
            '+1:word.isupper()': next_word.isupper(),  
        })  
    else:  
        features['EOS'] = True  

    return features  

def sent2features(sent):  
    return [word2features(sent, i) for i in range(len(sent))]  

def sent2labels(sent):  
    return [label for _, label in sent]  

def pos_tag_sentence(brown_sents, pos_labels, input_sentence=None):  
    X = [sent2features(sent) for sent in brown_sents]  
    y = [sent2labels(sent) for sent in brown_sents]  

    kf = KFold(n_splits=5, shuffle=True, random_state=0)  
    accuracies = []  
    total_confusion = defaultdict(lambda: defaultdict(int))  

    for train_idx, test_idx in kf.split(X):  
        X_train = [X[i] for i in train_idx]  
        y_train = [y[i] for i in train_idx]  
        X_test = [X[i] for i in test_idx]  
        y_test = [y[i] for i in test_idx]  

        crf = sklearn_crfsuite.CRF(  
            algorithm='lbfgs',  
            max_iterations=100,  
            all_possible_transitions=True  
        )  
        crf.fit(X_train, y_train)  

        y_pred = crf.predict(X_test)  

        flat_y_true = [label for sent in y_test for label in sent]  
        flat_y_pred = [label for sent in y_pred for label in sent]  

        accuracy = sklearn.metrics.accuracy_score(flat_y_true, flat_y_pred)  
        accuracies.append(accuracy)  

        labels = sorted(list(set(flat_y_true + flat_y_pred)))  

        cm = sklearn.metrics.confusion_matrix(flat_y_true, flat_y_pred, labels=labels)  

        for i, true_label in enumerate(labels):  
            for j, pred_label in enumerate(labels):  
                total_confusion[true_label][pred_label] += cm[i][j]  

    average_accuracy = np.mean(accuracies)  

    all_labels = sorted(total_confusion.keys())  
    cm_array = np.zeros((len(all_labels), len(all_labels)), dtype=int)  

    for i, true_label in enumerate(all_labels):  
        for j, pred_label in enumerate(all_labels):  
            cm_array[i][j] = total_confusion[true_label][pred_label]  

    tag_accuracy = {}  
    for idx, tag in enumerate(all_labels):  
        true_positive = cm_array[idx][idx]  
        total_true = cm_array[idx].sum()  
        tag_accuracy[tag] = true_positive / total_true if total_true > 0 else 0.0  

    tag_accuracy_df = pd.DataFrame.from_dict(tag_accuracy, orient='index', columns=['Accuracy'])  
    tag_accuracy_df.reset_index(inplace=True)  
    tag_accuracy
    tag_accuracy_df.columns = ['POS Tag', 'Accuracy']  

    result = {  
        'average_accuracy': average_accuracy,  
        'confusion_matrix': cm_array,  
        'tag_accuracy_df': tag_accuracy_df,  
        'model': crf,  
        'folds_used': 5  
    }  

    if input_sentence:  
        if isinstance(input_sentence, str):  
            tokens = input_sentence.split()  
        elif isinstance(input_sentence, list):  
            tokens = input_sentence  
        else:  
            raise TypeError("input_sentence must be a string or a list of tokens.")  

        input_features = [word2features([(word, '') for word in tokens], i)   
                          for i in range(len(tokens))]  
        prediction = crf.predict_single(input_features)  
        result['sentence_prediction'] = prediction  

    return result  
