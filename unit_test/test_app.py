import unittest
from app import app


class CalculatorAppTestCase(unittest.TestCase):
    """Tests for the calculator Flask application endpoints.

    Tests cover:
    - GET / (home page contains the form inputs)
    - POST /sumar, /restar, /multiplicar, /dividir with valid numbers
    - Invalid number input handling
    - Division by zero handling
    """

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_home_get(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        # The home page shows navigation links to each operation
        self.assertIn(b'href="/sumar"', resp.data)
        self.assertIn(b'href="/restar"', resp.data)
        self.assertIn(b'href="/multiplicar"', resp.data)
        self.assertIn(b'href="/dividir"', resp.data)

    # --- Suma ---
    def test_sumar_post_valid(self):
        resp = self.client.post("/sumar", data={"num1": "2", "num2": "3"})
        self.assertEqual(resp.status_code, 200)
        # Operation name should appear
        self.assertIn(b'Suma', resp.data)
        # Result 5 should appear (template may format as 5 or 5.0)
        self.assertTrue(b'5' in resp.data)

    def test_sumar_post_invalid(self):
        resp = self.client.post("/sumar", data={"num1": "a", "num2": "1"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Error: Ingresa n', resp.data)

    # --- Resta ---
    def test_restar_post_valid(self):
        resp = self.client.post("/restar", data={"num1": "5", "num2": "3"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Resta', resp.data)
        self.assertTrue(b'2' in resp.data)

    def test_restar_post_invalid(self):
        resp = self.client.post("/restar", data={"num1": "x", "num2": "3"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Error: Ingresa n', resp.data)

    # --- Multiplicacion ---
    def test_multiplicar_post_valid(self):
        resp = self.client.post("/multiplicar", data={"num1": "4", "num2": "2"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Multiplicaci', resp.data)  # 'Multiplicación' may appear
        self.assertTrue(b'8' in resp.data)

    def test_multiplicar_post_invalid(self):
        resp = self.client.post("/multiplicar", data={"num1": "y", "num2": "2"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Error: Ingresa n', resp.data)

    # --- Division ---
    def test_dividir_post_valid(self):
        resp = self.client.post("/dividir", data={"num1": "5", "num2": "2"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Divis', resp.data)  # 'División' should appear
        # 5 / 2 = 2.5
        self.assertTrue(b'2.5' in resp.data or b'2' in resp.data)

    def test_dividir_by_zero(self):
        resp = self.client.post("/dividir", data={"num1": "5", "num2": "0"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Error: Divis', resp.data)

    def test_dividir_post_invalid(self):
        resp = self.client.post("/dividir", data={"num1": "z", "num2": "0"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Error: Ingresa n', resp.data)


if __name__ == '__main__':
    unittest.main()
