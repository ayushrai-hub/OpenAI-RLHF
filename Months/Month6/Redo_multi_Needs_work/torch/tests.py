import unittest
from ideal_completion import get_boxes

class TestPlateDetector(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.sample1 = {"url":"https://media.istockphoto.com/id/857228238/photo/lamborghini-huracan-sports-car-front-view.jpg?s=612x612&w=0&k=20&c=A7sKNjaSjRyhb2F6NhoCljt-GXq9ZhV9_YkhlrVIIxg=",
                        "expected":[[250.45, 273.78, 377.55, 303.01]],
                        "num_plates":1
                        }
        cls.sample2 = {"url":"https://wp.motorcheck.co.uk/app/uploads/2023/03/car-number-plate.jpg",
                        "expected":[[ 23.6710, 156.7813, 471.9489, 248.8764],[ 26.5223,  30.3469, 466.5693, 123.2232]],
                        "num_plates":2
                        }
        
        cls.sample3 = {"url":"https://www.log.com.tr/wp-content/uploads/2019/12/yerli-otomobil-kokpitine-yakin-bakisi-galeri-3.jpg",
                       "expected":[],
                       "num_plates":0
                       }
        
        cls.iou_threshold = 0.7
        
        
    def get_iou_score(self, box1, box2):
        x1, y1, x2, y2 = box1
        x3, y3, x4, y4 = box2
        
        x_overlap = max(0, min(x2, x4) - max(x1, x3))
        y_overlap = max(0, min(y2, y4) - max(y1, y3))
        
        intersection = x_overlap * y_overlap
        union = (x2 - x1) * (y2 - y1) + (x4 - x3) * (y4 - y3) - intersection
        
        return intersection / union
        
    
    def test_sample1(self):
        boxes = get_boxes(self.sample1["url"])
        self.assertEqual(len(boxes), self.sample1["num_plates"])
        for i, box in enumerate(boxes):
            iou_score = self.get_iou_score(box, self.sample1["expected"][i])
            self.assertGreaterEqual(iou_score, self.iou_threshold)
            
    def test_sample2(self):
        boxes = get_boxes(self.sample2["url"])
        self.assertEqual(len(boxes), self.sample2["num_plates"])
        
        matched = [False] * len(self.sample2["expected"])
        for box in boxes:
            for i, expected_box in enumerate(self.sample2["expected"]):
                if not matched[i]:
                    iou_score = self.get_iou_score(box, expected_box)
                    if iou_score >= self.iou_threshold:
                        matched[i] = True
                        break
        self.assertTrue(all(matched))
        
    def test_sample3(self):
        boxes = get_boxes(self.sample3["url"])
        self.assertEqual(len(boxes), self.sample3["num_plates"])
        
if __name__ == '__main__':
    unittest.main(verbosity=2)