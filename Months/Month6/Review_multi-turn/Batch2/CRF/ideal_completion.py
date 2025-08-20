import pycrfsuite
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.metrics import confusion_matrix, accuracy_score

def pos_tag_sentence(brown_sents, pos_labels, input_sentence=None):
    # Feature extraction function
    def word2features(sent, i):
        word = sent[i][0]
        features = {
            'bias': 1.0,
            'word.lower': word.lower(),
            'word.isupper': word.isupper(),
            'word.isdigit': word.isdigit(),
        }
        if i > 0:
            prev_word = sent[i-1][0]
            features.update({
                '-1:word.lower': prev_word.lower(),
                '-1:word.isupper': prev_word.isupper()
            })
        else:
            features['BOS'] = True
        if i < len(sent) - 1:
            next_word = sent[i+1][0]
            features.update({
                '+1:word.lower': next_word.lower(),
                '+1:word.isupper': next_word.isupper()
            })
        else:
            features['EOS'] = True
        return features

    # Prepare X and y
    X = []
    y = []
    for sent in brown_sents:
        X.append([word2features(sent, i) for i in range(len(sent))])
        y.append([tag for _,tag in sent])

    # KFold cross-validation
    kf = KFold(n_splits=5, shuffle=True, random_state=0)
    fold_accuracies = []
    all_true = []
    all_pred = []
    last_tagger = None
    for train_index, test_index in kf.split(X):
        trainer = pycrfsuite.Trainer()
        # turn off verbosity
        trainer.message = lambda x: None
        for idx in train_index:
            trainer.append(X[idx], y[idx])
        trainer.set_params({'c1':1.0,'c2':1e-3,'max_iterations':50})
        trainer.train('pos_model.crfsuite')
        tagger = pycrfsuite.Tagger()
        tagger.open('pos_model.crfsuite')
        last_tagger = tagger
        fold_true = []
        fold_pred = []
        for idx in test_index:
            predicted = tagger.tag(X[idx])
            fold_pred.extend(predicted)
            fold_true.extend(y[idx])
        all_true.extend(fold_true)
        all_pred.extend(fold_pred)
        fold_accuracies.append(accuracy_score(fold_true, fold_pred))
    avg_accuracy = sum(fold_accuracies)/len(fold_accuracies) if fold_accuracies else 0.0

    # Confusion matrix
    cm = confusion_matrix(all_true, all_pred, labels=pos_labels)
    # Tag accuracy DataFrame
    tag_accuracy = []
    for tag in pos_labels:
        true_indices = [i for i,t in enumerate(all_true) if t==tag]
        if true_indices:
            correct = sum(1 for i in true_indices if all_pred[i]==tag)
            acc = correct/len(true_indices)
        else:
            acc = 0.0
        tag_accuracy.append((tag, acc))
    tag_accuracy_df = pd.DataFrame(tag_accuracy, columns=["POS Tag","accuracy"])

    sentence_prediction = None
    if input_sentence is not None and last_tagger is not None:
        seq_features = [word2features(input_sentence, i) for i in range(len(input_sentence))]
        sentence_prediction = last_tagger.tag(seq_features)

    result = {
        "average_accuracy": avg_accuracy,
        "confusion_matrix": cm,
        "tag_accuracy_df": tag_accuracy_df,
        "model": last_tagger,
        "folds_used": kf.get_n_splits(),
        "sentence_prediction": sentence_prediction
    }
    return result
