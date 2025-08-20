import unittest
from ideal_completion import pos_tag_sentence

class TestPOSTagging(unittest.TestCase):

    def setUp(self):
        # Larger mock dataset structure similar to the Brown corpus for 5-fold CV
        self.mock_brown_sents = [
            [('The', 'DET'), ('jury', 'NOUN'), ('said', 'VERB'), ('the', 'DET'), ('investigation', 'NOUN')],
            [('This', 'DET'), ('is', 'VERB'), ('a', 'DET'), ('test', 'NOUN')],
            [('An', 'DET'), ('example', 'NOUN'), ('sentence', 'NOUN')],
            [('Another', 'DET'), ('mock', 'NOUN'), ('sentence', 'NOUN')],
            [('Yet', 'ADV'), ('another', 'DET'), ('example', 'NOUN')],
            [('A', 'DET'), ('simple', 'ADJ'), ('test', 'NOUN')],
            [('One', 'NUM'), ('more', 'ADJ'), ('sentence', 'NOUN')],
            [('Sample', 'NOUN'), ('data', 'NOUN')],
        ]
        self.mock_pos_labels = ['DET', 'NOUN', 'VERB', 'ADV', 'ADJ', 'NUM']

    def test_confusion_matrix(self):
        # Test if the confusion matrix is produced as asked by the user
        output = pos_tag_sentence(self.mock_brown_sents, self.mock_pos_labels)
        confusion_matrix = output["confusion_matrix"]
        
        # Check if the confusion matrix shape is correct
        self.assertEqual(confusion_matrix.shape, (len(self.mock_pos_labels), len(self.mock_pos_labels)))

    def test_k_fold(self):
        # Test that 5-fold cross-validation is used, as asked by the user
        output = pos_tag_sentence(self.mock_brown_sents, self.mock_pos_labels)
        self.assertEqual(output["folds_used"], 5, "5-fold cross-validation should be used.")

    def test_accuracy_per_pos_tag(self):
        # Test if the accuracy value is produced for each pos
        output = pos_tag_sentence(self.mock_brown_sents, self.mock_pos_labels)
        tag_accuracy_df = output["tag_accuracy_df"]
        
        # Each POS tag should have an accuracy value
        self.assertEqual(len(tag_accuracy_df), len(self.mock_pos_labels))

        for tag in self.mock_pos_labels:
            self.assertIn(tag, tag_accuracy_df['POS Tag'].values, 
                          f"Missing accuracy for POS tag: {tag}")

    def test_sentence_tagging(self):
        # Test POS tagging for an untagged input sentence
        sample_sentence = [('This',), ('is',), ('a',), ('test',)]  # Untagged sample sentence
        expected_tags = ['DET', 'VERB', 'DET', 'NOUN']  # Expected POS tags for each word based on the mock data

        
        output = pos_tag_sentence(self.mock_brown_sents, self.mock_pos_labels, input_sentence=sample_sentence)
        sentence_prediction = output["sentence_prediction"]

        # Ensure the predictions are converted to lists if they are NumPy arrays
        sentence_prediction = list(sentence_prediction)
        expected_tags = list(expected_tags)  


        # Ensure the length of predictions matches the number of words in the sentence
        self.assertEqual(len(sentence_prediction), len(sample_sentence), 
                        "Predictions for input sentence should match the number of words.")

        # Check if predicted tags match the expected tags
        self.assertEqual(sentence_prediction, expected_tags, 
                        f"Expected tags {expected_tags} but got {sentence_prediction}")


if __name__ == '__main__':
    unittest.main(verbosity=2)