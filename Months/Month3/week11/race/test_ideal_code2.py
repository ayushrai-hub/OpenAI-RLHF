import unittest
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from ideal_code2 import simulate_race_condition  
class TestRaceConditionSimulation(unittest.TestCase):
    def test_single_run(self):
        # It Verifies that a single run of the simulation shows evidence of a race condition
        final_balance, expected_balance = simulate_race_condition()
        self.assertNotEqual(final_balance, expected_balance, "Single run did not show race condition")

    def test_multiple_runs(self):
        # It Assess the consistency and magnitude of race conditions over multiple runs
        num_runs = 10
        discrepancies = []

        for _ in range(num_runs):
            final_balance, expected_balance = simulate_race_condition()
            discrepancy = abs(final_balance - expected_balance)
            discrepancies.append(discrepancy)

        avg_discrepancy = statistics.mean(discrepancies)
        max_discrepancy = max(discrepancies)

        print(f"\nAverage discrepancy over {num_runs} runs: {avg_discrepancy:.2f}")
        print(f"Maximum discrepancy: {max_discrepancy:.2f}")

        # Verify that there is a significant average discrepancy, indicating consistent race conditions
        self.assertGreater(avg_discrepancy, 0, "No significant race condition observed over multiple runs")

    def test_thread_count_impact(self):
        # It examines how the number of threads affects the occurrence and severity of race conditions
        # Importance: Helps understand the relationship between concurrency level and race condition likelihood
        thread_counts = [2, 5, 10, 20]
        results = {}

        for thread_count in thread_counts:
            final_balance, expected_balance = simulate_race_condition(num_threads=thread_count)
            discrepancy = abs(final_balance - expected_balance)
            results[thread_count] = discrepancy

        print("\nDiscrepancies for different thread counts:")
        for thread_count, discrepancy in results.items():
            print(f"{thread_count} threads: {discrepancy:.2f}")

        # Verify that race conditions occur for at least one thread count configuration
        self.assertTrue(any(discrepancy > 0 for discrepancy in results.values()), 
                        "No race condition observed across different thread counts")

    def test_concurrent_runs(self):
        # It simulate multiple instances of the race condition scenario running concurrently
        # Importance: Tests the behavior of the simulation under high system load and parallelism
        num_concurrent_runs = 10

        with ThreadPoolExecutor(max_workers=num_concurrent_runs) as executor:
            futures = [executor.submit(simulate_race_condition) for _ in range(num_concurrent_runs)]
            results = [future.result() for future in as_completed(futures)]

        discrepancies = [abs(final - expected) for final, expected in results]
        avg_discrepancy = statistics.mean(discrepancies)
        max_discrepancy = max(discrepancies)

        print(f"\nAverage discrepancy over {num_concurrent_runs} concurrent runs: {avg_discrepancy:.2f}")
        print(f"Maximum discrepancy in concurrent runs: {max_discrepancy:.2f}")

        # Verify that race conditions occur even when multiple simulations run concurrently
        self.assertGreater(avg_discrepancy, 0, "No significant race condition observed in concurrent runs")

if __name__ == '__main__':
    unittest.main(verbosity=2)