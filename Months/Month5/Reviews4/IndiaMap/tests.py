import unittest
from Ideal_completion import get_india_map
class TestIndiaMap(unittest.TestCase):

    def test_india_map_shape(self):
        # The actual map you are comparing
        india_map_ = """
                   ............
                  .            .     .... 
                    .            .  .    .
                     .             .     .  
                      .                 .
                     .                . 
                    .  .             .
                     .                .
                    .                   .                             ..   ..
                   .                      .                         ..   .   .
                  .                      .                        .            .
          ..    .                          .          .         .                .
         .  .  .                              .      .  .        ..            .
        .   ...                                  . . .  .........            .
         .                                             .                    .
           .                                          .  . .               . 
   .........                                         .      .......       .
    .                                                .            . .   ...
      ...       .                                   .            . .  . .
       .       .  .                                .                   ..
    .         .    .                              .   
      .......       .                            .
                    .                           .
                     .                         . 
                      .                       .
                       .                     .
                        .                   .
                         .                 .
                          .               .
                           .             .
                            .           .
                             .           .
                              .         .
                               .       .
                                .     .
                                 .   .
                                  ...
        """

        # Compare the actual map to the expected map
        self.assertEqual(get_india_map().strip(), india_map_.strip())

if __name__ == '__main__':
    unittest.main(verbosity=2)
